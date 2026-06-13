"""Clous SEC data tools for OpenAI function calling / Agents SDK.

Provides:
  * ``CLOUS_TOOLS`` — a list of plain JSON tool schemas (the ``{"type":"function",
    "function": {...}}`` shape the OpenAI Chat Completions / Responses API expects),
  * ``dispatch(name, arguments)`` — calls the matching Clous endpoint and returns
    a JSON string suitable for a ``role: "tool"`` message.

Usage (2 lines):

    from clous_tools import CLOUS_TOOLS, dispatch
    resp = client.chat.completions.create(model="gpt-4o", messages=msgs, tools=CLOUS_TOOLS)
    # ... then: dispatch(call.function.name, json.loads(call.function.arguments))
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List

import _clous as clous

_STR = {"type": "string"}
_INT = {"type": "integer"}
_NUM = {"type": "number"}
_BOOL = {"type": "boolean"}


def _fn(name: str, description: str, props: Dict[str, Any], required: List[str] | None = None) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": props,
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


def _d(t: Dict[str, Any], desc: str) -> Dict[str, Any]:
    return {**t, "description": desc}


CLOUS_TOOLS: List[Dict[str, Any]] = [
    _fn(
        "search_filings",
        "Search the EDGAR filing index across all form types, filterable by "
        "company CIK, form type, date range, and keyword.",
        {
            "cik": _d(_STR, "Company CIK (zero-padded 10-digit)."),
            "form_type": _d(_STR, 'Form type, e.g. "10-K", "8-K", "4".'),
            "q": _d(_STR, "Keyword match on company name."),
            "filed_from": _d(_STR, "Earliest filed date, YYYY-MM-DD."),
            "filed_to": _d(_STR, "Latest filed date, YYYY-MM-DD."),
            "sic": _d(_STR, "SIC industry code."),
            "state_of_incorp": _d(_STR, "State of incorporation."),
            "is_xbrl": _d(_BOOL, "Restrict to XBRL filings."),
            "limit": _d(_INT, "Page size, 1-100 (default 25)."),
            "cursor": _d(_STR, "Pagination cursor from a prior page."),
        },
    ),
    _fn(
        "full_text_search",
        "Full-text search across the body of every EDGAR filing since 2001.",
        {
            "q": _d(_STR, 'Keyword or "exact phrase" to search filing text.'),
            "forms": _d(_STR, "Comma-separated form types, e.g. 8-K,10-K."),
            "date_from": _d(_STR, "Earliest filed date, YYYY-MM-DD."),
            "date_to": _d(_STR, "Latest filed date, YYYY-MM-DD."),
            "ciks": _d(_STR, "Comma-separated CIKs."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
        required=["q"],
    ),
    _fn(
        "resolve_entity",
        "Resolve and look up companies in the entity directory by CIK, ticker, or name.",
        {
            "cik": _d(_STR, "Company CIK."),
            "ticker": _d(_STR, "Ticker symbol."),
            "q": _d(_STR, "Company name substring."),
            "sic": _d(_STR, "SIC industry code."),
            "entity_type": _d(_STR, "Entity type filter."),
            "state_of_incorp": _d(_STR, "State of incorporation."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
    ),
    _fn(
        "get_company_financials",
        "Structured XBRL financial facts (every reported concept) for one company by CIK.",
        {
            "cik": _d(_STR, "Company CIK."),
            "concept": _d(_STR, 'XBRL concept, e.g. "us-gaap:Revenues".'),
        },
        required=["cik"],
    ),
    _fn(
        "search_insider_transactions",
        "Search Form 3/4/5 insider transactions by issuer, owner, transaction "
        "code, date, and value.",
        {
            "ticker": _d(_STR, "Issuer ticker."),
            "issuer": _d(_STR, "Issuer name."),
            "owner": _d(_STR, "Insider/owner name."),
            "issuer_cik": _d(_STR, "Issuer CIK."),
            "owner_cik": _d(_STR, "Owner CIK."),
            "trans_code": _d(_STR, "SEC transaction code, e.g. P, S, A, M, F."),
            "acquired_disposed": _d(_STR, '"A" (acquired) or "D" (disposed).'),
            "derivative": _d(_BOOL, "Restrict to derivative trades."),
            "date_from": _d(_STR, "Earliest date, YYYY-MM-DD."),
            "date_to": _d(_STR, "Latest date, YYYY-MM-DD."),
            "min_value_usd": _d(_NUM, "Minimum transaction value (USD)."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
    ),
    _fn(
        "search_13f_holdings",
        "Search 13F institutional holdings (manager -> security positions).",
        {
            "manager": _d(_STR, "13F manager name."),
            "issuer": _d(_STR, "Held issuer name."),
            "cusip": _d(_STR, "Security CUSIP."),
            "min_value": _d(_NUM, "Minimum position value (USD)."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
    ),
    _fn(
        "search_form_d_raises",
        "Search Form D private-placement capital raises.",
        {
            "state": _d(_STR, "Issuer state."),
            "industry": _d(_STR, "Industry group."),
            "min_amount": _d(_NUM, "Minimum total offering amount (USD)."),
            "q": _d(_STR, "Issuer name substring."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
    ),
    _fn(
        "get_8k_events",
        "Classify the numbered items an 8-K reports (5.02 leadership, 4.01 "
        "auditor, 2.02 earnings) with excerpts.",
        {"accession": _d(_STR, "8-K filing accession number.")},
        required=["accession"],
    ),
    _fn(
        "get_filing_briefing",
        "Get an on-demand AI briefing (plain-language summary) of a single "
        "filing by accession number.",
        {"accession": _d(_STR, "Filing accession number.")},
        required=["accession"],
    ),
    _fn(
        "list_events",
        "Query the Clous events feed — typed, evidence-backed SEC business-change "
        "events (executive changes, new filings, insider sells).",
        {
            "event_type": _d(_STR, "Exact event type, e.g. sec.8k.executive_change."),
            "cik": _d(_STR, "Issuer CIK (zero-padded 10-digit)."),
            "ticker": _d(_STR, "Issuer ticker."),
            "importance": {**_STR, "enum": ["high", "medium", "low"], "description": "Minimum importance."},
            "date_from": _d(_STR, "Earliest detected date, YYYY-MM-DD."),
            "limit": _d(_INT, "Page size, 1-100."),
            "cursor": _d(_STR, "Pagination cursor."),
        },
    ),
    _fn(
        "answer",
        "Ask a grounded natural-language question over SEC filings; returns an "
        "answer with citations to the source filings.",
        {
            "q": _d(_STR, "Natural-language question about SEC filings."),
            "cik": _d(_STR, "Scope to a company CIK."),
            "ticker": _d(_STR, "Scope to a ticker."),
            "accession": _d(_STR, "Scope to a single filing."),
            "forms": _d(_STR, "Comma-separated form types to scope to."),
            "max_sources": _d(_INT, "Max grounding sources, 1-8 (default 4)."),
        },
        required=["q"],
    ),
]


_HANDLERS: Dict[str, Callable[..., Any]] = {
    "search_filings": clous.search_filings,
    "full_text_search": clous.full_text_search,
    "resolve_entity": clous.resolve_entity,
    "get_company_financials": clous.get_company_financials,
    "search_insider_transactions": clous.search_insider_transactions,
    "search_13f_holdings": clous.search_13f_holdings,
    "search_form_d_raises": clous.search_form_d_raises,
    "get_8k_events": clous.get_8k_events,
    "get_filing_briefing": clous.get_filing_briefing,
    "list_events": clous.list_events,
    "answer": clous.answer,
}


def dispatch(name: str, arguments: Dict[str, Any] | str) -> str:
    """Execute a Clous tool by name and return its JSON envelope as a string.

    ``arguments`` may be the already-parsed dict or the raw JSON string the
    OpenAI SDK puts on ``tool_call.function.arguments``.
    """
    if isinstance(arguments, str):
        arguments = json.loads(arguments or "{}")
    handler = _HANDLERS.get(name)
    if handler is None:
        return clous._dumps({"error": f"unknown tool: {name}"})
    return clous._dumps(handler(**arguments))


__all__ = ["CLOUS_TOOLS", "dispatch"]
