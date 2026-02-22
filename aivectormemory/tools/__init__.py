TOOL_DEFINITIONS = [
    {
        "name": "remember",
        "description": "存入一条记忆。支持用户级（跨项目）和项目级存储，自动去重（相似度>0.95则更新）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "记忆内容，Markdown 格式"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "标签列表"},
                "scope": {"type": "string", "enum": ["user", "project"], "default": "project", "description": "作用域"}
            },
            "required": ["content", "tags"]
        }
    },
    {
        "name": "recall",
        "description": "语义搜索回忆记忆。通过向量相似度匹配，即使用词不同也能找到相关记忆。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索内容（语义搜索，可选）"},
                "scope": {"type": "string", "enum": ["user", "project", "all"], "default": "all"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "按标签过滤（无 query 时走纯标签精确查询）"},
                "top_k": {"type": "integer", "default": 5, "description": "返回结果数量"},
                "source": {"type": "string", "enum": ["manual", "auto_save"], "description": "按来源过滤：manual=手动记忆, auto_save=自动保存。不传则不过滤"},
                "brief": {"type": "boolean", "default": False, "description": "精简模式：true 时只返回 content 和 tags，省略 id/session_id/created_at 等元数据，适合启动加载场景节省上下文"}
            }
        }
    },
    {
        "name": "forget",
        "description": "删除一条或多条记忆。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "memory_id": {"type": "string", "description": "单个记忆 ID"},
                "memory_ids": {"type": "array", "items": {"type": "string"}, "description": "多个记忆 ID"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "按标签批量删除，删除所有匹配标签的记忆"},
                "scope": {"type": "string", "enum": ["user", "project", "all"], "default": "all", "description": "配合 tags 使用，限定删除范围"}
            }
        }
    },
    {
        "name": "status",
        "description": "读取或更新会话状态（阻塞状态、当前任务、进度等）。不传 state 参数则读取，传则部分更新。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {
                    "type": "object",
                    "description": "要更新的字段（部分更新）",
                    "properties": {
                        "is_blocked": {"type": "boolean"},
                        "block_reason": {"type": "string"},
                        "next_step": {"type": "string"},
                        "current_task": {"type": "string"},
                        "progress": {"type": "array", "items": {"type": "string"}},
                        "recent_changes": {"type": "array", "items": {"type": "string"}},
                        "pending": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        }
    },
    {
        "name": "track",
        "description": "问题跟踪：create/update/archive/delete/list 五个 action。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "update", "archive", "delete", "list"]},
                "title": {"type": "string", "description": "问题标题（create）"},
                "date": {"type": "string", "description": "日期 YYYY-MM-DD"},
                "issue_id": {"type": "integer", "description": "问题 ID（update/archive/delete）"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                "content": {"type": "string", "description": "排查内容"},
                "parent_id": {"type": "integer", "description": "父问题 ID（create，可选，默认 0）"},
                "description": {"type": "string", "description": "问题描述"},
                "investigation": {"type": "string", "description": "排查过程（逐步记录）"},
                "root_cause": {"type": "string", "description": "根本原因"},
                "solution": {"type": "string", "description": "解决方案"},
                "files_changed": {"type": "string", "description": "修改文件清单（JSON 数组）"},
                "test_result": {"type": "string", "description": "自测结果"},
                "notes": {"type": "string", "description": "注意事项"},
                "feature_id": {"type": "string", "description": "关联功能标识"},
                "include_archived": {"type": "boolean", "default": False, "description": "list 时是否包含已归档问题"},
                "issue_id": {"type": "integer", "description": "list 时传入可查单条问题（活跃+归档都查），避免拉全量列表"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "digest",
        "description": "提取待整理的记忆列表，按 session 范围和标签过滤，由 AI 端归纳总结。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "scope": {"type": "string", "enum": ["user", "project", "all"], "default": "project"},
                "since_sessions": {"type": "integer", "default": 20, "description": "最近 N 次会话"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "按标签过滤"},
                "compress": {"type": "boolean", "default": False, "description": "是否触发智能归纳压缩，合并同主题碎片、清理过时记忆"},
                "limit": {"type": "integer", "default": 50, "description": "单次返回最大条数，防止上下文溢出。返回 remaining 字段提示剩余条数"},
                "max_chars": {"type": "integer", "default": 8000, "description": "返回内容总字符数上限，单条超500字自动截断，防止撑爆上下文窗口"}
            }
        }
    },
    {
        "name": "task",
        "description": "任务管理：batch_create/update/list 三个 action。通过 feature_id 关联 spec 文档和问题追踪。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["batch_create", "update", "list", "delete"]},
                "feature_id": {"type": "string", "description": "关联的功能标识"},
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "sort_order": {"type": "integer", "default": 0},
                            "children": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "sort_order": {"type": "integer", "default": 0}
                                    },
                                    "required": ["title"]
                                },
                                "description": "子任务列表（可选，最多一级嵌套）"
                            }
                        },
                        "required": ["title"]
                    },
                    "description": "任务列表（batch_create）"
                },
                "task_id": {"type": "integer", "description": "任务 ID（update）"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "skipped"], "description": "任务状态"},
                "title": {"type": "string", "description": "任务标题（update 时可选修改）"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "readme",
        "description": "README 生成工具：从 TOOL_DEFINITIONS/pyproject.toml/STEERING_CONTENT 自动生成 README 内容，支持多语言和差异对比。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["generate", "diff"], "default": "generate", "description": "generate=生成内容, diff=对比差异"},
                "lang": {"type": "string", "default": "en", "description": "语言：en/zh-TW/ja/de/fr/es"},
                "sections": {"type": "array", "items": {"type": "string"}, "description": "指定生成的章节（可选）：header/tools/deps"}
            }
        }
    },
    {
        "name": "auto_save",
        "description": "【每次对话结束前必须调用】自动保存本次对话的关键信息。将决策、修改、踩坑、待办、偏好分类存储为独立记忆，自动打标签和去重。偏好类记忆固定 scope=user（跨项目通用）。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decisions": {"type": "array", "items": {"type": "string"}, "description": "本次对话做出的关键决策"},
                "modifications": {"type": "array", "items": {"type": "string"}, "description": "本次对话修改的文件和内容摘要"},
                "pitfalls": {"type": "array", "items": {"type": "string"}, "description": "本次对话遇到的坑和解决方案"},
                "todos": {"type": "array", "items": {"type": "string"}, "description": "本次对话产生的待办事项"},
                "preferences": {"type": "array", "items": {"type": "string"}, "description": "用户表达的技术偏好、设计风格倾向、架构选择习惯（固定 scope=user，跨项目通用）"},
                "scope": {"type": "string", "enum": ["user", "project"], "default": "project", "description": "作用域，默认项目级（preferences 固定 user）"},
                "extra_tags": {"type": "array", "items": {"type": "string"}, "description": "额外标签"}
            }
        }
    }
]

from aivectormemory.tools.remember import handle_remember
from aivectormemory.tools.recall import handle_recall
from aivectormemory.tools.forget import handle_forget
from aivectormemory.tools.status import handle_status
from aivectormemory.tools.track import handle_track
from aivectormemory.tools.digest import handle_digest
from aivectormemory.tools.auto_save import handle_auto_save
from aivectormemory.tools.task import handle_task
from aivectormemory.tools.readme import handle_readme

TOOL_HANDLERS = {
    "remember": handle_remember,
    "recall": handle_recall,
    "forget": handle_forget,
    "status": handle_status,
    "track": handle_track,
    "digest": handle_digest,
    "auto_save": handle_auto_save,
    "task": handle_task,
    "readme": handle_readme,
}
