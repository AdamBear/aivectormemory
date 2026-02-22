import json
from aivectormemory.db.state_repo import StateRepo
from aivectormemory.errors import success_response


def handle_status(args, *, cm, **_):
    repo = StateRepo(cm.conn, cm.project_dir)
    state_update = args.get("state")

    if state_update:
        if isinstance(state_update, str):
            state_update = json.loads(state_update)
        result = repo.upsert(**state_update)
        return json.dumps(success_response(state=result, action="updated"))
    else:
        state = repo.get()
        if not state:
            state = repo.upsert()
        return json.dumps(success_response(state=state, action="read"))
