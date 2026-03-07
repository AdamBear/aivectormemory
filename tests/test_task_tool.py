"""B2.7 自测：handle_task batch_create/update/list 验证"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
import tempfile
import sqlite_vec

from aivectormemory.db.schema import init_db
from aivectormemory.db.connection import ConnectionManager
from aivectormemory.tools.task import handle_task
from aivectormemory.errors import NotFoundError
import json


class FakeCM:
    def __init__(self, conn, project_dir):
        self.conn = conn
        self.project_dir = project_dir


def setup_db():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = f.name
    f.close()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    init_db(conn)
    return conn, db_path


def test_batch_create():
    conn, db_path = setup_db()
    try:
        cm = FakeCM(conn, "/test")
        result = handle_task({
            "action": "batch_create",
            "feature_id": "v0.2.5-task",
            "tasks": [
                {"title": "实现 TaskRepo", "sort_order": 1},
                {"title": "实现 handle_task", "sort_order": 2},
                {"title": "Web API", "sort_order": 3},
            ]
        }, cm=cm)
        assert "3" in result
        # 去重
        result2 = handle_task({
            "action": "batch_create",
            "feature_id": "v0.2.5-task",
            "tasks": [{"title": "实现 TaskRepo"}]
        }, cm=cm)
        assert "0" in result2
        print("PASS: batch_create")
    finally:
        conn.close()
        os.unlink(db_path)


def test_list():
    conn, db_path = setup_db()
    try:
        cm = FakeCM(conn, "/test")
        handle_task({
            "action": "batch_create",
            "feature_id": "feat-a",
            "tasks": [{"title": "T1"}, {"title": "T2"}]
        }, cm=cm)
        result = json.loads(handle_task({"action": "list", "feature_id": "feat-a"}, cm=cm))
        assert result["success"]
        assert len(result["tasks"]) == 2
        # 全部列表（需要 feature_id）
        result_all = json.loads(handle_task({"action": "list", "feature_id": "feat-a"}, cm=cm))
        assert len(result_all["tasks"]) == 2
        print("PASS: list")
    finally:
        conn.close()
        os.unlink(db_path)


def test_update():
    conn, db_path = setup_db()
    try:
        cm = FakeCM(conn, "/test")
        handle_task({
            "action": "batch_create",
            "feature_id": "feat-b",
            "tasks": [{"title": "任务1"}]
        }, cm=cm)
        tasks = json.loads(handle_task({"action": "list", "feature_id": "feat-b"}, cm=cm))["tasks"]
        task_id = tasks[0]["id"]
        result = handle_task({
            "action": "update",
            "task_id": task_id,
            "status": "completed"
        }, cm=cm)
        assert isinstance(result, str)
        assert "任务1" in result
        # 按状态过滤
        pending = json.loads(handle_task({"action": "list", "feature_id": "feat-b", "status": "pending"}, cm=cm))
        assert len(pending["tasks"]) == 0
        completed = json.loads(handle_task({"action": "list", "feature_id": "feat-b", "status": "completed"}, cm=cm))
        assert len(completed["tasks"]) == 1
        print("PASS: update")
    finally:
        conn.close()
        os.unlink(db_path)


def test_error_handling():
    conn, db_path = setup_db()
    try:
        cm = FakeCM(conn, "/test")
        try:
            handle_task({"action": "batch_create", "feature_id": "", "tasks": []}, cm=cm)
            assert False, "Should raise"
        except ValueError:
            pass
        try:
            handle_task({"action": "update", "task_id": 9999, "status": "completed"}, cm=cm)
            assert False, "Should raise"
        except (ValueError, NotFoundError):
            pass
        try:
            handle_task({"action": "unknown"}, cm=cm)
            assert False, "Should raise"
        except ValueError:
            pass
        print("PASS: error handling")
    finally:
        conn.close()
        os.unlink(db_path)


if __name__ == "__main__":
    test_batch_create()
    test_list()
    test_update()
    test_error_handling()
    print("\nAll B2 task tool tests passed!")
