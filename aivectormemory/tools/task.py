import json
from aivectormemory.db.task_repo import TaskRepo
from aivectormemory.errors import success_response


def handle_task(args, *, cm, **_):
    action = args.get("action")
    if not action:
        raise ValueError("action is required")

    repo = TaskRepo(cm.conn, cm.project_dir)

    if action == "batch_create":
        feature_id = args.get("feature_id", "").strip()
        if not feature_id:
            raise ValueError("feature_id is required for batch_create")
        tasks = args.get("tasks", [])
        if not tasks:
            raise ValueError("tasks array is required for batch_create")
        result = repo.batch_create(feature_id, tasks, task_type=args.get("task_type", "manual"))
        return json.dumps(success_response(**result))

    elif action == "update":
        task_id = args.get("task_id")
        if not task_id:
            raise ValueError("task_id is required for update")
        fields = {k: args[k] for k in ("status", "title") if k in args}
        result = repo.update(int(task_id), **fields)
        if not result:
            raise ValueError(f"Task {task_id} not found")
        return json.dumps(success_response(task=result))

    elif action == "list":
        feature_id = args.get("feature_id")
        status = args.get("status")
        tasks = repo.list_by_feature(feature_id=feature_id, status=status)
        return json.dumps(success_response(tasks=tasks))

    elif action == "delete":
        task_id = args.get("task_id")
        if not task_id:
            raise ValueError("task_id is required for delete")
        result = repo.delete(int(task_id))
        if not result:
            raise ValueError(f"Task {task_id} not found")
        return json.dumps(success_response(deleted=result))

    else:
        raise ValueError(f"Unknown action: {action}")
