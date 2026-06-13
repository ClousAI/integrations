# Clous tools for OpenAI function calling / Agents SDK

Plain JSON tool schemas + a `dispatch()` handler that give any OpenAI model
access to entity-resolved SEC filing data from the [Clous API](https://clous.ai).
Works with the Chat Completions / Responses API and the Agents SDK.

## Install

```bash
pip install openai requests
export CLOUS_API_KEY=sk_...        # get one at https://clous.ai
export OPENAI_API_KEY=...
```

## Use it in 2 lines

```python
from clous_tools import CLOUS_TOOLS, dispatch

resp = client.chat.completions.create(model="gpt-4o", messages=msgs, tools=CLOUS_TOOLS)
# when the model emits tool_calls:  dispatch(call.function.name, call.function.arguments)
```

`CLOUS_TOOLS` is a list of 11 function schemas in the exact
`{"type": "function", "function": {...}}` shape the SDK expects. `dispatch()`
runs the matching endpoint and returns a JSON string for the `role: "tool"`
message.

> If you don't need fine-grained tools at all, the simplest integration is the
> OpenAI-compatible endpoint: point the SDK at `base_url="https://api.clous.ai/v1"`
> with `model="clous"` and ask SEC questions directly — no tool wiring.

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
python example.py
```
