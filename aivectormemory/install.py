"""aivectormemory install - 交互式为当前项目配置 MCP + Steering 规则"""
import json
import os
import platform
import sys
from pathlib import Path

# (IDE名, MCP配置路径, MCP格式, 是否全局, Steering路径, Steering写入方式, Hooks目录)
# steering_mode: "file"=独立文件 "append"=追加到已有文件 None=不写Steering
# hooks_dir: lambda返回hooks目录路径, None=不支持hooks
IDES = [
    ("Kiro",           lambda root: root / ".kiro/settings/mcp.json",  "standard", False,
     lambda root: root / ".kiro/steering/aivectormemory.md", "file",
     lambda root: root / ".kiro/hooks"),
    ("Cursor",         lambda root: root / ".cursor/mcp.json",         "standard", False,
     lambda root: root / ".cursor/rules/aivectormemory.md", "file",
     lambda root: root / ".cursor"),
    ("Claude Code",    lambda root: root / ".mcp.json",                "standard", False,
     lambda root: root / "CLAUDE.md", "append",
     lambda root: root / ".claude"),
    ("Windsurf",       lambda root: root / ".windsurf/mcp.json",       "standard", False,
     lambda root: root / ".windsurf/rules/aivectormemory.md", "file",
     lambda root: root / ".windsurf"),
    ("VSCode",         lambda root: root / ".vscode/mcp.json",         "standard", False,
     lambda root: root / ".github/copilot-instructions.md", "append", None),
    ("Trae",           lambda root: root / ".trae/mcp.json",           "standard", False,
     lambda root: root / ".trae/rules/aivectormemory.md", "file", None),
    ("OpenCode",       lambda root: root / "opencode.json",            "opencode", False,
     lambda root: root / "AGENTS.md", "append",
     lambda root: root / ".opencode/plugins"),
    ("Claude Desktop", lambda _: _claude_desktop_path(),               "standard", True,
     None, None, None),
]

RUNNERS = [
    ("python -m aivectormemory（pip/pipx 安装）", lambda pdir: (sys.executable, ["-m", "aivectormemory", "--project-dir", pdir])),
    ("uvx aivectormemory（无需安装）", lambda pdir: ("uvx", ["aivectormemory@latest", "--project-dir", pdir])),
]


STEERING_MARKER = "<!-- aivectormemory-steering -->"

