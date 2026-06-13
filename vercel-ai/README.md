# Clous tools for the Vercel AI SDK

Drop-in [`tool()`](https://sdk.vercel.ai/docs/ai-sdk-core/tools-and-tool-calling)
definitions with zod schemas that give any Vercel AI SDK agent access to
entity-resolved SEC filing data from the [Clous API](https://clous.ai).

## Install

```bash
npm install            # ai, zod (+ @ai-sdk/openai for the example)
export CLOUS_API_KEY=sk_...        # get one at https://clous.ai
```

## Use it in 2 lines

```ts
import { clousTools } from "./clous-tools";

const result = await generateText({ model, prompt, tools: clousTools, maxSteps: 6 });
```

`clousTools` is a record of 11 `tool()` definitions. The shared HTTP/auth helper
lives in `_clous.ts` and reads `CLOUS_API_KEY` from the environment.

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

## Validate / run

```bash
npm run typecheck        # tsc --noEmit
npm run example          # tsx src/example.ts  (needs OPENAI_API_KEY)
```
