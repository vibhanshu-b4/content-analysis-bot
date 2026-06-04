from langchain.memory import ConversationBufferWindowMemory

_sessions = {}

def get_memory(session_id: str) -> ConversationBufferWindowMemory:
    if session_id not in _sessions:
        _sessions[session_id] = ConversationBufferWindowMemory(
            k=6, return_messages=True, memory_key="chat_history"
        )
    return _sessions[session_id]

def get_history(session_id: str) -> list:
    mem = get_memory(session_id)
    messages = mem.chat_memory.messages
    history = []
    for m in messages:
        role = "user" if m.type == "human" else "assistant"
        history.append({"role": role, "content": m.content})
    return history

def save_turn(session_id: str, human: str, ai: str):
    mem = get_memory(session_id)
    mem.chat_memory.add_user_message(human)
    mem.chat_memory.add_ai_message(ai)