STEERING_CONTENT = """# AIVectorMemory - 跨会话持久记忆

本项目已配置 AIVectorMemory MCP Server，提供以下 7 个工具。请在合适的时机主动调用。

---

## ⚠️ IDENTITY & TONE

- Role：你是首席工程师兼高级数据科学家
- Voice：Professional，Concise，Result-Oriented。No "I hope this helps"
- Authority：The user is the Lead Architect. Execute explicit commands immediately (not questions).

---

## ⚠️ 消息类型判断

收到用户消息后，严谨认真理解用户消息的意思然后判断消息类型，询问仅限闲聊，进度、讨论规则、简单确认不记录问题文档，其他所有情况必须需要记录问题文档，然后告诉用户方案，等用户确认后再执行

**⚠️ 回复时用自然语言说明判断结果**，例如：
- "这是个询问，直接回答"
- "这是个问题，方案如下..."
- "这个问题需要记录"

---

## ⚠️ 核心原则

1. **任何操作前必须验证，不能假设，不能靠记忆**。
2. **遇到需要处理的问题时禁止盲目测试，必须查看问题对应的代码文件，必须找到问题的根本原因，必须与实际错误对应**。
3. **禁止口头承诺，口头答应，一切以测试通过为准**。
4. **任何文件修改前必须查看代码强制严谨思考**。
5. **开发、自测过程中禁止让用户手动操作，能自己执行的不要让用户做**。

---

## ⚠️ IDE 卡死防范

- **禁止** `$(...)` + 管道组合
- **禁止** MySQL `-e` 执行多条语句
- **禁止** `python3 -c "..."` 执行多行脚本（超过2行必须写成 .py 文件再执行）
- **禁止** `lsof -ti:端口` 不加 ignoreWarning（会被安全检查拦截）
- **正确做法**：SQL 写入 `.sql` 文件用 `< data/xxx.sql` 执行；Python 验证脚本写成 .py 文件用 `python3 xxx.py` 执行；端口检查用 `lsof -ti:端口` + ignoreWarning:true

---

## ⚠️ 自测要求

**禁止让用户手动操作** - 能自己执行的，不要让用户做

- Python：`python -m pytest` 或直接运行脚本验证
- MCP Server：通过 stdio 发送 JSON-RPC 消息验证
- Web 看板：Playwright 验证
- 自测通过后才能说"等待验证"

---

# 启动检查

1. 严格按照本规则来执行
2. **调用 `status`** 获取会话状态（阻塞、进度、待处理）
3. 然后按问题跟踪步骤执行

**⚠️ 无论用户问什么问题，第一个动作必须是调用 status**

---

# 项目知识（从 MCP 加载）

**每次新会话加载项目知识**：`recall`（tags: ["项目知识"], scope: "project", top_k: 100）

**加载用户偏好**：`recall`（tags: ["preference"], scope: "user", top_k: 20）

**查询踩坑记录**：`recall`（query: 关键词, tags: ["踩坑"]）

# 开发规则

> 禁止口头承诺，一切以测试通过为准。
> 任何文件修改前必须强制严谨思考。
> 遇到报错或异常时严禁盲目测试，必须分析问题根本原因。

---

## 何时调用

- 新会话开始时：调用 `status`（不传参数）读取上次的工作状态，了解进度和阻塞情况
- 遇到踩坑/技术要点时：调用 `remember` 记录，标签加 "踩坑"
- 需要查找历史经验时：调用 `recall` 语义搜索，或按标签精确查询
- 发现 bug 或待处理事项时：调用 `track`（action: create）记录问题
- 修复问题后：调用 `track`（action: update）更新排查内容和结论
- 问题关闭时：调用 `track`（action: archive）归档
- 任务进度变化时：调用 `status`（传 state 参数）更新当前任务、进度、最近修改
- 对话结束前：调用 `auto_save` 保存本次对话的决策、修改、踩坑、待办、偏好

## 工具速查

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| remember | 存入记忆 | content, tags, scope(project/user) |
| recall | 语义搜索记忆 | query, tags, scope, top_k |
| forget | 删除记忆 | memory_id / memory_ids |
| status | 会话状态管理 | state(不传=读取, 传=更新) |
| track | 问题跟踪 | action(create/update/archive/list) |
| digest | 记忆摘要 | scope, since_sessions, tags |
| auto_save | 自动保存会话 | decisions, modifications, pitfalls, todos, preferences |

---

## 知识库（通过 MCP remember/recall 管理）

**遇到问题必记**：命令失败、框架踩坑、技术要点 → `remember`（标签：`踩坑`）

**查询踩坑记录**：`recall`（query: 关键词, tags: ["踩坑"]）

---

## 会话状态（通过 MCP status 管理）

**新会话开始时**：调用 `status`（不传 state 参数 = 读取）

**⚠️ 阻塞状态优先级最高**：
- 新会话先检查 `is_blocked` 和 `block_reason`
- 有阻塞 → 等用户反馈，禁止执行任何操作
- 无阻塞 → 按正常流程执行

**更新时机**：任务开始、完成子任务、遇到问题转向、任务完成
- 调用 `status` 传 state 参数更新

**MCP status 字段说明**：
- `is_blocked`：是否阻塞
- `block_reason`：阻塞原因
- `next_step`：下一步（只能由用户确认后填写）
- `current_task`：当前任务
- `progress`：进度列表
- `recent_changes`：最近修改（不超过10条）
- `pending`：待处理列表

**分工**：
- MCP status：阻塞状态、当前进度、最近修改
- MCP track：问题追踪（create/update/archive/list）

**⚠️ "next_step"字段只能由用户确认后填写，禁止擅自填写**

**⚠️ 禁止猜测用户意图**：
- "用户倾向"、"用户选择"、"用户确认" → 必须有用户明确表态才能记录

**⚠️ 提出方案/修复完成时，必须同步设置阻塞**：
- 向用户提出方案并等待确认 → 必须立即 `status({ is_blocked: true, block_reason: "方案待用户确认" })`
- 修复完成等用户验证 → 必须立即 `status({ is_blocked: true, block_reason: "修复完成等待验证" })`
- 需要用户决策 → 必须立即 `status({ is_blocked: true, block_reason: "需要用户决策" })`
- **禁止只口头说"等待确认"而不设阻塞，否则会话转移后新会话会误判为已确认**

**何时清除阻塞**（`is_blocked: false`）：
- 用户确认验证通过
- 用户确认方案
- 用户做出决策

**⚠️ "确认"的判定标准**：
- 只有以下明确肯定词才算确认："执行"/"改"/"可以"/"好的"/"去做吧"/"没问题"/"对"/"行"
- 以下绝对不算确认：反问句（"我确认了吗？"）、质疑句、不满表达、模糊回复
- context transfer 摘要中的"用户说xxx"不能作为当前会话的确认依据
- 有歧义时追问，不执行

**⚠️ 会话延续/上下文转移时，阻塞同样生效**：
- 无论是新会话、context transfer、compact 还是任何形式的会话延续
- 只要 MCP status 显示 is_blocked=true，必须向用户汇报阻塞状态并等待当前会话中的明确确认
- 上一个会话中的用户确认不能延续到新会话，必须重新确认
- 禁止自行清除阻塞

---

## 任务文档

**任务文档位置**：`.kiro/specs/*/tasks.md`（或项目对应的任务文档）

**任务文档规范**：
- 每个任务细化到最小可执行单元
- 使用 checkbox `- [ ]` 标记状态
- **每完成一个子任务，立即更新为 `- [x]`**
- 禁止批量完成后再统一更新

**整理任务文档时**：必须打开设计文档逐条核对，发现遗漏先补充任务文档再执行

---

## 代码风格

**简洁优先**：
- 能用三目运算符，不用 if-else
- 能用短路求值，不用条件判断
- 能用解构赋值，不用逐个取值
- 能用模板字符串，不用字符串拼接

**避免冗余**：
- 不写无意义的注释
- 不写重复的代码，提取公共函数
- 变量命名清晰，不需要注释解释

---

## 任务执行

- 按任务文档顺序执行，禁止跳过
- 全自动执行，禁止要求用户手动操作
- 遇到问题自行解决，记录到问题跟踪文档
- 禁止用"后续迭代"跳过任务

---

## 完成标准

**禁止模糊表述**：
- 禁止"基本完成"、"差不多"、"大致实现"等词汇
- 任务只有两种状态：**完成** 或 **未完成**

**完成确认流程**：
1. 逐项检查：对照任务清单逐一验证
2. 代码验证：确认代码存在且正确
3. 功能测试：编译或运行测试验证
4. 标记完成：测试通过后才标记完成

---

## 代码修改检查

**修改前**：
- `recall` 查询相关踩坑记录
- **必须先查看该功能的现有实现**
- **涉及数据存储时，必须确认数据流向**

**修改后**：
- 运行相关测试或编译验证
- 确认修改不影响其他功能

---

## 问题追踪（通过 MCP track 管理）

**工具**：`track`（action: create/update/list/archive）

**问题处理原则**：
- 一次只修一个问题
- 修复过程中发现新问题 → `track create` 记录标题后继续当前问题
- 用户中途打断提出新问题 → 同样 `track create` 记录，再决定优先级
- 当前问题修复完成后，再按顺序处理新问题

**发现新问题时判断**：新问题不解决，当前问题能否继续？
- 能继续 → `track create` 记录标题，继续当前问题
- 不能继续（阻塞）→ `track update` 当前问题标注阻塞，先处理阻塞问题

**问题记录流程**：
1. `track create`：记录问题标题 + 调用 `status` 更新 pending
2. 排查问题原因，`track update` 更新 content（根因、方案）
3. 向用户说明问题和方案
4. 修改代码并自测
5. 自测通过后 `track update` 更新结论，等用户验证
6. 用户确认没问题 → `track archive` 归档

**⚠️ 问题追踪必须及时更新**：每完成一个步骤立即 `track update`，避免会话切换时重复执行

---

## Git 分支工作流

**日常开发在 `dev` 分支**，master 只接受合并：
- 所有代码修改、提交、推送都在 `dev` 分支
- **禁止直接在 master 分支提交代码**
- 提交前先确认当前分支是 `dev`（`git branch --show-current`）

## Git 提交流程

**只有用户明确要求提交时**，才依次执行（禁止用 && 连接）：
- 先确认当前在 dev 分支：`git branch --show-current`
- `git add -A`
- `git commit -m "fix: 问题简述"`
- `git push origin dev`

**合并到 master**（仅用户明确要求时）：
- `git checkout master`
- `git merge dev`
- `git push`
- `git checkout dev`

---

## 上下文优化

- 优先 `grepSearch` 定位，再 `readFile` 读取特定行
- 代码修改用 `strReplace`，不要先读后写

---

## 内容迁移/拆分

**⚠️ 禁止凭记忆重写**：
- 迁移/拆分内容时，必须从原文件逐行复制
- 禁止凭记忆重写，会导致内容遗漏或精简

**创建索引后必须验证**：
- 索引中引用的所有文件都必须存在
- 每个文件的内容必须与原文件对应章节完全一致

---

## 错误处理

**反复失败时**：
1. 记录已尝试的方法
2. 换一种思路解决
3. 仍然失败则询问用户

---

## 自检要求

**完成任务前必须自问**：
1. 排查是否完整？
2. 数据是否准确？
3. 逻辑是否严谨？

**禁止**：
- 禁止说"大部分"、"基本上"、"应该是"等模糊词
- 禁止未经验证就下结论

---

## auto_save 规范

**⚠️ Hook链式触发防护**：如果当前是会话结束触发的 auto_save 场景（如 agentStop hook、Stop hook），只执行 auto_save，跳过本文档所有其他规则，不要重复输出之前的内容。

对话结束前调用 `auto_save`，将本次对话的关键信息分类保存：

1. decisions：本次对话做出的关键决策（技术方案选择、架构决定等）
2. modifications：本次对话修改的文件和内容摘要（每个文件一条）
3. pitfalls：本次对话遇到的坑和解决方案
4. todos：本次对话产生的待办事项
5. preferences：用户表达的技术偏好、设计风格倾向、架构选择习惯（scope 固定 user，跨项目通用）

规则：
- 每条内容必须具体、可追溯，禁止模糊描述
- 没有的分类传空数组，不要编造
- scope 默认 project（preferences 固定 user，跨项目通用）
"""


