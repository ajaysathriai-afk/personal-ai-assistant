def build_context(messages):
    context = ""
    for msg in messages[-6:]:   # last 6 messages only
        role = "User" if msg["role"] == "user" else "Assistant"
        context += f"{role}: {msg['content']}\n"
    return context
