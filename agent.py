import ollama
from tools import web_search, fetch_url, calculator

MODEL_NAME = "qwen2.5:0.5b"

SYSTEM_PROMPT = """
You are a research assistant.
You can use tools when helpful.
Available tools:
- search(query): search Wikipedia
- fetch(url): fetch URL contents
- calculator(expression): evaluate math expressions
"""

TOOLS = {
    "search": web_search,
    "fetch": fetch_url,
    "calculator": calculator,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            },
        },
    },
]

def run_agent(user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    # ---- First model call ----
    response = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOL_SCHEMAS,
        options={
            "temperature": 0.1,
            "num_predict": 256,
        },
    )

    msg = response.get("message", {})

    # ---- Case 1: normal text response ----
    if not msg or "tool_calls" not in msg:
        return msg.get("content", "I’m not sure how to answer that.")

    # ---- Case 2: tool calls ----
    tool_outputs = []

    for call in msg.get("tool_calls", []):
        fn_name = call.get("function", {}).get("name")
        args = call.get("function", {}).get("arguments", {})

        fn = TOOLS.get(fn_name)
        if not fn:
            continue

        try:
            result = fn(**args)
        except Exception as e:
            result = f"Tool error: {e}"

        tool_outputs.append(result)

    # ---- Feed tool output back ----
    messages.append(msg)
    messages.append({
        "role": "tool",
        "content": "\n\n".join(tool_outputs)[:4000],  # bound output
    })

    final = ollama.chat(
        model=MODEL_NAME,
        messages=messages,
        options={
            "temperature": 0.1,
            "num_predict": 256,
        },
    )

    return final.get("message", {}).get(
        "content",
        "I couldn’t produce a final answer."
    )