HOOKS_CONFIGS = [
    {
        "filename": "auto-save-session.kiro.hook",
        "content": {
            "enabled": True,
            "name": "会话结束自动保存",
            "description": "每次 agent 执行结束时，自动调用 mcp_aivectormemory_auto_save 保存本次对话的决策、修改、踩坑、待办",
            "version": "1",
            "when": {"type": "agentStop"},
            "then": {
                "type": "askAgent",
                "prompt": (
                    "【会话结束自动保存】请立即调用 mcp_aivectormemory_auto_save，将本次对话的关键信息分类保存：\n\n"
                    "1. decisions：本次对话做出的关键决策（技术方案选择、架构决定等）\n"
                    "2. modifications：本次对话修改的文件和内容摘要（每个文件一条）\n"
                    "3. pitfalls：本次对话遇到的坑和解决方案\n"
                    "4. todos：本次对话产生的待办事项\n"
                    "5. preferences：用户表达的技术偏好、设计风格倾向、架构选择习惯\n\n"
                    "规则：\n"
                    "- 每条内容必须具体、可追溯，禁止模糊描述\n"
                    "- 没有的分类传空数组，不要编造\n"
                    "- scope 默认 project（preferences 固定 user，跨项目通用）"
                ),
            },
            "shortName": "auto-save-session",
        },
    },
    {
        "filename": "dev-workflow-check.kiro.hook",
        "content": {
            "enabled": True,
            "name": "开发流程检查",
            "description": "每次收到用户消息时，检查核心原则、问题处理原则、自测要求",
            "version": "1",
            "when": {"type": "promptSubmit"},
            "then": {
                "type": "askAgent",
                "prompt": (
                    "## ⚠️ Hook链式触发防护\n\n"
                    "如果当前消息包含【会话结束自动保存】关键词，说明是 agentStop hook 触发的 auto-save，"
                    "跳过以下所有规则，直接执行 auto_save 即可。\n\n---\n\n"
                    "## ⚠️ 核心原则\n\n"
                    "1. 任何操作前必须验证，不能假设，不能靠记忆\n"
                    "2. 遇到问题禁止盲目测试，必须查看代码找到根本原因\n"
                    "3. 禁止口头承诺，一切以测试通过为准\n"
                    "4. 任何文件修改前必须查看代码严谨思考\n"
                    "5. 开发、自测过程中禁止让用户手动操作\n\n"
                    "## ⚠️ 自测要求\n\n"
                    "禁止让用户手动操作 - 能自己执行的，不要让用户做\n\n"
                    "- Python：python -m pytest 或直接运行脚本验证\n"
                    "- MCP Server：通过 stdio 发送 JSON-RPC 消息验证\n"
                    "- Web 看板：Playwright 验证\n"
                    "- 自测通过后才能说\"等待验证\""
                ),
            },
            "shortName": "dev-workflow-check",
        },
    },
    {
        "filename": "pre-tool-use-check.kiro.hook",
        "content": {
            "enabled": True,
            "name": "代码修改前检查 track issue",
            "description": "Edit/Write 工具执行前，检查当前项目是否有活跃的 track issue，没有则拒绝执行",
            "version": "1",
            "when": {"type": "preToolUse", "matcher": "Edit|Write"},
            "then": {
                "type": "command",
                "command": "",  # 占位，install 时动态填充
            },
            "shortName": "pre-tool-use-check",
        },
    },
]


