#!/usr/bin/env python3
import subprocess, time

proc = subprocess.Popen(
    ["/opt/homebrew/opt/python@3.12/bin/python3.12", "-m", "aivectormemory",
     "--project-dir", "/Users/macos/item/run-memory-mcp-server"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(2)
proc.terminate()
out = proc.stdout.read().decode()
err = proc.stderr.read().decode()
print(f"stdout: {out[:300]}")
print(f"stderr: {err[:500]}")
