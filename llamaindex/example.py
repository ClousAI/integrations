"""Tiny runnable LlamaIndex example using the Clous tools.

Requires: pip install llama-index llama-index-llms-openai
Env: CLOUS_API_KEY (Clous), OPENAI_API_KEY (the agent LLM).

    python example.py
"""

import os

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

from clous_tools import clous_tools


def main() -> None:
    llm = OpenAI(model="gpt-4o-mini")
    agent = ReActAgent.from_tools(clous_tools(), llm=llm, verbose=True)
    resp = agent.chat(
        "What were Apple's three most recent 8-K filings about? "
        "Resolve the ticker AAPL to a CIK first."
    )
    print(resp)


if __name__ == "__main__":
    if not os.environ.get("CLOUS_API_KEY"):
        raise SystemExit("Set CLOUS_API_KEY first (get one at https://clous.ai).")
    main()