AUTO_SAVE_PROMPT = (
    "立即调用 auto_save 保存本次会话，不要重复分析对话内容，不要输出其他内容。"
)

def _check_track_script_path() -> Path:
    """返回包内 check_track.sh 的路径"""
    return Path(__file__).parent / "hooks" / "check_track.sh"


CLAUDE_CODE_HOOKS_CONFIG = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": "",  # 占位，install 时动态填充实际路径
                        "timeout": 10,
                    }
                ]
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "prompt",
                        "prompt": AUTO_SAVE_PROMPT + "\n\nContext: $ARGUMENTS",
                        "timeout": 30,
                    }
                ]
            }
        ]
    }
}

CURSOR_HOOKS_CONFIG = {
    "version": 1,
    "hooks": {
        "stop": [
            {
                "command": "echo 'Please call auto_save (mcp_aivectormemory_auto_save) to save this session: decisions, modifications, pitfalls, todos, preferences. Each item must be specific. Empty categories use empty arrays.' >&2; exit 2",
            }
        ]
    }
}

WINDSURF_HOOKS_CONFIG = {
    "hooks": {
        "post_cascade_response": [
            {
                "command": "echo 'Reminder: call auto_save to save session data if not done yet.' >&2; exit 0",
                "show_output": False,
            }
        ]
    }
}


