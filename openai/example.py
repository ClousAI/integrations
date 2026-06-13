"""Tiny runnable OpenAI function-calling example using the Clous tools.

Requires: pip install openai
Env: CLOUS_API_KEY (Clous), OPENAI_API_KEY (the model).

    python example.py
"""

import json
import os

from openai import OpenAI

from clous_tools import CLOUS_TOOLS, dispatch


def main() -> None:
    client = OpenAI()
    messages = [
        {"role": "user", "content": "What is NVIDIA's most recent reported revenue? "
         "Resolve the ticker NVDA to a CIK, then pull financials."}
    ]

    # Tool-calling loop.
    for _ in range(6):
        resp = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=CLOUS_TOOLS,
        )
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            print(msg.content)
            return
        for call in msg.tool_calls:
            result = dispatch(call.function.name, call.function.arguments)
            print(f"[tool] {call.function.name}({call.function.arguments}) -> {result[:200]}...")
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })


if __name__ == "__main__":
    if not os.environ.get("CLOUS_API_KEY"):
        raise SystemExit("Set CLOUS_API_KEY first (get one at https://clous.ai).")
    main()
