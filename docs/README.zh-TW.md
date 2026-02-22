🌐 [简体中文](../README.md) | 繁體中文 | [English](README.en.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>為 AI 程式助手裝上記憶 — 跨會話持久化記憶 MCP Server</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **問題**：AI 助手每次新會話都「失憶」，反覆踩同樣的坑、忘記專案約定、遺失開發進度。更糟的是，為了補償失憶，你不得不在每次對話中重複注入大量上下文，白白浪費 Token。
>
> **AIVectorMemory**：透過 MCP 協議為 AI 提供本地向量記憶庫，讓它記住一切 — 專案知識、踩坑記錄、開發決策、工作進度 — 跨會話永不遺失。語義檢索按需召回，不再全量注入，大幅降低 Token 消耗。

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔍 **語義搜尋** | 基於向量相似度，搜「資料庫逾時」能找到「MySQL 連線池踩坑」 |
| 🏠 **完全本地** | ONNX Runtime 本地推理，無需 API Key，資料不出本機 |
| 🔄 **智慧去重** | 餘弦相似度 > 0.95 自動更新，不會重複儲存 |
| 📊 **Web 看板** | 內建管理介面，3D 向量網路視覺化 |
| 🔌 **全 IDE 支援** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae 等 |
| 📁 **專案隔離** | 多專案共用一個 DB，透過 project_dir 自動隔離 |
| 🏷️ **標籤體系** | 記憶分類管理，支援標籤搜尋、重新命名、合併 |
| 💰 **節省 Token** | 語義檢索按需召回，替代全量上下文注入，減少 50%+ 重複 Token 消耗 |
| 📋 **問題追蹤** | 輕量級 issue tracker，AI 自動記錄和歸檔 |
| 🔐 **Web 認證** | 看板支援 Token 認證，防止未授權存取 |
| ⚡ **Embedding 快取** | 相同內容不重複計算向量，提升寫入效能 |
| 📤 **匯出/匯入** | 記憶資料 JSON 匯出匯入，支援遷移和備份 |
| 🎯 **操作回饋** | Toast 提示、空狀態引導，互動體驗完整 |
| ➕ **看板新增專案** | 前端直接新增專案，支援目錄瀏覽器選擇 |

## 🏗️ 架構

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
│  │     SQLite + sqlite-vec（向量索引）         │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 快速開始

### 方式一：pip 安裝

```bash
pip install aivectormemory
pip install --upgrade aivectormemory  # 升級到最新版
cd /path/to/your/project
run install          # 互動式選擇 IDE，一鍵配置
```

### 方式二：uvx 執行（零安裝）

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### 方式三：手動配置

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
<summary>📍 各 IDE 設定檔位置</summary>

| IDE | 設定檔路徑 |
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

## 🛠️ 7 個 MCP 工具

### `remember` — 存入記憶

```
content (string, 必填)   記憶內容，Markdown 格式
tags    (string[], 必填)  標籤，如 ["踩坑", "python"]
scope   (string)          "project"（預設）/ "user"（跨專案）
```

相似度 > 0.95 自動更新已有記憶，不重複儲存。

### `recall` — 語義搜尋

```
query   (string)     語義搜尋關鍵詞
tags    (string[])   標籤精確過濾
scope   (string)     "project" / "user" / "all"
top_k   (integer)    回傳數量，預設 5
```

向量相似度匹配，用詞不同也能找到相關記憶。

### `forget` — 刪除記憶

```
memory_id  (string)     單個 ID
memory_ids (string[])   批次 ID
```

### `status` — 會話狀態

```
state (object, 可選)   不傳=讀取，傳=更新
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

跨會話保持工作進度，新會話自動恢復上下文。

### `track` — 問題追蹤

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   問題標題
issue_id (integer)  問題 ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   排查內容
```

### `digest` — 記憶摘要

```
scope          (string)    範圍
since_sessions (integer)   最近 N 次會話
tags           (string[])  標籤過濾
```

### `auto_save` — 自動儲存

```
decisions[]      關鍵決策
modifications[]  檔案修改摘要
pitfalls[]       踩坑記錄
todos[]          待辦事項
```

每次對話結束自動分類儲存，打標籤，去重。

## 📊 Web 看板

```bash
run web --port 9080
run web --port 9080 --quiet          # 屏蔽請求日誌
run web --port 9080 --quiet --daemon  # 背景執行（macOS/Linux）
```

瀏覽器存取 `http://localhost:9080`

- 多專案切換，記憶瀏覽/搜尋/編輯/刪除/匯出/匯入
- 語義搜尋（向量相似度匹配）
- 專案資料一鍵刪除
- 會話狀態、問題追蹤
- 標籤管理（重新命名、合併、批次刪除）
- Token 認證保護
- 3D 向量記憶網路視覺化
- 🌐 多語言支援（简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語）

<p align="center">
  <img src="dashboard-projects.png" alt="專案選擇" width="100%">
  <br>
  <em>專案選擇</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="統計概覽 & 向量網路視覺化" width="100%">
  <br>
  <em>統計概覽 & 向量網路視覺化</em>
</p>

## ⚡ 搭配 Steering 規則

AIVectorMemory 是儲存層，透過 Steering 規則告訴 AI **何時、如何**呼叫這些工具。

執行 `run install` 會自動產生 Steering 規則和 Hooks 設定，無需手動編寫。

| IDE | Steering 位置 | Hooks |
|-----|--------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md`（追加） | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md`（追加） | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md`（追加） | `.opencode/plugins/*.js` |

<details>
<summary>📋 Steering 規則範例（自動產生）</summary>

```markdown
# AIVectorMemory - 跨會話持久記憶

## 啟動檢查

每次新會話開始時，按以下順序執行：

1. 呼叫 `status`（不傳參數）讀取會話狀態，檢查 `is_blocked` 和 `block_reason`
2. 呼叫 `recall`（tags: ["項目知識"], scope: "project"）載入項目知識
3. 呼叫 `recall`（tags: ["preference"], scope: "user"）載入使用者偏好

## 何時呼叫

- 新會話開始時：呼叫 `status` 讀取上次的工作狀態
- 遇到踩坑/技術要點時：呼叫 `remember` 記錄，標籤加 "踩坑"
- 需要查找歷史經驗時：呼叫 `recall` 語義搜尋
- 發現 bug 或待處理事項時：呼叫 `track`（action: create）
- 任務進度變化時：呼叫 `status`（傳 state 參數）更新
- 對話結束前：呼叫 `auto_save` 儲存本次對話

## 會話狀態管理

status 欄位：is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

⚠️ **阻塞防護**：提出方案等待確認、修復完成等待驗證時，必須同步呼叫 `status` 設定 `is_blocked: true`。這可以防止會話轉移時新會話誤判為「已確認」而擅自執行。

## 問題追蹤

1. `track create` → 記錄問題
2. `track update` → 更新排查內容
3. `track archive` → 歸檔已解決問題
```

</details>

<details>
<summary>🔗 Hooks 設定範例（Kiro 專屬，自動產生）</summary>

會話結束自動儲存已移除，開發流程檢查（`.kiro/hooks/dev-workflow-check.kiro.hook`）：

```json
{
  "enabled": true,
  "name": "開發流程檢查",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "核心原則：操作前驗證、禁止盲目測試、自測通過才能說完成"
  }
}
```

</details>

## 🇨🇳 中國大陸使用者

首次執行自動下載 Embedding 模型（~200MB），如果慢：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或在 MCP 設定中加 env：

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 技術棧

| 元件 | 技術 |
|------|------|
| 執行環境 | Python >= 3.10 |
| 向量資料庫 | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| 分詞器 | HuggingFace Tokenizers |
| 協議 | Model Context Protocol (MCP) |
| Web | 原生 HTTPServer + Vanilla JS |

## 📋 更新日誌

### v0.2.4

- 🔇 Stop hook prompt 改為直接指令，消除 Claude Code 重複回覆
- 🛡️ Steering 規則 auto_save 規範增加短路防護，會話結束場景跳過其他規則
- 🐛 `_copy_check_track_script` 冪等性修復（返回變更狀態避免誤報「已同步」）
- 🐛 issue_repo delete 中 `row.get()` 對 `sqlite3.Row` 不相容修復（改用 `row.keys()` 判斷）
- 🐛 Web 看板專案選擇頁面捲動修復（專案多時無法捲動）
- 🐛 Web 看板 CSS 污染修復（strReplace 全域替換導致 6 處樣式異常）
- 🔄 Web 看板所有 confirm() 彈窗替換為自訂 showConfirm 模態框（記憶/問題/標籤/專案刪除）
- 🔄 Web 看板刪除操作增加 API 錯誤回應處理（toast 提示替代 alert）
- 🧹 `.gitignore` 補充 `.devmemory/` 舊版殘留目錄忽略規則
- 🧪 pytest 臨時專案資料庫殘留自動清理（conftest.py session fixture）

### v0.2.3

- 🛡️ PreToolUse Hook：Edit/Write 前強制檢查 track issue，無活躍問題則拒絕執行（Claude Code / Kiro / OpenCode 三端支援）
- 🔌 OpenCode 外掛升級為 `@opencode-ai/plugin` SDK 格式（tool.execute.before hook）
- 🔧 `run install` 自動部署 check_track.sh 檢查腳本並動態填充路徑
- 🐛 issue_repo archive/delete 中 `row.get()` 對 `sqlite3.Row` 不相容修復
- 🐛 session_id 從 DB 讀取最新值再遞增，避免多實例競態
- 🐛 track date 參數格式校驗（YYYY-MM-DD）+ issue_id 類型校驗
- 🐛 Web API 請求解析安全加固（Content-Length 校驗 + 10MB 上限 + JSON 異常捕獲）
- 🐛 Tag 過濾 scope 邏輯修復（`filter_dir is not None` 替代 falsy 判斷）
- 🐛 Export 向量資料 struct.unpack 位元組長度校驗
- 🐛 Schema 版本化遷移（schema_version 表 + v1/v2/v3 增量遷移）
- 🐛 `__init__.py` 版本號同步修復

### v0.2.2

- 🔇 Web 看板 `--quiet` 參數屏蔽請求日誌
- 🔄 Web 看板 `--daemon` 參數背景執行（macOS/Linux）
- 🔧 `run install` MCP 配置生成修復（sys.executable + 完整欄位）
- 📋 問題追蹤增刪改歸檔（Web 看板新增/編輯/歸檔/刪除 + 記憶關聯）
- 👆 所有列表頁點擊行任意位置彈出編輯彈窗（記憶/問題/標籤）
- 🔒 會話延續/上下文轉移時阻塞規則強制生效（跨會話必須重新確認）

### v0.2.1

- ➕ 看板前端新增專案（目錄瀏覽器 + 手動輸入）
- 🏷️ 標籤跨專案污染修復（標籤操作限定當前專案 + 全域記憶範圍）
- 📐 彈窗分頁省略號截斷 + 寬度 80%
- 🔌 OpenCode install 自動生成 auto_save 外掛（session.idle 事件觸發）
- 🔗 Claude Code / Cursor / Windsurf install 自動生成 Hooks 設定（會話結束自動儲存）
- 🎯 看板互動體驗補全（Toast 回饋、空狀態引導、匯出/匯入工具列）
- 🔧 統計概覽卡片點擊跳轉（點擊記憶數/問題數直接彈窗查看）
- 🏷️ 標籤管理頁區分專案/全域標籤來源（📁/🌐 標記）
- 🏷️ 專案卡片標籤數合併全域記憶標籤

### v0.2.0

- 🔐 Web 看板 Token 認證機制
- ⚡ Embedding 向量快取，相同內容不重複計算
- 🔍 recall 支援 query + tags 組合查詢
- 🗑️ forget 支援批次刪除（memory_ids 參數）
- 📤 記憶匯出/匯入（JSON 格式）
- 🔎 Web 看板語義搜尋
- 🗂️ Web 看板專案刪除按鈕
- 📊 Web 看板效能最佳化（消除全表掃描）
- 🧠 digest 智慧壓縮
- 💾 session_id 持久化
- 📏 content 長度限制保護
- 🏷️ version 動態引用（不再寫死）

### v0.1.x

- 初始版本：7 個 MCP 工具、Web 看板、3D 向量視覺化、多語言支援

## License

MIT
