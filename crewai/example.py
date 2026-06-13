"""Tiny runnable CrewAI example using the Clous tools.

Requires: pip install crewai
Env: CLOUS_API_KEY (Clous), OPENAI_API_KEY (the agent LLM, CrewAI default).

    python example.py
"""

import os

from crewai import Agent, Crew, Task

from clous_tools import clous_tools


def main() -> None:
    analyst = Agent(
        role="SEC filings analyst",
        goal="Answer questions about public companies using Clous SEC data.",
        backstory="You are meticulous and always cite the filing you used.",
        tools=clous_tools(),
        verbose=True,
    )
    task = Task(
        description="Summarize Tesla's most recent 8-K. Resolve ticker TSLA to a "
        "CIK, find the latest 8-K, then classify its events.",
        expected_output="A short summary of the 8-K's reported items.",
        agent=analyst,
    )
    crew = Crew(agents=[analyst], tasks=[task])
    print(crew.kickoff())


if __name__ == "__main__":
    if not os.environ.get("CLOUS_API_KEY"):
        raise SystemExit("Set CLOUS_API_KEY first (get one at https://clous.ai).")
    main()
