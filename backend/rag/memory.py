_sessions = {}

def get_memory(session_id: str) -> list:
    if session_id not in _sessions:
        _sessions[session_id] = []
    return _sessions[session_id]

def get_history(session_id: str) -> list:
    mem = get_memory(session_id)
    return mem[-12:]

def save_turn(session_id: str, human: str, ai: str):
    mem = get_memory(session_id)
    mem.append({"role": "user", "content": human})
    mem.append({"role": "assistant", "content": ai})
    _sessions[session_id] = mem[-12:]