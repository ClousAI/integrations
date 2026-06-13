# Clous tools for LlamaIndex

Drop-in [`FunctionTool`](https://docs.llamaindex.ai/en/stable/module_guides/deploying/agents/tools/)
definitions that give any LlamaIndex agent access to entity-resolved SEC filing
data from the [Clous API](https://clous.ai).

## Install

```bash
pip install llama-index-core requests
export CLOUS_API_KEY=sk_...        # get one at https://clous.ai
```

## Use it in 2 lines

```python
from clous_tools import clous_tools

agent = ReActAgent.from_tools(clous_tools(), llm=llm)
```

`clous_tools()` returns 11 `FunctionTool`s. LlamaIndex derives each tool's JSON
schema from the wrapped function's type hints and docstring.

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
pip install llama-index-llms-openai
export OPENAI_API_KEY=...
python example.py
```
