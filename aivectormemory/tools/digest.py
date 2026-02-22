import json
from aivectormemory.config import USER_SCOPE_DIR
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.errors import success_response

COMPRESS_HINT = (
    "请对以上记忆执行归纳压缩：\n"
    "1. 将同主题的碎片记忆合并为一条精炼摘要\n"
    "2. 标记/清理过时记忆（如已归档 issue 的待修复记录）\n"
    "3. 归纳结果用 remember 写回，碎片用 forget 删除\n"
    "4. 保留关键决策和踩坑记录，不要丢失重要信息"
)


MAX_CONTENT_LEN = 500
DEFAULT_MAX_CHARS = 8000


def handle_digest(args, *, cm, session_id, **_):
    scope = args.get("scope", "project")
    since = args.get("since_sessions", 20)
    tags = args.get("tags")
    compress = args.get("compress", False)
    limit = args.get("limit", 50)
    max_chars = args.get("max_chars", DEFAULT_MAX_CHARS)

    start_sid = max(1, session_id - since + 1)
    end_sid = session_id

    repo = MemoryRepo(cm.conn, cm.project_dir)
    pdir = USER_SCOPE_DIR if scope == "user" else cm.project_dir
    rows = repo.get_by_session_range(start_sid, end_sid, project_dir=pdir)

    all_matched = []
    for r in rows:
        if tags:
            mem_tags = json.loads(r.get("tags", "[]")) if isinstance(r.get("tags"), str) else r.get("tags", [])
            if not any(t in mem_tags for t in tags):
                continue
        all_matched.append(r)

    total = len(all_matched)
    truncated, char_count = [], 0
    for r in all_matched[:limit]:
        content = r["content"]
        if len(content) > MAX_CONTENT_LEN:
            content = content[:MAX_CONTENT_LEN] + "..."
        if char_count + len(content) > max_chars and truncated:
            break
        char_count += len(content)
        truncated.append({"id": r["id"], "content": content, "tags": r["tags"], "created_at": r["created_at"]})

    remaining = total - len(truncated)

    result = success_response(
        memories=truncated, total_count=total, returned_count=len(truncated),
        remaining=remaining, session_range={"start": start_sid, "end": end_sid},
        char_count=char_count, max_chars=max_chars
    )
    if compress:
        result["compress_hint"] = COMPRESS_HINT
    return json.dumps(result)
