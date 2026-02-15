import json
from urllib.parse import urlparse, parse_qs
from aivectormemory.config import USER_SCOPE_DIR
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.state_repo import StateRepo
from aivectormemory.db.issue_repo import IssueRepo


def _resolve_project(cm, params):
    """如果 URL 带 ?project=xxx 则覆盖 cm.project_dir，返回临时 project_dir"""
    override = params.get("project", [None])[0]
    return override if override is not None else cm.project_dir


def handle_api_request(handler, cm):
    parsed = urlparse(handler.path)
    path = parsed.path
    params = parse_qs(parsed.query)
    pdir = _resolve_project(cm, params)

    routes = {
        "GET": {
            "/api/memories": lambda: get_memories(cm, params, pdir),
            "/api/status": lambda: get_status(cm, pdir),
            "/api/issues": lambda: get_issues(cm, params, pdir),
            "/api/stats": lambda: get_stats(cm, pdir),
            "/api/tags": lambda: get_tags(cm, params, pdir),
            "/api/projects": lambda: get_projects(cm),
        },
        "PUT": {
            "/api/status": lambda: put_status(handler, cm, pdir),
            "/api/tags/rename": lambda: rename_tag(handler, cm, pdir),
            "/api/tags/merge": lambda: merge_tags(handler, cm, pdir),
        },
        "DELETE": {
            "/api/memories": lambda: delete_memories_batch(handler, cm, pdir),
            "/api/tags/delete": lambda: delete_tags(handler, cm, pdir),
        },
    }

    method = handler.command
    if path.startswith("/api/memories/") and len(path.split("/")) == 4:
        mid = path.split("/")[3]
        if method == "GET":
            return _json_response(handler, get_memory_detail(cm, mid, pdir))
        elif method == "PUT":
            return _json_response(handler, put_memory(handler, cm, mid, pdir))
        elif method == "DELETE":
            return _json_response(handler, delete_memory(cm, mid, pdir))

    if path.startswith("/api/issues/") and len(path.split("/")) == 4:
        iid = int(path.split("/")[3])
        if method == "PUT":
            return _json_response(handler, put_issue(handler, cm, iid, pdir))

    route_fn = routes.get(method, {}).get(path)
    if route_fn:
        _json_response(handler, route_fn())
    else:
        handler.send_error(404, "API not found")


def _read_body(handler) -> dict:
    length = int(handler.headers.get("Content-Length", 0))
    return json.loads(handler.rfile.read(length)) if length else {}


def _json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", len(body))
    handler.end_headers()
    handler.wfile.write(body)


def get_memories(cm, params, pdir):
    scope = params.get("scope", ["all"])[0]
    query = params.get("query", [None])[0]
    tag = params.get("tag", [None])[0]
    limit = int(params.get("limit", [100])[0])
    offset = int(params.get("offset", [0])[0])

    repo = MemoryRepo(cm.conn, pdir)
    filter_dir = pdir if scope == "project" else (USER_SCOPE_DIR if scope == "user" else None)

    if tag:
        all_rows = repo.list_by_tags([tag], scope=scope, project_dir=filter_dir or USER_SCOPE_DIR, limit=9999)
        total = len(all_rows)
        results = all_rows[offset:offset + limit]
    else:
        rows = repo.get_all(limit=limit, offset=offset, project_dir=filter_dir)
        total = repo.count(project_dir=filter_dir)
        results = [r for r in rows if not query or query.lower() in r.get("content", "").lower()] if query else rows

    return {"memories": results, "total": total}


def get_memory_detail(cm, mid, pdir):
    repo = MemoryRepo(cm.conn, pdir)
    mem = repo.get_by_id(mid)
    return mem or {"error": "not found"}


