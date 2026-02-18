from datetime import datetime, timezone


class IssueRepo:
    def __init__(self, conn, project_dir: str = ""):
        self.conn = conn
        self.project_dir = project_dir

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _next_number(self, date: str) -> int:
        row = self.conn.execute(
            "SELECT MAX(issue_number) as max_num FROM issues WHERE date=? AND project_dir=?",
            (date, self.project_dir)
        ).fetchone()
        return (row["max_num"] or 0) + 1

    def create(self, date: str, title: str, content: str = "", memory_id: str = "") -> dict:
        # 去重：同项目 + 同标题 + 未归档 → 返回已有记录
        existing = self.conn.execute(
            "SELECT * FROM issues WHERE project_dir=? AND title=? AND status!='archived'",
            (self.project_dir, title)
        ).fetchone()
        if existing:
            return {"id": existing["id"], "issue_number": existing["issue_number"], "date": existing["date"], "deduplicated": True}
        now = self._now()
        num = self._next_number(date)
        cur = self.conn.execute(
            "INSERT INTO issues (project_dir, issue_number, date, title, status, content, memory_id, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (self.project_dir, num, date, title, "pending", content, memory_id, now, now)
        )
        self.conn.commit()
        return {"id": cur.lastrowid, "issue_number": num, "date": date}

    def update(self, issue_id: int, **fields) -> dict | None:
        row = self.conn.execute("SELECT * FROM issues WHERE id=? AND project_dir=?",
                                (issue_id, self.project_dir)).fetchone()
        if not row:
            return None
        allowed = {"title", "status", "content", "memory_id"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return dict(row)
        updates["updated_at"] = self._now()
        set_clause = ",".join(f"{k}=?" for k in updates)
        self.conn.execute(f"UPDATE issues SET {set_clause} WHERE id=?", [*updates.values(), issue_id])
        self.conn.commit()
        return dict(self.conn.execute("SELECT * FROM issues WHERE id=?", (issue_id,)).fetchone())

    def archive(self, issue_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM issues WHERE id=? AND project_dir=?",
                                (issue_id, self.project_dir)).fetchone()
        if not row:
            return None
        now = self._now()
        self.conn.execute(
            "INSERT INTO issues_archive (project_dir, issue_number, date, title, content, memory_id, archived_at, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (row["project_dir"], row["issue_number"], row["date"], row["title"], row["content"], row["memory_id"] if "memory_id" in row.keys() else "", now, row["created_at"])
        )
        self.conn.execute("DELETE FROM issues WHERE id=?", (issue_id,))
        self.conn.commit()
        memory_id = row["memory_id"] if "memory_id" in row.keys() else ""
        return {"issue_id": issue_id, "archived_at": now, "memory_id": memory_id}

    def list_by_date(self, date: str | None = None, status: str | None = None) -> list[dict]:
        sql, params = "SELECT * FROM issues WHERE project_dir=?", [self.project_dir]
        if date:
            sql += " AND date=?"
            params.append(date)
        if status:
            sql += " AND status=?"
            params.append(status)
        sql += " ORDER BY date DESC, issue_number ASC"
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def list_archived(self, date: str | None = None) -> list[dict]:
        sql, params = "SELECT * FROM issues_archive WHERE project_dir=?", [self.project_dir]
        if date:
            sql += " AND date=?"
            params.append(date)
        sql += " ORDER BY date DESC, issue_number ASC"
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def get_by_id(self, issue_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM issues WHERE id=? AND project_dir=?",
                                (issue_id, self.project_dir)).fetchone()
        return dict(row) if row else None
    def delete(self, issue_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM issues WHERE id=? AND project_dir=?",
                                (issue_id, self.project_dir)).fetchone()
        if not row:
            return None
        memory_id = row["memory_id"] if "memory_id" in row.keys() else ""
        self.conn.execute("DELETE FROM issues WHERE id=?", (issue_id,))
        self.conn.commit()
        return {"issue_id": issue_id, "deleted": True, "memory_id": memory_id}

    def delete_archived(self, archive_id: int) -> dict | None:
        row = self.conn.execute("SELECT * FROM issues_archive WHERE id=? AND project_dir=?",
                                (archive_id, self.project_dir)).fetchone()
        if not row:
            return None
        memory_id = row["memory_id"] if "memory_id" in row.keys() else ""
        self.conn.execute("DELETE FROM issues_archive WHERE id=?", (archive_id,))
        self.conn.commit()
        return {"archive_id": archive_id, "deleted": True, "memory_id": memory_id}

