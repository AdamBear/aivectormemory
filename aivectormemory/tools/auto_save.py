import json
import os
from aivectormemory.config import DEDUP_THRESHOLD
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.task_repo import TaskRepo
from aivectormemory.errors import success_response

DIGEST_TASK_TITLE = "归纳 {count} 条碎片记忆"
DEFAULT_DIGEST_THRESHOLD = 20

DIGEST_HINT = (
    "⚠️ 碎片记忆已达 {count} 条，请立即执行归纳：\n"
    "1. 调用 digest（scope: project, compress: true）获取碎片列表\n"
    "2. 将同主题碎片合并为精炼摘要，用 remember 写回\n"
    "3. 用 forget 删除已合并的碎片\n"
    "4. 保留关键决策和踩坑记录，不要丢失重要信息"
)

CATEGORY_TAG_MAP = {
    "decisions": "decision",
    "modifications": "modification",
    "pitfalls": "pitfall",
    "todos": "todo",
    "preferences": "preference",
}

CATEGORY_SCOPE_OVERRIDE = {
    "preferences": "user",
}


def handle_auto_save(args, *, cm, engine, session_id, **_):
    scope = args.get("scope", "project")
    repo = MemoryRepo(cm.conn, cm.project_dir)
    saved = []

    for category, tag in CATEGORY_TAG_MAP.items():
        items = args.get(category, [])
        if not isinstance(items, list):
            continue
        cat_scope = CATEGORY_SCOPE_OVERRIDE.get(category, scope)
        for item in items:
            if not item or not isinstance(item, str):
                continue
            item = item[:5000] if len(item) > 5000 else item
            embedding = engine.encode(item)
            tags = [tag] + args.get("extra_tags", [])
            result = repo.insert(item, tags, cat_scope, session_id, embedding, DEDUP_THRESHOLD, source="auto_save")
            saved.append({"id": result["id"], "action": result["action"], "category": category})

    result = success_response(saved=saved, count=len(saved))
    hint = _check_digest_threshold(cm, repo)
    if hint:
        result["digest_hint"] = hint
    return json.dumps(result)


def _check_digest_threshold(cm, repo):
    threshold = int(os.environ.get("AVM_DIGEST_THRESHOLD", DEFAULT_DIGEST_THRESHOLD))
    count = repo.count_by_source("auto_save")
    if count < threshold:
        return None
    task_repo = TaskRepo(cm.conn, cm.project_dir)
    existing = task_repo.list_by_feature(feature_id="_sys/digest", status="pending")
    if not existing:
        title = DIGEST_TASK_TITLE.format(count=count)
        task_repo.batch_create("_sys/digest", [{"title": title, "sort_order": 0}], task_type="system")
    return DIGEST_HINT.format(count=count)
