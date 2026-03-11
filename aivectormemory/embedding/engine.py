import os
import sys
import numpy as np
from functools import lru_cache
from pathlib import Path
from aivectormemory.config import MODEL_NAME, MODEL_DIMENSION, DB_DIR
from aivectormemory.log import log

QUANTIZED_DIR = DB_DIR / "models"
QUANTIZED_FILENAME = "model_int8.onnx"


class EmbeddingEngine:
    def __init__(self):
        self._session = None
        self._tokenizer = None
        self._encode_cached = lru_cache(maxsize=1024)(self._encode_impl)

    @property
    def ready(self) -> bool:
        return self._session is not None

    def load(self):
        if self.ready:
            return
        try:
            from huggingface_hub import hf_hub_download
            from tokenizers import Tokenizer
            import onnxruntime as ort

            model_dir = self._download_model(hf_hub_download)
            self._tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
            self._tokenizer.enable_padding()
            self._tokenizer.enable_truncation(max_length=512)

            fp32_path = model_dir / "model.onnx"
            if not fp32_path.exists():
                fp32_path = model_dir / "onnx" / "model.onnx"

            model_path = self._get_quantized_model(fp32_path)

            self._session = ort.InferenceSession(
                str(model_path),
                providers=["CPUExecutionProvider"]
            )
            log.info("Embedding model loaded: %s (quantized=%s)", MODEL_NAME, model_path != fp32_path)
        except Exception as e:
            log.error("Failed to load embedding model: %s", e)
            raise

    def _download_model(self, hf_hub_download) -> Path:
        from huggingface_hub import snapshot_download
        model_dir = Path(snapshot_download(
            MODEL_NAME,
            allow_patterns=["tokenizer.json", "tokenizer_config.json",
                           "model.onnx", "onnx/model.onnx",
                           "special_tokens_map.json", "config.json"]
        ))
        return model_dir

    def _get_quantized_model(self, fp32_path: Path) -> Path:
        quantized_path = QUANTIZED_DIR / QUANTIZED_FILENAME
        if quantized_path.exists():
            return quantized_path
        tmp_path = quantized_path.with_suffix(".tmp")
        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            QUANTIZED_DIR.mkdir(parents=True, exist_ok=True)
            log.info("Quantizing model to INT8 (first time only)...")
            quantize_dynamic(str(fp32_path), str(tmp_path), weight_type=QuantType.QInt8)
            tmp_path.rename(quantized_path)
            log.info("Quantized model saved: %s (%.0fMB -> %.0fMB)",
                     quantized_path,
                     fp32_path.stat().st_size / 1024 / 1024,
                     quantized_path.stat().st_size / 1024 / 1024)
            return quantized_path
        except Exception as e:
            log.warning("INT8 quantization unavailable (%s), using FP32 model", e)
            if tmp_path.exists():
                tmp_path.unlink()
            return fp32_path

    def encode(self, text: str) -> list[float]:
        if not self.ready:
            self.load()
        return list(self._encode_cached(text))

    def _encode_impl(self, text: str) -> tuple[float, ...]:
        prefixed = f"query: {text}"
        encoded = self._tokenizer.encode(prefixed)

        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)

        outputs = self._session.run(
            None,
            {"input_ids": input_ids, "attention_mask": attention_mask, "token_type_ids": token_type_ids}
        )

        hidden = outputs[0]
        mask_expanded = attention_mask[:, :, np.newaxis].astype(np.float32)
        summed = (hidden * mask_expanded).sum(axis=1)
        counts = mask_expanded.sum(axis=1).clip(min=1e-9)
        pooled = summed / counts

        norm = np.linalg.norm(pooled, axis=1, keepdims=True).clip(min=1e-9)
        normalized = (pooled / norm)[0]

        return tuple(normalized.tolist())

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.encode(t) for t in texts]