OPENCODE_PLUGIN_CONTENT = """\
// AIVectorMemory plugin for OpenCode (@opencode-ai/plugin)
// - tool.execute.before: 检查 Edit/Write 前是否有活跃 track issue
// - event: stop 时提醒调用 auto_save
import { execSync } from "child_process";
import { homedir } from "os";
import { existsSync } from "fs";
import { join } from "path";

const DB_PATH = join(homedir(), ".aivectormemory", "memory.db");

function hasActiveIssues(projectDir) {
  if (!existsSync(DB_PATH)) return true; // 首次使用放行
  try {
    const result = execSync(
      `sqlite3 "${DB_PATH}" "SELECT COUNT(*) FROM issues WHERE project_dir='${projectDir}' AND status IN ('pending','in_progress');"`,
      { encoding: "utf-8", timeout: 5000 }
    ).trim();
    return parseInt(result, 10) > 0;
  } catch {
    return true; // 查询失败放行
  }
}

export default async ({ project }) => ({
  "tool.execute.before": async ({ tool, sessionID }, output) => {
    if (tool !== "Edit" && tool !== "Write" && tool !== "edit" && tool !== "write") return;
    const projectDir = project?.path || process.cwd();
    if (!hasActiveIssues(projectDir)) {
      output.args = {
        ...output.args,
        __blocked: "⚠️ 当前项目没有活跃的 track issue。请先调用 track(action: create) 记录问题后再修改代码。",
      };
    }
  },
  event: async ({ event }) => {
    if (event.type === "session.stop" || event.type === "stop") {
      console.error(
        "Reminder: call auto_save (mcp_aivectormemory_auto_save) to save session data."
      );
    }
  },
});
"""


