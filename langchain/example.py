"""Tiny runnable LangChain example using the Clous tools.

Requires: pip install langchain langchain-openai
Env: CLOUS_API_KEY (Clous), OPENAI_API_KEY (the agent LLM).

    python example.py
"""

import os

from langchain_openai import ChatOpenAI

from clous_tools import clous_tools


def main() -> None:
    # Any tool-calling chat model works; here we use OpenAI for brevity.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(clous_tools())

    tools_by_name = {t.name: t for t in clous_tools()}
    question = "Find the three most recent 8-K filings for NVIDIA (CIK 0001045810)."
    messages = [("user", question)]

    ai = llm_with_tools.invoke(messages)
    print("Model requested tool calls:")
    for call in ai.tool_calls:
        print(" ", call["name"], call["args"])
        result = tools_by_name[call["name"]].invoke(call["args"])
        print("  ->", result[:400], "...")


if __name__ == "__main__":
    if not os.environ.get("CLOUS_API_KEY"):
        raise SystemExit("Set CLOUS_API_KEY first (get one at https://clous.ai).")
    main()
