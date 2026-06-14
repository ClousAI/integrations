# Clous framework integrations

Drop-in tool definitions that give your AI agents access to **entity-resolved SEC
filing data** from the [Clous API](https://clous.ai) — in about two lines.

Each folder is independently usable: copy it into your project, set
`CLOUS_API_KEY`, and import. Every framework wraps the same ~11 core Clous
endpoints and shares a tiny per-language HTTP helper (`_clous.py` / `_clous.ts`)
so the wire logic stays DRY.

| Framework | Language | Folder | What you get |
|-----------|----------|--------|--------------|
| [LangChain](./langchain) | Python | `langchain/` | `StructuredTool`s + `ClousToolkit` |
| [LlamaIndex](./llamaindex) | Python | `llamaindex/` | `FunctionTool`s |
| [OpenAI function calling / Agents SDK](./openai) | Python | `openai/` | JSON tool schemas + `dispatch()` |
| [Vercel AI SDK](./vercel-ai) | TypeScript | `vercel-ai/` | `tool()` defs with zod schemas |
| [CrewAI](./crewai) | Python | `crewai/` | `BaseTool` subclasses |

## The 11 core tools

| Tool | Endpoint | What it does |
|------|----------|--------------|
| `search_filings` | `GET /v1/filings` | Search the EDGAR filing index by CIK, form type, date, keyword |
| `full_text_search` | `GET /v1/full-text` | Full-text search across every filing body since 2001 |
| `resolve_entity` | `GET /v1/entities` | Resolve companies by CIK, ticker, or name |
| `get_company_financials` | `GET /v1/financials/{cik}` | Structured XBRL financial facts |
| `search_insider_transactions` | `GET /v1/insider` | Form 3/4/5 insider trades |
| `search_13f_holdings` | `GET /v1/holdings` | 13F institutional holdings |
| `search_form_d_raises` | `GET /v1/raises` | Form D private-placement raises |
| `get_8k_events` | `GET /v1/filings/{accession}/events` | Classify 8-K items with excerpts |
| `get_filing_briefing` | `GET /v1/filings/{accession}/briefing` | AI plain-language filing summary |
| `list_events` | `GET /v1/events` | Typed, evidence-backed SEC business-change events feed |
| `answer` | `POST /v1/answer` | Grounded NL Q&A with citations |

These are a curated subset for agent use. The full Clous API exposes ~50
endpoints (insider Form 144, 13D/13G, Form ADV, enforcement, litigation, patents,
N-PORT fund holdings, and more) — see the [API docs](https://docs.clous.ai).

## Getting started

1. Grab an API key at [clous.ai](https://clous.ai).
2. `export CLOUS_API_KEY=sk_...`
3. Open the folder for your framework and follow its README (each has a 2-line
   integration snippet + a runnable `example`).

All tools read `CLOUS_API_KEY` from the environment, send
`Authorization: Bearer $CLOUS_API_KEY`, and return the Clous response envelope
`{ data[], page, as_of, source, query_echo, warnings }`. Pass `fields=` (where
supported) to trim the response to just the columns you need.

## Even simpler integrations

If you don't want to wire up individual tools, two paths need almost no glue:

- **OpenAI-compatible chat endpoint.** Point any OpenAI client at
  `base_url="https://api.clous.ai/v1"` with `model="clous"` and ask SEC questions
  in natural language — Clous does the retrieval and grounding for you.

  ```python
  from openai import OpenAI
  client = OpenAI(base_url="https://api.clous.ai/v1", api_key="$CLOUS_API_KEY")
  client.chat.completions.create(model="clous", messages=[{"role": "user",
      "content": "What did NVIDIA report in its latest 8-K?"}])
  ```

- **MCP server.** Use the official Clous MCP server (`@clousai/mcp`) to expose all
  49 Clous tools to any MCP-compatible client (Claude, Cursor, etc.) with no
  code. See [github.com/clousai/mcp](https://github.com/clousai/mcp).

## License

MIT — see [LICENSE](./LICENSE). Clous serves public SEC EDGAR data and is
independent of the U.S. Securities and Exchange Commission.
