🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | English | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Give your AI coding assistant a memory — Cross-session persistent memory MCP Server</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problem**: AI assistants "forget" everything with each new session — repeating the same mistakes, forgetting project conventions, losing development progress. Worse, to compensate for this amnesia, you have to inject massive context into every conversation, wasting tokens.
>
> **AIVectorMemory**: Provides a local vector memory store for AI via the MCP protocol, letting it remember everything — project knowledge, pitfalls, development decisions, work progress — persisted across sessions. Semantic retrieval recalls on demand, no more bulk injection, dramatically reducing token consumption.

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Semantic Search** | Vector similarity based — searching "database timeout" finds "MySQL connection pool pitfall" |
| 🏠 **Fully Local** | ONNX Runtime local inference, no API Key needed, data never leaves your machine |
| 🔄 **Smart Dedup** | Cosine similarity > 0.95 auto-updates, no duplicate storage |
| 📊 **Web Dashboard** | Built-in management UI with 3D vector network visualization |
| 🔌 **All IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae and more |
| 📁 **Project Isolation** | Single DB shared across projects, auto-isolated by project_dir |
| 🏷️ **Tag System** | Memory categorization, tag search, rename, merge |
| 💰 **Save Tokens** | Semantic retrieval on demand replaces bulk context injection, reducing 50%+ redundant token usage |
| 📋 **Issue Tracking** | Lightweight issue tracker, AI auto-records and archives |
| 🔐 **Web Auth** | Dashboard supports Token authentication to prevent unauthorized access |
| ⚡ **Embedding Cache** | No redundant vector computation for identical content, faster writes |
| 📤 **Export/Import** | Memory data JSON export and import, supports migration and backup |
| 🎯 **Action Feedback** | Toast notifications, empty state guides, complete interaction experience |
| ➕ **Add Projects** | Add projects directly from dashboard with directory browser |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   AI IDE                         │
│  OpenCode / Claude Code / Cursor / Kiro / ...   │
└──────────────────────┬──────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────┐
│              AIVectorMemory Server               │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ remember │ │  recall   │ │   auto_save      │ │
│  │ forget   │ │  digest   │ │   status/track   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │            │               │             │
│  ┌────▼────────────▼───────────────▼──────────┐  │
│  │         Embedding Engine (ONNX)            │  │
│  │      intfloat/multilingual-e5-small        │  │
│  └────────────────────┬───────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼───────────────────────┐  │
│  │     SQLite + sqlite-vec (Vector Index)     │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: pip install

```bash
pip install aivectormemory
pip install --upgrade aivectormemory  # Upgrade to latest version
cd /path/to/your/project
run install          # Interactive IDE selection, one-click setup
```

### Option 2: uvx (zero install)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Option 3: Manual configuration

```json
{
  "mcpServers": {
    "aivectormemory": {
      "command": "run",
      "args": ["--project-dir", "/path/to/your/project"]
    }
  }
}
```

<details>
<summary>📍 IDE Configuration File Locations</summary>

| IDE | Config Path |
|-----|------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 MCP Tools

### `remember` — Store a memory

```
content (string, required)   Memory content in Markdown format
tags    (string[], required)  Tags, e.g. ["pitfall", "python"]
scope   (string)              "project" (default) / "user" (cross-project)
```

Similarity > 0.95 auto-updates existing memory, no duplicates.

### `recall` — Semantic search

```
query   (string)     Semantic search keywords
tags    (string[])   Exact tag filter
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Number of results, default 5
```

Vector similarity matching — finds related memories even with different wording.

### `forget` — Delete memories

```
memory_id  (string)     Single ID
memory_ids (string[])   Batch IDs
```

### `status` — Session state

```
state (object, optional)   Omit to read, pass to update
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Maintains work progress across sessions, auto-restores context in new sessions.

### `track` — Issue tracking

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Issue title
issue_id (integer)  Issue ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Investigation content
```

### `digest` — Memory summary

```
scope          (string)    Scope
since_sessions (integer)   Last N sessions
tags           (string[])  Tag filter
```

### `auto_save` — Auto save

```
decisions[]      Key decisions
modifications[]  File modification summaries
pitfalls[]       Pitfall records
todos[]          Todo items
```

Auto-categorizes, tags, and deduplicates at the end of each conversation.

## 📊 Web Dashboard

```bash
run web --port 9080
run web --port 9080 --quiet          # Suppress request logs
run web --port 9080 --quiet --daemon  # Run in background (macOS/Linux)
```

Visit `http://localhost:9080` in your browser.

