"""集成测试：通过 stdio JSON-RPC 调用每个工具"""
import json
import subprocess
import tempfile
import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call_tools(messages: list[dict], project_dir: str) -> list[dict]:
    init_msgs = [
        {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
    ]
    all_msgs = init_msgs + messages
    input_data = "\n".join(json.dumps(m) for m in all_msgs) + "\n"
    env = {**os.environ, "HF_ENDPOINT": "https://hf-mirror.com"}
    proc = subprocess.run(
        [".venv/bin/python", "-m", "aivectormemory", "--project-dir", project_dir],
        input=input_data, capture_output=True, text=True, timeout=60, env=env
    )
    responses = []
    for line in proc.stdout.strip().split("\n"):
        if line.strip():
            responses.append(json.loads(line))
    return responses[1:]


def parse_tool_result(resp):
    text = resp["result"]["content"][0]["text"]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def test_remember_and_recall():
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "remember", "arguments": {
                "content": "Python 的 GIL 限制了多线程并行执行",
                "tags": ["python", "踩坑"], "scope": "project"
            }
        }},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "recall", "arguments": {"query": "Python 多线程性能问题"}
        }},
    ]
    responses = call_tools(msgs, PROJECT_DIR)

    r1 = parse_tool_result(responses[0])
    assert isinstance(r1, str)

    r2 = parse_tool_result(responses[1])
    assert isinstance(r2, dict)
    assert r2["success"]
    assert len(r2["memories"]) >= 1


def test_recall_by_tags_only():
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "remember", "arguments": {"content": "项目路径规范", "tags": ["项目知识"], "scope": "project"}
        }},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "remember", "arguments": {"content": "MySQL 常用命令", "tags": ["项目知识"], "scope": "project"}
        }},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
            "name": "remember", "arguments": {"content": "sqlite-vec 踩坑", "tags": ["踩坑"], "scope": "project"}
        }},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
            "name": "recall", "arguments": {"tags": ["项目知识"], "scope": "project", "top_k": 100}
        }},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
            "name": "recall", "arguments": {"tags": ["踩坑"], "scope": "project", "top_k": 100}
        }},
    ]
    responses = call_tools(msgs, PROJECT_DIR)
    r4 = parse_tool_result(responses[3])
    assert r4["success"]
    assert len(r4["memories"]) >= 2
    r5 = parse_tool_result(responses[4])
    assert r5["success"]
    assert len(r5["memories"]) >= 1


def test_forget():
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "remember", "arguments": {"content": "待删除的临时测试记忆_" + os.urandom(4).hex(), "tags": ["test_temp"]}
        }},
    ]
    r = call_tools(msgs, PROJECT_DIR)
    r1_text = parse_tool_result(r[0])
    assert isinstance(r1_text, str)
    import re as _re
    _id_match = _re.search(r'([a-f0-9]{12})', r1_text)
    mem_id = _id_match.group(1) if _id_match else None
    assert mem_id, f"Could not extract memory id from: {r1_text}"

    msgs2 = [
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "forget", "arguments": {"memory_id": mem_id}
        }},
    ]
    r2 = call_tools(msgs2, PROJECT_DIR)
    result = parse_tool_result(r2[0])
    assert isinstance(result, str)
    assert "1" in result


def test_status_read_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        msgs = [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
                "name": "status", "arguments": {"state": {"current_task": "测试任务", "is_blocked": True, "block_reason": "等待确认"}}
            }},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                "name": "status", "arguments": {}
            }},
        ]
        responses = call_tools(msgs, tmpdir)

        r1 = parse_tool_result(responses[0])
        assert r1["success"]
        assert r1["state"]["current_task"] == "测试任务"

        r2 = parse_tool_result(responses[1])
        assert r2["success"]
        assert r2["state"]["is_blocked"] is True


def test_track_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        msgs = [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "create", "title": "测试问题", "date": "2025-02-13"}
            }},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "list", "date": "2025-02-13"}
            }},
        ]
        responses = call_tools(msgs, tmpdir)

        r1 = parse_tool_result(responses[0])
        assert isinstance(r1, str)
        assert "#1" in r1
        issue_num = 1

        r2 = parse_tool_result(responses[1])
        assert isinstance(r2, dict)
        assert r2["success"]
        assert len(r2["issues"]) == 1

        msgs2 = [
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "update", "issue_id": issue_num, "status": "in_progress", "content": "排查中..."}
            }},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "archive", "issue_id": issue_num, "content": "完整排查记录"}
            }},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "list", "date": "2025-02-13"}
            }},
            {"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {
                "name": "track", "arguments": {"action": "list", "issue_id": issue_num}
            }},
        ]
        r3 = call_tools(msgs2, tmpdir)
        assert isinstance(parse_tool_result(r3[0]), str)
        assert isinstance(parse_tool_result(r3[1]), str)
        r_list = parse_tool_result(r3[2])
        assert len(r_list["issues"]) == 0
        r_list_archived = parse_tool_result(r3[3])
        assert len(r_list_archived["issues"]) == 1


def test_auto_save():
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "auto_save", "arguments": {
                "preferences": ["偏好单数据库架构", "偏好 sqlite-vec 向量搜索"]
            }
        }},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "name": "recall", "arguments": {"query": "单数据库架构", "scope": "user"}
        }},
    ]
    responses = call_tools(msgs, PROJECT_DIR)

    r1 = parse_tool_result(responses[0])
    assert isinstance(r1, str)

    r2 = parse_tool_result(responses[1])
    assert isinstance(r2, dict)
    assert r2["success"]
    assert len(r2["memories"]) >= 1
