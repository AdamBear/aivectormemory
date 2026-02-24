"""测试 MCP server stdio 启动是否正常响应"""
import subprocess
import json
import sys
import time

# 场景1: 不带 --project-dir（用户级配置的方式）
cmd1 = ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "aivectormemory"]
# 场景2: 带 --project-dir（工作区配置的方式）
cmd2 = ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "aivectormemory", "--project-dir", "/Users/macos/item/run-memory-mcp-server"]

init_msg = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "0.1"}
    }
}) + "\n"

for label, cmd in [("无 --project-dir", cmd1), ("有 --project-dir", cmd2)]:
    print(f"\n{'='*60}")
    print(f"测试: {label}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/Users/macos/item/run-memory-mcp-server"
        )
        stdout, stderr = proc.communicate(input=init_msg.encode(), timeout=8)
        print(f"退出码: {proc.returncode}")
        if stdout:
            print(f"stdout: {stdout.decode()[:500]}")
        else:
            print("stdout: (空)")
        if stderr:
            print(f"stderr: {stderr.decode()[:500]}")
        else:
            print("stderr: (空)")
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        print("超时(8s)，进程已 kill")
        if stdout:
            print(f"stdout: {stdout.decode()[:500]}")
        if stderr:
            print(f"stderr: {stderr.decode()[:500]}")
    except Exception as e:
        print(f"异常: {e}")
