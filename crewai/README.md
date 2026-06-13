# Clous tools for CrewAI

Drop-in [`BaseTool`](https://docs.crewai.com/concepts/tools) subclasses that give
any CrewAI agent access to entity-resolved SEC filing data from the
[Clous API](https://clous.ai).

## Install

```bash
pip install crewai requests
export CLOUS_API_KEY=sk_...        # get one at https://clous.ai
```

## Use it in 2 lines

```python
from clous_tools import clous_tools

agent = Agent(role="SEC analyst", goal="...", tools=clous_tools())
```

`clous_tools()` returns 11 instantiated `BaseTool`s.

## Tools

| Tool | Endpoint |
|------|----------|
| `search_filings` | `GET /v1/filings` |
| `full_text_search` | `GET /v1/full-text` |
| `resolve_entity` | `GET /v1/entities` |
| `get_company_financials` | `GET /v1/financials/{cik}` |
| `search_insider_transactions` | `GET /v1/insider` |
| `search_13f_holdings` | `GET /v1/holdings` |
| `search_form_d_raises` | `GET /v1/raises` |
| `get_8k_events` | `GET /v1/filings/{accession}/events` |
| `get_filing_briefing` | `GET /v1/filings/{accession}/briefing` |
| `list_events` | `GET /v1/events` |
| `answer` | `POST /v1/answer` |

The HTTP/auth logic lives in `_clous.py`. Tools read `CLOUS_API_KEY` from the
environment.

## Runnable example

```bash
export OPENAI_API_KEY=...
python example.py
```
