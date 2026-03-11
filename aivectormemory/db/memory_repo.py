import json

from .base import BaseMemoryRepo


class MemoryRepo(BaseMemoryRepo):
    TABLE = "memories"
    VEC_TABLE = "vec_memories"
    TAG_TABLE = "memory_tags"

    def insert(self, content: str, tags: list[str], scope: str, session_id: int,
               embedding: list[float], dedup_threshold: float = 0.95,
               source: str = "manual") -> dict:
        return super().insert(content, tags, session_id, embedding, dedup_threshold, source, scope=scope)

    def _build_insert(self, mid, content, tags, source, session_id, now, extra):
        scope = extra.get("scope", "project")
        cols = "id, content, tags, scope, source, project_dir, session_id, created_at, updated_at"
        vals = [mid, content, json.dumps(tags, ensure_ascii=False), scope, source, self.project_dir, session_id, now, now]
        return cols, vals

    def _is_same_scope(self, mid: str) -> bool:
        mem = self.conn.execute("SELECT project_dir FROM memories WHERE id=?", (mid,)).fetchone()
        return mem and mem["project_dir"] == self.project_dir

    def _match_filters(self, mem, filters) -> bool:
        scope = filters.get("scope", "all")
        if scope == "project" and mem["project_dir"] != filters.get("project_dir", self.project_dir):
            return False
        source = filters.get("source")
        return not source or mem.get("source", "manual") == source

    def _build_tag_filter(self, base_sql: str, tags: list[str],
                          tags_mode: str, scope: str = "all",
                          project_dir: str = "", source: str | None = None,
                          query: str | None = None) -> tuple[str, list]:
        sql, params = base_sql, []
        if scope == "project":
            sql += " AND project_dir=?"
            params.append(project_dir or self.project_dir)
        if source:
            sql += " AND source=?"
            params.append(source)
        if tags_mode == "any":
            sql += " AND (" + " OR ".join(
                ["id IN (SELECT memory_id FROM memory_tags WHERE tag=?)" for _ in tags]) + ")"
            params.extend(tags)
        else:
            for tag in tags:
                sql += " AND id IN (SELECT memory_id FROM memory_tags WHERE tag=?)"
                params.append(tag)
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        return sql, params

    def list_by_tags(self, tags: list[str], scope: str = "all", project_dir: str = "",
                     limit: int = 100, offset: int = 0, source: str | None = None,
                     tags_mode: str = "all", query: str | None = None, **_) -> list[dict]:
        sql, params = self._build_tag_filter(
            "SELECT * FROM memories WHERE 1=1",
            tags, tags_mode, scope, project_dir, source, query)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def count_by_tags(self, tags: list[str], scope: str = "all", project_dir: str = "",
                      source: str | None = None, tags_mode: str = "all",
                      query: str | None = None) -> int:
        sql, params = self._build_tag_filter(
            "SELECT COUNT(*) FROM memories WHERE 1=1",
            tags, tags_mode, scope, project_dir, source, query)
        return self.conn.execute(sql, params).fetchone()[0]

    def _build_filter(self, base_sql: str, project_dir: str | None = None,
                      query: str | None = None, source: str | None = None,
                      exclude_tags: list[str] | None = None) -> tuple[str, list]:
        sql, params = base_sql, []
        if project_dir is not None:
            sql += " AND project_dir = ?"
            params.append(project_dir)
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        if source:
            sql += " AND source = ?"
            params.append(source)
        if exclude_tags:
            for tag in exclude_tags:
                sql += " AND id NOT IN (SELECT memory_id FROM memory_tags WHERE tag=?)"
                params.append(tag)
        return sql, params

    def get_all(self, limit: int = 100, offset: int = 0, project_dir: str | None = None,
                query: str | None = None, source: str | None = None,
                exclude_tags: list[str] | None = None) -> list[dict]:
        sql, params = self._build_filter(
            "SELECT * FROM memories WHERE 1=1", project_dir, query, source, exclude_tags)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def count(self, project_dir: str | None = None, query: str | None = None,
             source: str | None = None, exclude_tags: list[str] | None = None) -> int:
        sql, params = self._build_filter(
            "SELECT COUNT(*) FROM memories WHERE 1=1", project_dir, query, source, exclude_tags)
        return self.conn.execute(sql, params).fetchone()[0]

    def get_tag_counts(self, project_dir: str | None = None) -> dict[str, int]:
        if project_dir is not None:
            rows = self.conn.execute(
                "SELECT mt.tag, COUNT(*) as cnt FROM memory_tags mt "
                "JOIN memories m ON mt.memory_id = m.id WHERE m.project_dir=? GROUP BY mt.tag",
                (project_dir,)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT tag, COUNT(*) as cnt FROM memory_tags GROUP BY tag").fetchall()
        return {r["tag"]: r["cnt"] for r in rows}

    def get_ids_with_tag(self, tag: str, project_dir: str | None = None) -> list[dict]:
        sql = "SELECT m.id, m.tags FROM memories m JOIN memory_tags mt ON m.id = mt.memory_id WHERE mt.tag=?"
        params: list = [tag]
        if project_dir is not None:
            sql += " AND m.project_dir=?"
            params.append(project_dir)
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]
