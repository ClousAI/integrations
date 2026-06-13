/**
 * Clous SEC data tools for the Vercel AI SDK.
 *
 * Usage (2 lines):
 *
 *   import { clousTools } from "./clous-tools";
 *   const result = await generateText({ model, prompt, tools: clousTools });
 *
 * `clousTools` is a record of 11 `tool()` definitions with zod input schemas,
 * each wrapping one core Clous endpoint. They read `CLOUS_API_KEY` from the env
 * via the shared `_clous.ts` helper and return the raw JSON envelope.
 */

import { tool } from "ai";
import { z } from "zod";

import { clousGet, clousPost } from "./_clous";

const limit = z.number().int().min(1).max(100).optional().describe("Page size, 1-100 (default 25).");
const cursor = z.string().optional().describe("Pagination cursor from a prior page.");

export const clousTools = {
  search_filings: tool({
    description:
      "Search the EDGAR filing index across all form types, filterable by company CIK, form type, date range, and keyword.",
    parameters: z.object({
      cik: z.string().optional().describe("Company CIK (zero-padded 10-digit)."),
      form_type: z.string().optional().describe('Form type, e.g. "10-K", "8-K", "4".'),
      q: z.string().optional().describe("Keyword match on company name."),
      filed_from: z.string().optional().describe("Earliest filed date, YYYY-MM-DD."),
      filed_to: z.string().optional().describe("Latest filed date, YYYY-MM-DD."),
      sic: z.string().optional().describe("SIC industry code."),
      state_of_incorp: z.string().optional().describe("State of incorporation."),
      is_xbrl: z.boolean().optional().describe("Restrict to XBRL filings."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/filings", args),
  }),

  full_text_search: tool({
    description: "Full-text search across the body of every EDGAR filing since 2001.",
    parameters: z.object({
      q: z.string().describe('Keyword or "exact phrase" to search filing text.'),
      forms: z.string().optional().describe("Comma-separated form types, e.g. 8-K,10-K."),
      date_from: z.string().optional().describe("Earliest filed date, YYYY-MM-DD."),
      date_to: z.string().optional().describe("Latest filed date, YYYY-MM-DD."),
      ciks: z.string().optional().describe("Comma-separated CIKs."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/full-text", args),
  }),

  resolve_entity: tool({
    description: "Resolve and look up companies in the entity directory by CIK, ticker, or name.",
    parameters: z.object({
      cik: z.string().optional().describe("Company CIK."),
      ticker: z.string().optional().describe("Ticker symbol."),
      q: z.string().optional().describe("Company name substring."),
      sic: z.string().optional().describe("SIC industry code."),
      entity_type: z.string().optional().describe("Entity type filter."),
      state_of_incorp: z.string().optional().describe("State of incorporation."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/entities", args),
  }),

  get_company_financials: tool({
    description: "Structured XBRL financial facts (every reported concept) for one company by CIK.",
    parameters: z.object({
      cik: z.string().describe("Company CIK."),
      concept: z.string().optional().describe('XBRL concept, e.g. "us-gaap:Revenues".'),
    }),
    execute: async ({ cik, concept }) =>
      clousGet(`/v1/financials/${encodeURIComponent(cik)}`, { concept }),
  }),

  search_insider_transactions: tool({
    description:
      "Search Form 3/4/5 insider transactions by issuer, owner, transaction code, date, and value.",
    parameters: z.object({
      ticker: z.string().optional().describe("Issuer ticker."),
      issuer: z.string().optional().describe("Issuer name."),
      owner: z.string().optional().describe("Insider/owner name."),
      issuer_cik: z.string().optional().describe("Issuer CIK."),
      owner_cik: z.string().optional().describe("Owner CIK."),
      trans_code: z.string().optional().describe("SEC transaction code, e.g. P, S, A, M, F."),
      acquired_disposed: z.string().optional().describe('"A" (acquired) or "D" (disposed).'),
      derivative: z.boolean().optional().describe("Restrict to derivative trades."),
      date_from: z.string().optional().describe("Earliest date, YYYY-MM-DD."),
      date_to: z.string().optional().describe("Latest date, YYYY-MM-DD."),
      min_value_usd: z.number().optional().describe("Minimum transaction value (USD)."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/insider", args),
  }),

  search_13f_holdings: tool({
    description: "Search 13F institutional holdings (manager -> security positions).",
    parameters: z.object({
      manager: z.string().optional().describe("13F manager name."),
      issuer: z.string().optional().describe("Held issuer name."),
      cusip: z.string().optional().describe("Security CUSIP."),
      min_value: z.number().optional().describe("Minimum position value (USD)."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/holdings", args),
  }),

  search_form_d_raises: tool({
    description: "Search Form D private-placement capital raises.",
    parameters: z.object({
      state: z.string().optional().describe("Issuer state."),
      industry: z.string().optional().describe("Industry group."),
      min_amount: z.number().optional().describe("Minimum total offering amount (USD)."),
      q: z.string().optional().describe("Issuer name substring."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/raises", args),
  }),

  get_8k_events: tool({
    description:
      "Classify the numbered items an 8-K reports (5.02 leadership, 4.01 auditor, 2.02 earnings) with excerpts.",
    parameters: z.object({
      accession: z.string().describe("8-K filing accession number."),
    }),
    execute: async ({ accession }) =>
      clousGet(`/v1/filings/${encodeURIComponent(accession)}/events`),
  }),

  get_filing_briefing: tool({
    description:
      "Get an on-demand AI briefing (plain-language summary) of a single filing by accession number.",
    parameters: z.object({
      accession: z.string().describe("Filing accession number."),
    }),
    execute: async ({ accession }) =>
      clousGet(`/v1/filings/${encodeURIComponent(accession)}/briefing`),
  }),

  list_events: tool({
    description:
      "Query the Clous events feed — typed, evidence-backed SEC business-change events (executive changes, new filings, insider sells).",
    parameters: z.object({
      event_type: z.string().optional().describe("Exact event type, e.g. sec.8k.executive_change."),
      cik: z.string().optional().describe("Issuer CIK (zero-padded 10-digit)."),
      ticker: z.string().optional().describe("Issuer ticker."),
      importance: z.enum(["high", "medium", "low"]).optional().describe("Minimum importance."),
      date_from: z.string().optional().describe("Earliest detected date, YYYY-MM-DD."),
      limit,
      cursor,
    }),
    execute: async (args) => clousGet("/v1/events", args),
  }),

  answer: tool({
    description:
      "Ask a grounded natural-language question over SEC filings; returns an answer with citations to the source filings.",
    parameters: z.object({
      q: z.string().describe("Natural-language question about SEC filings."),
      cik: z.string().optional().describe("Scope to a company CIK."),
      ticker: z.string().optional().describe("Scope to a ticker."),
      accession: z.string().optional().describe("Scope to a single filing."),
      forms: z.string().optional().describe("Comma-separated form types to scope to."),
      max_sources: z.number().int().min(1).max(8).optional().describe("Max grounding sources (default 4)."),
    }),
    execute: async (args) => clousPost("/v1/answer", args),
  }),
};

export default clousTools;
