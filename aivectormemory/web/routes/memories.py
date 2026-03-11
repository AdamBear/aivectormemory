import json

from aivectormemory.utils import now_iso, safe_table
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.user_memory_repo import UserMemoryRepo


def get_memories(cm, params, pdir):
    scope = params.get("scope", ["all"])[0]
    query = params.get("query", [None])[0]
    tag = params.get("tag", [None])[0]
    source = params.get("source", [None])[0]
    exclude_tags_raw = params.get("exclude_tags", [None])[0]
    limit = int(params.get("limit", [100])[0])
    offset = int(params.get("offset", [0])[0])

    repo = MemoryRepo(cm.conn, pdir)
    user_repo = UserMemoryRepo(cm.conn)
    ex_tags = exclude_tags_raw.split(",") if exclude_tags_raw else None

    if tag:
        # SQL-level: tag + query + source filtering with pagination
        if scope == "user":
            results = user_repo.list_by_tags([tag], limit=limit, offset=offset, source=source, query=query)
            total = user_repo.count_by_tags([tag], source=source, query=query)
        elif scope == "project":
            results = repo.list_by_tags([tag], scope="project", project_dir=pdir, limit=limit, offset=offset, source=source, query=query)
            total = repo.count_by_tags([tag], scope="project", project_dir=pdir, source=source, query=query)
        else:
            p_rows = repo.list_by_tags([tag], scope="project", project_dir=pdir, limit=limit, offset=offset, source=source, query=query)
            p_total = repo.count_by_tags([tag], scope="project", project_dir=pdir, source=source, query=query)
            u_total = user_repo.count_by_tags([tag], source=source, query=query)
            total = p_total + u_total
            if len(p_rows) < limit:
                u_offset = max(0, offset - p_total)
                u_rows = user_repo.list_by_tags([tag], limit=limit - len(p_rows), offset=u_offset, source=source, query=query)
                results = p_rows + u_rows
            else:
                results = p_rows
    elif ex_tags:
        # SQL-level: exclude_tags + query + source filtering with pagination
        if scope == "user":
            results = user_repo.get_all(limit=limit, offset=offset, query=query, source=source, exclude_tags=ex_tags)
            total = user_repo.count(query=query, source=source, exclude_tags=ex_tags)
        elif scope == "project":
            results = repo.get_all(limit=limit, offset=offset, project_dir=pdir, query=query, source=source, exclude_tags=ex_tags)
            total = repo.count(project_dir=pdir, query=query, source=source, exclude_tags=ex_tags)
        else:
            p_rows = repo.get_all(limit=limit, offset=offset, query=query, source=source, exclude_tags=ex_tags)
            p_total = repo.count(query=query, source=source, exclude_tags=ex_tags)
            u_total = user_repo.count(query=query, source=source, exclude_tags=ex_tags)
            total = p_total + u_total
            if len(p_rows) < limit:
                u_offset = max(0, offset - p_total)
                u_rows = user_repo.get_all(limit=limit - len(p_rows), offset=u_offset, query=query, source=source, exclude_tags=ex_tags)
                results = p_rows + u_rows
            else:
                results = p_rows
    else:
        # SQL-level: query + source filtering with pagination
        if scope == "user":
            results = user_repo.get_all(limit=limit, offset=offset, query=query, source=source)
            total = user_repo.count(query=query, source=source)
        elif scope == "project":
            results = repo.get_all(limit=limit, offset=offset, project_dir=pdir, query=query, source=source)
            total = repo.count(project_dir=pdir, query=query, source=source)
        else:
            p_rows = repo.get_all(limit=limit, offset=offset, query=query, source=source)
            p_total = repo.count(query=query, source=source)
            u_total = user_repo.count(query=query, source=source)
            total = p_total + u_total
            if len(p_rows) < limit:
                u_offset = max(0, offset - p_total)
                u_rows = user_repo.get_all(limit=limit - len(p_rows), offset=u_offset, query=query, source=source)
                results = p_rows + u_rows
            else:
                results = p_rows

    return {"memories": results, "total": total}


def get_memory_detail(cm, mid, pdir):
    repo = MemoryRepo(cm.conn, pdir)
    mem = repo.get_by_id(mid)
    if mem:
        return mem
    user_repo = UserMemoryRepo(cm.conn)
    mem = user_repo.get_by_id(mid)
    return mem or {"error": "not found"}