def put_memory(handler, cm, mid, pdir):
    body = _read_body(handler)
    repo = MemoryRepo(cm.conn, pdir)
    mem = repo.get_by_id(mid)
    if not mem:
        return {"error": "not found"}
    now = repo._now()
    updates = {}
    if "content" in body:
        updates["content"] = body["content"]
    if "tags" in body:
        updates["tags"] = json.dumps(body["tags"])
    if updates:
        updates["updated_at"] = now
        set_clause = ",".join(f"{k}=?" for k in updates)
        cm.conn.execute(f"UPDATE memories SET {set_clause} WHERE id=?", [*updates.values(), mid])
        cm.conn.commit()
    return repo.get_by_id(mid)


def delete_memory(cm, mid, pdir):
    repo = MemoryRepo(cm.conn, pdir)
    if repo.delete(mid):
        return {"deleted": True, "id": mid}
    return {"error": "not found"}


def delete_memories_batch(handler, cm, pdir):
    body = _read_body(handler)
    ids = body.get("ids", [])
    repo = MemoryRepo(cm.conn, pdir)
    deleted = [mid for mid in ids if repo.delete(mid)]
    return {"deleted_count": len(deleted), "ids": deleted}


def get_status(cm, pdir):
    repo = StateRepo(cm.conn, pdir)
    state = repo.get()
    return state or {"empty": True}


def put_status(handler, cm, pdir):
    body = _read_body(handler)
    repo = StateRepo(cm.conn, pdir)
    return repo.upsert(**body)


def get_issues(cm, params, pdir):
    date = params.get("date", [None])[0]
    status = params.get("status", [None])[0]
    include_archived = params.get("include_archived", ["false"])[0] == "true"
    repo = IssueRepo(cm.conn, pdir)
    if status == "archived":
        issues = repo.list_archived(date=date)
    elif status:
        issues = repo.list_by_date(date=date, status=status)
    else:
        issues = repo.list_by_date(date=date) + repo.list_archived(date=date)
    return {"issues": issues}


def put_issue(handler, cm, iid, pdir):
    body = _read_body(handler)
    repo = IssueRepo(cm.conn, pdir)
    result = repo.update(iid, **body)
    return result or {"error": "not found"}


