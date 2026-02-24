"""清理用户级 MCP 配置中的重复 aivectormemory 条目"""
import json
from pathlib import Path

filepath = Path.home() / ".kiro/settings/mcp.json"
config = json.loads(filepath.read_text("utf-8"))

if "aivectormemory" in config.get("mcpServers", {}):
    del config["mcpServers"]["aivectormemory"]
    filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"✓ 已删除用户级 aivectormemory 条目: {filepath}")
    print(f"  剩余 servers: {list(config['mcpServers'].keys())}")
else:
    print("- 用户级配置中没有 aivectormemory，无需修改")
