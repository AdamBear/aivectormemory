import json
import re
from datetime import date
from aivectormemory.db.issue_repo import IssueRepo
from aivectormemory.db.task_repo import TaskRepo
from aivectormemory.errors import success_response

ISSUE_STEPS = [
    "排查问题原因",
    "确定解决方案",
    "修改代码",
    "自测验证",
    "等待用户验证",
]

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_date(d: str) -> str:
    if not _DATE_RE.match(d):
        raise ValueError(f"Invalid date format: {d}, expected YYYY-MM-DD")
    return d


def _validate_issue_id(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        raise ValueError(f"issue_id must be an integer, got: {val}")


def handle_track(args, *, cm, **_):
    action = args.get("action")
    if not action:
        raise ValueError("action is required")

    repo = IssueRepo(cm.conn, cm.project_dir)
    today = date.today().isoformat()

    if action == "create":
        title = args.get("title")
        if not title:
            raise ValueError("title is required for create")
        d = _validate_date(args.get("date", today))
        result = repo.create(d, title, args.get("content", ""), args.get("memory_id", ""), args.get("parent_id", 0))
        # 非去重时自动创建关联任务
        if not result.get("deduplicated"):
            feature_id = f"issue/{result['issue_number']}"
            task_repo = TaskRepo(cm.conn, cm.project_dir)
            steps = [{"title": s, "sort_order": i + 1} for i, s in enumerate(ISSUE_STEPS)]
            task_repo.batch_create(feature_id, steps, task_type="system")
            repo.update(result["id"], feature_id=feature_id)
        return json.dumps(success_response(**result))

    elif action == "update":
        issue_id = _validate_issue_id(args.get("issue_id"))
        fields = {k: args[k] for k in ("title", "status", "content", "memory_id",
                  "description", "investigation", "root_cause", "solution",
                  "files_changed", "test_result", "notes", "feature_id") if k in args}
        result = repo.update(issue_id, **fields)
        if not result:
            raise ValueError(f"Issue {issue_id} not found")
        return json.dumps(success_response(issue=result))

    elif action == "archive":
        issue_id = _validate_issue_id(args.get("issue_id"))
        content = args.get("content")
        if content:
            repo.update(issue_id, content=content)
        # 归档前获取 feature_id（归档后 get_by_id 查不到）
        issue = repo.get_by_id(issue_id)
        fid = issue.get("feature_id") if issue else None
        result = repo.archive(issue_id)
        if not result:
            raise ValueError(f"Issue {issue_id} not found")
        # 批量完成关联任务
        if fid:
            task_repo = TaskRepo(cm.conn, cm.project_dir)
            task_repo.complete_by_feature(fid)
        return json.dumps(success_response(**result))

    elif action == "delete":
        issue_id = _validate_issue_id(args.get("issue_id"))
        result = repo.delete(issue_id)
        if not result:
            raise ValueError(f"Issue {issue_id} not found")
        return json.dumps(success_response(**result))

    elif action == "list":
        # 支持按 issue_id 查单条（活跃+归档都查）
        issue_id = args.get("issue_id")
        if issue_id is not None:
            issue_id = _validate_issue_id(issue_id)
            row = repo.get_by_id(issue_id)
            if not row:
                row = repo.get_archived_by_id(issue_id)
            return json.dumps(success_response(issues=[row] if row else []))

        d = args.get("date")
        if d:
            _validate_date(d)
        status = args.get("status")
        include_archived = args.get("include_archived", False)
        issues = repo.list_by_date(date=d, status=status)
        if include_archived:
            archived = repo.list_archived(date=d)
            issues = issues + archived
        return json.dumps(success_response(issues=issues))

    else:
        raise ValueError(f"Unknown action: {action}")
