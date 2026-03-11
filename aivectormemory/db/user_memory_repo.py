import json

from .base import BaseMemoryRepo


class UserMemoryRepo(BaseMemoryRepo):
    """管理 user_memories + vec_user_memories 表（跨项目用户偏好）"""
    TABLE = "user_memories"
    VEC_TABLE = "vec_user_memories"
    TAG_TABLE = "user_memory_tags"

    def __init__(self, conn):
        super().__init__(conn, project_dir="")

    def _build_insert(self, mid, content, tags, source, session_id, now, extra):
        cols = "id, content, tags, source, session_id, created_at, updated_at"
        vals = [mid, content, json.dumps(tags, ensure_ascii=False), source, session_id, now, now]
        return cols, vals

    def _build_tag_filter(self, base_sql: str, tags: list[str],
                          tags_mode: str, source: str | None = None,
                          query: str | None = None) -> tuple[str, list]:
        sql, params = base_sql, []
        if source:
            sql += " AND source=?"
            params.append(source)
        if tags_mode == "any":
            sql += " AND (" + " OR ".join(
                ["id IN (SELECT memory_id FROM user_memory_tags WHERE tag=?)" for _ in tags]) + ")"
            params.extend(tags)
        else:
            for tag in tags:
                sql += " AND id IN (SELECT memory_id FROM user_memory_tags WHERE tag=?)"
                params.append(tag)
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        return sql, params

    def list_by_tags(self, tags: list[str], limit: int = 100, offset: int = 0,
                     source: str | None = None, tags_mode: str = "all",
                     query: str | None = None, **_) -> list[dict]:
        sql, params = self._build_tag_filter(
            "SELECT * FROM user_memories WHERE 1=1",
            tags, tags_mode, source, query)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def count_by_tags(self, tags: list[str], source: str | None = None,
                      tags_mode: str = "all", query: str | None = None) -> int:
        sql, params = self._build_tag_filter(
            "SELECT COUNT(*) FROM user_memories WHERE 1=1",
            tags, tags_mode, source, query)
        return self.conn.execute(sql, params).fetchone()[0]

    def get_all(self, limit: int = 100, offset: int = 0, query: str | None = None,
                source: str | None = None, exclude_tags: list[str] | None = None) -> list[dict]:
        sql, params = "SELECT * FROM user_memories WHERE 1=1", []
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        if source:
            sql += " AND source=?"
            params.append(source)
        if exclude_tags:
            for tag in exclude_tags:
                sql += " AND id NOT IN (SELECT memory_id FROM user_memory_tags WHERE tag=?)"
                params.append(tag)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def count(self, query: str | None = None, source: str | None = None,
             exclude_tags: list[str] | None = None) -> int:
        sql, params = "SELECT COUNT(*) FROM user_memories WHERE 1=1", []
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        if source:
            sql += " AND source=?"
            params.append(source)
        if exclude_tags:
            for tag in exclude_tags:
                sql += " AND id NOT IN (SELECT memory_id FROM user_memory_tags WHERE tag=?)"
                params.append(tag)
        return self.conn.execute(sql, params).fetchone()[0]

    def get_tag_counts(self) -> dict[str, int]:
        rows = self.conn.execute(
            "SELECT tag, COUNT(*) as cnt FROM user_memory_tags GROUP BY tag").fetchall()
        return {r["tag"]: r["cnt"] for r in rows}

    def get_ids_with_tag(self, tag: str) -> list[dict]:
        return [dict(r) for r in self.conn.execute(
            "SELECT um.id, um.tags FROM user_memories um JOIN user_memory_tags umt ON um.id = umt.memory_id WHERE umt.tag=?",
            (tag,)
        ).fetchall()]