def _copy_check_track_script(target_dir: Path) -> tuple[Path, bool]:
    """复制 check_track.sh 到目标目录，返回 (目标路径, 是否有变更)"""
    import shutil
    target_dir.mkdir(parents=True, exist_ok=True)
    src = _check_track_script_path()
    dst = target_dir / "check_track.sh"
    if not dst.exists() or dst.read_text("utf-8") != src.read_text("utf-8"):
        shutil.copy2(src, dst)
        dst.chmod(0o755)
        return dst, True
    return dst, False


def _build_claude_code_hooks(script_path: str) -> dict:
    """构建 Claude Code hooks 配置，填充实际脚本路径"""
    import copy
    cfg = copy.deepcopy(CLAUDE_CODE_HOOKS_CONFIG)
    cfg["hooks"]["PreToolUse"][0]["hooks"][0]["command"] = script_path
    return cfg


def _write_claude_code_hooks(hooks_dir: Path) -> list[str]:
    """写入 Claude Code hooks 到 .claude/settings.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # 复制检查脚本
    script_dir = hooks_dir / "hooks"
    script_path, script_changed = _copy_check_track_script(script_dir)
    results.append(f"{'✓ 已同步' if script_changed else '- 无变更'}  Script: .claude/hooks/check_track.sh")
    # 构建配置
    new_hooks_cfg = _build_claude_code_hooks(str(script_path))
    filepath = hooks_dir / "settings.json"
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    existing = config.get("hooks", {})
    new_hooks = new_hooks_cfg["hooks"]
    changed = False
    for event_name in ("PreToolUse", "Stop"):
        if existing.get(event_name) != new_hooks[event_name]:
            changed = True
            break
    if changed:
        config.setdefault("hooks", {})
        config["hooks"]["PreToolUse"] = new_hooks["PreToolUse"]
        config["hooks"]["Stop"] = new_hooks["Stop"]
        filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        results.append("✓ 已生成  Hook: .claude/settings.json (PreToolUse + Stop)")
    else:
        results.append("- 无变更  Hook: .claude/settings.json (PreToolUse + Stop)")
    return results


def _write_cursor_hooks(hooks_dir: Path) -> list[str]:
    """写入 Cursor hooks 到 .cursor/hooks.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    filepath = hooks_dir / "hooks.json"
    new_content = json.dumps(CURSOR_HOOKS_CONFIG, indent=2, ensure_ascii=False) + "\n"
    if filepath.exists():
        existing = filepath.read_text("utf-8")
        if existing.strip() == new_content.strip():
            results.append("- 无变更  Hook: .cursor/hooks.json (stop)")
            return results
    filepath.write_text(new_content, encoding="utf-8")
    results.append("✓ 已生成  Hook: .cursor/hooks.json (stop)")
    return results


def _write_windsurf_hooks(hooks_dir: Path) -> list[str]:
    """写入 Windsurf hooks 到 .windsurf/hooks.json"""
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    filepath = hooks_dir / "hooks.json"
    new_content = json.dumps(WINDSURF_HOOKS_CONFIG, indent=2, ensure_ascii=False) + "\n"
    if filepath.exists():
        existing = filepath.read_text("utf-8")
        if existing.strip() == new_content.strip():
            results.append("- 无变更  Hook: .windsurf/hooks.json (post_cascade_response)")
            return results
    filepath.write_text(new_content, encoding="utf-8")
    results.append("✓ 已生成  Hook: .windsurf/hooks.json (post_cascade_response)")
    return results


