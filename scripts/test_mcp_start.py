#!/usr/bin/env python3
"""测试 MCP server 能否通过 stdio 正常启动并响应 initialize"""
import subprocess, json, sys

proc = subprocess.Popen(
    ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "aivectormemory",
     "--project-dir", "/Users/macos/item/run-memory-mcp-server"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

# 发送 JSON-RPC initialize
msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}})
header = f"Content-Length: {len(msg)}\r\n\r\n"
proc.stdin.write(header.encode() + msg.encode())
proc.stdin.flush()

# 读取响应
import select
ready, _, _ = select.select([proc.stdout], [], [], 5)
if ready:
    line = proc.stdout.readline().decode()
    print(f"header: {line.strip()}")
    proc.stdout.readline()  # empty line
    content_len = int(line.split(":")[1].strip())
    body = proc.stdout.read(content_len).decode()
    resp = json.loads(body)
    print(f"response: {json.dumps(resp, indent=2, ensure_ascii=False)[:500]}")
    print("MCP server 启动正常")
else:
    stderr = proc.stderr.read().decode()
    print(f"超时，stderr: {stderr[:500]}")
    print("MCP server 启动失败")

proc.terminate()