def put_memory(handler, cm, mid, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    repo = MemoryRepo(cm.conn, pdir)
    mem = repo.get_by_id(mid)
    table = "memories"
    if not mem:
        user_repo = UserMemoryRepo(cm.conn)
        mem = user_repo.get_by_id(mid)
        table = "user_memories"
    if not mem:
        return {"error": "not found"}
    now = now_iso()
    updates = {}
    if "content" in body:
        updates["content"] = body["content"]
    if "tags" in body:
        updates["tags"] = json.dumps(body["tags"])
    if updates:
        updates["updated_at"] = now
        set_clause = ",".join(f"{k}=?" for k in updates)
        cm.conn.execute(f"UPDATE {safe_table(table)} SET {set_clause} WHERE id=?", [*updates.values(), mid])
        cm.conn.commit()
    if table == "user_memories":
        return UserMemoryRepo(cm.conn).get_by_id(mid)
    return repo.get_by_id(mid)


def delete_memory(cm, mid, pdir):
    repo = MemoryRepo(cm.conn, pdir)
    if repo.delete(mid):
        return {"deleted": True, "id": mid}
    user_repo = UserMemoryRepo(cm.conn)
    if user_repo.delete(mid):
        return {"deleted": True, "id": mid}
    return {"error": "not found"}


def delete_memories_batch(handler, cm, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    ids = body.get("ids", [])
    repo = MemoryRepo(cm.conn, pdir)
    user_repo = UserMemoryRepo(cm.conn)
    deleted = []
    for mid in ids:
        if repo.delete(mid):
            deleted.append(mid)
        elif user_repo.delete(mid):
            deleted.append(mid)
    return {"deleted_count": len(deleted), "ids": deleted}


def _fetch_embedding(cm, mid, vec_table):
    import struct
    row = cm.conn.execute(f"SELECT embedding FROM {safe_table(vec_table)} WHERE id=?", (mid,)).fetchone()
    if not row:
        return None
    raw = row["embedding"]
    if isinstance(raw, (bytes, memoryview)):
        if len(raw) >= 4 and len(raw) % 4 == 0:
            return list(struct.unpack(f'{len(raw)//4}f', raw))
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def export_memories(cm, params, pdir):
    scope = params.get("scope", ["all"])[0]
    repo = MemoryRepo(cm.conn, pdir)
    user_repo = UserMemoryRepo(cm.conn)
    page_size = 200

    result = []
    if scope in ("user", "all"):
        total_u = user_repo.count()
        for off in range(0, total_u, page_size):
            for m in user_repo.get_all(limit=page_size, offset=off):
                entry = dict(m)
                entry["embedding"] = _fetch_embedding(cm, m["id"], "vec_user_memories")
                result.append(entry)
    if scope in ("project", "all"):
        total_p = repo.count(project_dir=pdir) if scope == "project" else repo.count()
        pd = pdir if scope == "project" else None
        for off in range(0, total_p, page_size):
            for m in repo.get_all(limit=page_size, offset=off, project_dir=pd):
                entry = dict(m)
                entry["embedding"] = _fetch_embedding(cm, m["id"], "vec_memories")
                result.append(entry)

    return {"memories": result, "count": len(result), "project_dir": pdir}


def import_memories(handler, cm, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    items = body.get("memories", [])
    if not items:
        return {"error": "no memories to import"}
    repo = MemoryRepo(cm.conn, pdir)
    user_repo = UserMemoryRepo(cm.conn)
    imported, skipped = 0, 0
    for item in items:
        mid = item.get("id", "")
        if not mid or repo.get_by_id(mid) or user_repo.get_by_id(mid):
            skipped += 1
            continue
        now = now_iso()
        tags = item.get("tags", "[]")
        tags_str = json.dumps(tags, ensure_ascii=False) if isinstance(tags, list) else tags
        scope = item.get("scope", "project")
        embedding = item.get("embedding")
        if not embedding:
            from aivectormemory.embedding.engine import EmbeddingEngine
            embedding = EmbeddingEngine().encode(item.get("content", ""))
        if scope == "user":
            cm.conn.execute(
                "INSERT INTO user_memories (id, content, tags, source, session_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                (mid, item.get("content", ""), tags_str, item.get("source", "manual"),
                 item.get("session_id", 0), item.get("created_at", now), now))
            cm.conn.execute("INSERT INTO vec_user_memories (id, embedding) VALUES (?,?)", (mid, json.dumps(embedding)))
        else:
            cm.conn.execute(
                "INSERT INTO memories (id, content, tags, scope, project_dir, session_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (mid, item.get("content", ""), tags_str, scope,
                 item.get("project_dir", pdir), item.get("session_id", 0), item.get("created_at", now), now))
            cm.conn.execute("INSERT INTO vec_memories (id, embedding) VALUES (?,?)", (mid, json.dumps(embedding)))
        imported += 1
    cm.conn.commit()
    return {"imported": imported, "skipped": skipped}


def search_memories(handler, cm, pdir):
    from aivectormemory.web.api import _read_body
    body = _read_body(handler)
    query = body.get("query", "").strip()
    if not query:
        return {"error": "query required"}
    top_k = body.get("top_k", 20)
    scope = body.get("scope", "all")
    tags = body.get("tags", [])

    engine = getattr(cm, "_embedding_engine", None)
    if not engine:
        return {"error": "embedding engine not loaded"}

    embedding = engine.encode(query)
    repo = MemoryRepo(cm.conn, pdir)
    user_repo = UserMemoryRepo(cm.conn)

    if scope == "user":
        if tags:
            results = user_repo.search_by_vector_with_tags(embedding, tags, top_k=top_k)
        else:
            results = user_repo.search_by_vector(embedding, top_k=top_k)
    elif scope == "project":
        if tags:
            results = repo.search_by_vector_with_tags(embedding, tags, top_k=top_k, scope="project", project_dir=pdir)
        else:
            results = repo.search_by_vector(embedding, top_k=top_k, scope="project", project_dir=pdir)
    else:
        if tags:
            proj_results = repo.search_by_vector_with_tags(embedding, tags, top_k=top_k, scope="project", project_dir=pdir)
            user_results = user_repo.search_by_vector_with_tags(embedding, tags, top_k=top_k)
        else:
            proj_results = repo.search_by_vector(embedding, top_k=top_k, scope="project", project_dir=pdir)
            user_results = user_repo.search_by_vector(embedding, top_k=top_k)
        results = sorted(proj_results + user_results, key=lambda x: x.get("distance", 0))[:top_k]

    for r in results:
        r["similarity"] = round(1 - (r.get("distance", 0) ** 2) / 2, 4)
    return {"results": results, "count": len(results), "query": query}