def _write_opencode_plugins(plugins_dir: Path) -> list[str]:
    """写入 OpenCode 插件文件，返回变更列表"""
    results = []
    plugins_dir.mkdir(parents=True, exist_ok=True)
    filepath = plugins_dir / "aivectormemory-auto-save.js"
    if filepath.exists() and filepath.read_text("utf-8").strip() == OPENCODE_PLUGIN_CONTENT.strip():
        results.append("- 无变更  Plugin: aivectormemory-auto-save.js")
    else:
        filepath.write_text(OPENCODE_PLUGIN_CONTENT, encoding="utf-8")
        results.append("✓ 已生成  Plugin: aivectormemory-auto-save.js")
    return results


def _write_hooks(hooks_dir: Path) -> list[str]:
    """写入 hook 文件到指定目录（Kiro），返回变更列表"""
    import copy
    results = []
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # 复制 check_track.sh 到 hooks 目录
    script_path, script_changed = _copy_check_track_script(hooks_dir)
    results.append(f"{'✓ 已同步' if script_changed else '- 无变更'}  Script: check_track.sh")
    for hook in HOOKS_CONFIGS:
        content = copy.deepcopy(hook["content"])
        # 动态填充 pre-tool-use-check 的 command 路径
        if hook["filename"] == "pre-tool-use-check.kiro.hook":
            content["then"]["command"] = str(script_path)
        filepath = hooks_dir / hook["filename"]
        new_content = json.dumps(content, indent=2, ensure_ascii=False) + "\n"
        if filepath.exists():
            existing = filepath.read_text("utf-8")
            if existing.strip() == new_content.strip():
                results.append(f"- 无变更  Hook: {hook['filename']}")
                continue
        filepath.write_text(new_content, encoding="utf-8")
        results.append(f"✓ 已生成  Hook: {hook['filename']}")
    return results


def _write_steering(filepath: Path, mode: str) -> bool:
    if mode == "file":
        content = STEERING_CONTENT.strip() + "\n"
        if filepath.exists() and filepath.read_text("utf-8").strip() == content.strip():
            return False
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding="utf-8")
        return True
    if mode == "append":
        existing = filepath.read_text("utf-8") if filepath.exists() else ""
        block = f"\n{STEERING_MARKER}\n{STEERING_CONTENT.strip()}\n"
        if STEERING_MARKER in existing:
            start = existing.index(STEERING_MARKER)
            next_marker = existing.find("\n<!-- ", start + len(STEERING_MARKER))
            end = next_marker if next_marker != -1 else len(existing)
            old_block = existing[start:end]
            new_block = f"{STEERING_MARKER}\n{STEERING_CONTENT.strip()}\n"
            if old_block.strip() == new_block.strip():
                return False
            updated = existing[:start] + new_block + existing[end:]
            filepath.write_text(updated, encoding="utf-8")
            return True
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(block)
        return True
    return False


def _claude_desktop_path() -> Path | None:
    s = platform.system()
    if s == "Darwin":
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    if s == "Windows":
        import os
        return Path(os.environ.get("APPDATA", "")) / "Claude/claude_desktop_config.json"
    if s == "Linux":
        return Path.home() / ".config/Claude/claude_desktop_config.json"
    return None


def _build_config(cmd: str, args: list[str], fmt: str) -> dict:
    env_block = {}
    hf_endpoint = os.environ.get("HF_ENDPOINT", "")
    if hf_endpoint:
        env_block["HF_ENDPOINT"] = hf_endpoint
    if fmt == "opencode":
        cfg = {"type": "local", "command": [cmd] + args, "enabled": True}
        if env_block:
            cfg["env"] = env_block
        return cfg
    cfg = {
        "command": cmd,
        "args": args,
        "disabled": False,
        "autoApprove": ["remember", "recall", "forget", "status", "track", "digest", "auto_save"],
    }
    if env_block:
        cfg["env"] = env_block
    return cfg


