"""11 条功能完善需求自测脚本"""
import sys, os, json, sqlite3, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aivectormemory.db import ConnectionManager, init_db
from aivectormemory.db.memory_repo import MemoryRepo
from aivectormemory.db.schema import init_db as schema_init
from aivectormemory.embedding.engine import EmbeddingEngine
from aivectormemory.tools.remember import handle_remember
from aivectormemory.tools.recall import handle_recall
from aivectormemory.tools.forget import handle_forget
from aivectormemory import __version__

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")

# 创建临时数据库
tmpdir = tempfile.mkdtemp()
os.environ["AIVECTORMEMORY_DB_DIR"] = tmpdir
cm = ConnectionManager(project_dir="/tmp/test_project")
init_db(cm.conn)

# 加载 embedding engine
engine = EmbeddingEngine()
engine.load()

print("\n#85: server.py version 一致性")
check("__version__ 与 pyproject.toml 一致", __version__ == "0.2.3", f"got {__version__}")
from aivectormemory.server import MCPServer
import inspect
src = inspect.getsource(MCPServer.handle_initialize)
check("server.py 使用 __version__", "__version__" in src, "handle_initialize 未引用 __version__")

print("\n#87: session_id 持久化")
cols = {r[1] for r in cm.conn.execute("PRAGMA table_info(session_state)").fetchall()}
check("session_state 有 last_session_id 列", "last_session_id" in cols, f"cols={cols}")

print("\n#86: remember content 长度限制")
long_content = "x" * 6000
result_text = handle_remember(
    {"content": long_content, "tags": ["test_truncate"], "scope": "project"},
    cm=cm, engine=engine, session_id=1
)
# 从自然语言返回中提取 id
import re as _re
_id_match = _re.search(r'([a-f0-9]{12})', result_text)
mid = _id_match.group(1) if _id_match else None
mem = MemoryRepo(cm.conn, cm.project_dir).get_by_id(mid)
check("content 被截断到 5000", mem and len(mem["content"]) == 5000, f"len={len(mem['content']) if mem else 'None'}")

print("\n#94: embedding encode 缓存")
v1 = engine.encode("test cache hit")
v2 = engine.encode("test cache hit")
check("相同文本返回相同向量", v1 == v2)
check("缓存命中", engine._encode_cached.cache_info().hits >= 1, f"hits={engine._encode_cached.cache_info().hits}")

print("\n#96: forget 按标签批量删除")
test_contents = [
    "Python Flask 框架路由配置详解",
    "MySQL 索引优化与慢查询分析",
    "Docker 容器网络模式对比"
]
for c in test_contents:
    handle_remember(
        {"content": c, "tags": ["batch_del"], "scope": "project"},
        cm=cm, engine=engine, session_id=1
    )
repo = MemoryRepo(cm.conn, cm.project_dir)
before = len(repo.list_by_tags(["batch_del"], scope="project", project_dir=cm.project_dir))
check("批量删除前有记忆", before >= 3, f"count={before}")
forget_text = handle_forget(
    {"tags": ["batch_del"], "scope": "project"},
    cm=cm, engine=engine, session_id=1
)
check("forget 按标签删除成功", "3" in forget_text or "删除" in forget_text, f"result={forget_text}")
after = len(repo.list_by_tags(["batch_del"], scope="project", project_dir=cm.project_dir))
check("删除后无残留", after == 0, f"remaining={after}")

print("\n#83: recall tags+query 组合查询")
handle_remember(
    {"content": "Python asyncio 事件循环机制", "tags": ["技术笔记"], "scope": "project"},
    cm=cm, engine=engine, session_id=1
)
handle_remember(
    {"content": "Go goroutine 并发模型", "tags": ["技术笔记"], "scope": "project"},
    cm=cm, engine=engine, session_id=1
)
handle_remember(
    {"content": "今天天气不错", "tags": ["闲聊"], "scope": "project"},
    cm=cm, engine=engine, session_id=1
)
result = json.loads(handle_recall(
    {"query": "并发编程", "tags": ["技术笔记"], "top_k": 5, "scope": "project"},
    cm=cm, engine=engine, session_id=1
))
memories = result.get("memories", [])
check("tags+query 返回结果", len(memories) > 0, f"count={len(memories)}")
contents = [m["content"] for m in memories]
check("结果不含闲聊标签", all("天气" not in c for c in contents), f"contents={contents}")

print("\n#84: Web 看板全表扫描性能优化")
check("get_tag_counts 方法存在", hasattr(repo, "get_tag_counts"))
check("get_ids_with_tag 方法存在", hasattr(repo, "get_ids_with_tag"))
tag_counts = repo.get_tag_counts()
check("get_tag_counts 返回 dict", isinstance(tag_counts, dict), f"type={type(tag_counts)}")
ids_with = repo.get_ids_with_tag("技术笔记")
check("get_ids_with_tag 返回 list", isinstance(ids_with, list) and len(ids_with) > 0, f"count={len(ids_with)}")

print("\n#93: Web 看板认证机制")
from aivectormemory.web.app import WebHandler, run_web
check("WebHandler 有 auth_token 属性", hasattr(WebHandler, "auth_token"))
check("WebHandler 有 _check_auth 方法", hasattr(WebHandler, "_check_auth"))
import aivectormemory.__main__ as main_mod
src_main = inspect.getsource(main_mod)
check("__main__ 有 --token 参数", "--token" in src_main)
check("__main__ 有 --bind 参数", "--bind" in src_main)

print("\n#95: 记忆导出/导入")
from aivectormemory.web.api import export_memories, import_memories
check("export_memories 函数存在", callable(export_memories))
check("import_memories 函数存在", callable(import_memories))

print("\n#97: Web 看板语义搜索")
from aivectormemory.web.api import search_memories
check("search_memories 函数存在", callable(search_memories))
# 验证 app.py 中 embedding engine 加载逻辑
app_src = inspect.getsource(run_web)
check("run_web 加载 EmbeddingEngine", "EmbeddingEngine" in app_src)
check("run_web 挂载 _embedding_engine", "_embedding_engine" in app_src)

# 汇总
print(f"\n{'='*50}")
print(f"结果: {PASS} 通过, {FAIL} 失败, 共 {PASS+FAIL} 项")
if FAIL > 0:
    sys.exit(1)
else:
    print("全部通过 ✅")
