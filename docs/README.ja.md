🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [Español](README.es.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | 日本語

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>AIコーディングアシスタントに記憶を — セッション間永続記憶MCPサーバー</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **問題**：AIアシスタントは新しいセッションごとにすべてを「忘れて」しまいます — 同じミスを繰り返し、プロジェクトの規約を忘れ、開発の進捗を失います。さらに悪いことに、この記憶喪失を補うために、毎回の会話に大量のコンテキストを注入する必要があり、トークンを無駄にしています。
>
> **AIVectorMemory**：MCPプロトコルを通じてAIにローカルベクトル記憶ストアを提供し、すべてを記憶させます — プロジェクト知識、つまずいた記録、開発の意思決定、作業進捗 — セッション間で永続化。セマンティック検索でオンデマンドに呼び出し、一括注入不要、トークン消費を大幅に削減。

## ✨ 主な機能

| 機能 | 説明 |
|------|------|
| 🔍 **セマンティック検索** | ベクトル類似度ベース —「データベースタイムアウト」で検索すると「MySQLコネクションプールの問題」が見つかる |
| 🏠 **完全ローカル** | ONNX Runtimeローカル推論、APIキー不要、データはマシンから出ない |
| 🔄 **スマート重複排除** | コサイン類似度 > 0.95 で自動更新、重複保存なし |
| 📊 **Webダッシュボード** | 内蔵管理UI、3Dベクトルネットワーク可視化 |
| 🔌 **全IDE対応** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae など |
| 📁 **プロジェクト分離** | 単一DBを複数プロジェクトで共有、project_dirで自動分離 |
| 🏷️ **タグシステム** | 記憶の分類管理、タグ検索・名前変更・統合 |
| 💰 **トークン節約** | セマンティック検索でオンデマンド呼び出し、一括コンテキスト注入を置き換え、50%+の冗長トークンを削減 |
| 📋 **問題追跡** | 軽量イシュートラッカー、AIが自動記録・アーカイブ |
| 🔐 **Web認証** | ダッシュボードがToken認証をサポート、不正アクセスを防止 |
| ⚡ **Embeddingキャッシュ** | 同一コンテンツの冗長なベクトル計算なし、書き込み高速化 |
| 📤 **エクスポート/インポート** | 記憶データのJSONエクスポート・インポート、移行とバックアップをサポート |
| 🎯 **操作フィードバック** | Toast通知、空状態ガイド、完全なインタラクション体験 |
| ➕ **プロジェクト追加** | ダッシュボードから直接プロジェクトを追加、ディレクトリブラウザ対応 |

## 🏗️ アーキテクチャ

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
│  │     SQLite + sqlite-vec（ベクトルインデックス）│  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 クイックスタート

### 方法1：pip インストール

```bash
pip install aivectormemory
pip install --upgrade aivectormemory  # 最新版にアップグレード
cd /path/to/your/project
run install          # 対話式IDE選択、ワンクリック設定
```

### 方法2：uvx 実行（インストール不要）

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### 方法3：手動設定

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
<summary>📍 各IDE設定ファイルの場所</summary>

| IDE | 設定ファイルパス |
|-----|----------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7つのMCPツール

### `remember` — 記憶を保存

```
content (string, 必須)   記憶内容、Markdown形式
tags    (string[], 必須)  タグ、例 ["つまずき", "python"]
scope   (string)          "project"（デフォルト）/ "user"（プロジェクト横断）
```

類似度 > 0.95 で既存の記憶を自動更新、重複保存なし。

### `recall` — セマンティック検索

```
query   (string)     セマンティック検索キーワード
tags    (string[])   タグ精密フィルター
scope   (string)     "project" / "user" / "all"
top_k   (integer)    返却数、デフォルト 5
```

ベクトル類似度マッチング — 異なる言葉でも関連する記憶を発見。

### `forget` — 記憶を削除

```
memory_id  (string)     単一ID
memory_ids (string[])   一括ID
```

### `status` — セッション状態

```
state (object, 任意)   省略=読み取り、指定=更新
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

セッション間で作業進捗を維持、新セッションで自動的にコンテキストを復元。

### `track` — 問題追跡

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   問題タイトル
issue_id (integer)  問題ID
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   調査内容
```

### `digest` — 記憶サマリー

```
scope          (string)    スコープ
since_sessions (integer)   直近N回のセッション
tags           (string[])  タグフィルター
```

### `auto_save` — 自動保存

```
decisions[]      重要な意思決定
modifications[]  ファイル変更サマリー
pitfalls[]       つまずき記録
todos[]          未処理項目
```

各会話の終了時に自動的に分類・タグ付け・重複排除して保存。

## 📊 Webダッシュボード

```bash
run web --port 9080
run web --port 9080 --quiet          # リクエストログを非表示
run web --port 9080 --quiet --daemon  # バックグラウンド実行（macOS/Linux）
```

ブラウザで `http://localhost:9080` にアクセス。

- マルチプロジェクト切り替え、記憶の閲覧/検索/編集/削除/エクスポート/インポート
- セマンティック検索（ベクトル類似度マッチング）
- プロジェクトデータのワンクリック削除
- セッション状態、問題追跡
- タグ管理（名前変更、統合、一括削除）
- Token認証保護
- 3Dベクトル記憶ネットワーク可視化
- 🌐 多言語対応（简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語）

<p align="center">
  <img src="dashboard-projects.png" alt="プロジェクト選択" width="100%">
  <br>
  <em>プロジェクト選択</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="統計概要 & ベクトルネットワーク可視化" width="100%">
  <br>
  <em>統計概要 & ベクトルネットワーク可視化</em>
</p>

## ⚡ Steeringルールとの組み合わせ

AIVectorMemoryはストレージ層です。Steeringルールを使ってAIに**いつ、どのように**ツールを呼び出すかを指示します。

`run install` を実行すると、Steeringルールとフック設定が自動生成されます。手動設定は不要です。

| IDE | Steeringの場所 | Hooks |
|-----|---------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md`（追記） | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md`（追記） | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md`（追記） | `.opencode/plugins/*.js` |

<details>
<summary>📋 Steeringルール例（自動生成）</summary>

```markdown
# AIVectorMemory - セッション間永続メモリ

## 起動チェック

新しいセッション開始時に、以下の順序で実行：

1. `status`（パラメータなし）を呼び出してセッション状態を読み取り、`is_blocked` と `block_reason` を確認
2. `recall`（tags: ["プロジェクト知識"], scope: "project"）を呼び出してプロジェクト知識を読み込み
3. `recall`（tags: ["preference"], scope: "user"）を呼び出してユーザー設定を読み込み

## いつ呼び出すか

- 新セッション開始時：`status` を呼び出して前回の作業状態を読み取り
- つまずき発見時：`remember` を呼び出して記録、タグ "つまずき" を追加
- 過去の経験が必要な時：`recall` でセマンティック検索
- バグやTODO発見時：`track`（action: create）を呼び出し
- タスク進捗変更時：`status`（stateパラメータ渡し）で更新
- 会話終了前：`auto_save` を呼び出してこのセッションを保存

## セッション状態管理

statusフィールド：is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

⚠️ **ブロッキング保護**：プラン提案で確認待ち、または修正完了で検証待ちの場合、必ず同時に `status` を呼び出して `is_blocked: true` を設定してください。これにより、コンテキスト転送後に新しいセッションが誤って「確認済み」と判断して自律的に実行することを防ぎます。

## 問題追跡

1. `track create` → 問題を記録
2. `track update` → 調査内容を更新
3. `track archive` → 解決済み問題をアーカイブ
```

</details>

<details>
<summary>🔗 フック設定例（Kiro専用、自動生成）</summary>

セッション終了時の自動保存（`.kiro/hooks/auto-save-session.kiro.hook`）：

```json
{
  "enabled": true,
  "name": "セッション自動保存",
  "version": "1",
  "when": { "type": "agentStop" },
  "then": {
    "type": "askAgent",
    "prompt": "auto_saveを呼び出して、このセッションの決定、変更、つまずき、TODOを分類して保存"
  }
}
```

開発ワークフローチェック（`.kiro/hooks/dev-workflow-check.kiro.hook`）：

```json
{
  "enabled": true,
  "name": "開発ワークフローチェック",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "核心原則：行動前に検証、盲目的なテスト禁止、テスト合格後のみ完了とマーク"
  }
}
```

</details>

## 🇨🇳 中国本土のユーザー

初回実行時にEmbeddingモデル（約200MB）が自動ダウンロードされます。遅い場合：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

またはMCP設定にenvを追加：

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 技術スタック

| コンポーネント | 技術 |
|---------------|------|
| ランタイム | Python >= 3.10 |
| ベクトルDB | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| トークナイザー | HuggingFace Tokenizers |
| プロトコル | Model Context Protocol (MCP) |
| Web | ネイティブHTTPServer + Vanilla JS |

## 📋 更新履歴

### v0.2.4

- 🔇 Stop hook プロンプトを直接指示に変更、Claude Code の重複応答を解消
- 🛡️ Steering ルール auto_save 仕様にショートサーキット保護追加、セッション終了時に他のルールをスキップ
- 🐛 `_copy_check_track_script` 冪等性修正（変更状態を返却し「同期済み」の誤報を回避）
- 🐛 issue_repo delete の `row.get()` が `sqlite3.Row` と非互換の修正（`row.keys()` で判定）
- 🐛 Web ダッシュボード プロジェクト選択ページのスクロール修正（プロジェクトが多い場合にスクロール不可）
- 🐛 Web ダッシュボード CSS 汚染修正（strReplace グローバル置換で 6 つのスタイルセレクタが破損）
- 🔄 Web ダッシュボードの全 confirm() ダイアログをカスタム showConfirm モーダルに置換（メモリ/イシュー/タグ/プロジェクト削除）
- 🔄 Web ダッシュボード削除操作に API エラーレスポンス処理を追加（alert の代わりに toast）
- 🧹 `.gitignore` に `.devmemory/` レガシーディレクトリの無視ルールを追加
- 🧪 pytest 一時プロジェクト DB 残留の自動クリーンアップ（conftest.py セッションフィクスチャ）

### v0.2.3

- 🛡️ PreToolUse Hook：Edit/Write 前に track issue を強制チェック、アクティブな問題がなければ実行拒否（Claude Code / Kiro / OpenCode 対応）
- 🔌 OpenCode プラグインを `@opencode-ai/plugin` SDK 形式にアップグレード（tool.execute.before hook）
- 🔧 `run install` で check_track.sh スクリプトを自動デプロイ、パスを動的に注入
- 🐛 issue_repo archive/delete の `row.get()` が `sqlite3.Row` と非互換な問題を修正
- 🐛 session_id を DB から最新値を読み取ってからインクリメント、マルチインスタンス競合を回避
- 🐛 track date パラメータ形式バリデーション（YYYY-MM-DD）+ issue_id 型バリデーション
- 🐛 Web API リクエスト解析のセキュリティ強化（Content-Length バリデーション + 10MB 上限 + JSON エラーハンドリング）
- 🐛 Tag フィルター scope ロジック修正（`filter_dir is not None` で falsy 判定を置換）
- 🐛 Export ベクトルデータ struct.unpack バイト長バリデーション
- 🐛 Schema バージョン管理マイグレーション（schema_version テーブル + v1/v2/v3 増分マイグレーション）
- 🐛 `__init__.py` バージョン番号同期修正

### v0.2.2

- 🔇 Web ダッシュボード `--quiet` パラメータでリクエストログを非表示
- 🔄 Web ダッシュボード `--daemon` パラメータでバックグラウンド実行（macOS/Linux）
- 🔧 `run install` MCP 設定生成の修正（sys.executable + 完全なフィールド）
- 📋 問題追跡の CRUD とアーカイブ（Web ダッシュボード 追加/編集/アーカイブ/削除 + 記憶関連付け）
- 👆 リスト行の任意の場所をクリックで編集モーダルを表示（記憶/問題/タグ）
- 🛡️ Hook チェーントリガー防護（agentStop + promptSubmit の組み合わせでルールの重複注入を防止）
- 🔒 セッション継続/コンテキスト転送時にブロッキングルールを強制適用（再確認が必要）

### v0.2.1

- ➕ Webダッシュボードからプロジェクト追加（ディレクトリブラウザ + 手動入力）
- 🏷️ タグのプロジェクト間汚染修正（タグ操作を現在のプロジェクト + グローバル記憶に限定）
- 📐 モーダルページネーション省略記号切り詰め + 幅80%
- 🔌 OpenCode installがauto_saveプラグインを自動生成（session.idleイベントトリガー）
- 🔗 Claude Code / Cursor / Windsurf installがHooks設定を自動生成（セッション終了時の自動保存）
- 🎯 Webダッシュボード操作体験改善（Toastフィードバック、空状態ガイド、エクスポート/インポートツールバー）
- 🔧 統計カードクリックジャンプ（記憶数/問題数クリックで詳細表示）
- 🏷️ タグ管理ページでプロジェクト/グローバルタグの出所を区別（📁/🌐 マーカー）
- 🏷️ プロジェクトカードのタグ数にグローバル記憶のタグを統合

### v0.2.0

- 🔐 WebダッシュボードToken認証
- ⚡ Embeddingベクトルキャッシュ、同一コンテンツの冗長計算なし
- 🔍 recall が query + tags の組み合わせ検索をサポート
- 🗑️ forget が一括削除をサポート（memory_ids パラメータ）
- 📤 記憶のエクスポート/インポート（JSON形式）
- 🔎 Webダッシュボードセマンティック検索
- 🗂️ Webダッシュボードプロジェクト削除ボタン
- 📊 Webダッシュボードパフォーマンス最適化（フルテーブルスキャン排除）
- 🧠 digest スマート圧縮
- 💾 session_id 永続化
- 📏 content 長さ制限保護
- 🏷️ version 動的参照（ハードコードなし）

### v0.1.x

- 初期リリース：7つのMCPツール、Webダッシュボード、3Dベクトル可視化、多言語対応

## License

MIT
