"""测试 MCP Server stdio 连接"""
import subprocess, json, sys

cmd = ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "aivectormemory",
       "--project-dir", "/Users/macos/item/run-memory-mcp-server"]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# 发送 initialize
init_msg = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {},
               "clientInfo": {"name": "test", "version": "1.0"}}})
header = f"Content-Length: {len(init_msg.encode())}\r\n\r\n"
proc.stdin.write(header.encode())
proc.stdin.write(init_msg.encode())
proc.stdin.flush()

# 读取响应
import select, time
time.sleep(2)

# 读 stderr
stderr_data = b""
while select.select([proc.stderr], [], [], 0.1)[0]:
    stderr_data += proc.stderr.read1(4096)

# 读 stdout
stdout_data = b""
while select.select([proc.stdout], [], [], 0.1)[0]:
    stdout_data += proc.stdout.read1(4096)

proc.terminate()
proc.wait(timeout=5)

print("=== STDERR ===")
print(stderr_data.decode("utf-8", errors="replace"))
print("=== STDOUT ===")
print(stdout_data.decode("utf-8", errors="replace"))
print("=== EXIT CODE ===")
print(proc.returncode)
