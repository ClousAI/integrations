# Clous tools for LangChain

Drop-in [`StructuredTool`](https://python.langchain.com/docs/how_to/custom_tools/)
definitions that give any LangChain agent access to entity-resolved SEC filing
data from the [Clous API](https://clous.ai).

## Install

```bash
pip install langchain langchain-core requests
export CLOUS_API_KEY=sk_...        # get one at https://clous.ai
```

## Use it in 2 lines

```python
from clous_tools import clous_tools

llm_with_tools = llm.bind_tools(clous_tools())   # or pass clous_tools() to create_react_agent
```

`clous_tools()` returns a list of 11 tools. A `ClousToolkit().get_tools()` is
also provided if you prefer the toolkit pattern.

## Tools

| Tool | Endpoint | What it does |
|------|----------|--------------|
| `search_filings` | `GET /v1/filings` | Search the EDGAR filing index by CIK, form type, date, keyword |
| `full_text_search` | `GET /v1/full-text` | Full-text search across all filing bodies since 2001 |
| `resolve_entity` | `GET /v1/entities` | Resolve companies by CIK, ticker, or name |
| `get_company_financials` | `GET /v1/financials/{cik}` | Structured XBRL financial facts |
| `search_insider_transactions` | `GET /v1/insider` | Form 3/4/5 insider trades |
| `search_13f_holdings` | `GET /v1/holdings` | 13F institutional holdings |
| `search_form_d_raises` | `GET /v1/raises` | Form D private-placement raises |
| `get_8k_events` | `GET /v1/filings/{accession}/events` | Classify 8-K items with excerpts |
| `get_filing_briefing` | `GET /v1/filings/{accession}/briefing` | AI plain-language filing summary |
| `list_events` | `GET /v1/events` | Typed SEC business-change events feed |
| `answer` | `POST /v1/answer` | Grounded NL Q&A with citations |

The HTTP/auth logic lives in `_clous.py` (shared, dependency-light). Tools read
`CLOUS_API_KEY` from the environment.

## Runnable example

```bash
pip install langchain-openai
export OPENAI_API_KEY=...
python example.py
```
