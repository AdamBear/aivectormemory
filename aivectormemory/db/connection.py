import sqlite3
import sqlite_vec
from pathlib import Path
from aivectormemory.config import get_db_path


class ConnectionManager:
    def __init__(self, project_dir: str | None = None):
        self._db_path = get_db_path()
        self.project_dir = str(Path(project_dir or Path.cwd()).resolve())
        self._conn: sqlite3.Connection | None = None

    def _ensure_dir(self):
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> sqlite3.Connection:
        self._ensure_dir()
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        return conn

    @property
    def conn(self) -> sqlite3.Connection:
        if not self._conn:
            self._conn = self._connect()
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
