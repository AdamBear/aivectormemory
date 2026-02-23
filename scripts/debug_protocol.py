import json, subprocess, tempfile, os

with tempfile.TemporaryDirectory() as tmpdir:
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    ]
    input_data = "\n".join(json.dumps(m) for m in msgs) + "\n"
    env = {**os.environ, "HF_ENDPOINT": "https://hf-mirror.com"}
    proc = subprocess.run(
        [".venv/bin/python", "-m", "aivectormemory", "--project-dir", tmpdir],
        input=input_data, capture_output=True, text=True, timeout=30, env=env
    )
    print("STDOUT:", proc.stdout[:2000])
    print("STDERR:", proc.stderr[:2000])
    print("RETURNCODE:", proc.returncode)