def _merge_config(filepath: Path, key: str, server_name: str, server_config: dict) -> bool:
    config = {}
    if filepath.exists():
        try:
            config = json.loads(filepath.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            config = {}
    config.setdefault(key, {})
    if server_name in config[key] and config[key][server_name] == server_config:
        return False
    config[key][server_name] = server_config
    old_key = "devmemory"
    if old_key in config[key] and old_key != server_name:
        del config[key][old_key]
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def _choose(prompt: str, options: list[tuple], allow_all: bool = False) -> list | None:
    for i, (label, *_) in enumerate(options, 1):
        print(f"  {i}. {label}")
    if allow_all:
        print(f"  a. 全部安装")
    print()
    choice = input(f"{prompt}: ").strip().lower()
    if not choice:
        return None
    if allow_all and choice == "a":
        return list(range(len(options)))
    nums = {int(p.strip()) - 1 for p in choice.split(",") if p.strip().isdigit()}
    selected = [i for i in nums if 0 <= i < len(options)]
    return selected or None


def run_install(project_dir: str | None = None):
    pdir = str(Path(project_dir or ".").resolve()).replace("\\", "/")
    print(f"项目目录: {pdir}\n")

    # 1. 选择启动方式
    print("启动方式：")
    runner_indices = _choose("选择启动方式 [1]", RUNNERS)
    if runner_indices is None:
        runner_indices = [0]  # 默认 pip/pipx
    cmd, args = RUNNERS[runner_indices[0]][1](pdir)
    print(f"  → {cmd} {' '.join(args)}\n")

    # 2. 选择 IDE
    print("支持的 IDE：")
    valid_ides = []
    for name, path_fn, fmt, is_global, steering_fn, steering_mode, hooks_fn in IDES:
        p = path_fn(Path(pdir))
        if p is None:
            continue
        tag = " (全局)" if is_global else ""
        valid_ides.append((f"{name}{tag}", path_fn, fmt, steering_fn, steering_mode, hooks_fn))

    ide_indices = _choose("选择 IDE（编号，逗号分隔多选，a=全部）", valid_ides, allow_all=True)
    if ide_indices is None:
        print("未选择，退出")
        return

    # 3. 写入配置
    print()
    root = Path(pdir)
    for idx in ide_indices:
        label, path_fn, fmt, steering_fn, steering_mode, hooks_fn = valid_ides[idx]
        filepath = path_fn(root)
        if filepath is None:
            continue
        server_config = _build_config(cmd, args, fmt)
        key = "mcp" if fmt == "opencode" else "mcpServers"
        changed = _merge_config(filepath, key, "aivectormemory", server_config)
        status = "✓ 已更新" if changed else "- 无变更"
        print(f"  {status}  {label} MCP 配置")

        # 4. 写入 Steering 规则
        if steering_fn and steering_mode:
            steering_path = steering_fn(root)
            s_changed = _write_steering(steering_path, steering_mode)
            s_status = "✓ 已生成" if s_changed else "- 无变更"
            print(f"  {s_status}  {label} Steering 规则 → {steering_path.relative_to(root)}")

        # 5. 写入 Hooks / Plugins
        if hooks_fn:
            hooks_dir = hooks_fn(root)
            hooks_dir_str = str(hooks_dir)
            if hooks_dir_str.endswith(".opencode/plugins"):
                hook_results = _write_opencode_plugins(hooks_dir)
            elif hooks_dir_str.endswith(".claude"):
                hook_results = _write_claude_code_hooks(hooks_dir)
            elif hooks_dir_str.endswith(".cursor"):
                hook_results = _write_cursor_hooks(hooks_dir)
            elif hooks_dir_str.endswith(".windsurf"):
                hook_results = _write_windsurf_hooks(hooks_dir)
            else:
                hook_results = _write_hooks(hooks_dir)
            for r in hook_results:
                print(f"  {r}")

    print("\n安装完成，重启 IDE 即可使用")

    # 6. 注册项目到数据库（Web 看板可见）
    try:
        from aivectormemory.db.connection import ConnectionManager
        from aivectormemory.db.schema import init_db
        cm = ConnectionManager(pdir)
        init_db(cm.conn)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        cm.conn.execute(
            "INSERT OR IGNORE INTO session_state (project_dir, is_blocked, block_reason, next_step, current_task, progress, recent_changes, pending, updated_at) VALUES (?,0,'','','','[]','[]','[]',?)",
            (pdir, now)
        )
        cm.conn.commit()
        cm.close()
    except Exception as e:
        print(f"\n⚠️  项目注册到数据库失败（Web 看板可能不显示此项目）: {e}")