def get_stats(cm, pdir):
    repo = MemoryRepo(cm.conn, pdir)
    issue_repo = IssueRepo(cm.conn, pdir)

    proj_count = repo.count(project_dir=pdir)
    user_count = repo.count(project_dir=USER_SCOPE_DIR)
    total_count = repo.count()

    all_issues = issue_repo.list_by_date()
    status_counts = {}
    for i in all_issues:
        s = i["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    archived_issues = issue_repo.list_archived()
    status_counts["archived"] = len(archived_issues)

    tag_counts = {}
    for m in repo.get_all(limit=1000):
        mtags = json.loads(m.get("tags", "[]")) if isinstance(m.get("tags"), str) else m.get("tags", [])
        for t in mtags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    return {
        "memories": {"project": proj_count, "user": user_count, "total": total_count},
        "issues": status_counts,
        "tags": tag_counts,
    }


def get_tags(cm, params, pdir):
    query = params.get("query", [None])[0]
    repo = MemoryRepo(cm.conn, pdir)
    all_mems = repo.get_all(limit=10000)
    tag_counts = {}
    for m in all_mems:
        mtags = json.loads(m.get("tags", "[]")) if isinstance(m.get("tags"), str) else m.get("tags", [])
        for t in mtags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
    tags = [{"name": k, "count": v} for k, v in sorted(tag_counts.items(), key=lambda x: -x[1])]
    if query:
        q = query.lower()
        tags = [t for t in tags if q in t["name"].lower()]
    return {"tags": tags, "total": len(tags)}


def rename_tag(handler, cm, pdir):
    body = _read_body(handler)
    old_name = body.get("old_name", "")
    new_name = body.get("new_name", "").strip()
    if not old_name or not new_name:
        return {"error": "old_name and new_name required"}
    repo = MemoryRepo(cm.conn, pdir)
    updated = 0
    for m in repo.get_all(limit=10000):
        tags = json.loads(m["tags"]) if isinstance(m.get("tags"), str) else m.get("tags", [])
        if old_name in tags:
            tags = [new_name if t == old_name else t for t in tags]
            tags = list(dict.fromkeys(tags))  # dedup
            cm.conn.execute("UPDATE memories SET tags=?, updated_at=? WHERE id=?",
                            (json.dumps(tags, ensure_ascii=False), repo._now(), m["id"]))
            updated += 1
    cm.conn.commit()
    return {"updated": updated, "old_name": old_name, "new_name": new_name}


def merge_tags(handler, cm, pdir):
    body = _read_body(handler)
    source_tags = body.get("source_tags", [])
    target_name = body.get("target_name", "").strip()
    if not source_tags or not target_name:
        return {"error": "source_tags and target_name required"}
    repo = MemoryRepo(cm.conn, pdir)
    updated = 0
    for m in repo.get_all(limit=10000):
        tags = json.loads(m["tags"]) if isinstance(m.get("tags"), str) else m.get("tags", [])
        if any(t in source_tags for t in tags):
            tags = [target_name if t in source_tags else t for t in tags]
            tags = list(dict.fromkeys(tags))
            cm.conn.execute("UPDATE memories SET tags=?, updated_at=? WHERE id=?",
                            (json.dumps(tags, ensure_ascii=False), repo._now(), m["id"]))
            updated += 1
    cm.conn.commit()
    return {"updated": updated, "target_name": target_name}


def delete_tags(handler, cm, pdir):
    body = _read_body(handler)
    tag_names = body.get("tags", [])
    if not tag_names:
        return {"error": "tags required"}
    repo = MemoryRepo(cm.conn, pdir)
    updated = 0
    for m in repo.get_all(limit=10000):
        tags = json.loads(m["tags"]) if isinstance(m.get("tags"), str) else m.get("tags", [])
        new_tags = [t for t in tags if t not in tag_names]
        if len(new_tags) != len(tags):
            cm.conn.execute("UPDATE memories SET tags=?, updated_at=? WHERE id=?",
                            (json.dumps(new_tags, ensure_ascii=False), repo._now(), m["id"]))
            updated += 1
    cm.conn.commit()
    return {"deleted_tags": tag_names, "updated_memories": updated}


def get_projects(cm):
    conn = cm.conn
    rows = conn.execute(
        "SELECT project_dir, COUNT(*) as mem_count FROM memories GROUP BY project_dir"
    ).fetchall()
    projects = {}
    for r in rows:
        pd = r["project_dir"]
        projects.setdefault(pd, {"project_dir": pd, "memories": 0, "issues": 0, "tags": set()})
        projects[pd]["memories"] = r["mem_count"]

    issue_rows = conn.execute(
        "SELECT project_dir, COUNT(*) as cnt FROM issues GROUP BY project_dir"
    ).fetchall()
    archive_rows = conn.execute(
        "SELECT project_dir, COUNT(*) as cnt FROM issues_archive GROUP BY project_dir"
    ).fetchall()
    for r in issue_rows:
        pd = r["project_dir"]
        projects.setdefault(pd, {"project_dir": pd, "memories": 0, "issues": 0, "tags": set()})
        projects[pd]["issues"] += r["cnt"]
    for r in archive_rows:
        pd = r["project_dir"]
        projects.setdefault(pd, {"project_dir": pd, "memories": 0, "issues": 0, "tags": set()})
        projects[pd]["issues"] += r["cnt"]

    tag_rows = conn.execute("SELECT project_dir, tags FROM memories").fetchall()
    for r in tag_rows:
        pd = r["project_dir"]
        if pd in projects:
            tags = json.loads(r["tags"]) if isinstance(r["tags"], str) else (r["tags"] or [])
            projects[pd]["tags"].update(tags)

    result = []
    for pd, info in sorted(projects.items(), key=lambda x: -x[1]["memories"]):
        if pd == USER_SCOPE_DIR or not pd:
            continue
        result.append({
            "project_dir": pd,
            "name": pd.replace("\\", "/").rsplit("/", 1)[-1] if pd else "unknown",
            "memories": info["memories"],
            "issues": info["issues"],
            "tags": len(info["tags"]),
        })
    return {"projects": result}