- Multi-project switching, memory browse/search/edit/delete/export/import
- Semantic search (vector similarity matching)
- One-click project data deletion
- Session status, issue tracking
- Tag management (rename, merge, batch delete)
- Token authentication protection
- 3D vector memory network visualization
- 🌐 Multi-language support (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Project Selection" width="100%">
  <br>
  <em>Project Selection</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Overview & Vector Network Visualization" width="100%">
  <br>
  <em>Overview & Vector Network Visualization</em>
</p>

## ⚡ Pairing with Steering Rules

AIVectorMemory is the storage layer. Use Steering rules to tell AI **when and how** to call these tools.

Running `run install` auto-generates Steering rules and Hooks config — no manual setup needed.

| IDE | Steering Location | Hooks |
|-----|------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (appended) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (appended) | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (appended) | `.opencode/plugins/*.js` |

<details>
<summary>📋 Steering Rules Example (auto-generated)</summary>

```markdown
# AIVectorMemory - Cross-Session Persistent Memory

## Startup Check

At the start of each new session, execute in order:

1. Call `status` (no params) to read session state, check `is_blocked` and `block_reason`
2. Call `recall` (tags: ["project-knowledge"], scope: "project") to load project knowledge
3. Call `recall` (tags: ["preference"], scope: "user") to load user preferences

## When to Call

- New session starts: call `status` to read previous work state
- Hit a pitfall: call `remember` to record, add tag "pitfall"
- Need historical experience: call `recall` for semantic search
- Found a bug or TODO: call `track` (action: create)
- Task progress changes: call `status` (pass state param) to update
- Before conversation ends: call `auto_save` to save this session

## Session State Management

status fields: is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

⚠️ **Blocking safeguard**: When proposing a plan awaiting confirmation or completing a fix awaiting verification, always call `status` to set `is_blocked: true` simultaneously. This prevents a new session from mistakenly assuming "confirmed" and executing autonomously after context transfer.

## Issue Tracking

1. `track create` → Record issue
2. `track update` → Update investigation content
3. `track archive` → Archive resolved issues
```

</details>

<details>
<summary>🔗 Hooks Config Example (Kiro only, auto-generated)</summary>

Auto-save on session end removed. Dev workflow check (`.kiro/hooks/dev-workflow-check.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Dev Workflow Check",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Core principles: verify before acting, no blind testing, only mark done after tests pass"
  }
}
```

</details>

## 🇨🇳 Users in China

The embedding model (~200MB) is auto-downloaded on first run. If slow:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Or add env to MCP config:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python >= 3.10 |
| Vector DB | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protocol | Model Context Protocol (MCP) |
| Web | Native HTTPServer + Vanilla JS |

## 📋 Changelog

### v0.2.4

- 🔇 Stop hook prompt changed to direct instruction, eliminating Claude Code duplicate replies
- 🛡️ Steering rules auto_save spec adds short-circuit protection, skipping other rules on session end
- 🐛 `_copy_check_track_script` idempotency fix (return change status to avoid false "synced" reports)
- 🐛 issue_repo delete `row.get()` incompatibility with `sqlite3.Row` fix (use `row.keys()` check)
- 🐛 Web dashboard project selection page scroll fix (unable to scroll with many projects)
- 🐛 Web dashboard CSS pollution fix (strReplace global replacement corrupted 6 style selectors)
- 🔄 Web dashboard all confirm() dialogs replaced with custom showConfirm modal (memory/issue/tag/project delete)
- 🔄 Web dashboard delete operations add API error response handling (toast instead of alert)
- 🧹 `.gitignore` adds `.devmemory/` legacy directory ignore rule
- 🧪 pytest temp project DB residual auto-cleanup (conftest.py session fixture)

### v0.2.3

- 🛡️ PreToolUse Hook: enforce track issue check before Edit/Write, reject if no active issues (Claude Code / Kiro / OpenCode)
- 🔌 OpenCode plugin upgraded to `@opencode-ai/plugin` SDK format (tool.execute.before hook)
- 🔧 `run install` auto-deploys check_track.sh script with dynamic path injection
- 🐛 Fix issue_repo archive/delete `row.get()` incompatibility with `sqlite3.Row`
- 🐛 Fix session_id race condition: read latest value from DB before incrementing
- 🐛 Add track date format validation (YYYY-MM-DD) + issue_id type validation
- 🐛 Harden Web API request parsing (Content-Length validation + 10MB limit + JSON error handling)
- 🐛 Fix tag filter scope logic (`filter_dir is not None` instead of falsy check)
- 🐛 Add export vector data struct.unpack byte length validation
- 🐛 Schema versioned migration (schema_version table + v1/v2/v3 incremental migration)
- 🐛 Fix `__init__.py` version number sync

### v0.2.2

- 🔇 Web dashboard `--quiet` flag to suppress request logs
- 🔄 Web dashboard `--daemon` flag for background execution (macOS/Linux)
- 🔧 `run install` MCP config generation fix (sys.executable + complete fields)
- 📋 Issue tracking CRUD & archive (Web dashboard add/edit/archive/delete + memory association)
- 👆 Click anywhere on list row to open edit modal (memories/issues/tags)
- 🔒 Blocking rules enforced across session continuations/context transfers (re-confirmation required)

### v0.2.1

- ➕ Add projects from Web dashboard (directory browser + manual input)
- 🏷️ Fix tag cross-project pollution (tag operations scoped to current project + global memories)
- 📐 Modal pagination ellipsis truncation + 80% width
- 🔌 OpenCode install auto-generates auto_save plugin (session.idle event trigger)
- 🔗 Claude Code / Cursor / Windsurf install auto-generates Hooks config (auto-save on session end)
- 🎯 Web dashboard UX improvements (Toast feedback, empty state guides, export/import toolbar)
- 🔧 Stats card click-through (click memory/issue counts to view details)
- 🏷️ Tag management page distinguishes project/global tag sources (📁/🌐 markers)
- 🏷️ Project card tag counts now include global memory tags

### v0.2.0

- 🔐 Web dashboard Token authentication
- ⚡ Embedding vector cache, no redundant computation for identical content
- 🔍 recall supports combined query + tags search
- 🗑️ forget supports batch deletion (memory_ids parameter)
- 📤 Memory export/import (JSON format)
- 🔎 Web dashboard semantic search
- 🗂️ Web dashboard project delete button
- 📊 Web dashboard performance optimization (eliminated full table scans)
- 🧠 digest smart compression
- 💾 session_id persistence
- 📏 content length limit protection
- 🏷️ version dynamic reference (no longer hardcoded)

### v0.1.x

- Initial release: 7 MCP tools, Web dashboard, 3D vector visualization, multi-language support

## License

MIT
