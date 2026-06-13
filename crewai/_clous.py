"""Tiny shared HTTP helper + endpoint definitions for the Clous SEC data API.

This module is intentionally dependency-light (only the stdlib + `requests`) and
is copied verbatim into every framework folder so each folder is independently
usable. It centralises:

  * the base URL and bearer-token auth (``CLOUS_API_KEY`` from the environment),
  * a single ``clous_get`` / ``clous_post`` request helper that returns the
    parsed JSON envelope ``{data, page, as_of, source, query_echo, warnings}``,
  * thin Python functions for the ~11 core Clous endpoints, each accepting the
    same parameters documented at https://docs.clous.ai and dropping ``None``s.

Framework adapters (LangChain, LlamaIndex, OpenAI, CrewAI) wrap these functions;
the wire logic lives here exactly once.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

import requests

CLOUS_BASE_URL = os.environ.get("CLOUS_BASE_URL", "https://api.clous.ai").rstrip("/")
DEFAULT_TIMEOUT = float(os.environ.get("CLOUS_TIMEOUT", "60"))


def _api_key() -> str:
    key = os.environ.get("CLOUS_API_KEY")
    if not key:
        raise RuntimeError(
            "CLOUS_API_KEY is not set. Get a key at https://clous.ai and "
            "export CLOUS_API_KEY=<your key>."
        )
    return key


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Accept": "application/json",
        "User-Agent": "clous-integrations/0.1 (+https://github.com/clousai/integrations)",
    }


def _clean(params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Drop ``None`` values and serialise lists to comma-joined strings."""
    out: Dict[str, Any] = {}
    for k, v in (params or {}).items():
        if v is None:
            continue
        if isinstance(v, (list, tuple)):
            v = ",".join(str(x) for x in v)
        if isinstance(v, bool):
            v = "true" if v else "false"
        out[k] = v
    return out


def clous_get(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """GET ``{CLOUS_BASE_URL}{path}`` and return the parsed JSON envelope."""
    resp = requests.get(
        f"{CLOUS_BASE_URL}{path}",
        params=_clean(params),
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def clous_post(path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """POST ``{CLOUS_BASE_URL}{path}`` and return the parsed JSON envelope."""
    resp = requests.post(
        f"{CLOUS_BASE_URL}{path}",
        json=_clean(body),
        headers=_headers(),
        timeout=DEFAULT_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


# ────────────────────────────────────────────────────────────── core endpoints
# Each function maps 1:1 to a Clous endpoint. They return the raw JSON envelope
# (a dict). Framework wrappers JSON-encode the result for the model.


def search_filings(
    cik: Optional[str] = None,
    form_type: Optional[str] = None,
    q: Optional[str] = None,
    filed_from: Optional[str] = None,
    filed_to: Optional[str] = None,
    sic: Optional[str] = None,
    state_of_incorp: Optional[str] = None,
    is_xbrl: Optional[bool] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Search the EDGAR filing index across all form types."""
    return clous_get(
        "/v1/filings",
        {
            "cik": cik,
            "form_type": form_type,
            "q": q,
            "filed_from": filed_from,
            "filed_to": filed_to,
            "sic": sic,
            "state_of_incorp": state_of_incorp,
            "is_xbrl": is_xbrl,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def full_text_search(
    q: str,
    forms: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    ciks: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Full-text search across the body of every EDGAR filing since 2001."""
    return clous_get(
        "/v1/full-text",
        {
            "q": q,
            "forms": forms,
            "date_from": date_from,
            "date_to": date_to,
            "ciks": ciks,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def resolve_entity(
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    q: Optional[str] = None,
    sic: Optional[str] = None,
    entity_type: Optional[str] = None,
    state_of_incorp: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Resolve / look up companies by CIK, ticker, or name."""
    return clous_get(
        "/v1/entities",
        {
            "cik": cik,
            "ticker": ticker,
            "q": q,
            "sic": sic,
            "entity_type": entity_type,
            "state_of_incorp": state_of_incorp,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def get_company_financials(
    cik: str,
    concept: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Structured XBRL financial facts for one company by CIK."""
    return clous_get(
        f"/v1/financials/{cik}",
        {"concept": concept, "fields": fields},
    )


def search_insider_transactions(
    ticker: Optional[str] = None,
    issuer: Optional[str] = None,
    owner: Optional[str] = None,
    issuer_cik: Optional[str] = None,
    owner_cik: Optional[str] = None,
    trans_code: Optional[str] = None,
    acquired_disposed: Optional[str] = None,
    derivative: Optional[bool] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_value_usd: Optional[float] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Search Form 3/4/5 insider transactions."""
    return clous_get(
        "/v1/insider",
        {
            "ticker": ticker,
            "issuer": issuer,
            "owner": owner,
            "issuer_cik": issuer_cik,
            "owner_cik": owner_cik,
            "trans_code": trans_code,
            "acquired_disposed": acquired_disposed,
            "derivative": derivative,
            "date_from": date_from,
            "date_to": date_to,
            "min_value_usd": min_value_usd,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def search_13f_holdings(
    manager: Optional[str] = None,
    issuer: Optional[str] = None,
    cusip: Optional[str] = None,
    min_value: Optional[float] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Search 13F institutional holdings (manager -> security positions)."""
    return clous_get(
        "/v1/holdings",
        {
            "manager": manager,
            "issuer": issuer,
            "cusip": cusip,
            "min_value": min_value,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def search_form_d_raises(
    state: Optional[str] = None,
    industry: Optional[str] = None,
    min_amount: Optional[float] = None,
    q: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Search Form D private-placement capital raises."""
    return clous_get(
        "/v1/raises",
        {
            "state": state,
            "industry": industry,
            "min_amount": min_amount,
            "q": q,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def get_8k_events(accession: str) -> Dict[str, Any]:
    """Classify the numbered items an 8-K reports (with excerpts)."""
    return clous_get(f"/v1/filings/{accession}/events")


def get_filing_briefing(accession: str) -> Dict[str, Any]:
    """On-demand AI briefing (plain-language summary) of a single filing."""
    return clous_get(f"/v1/filings/{accession}/briefing")


def list_events(
    event_type: Optional[str] = None,
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    importance: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
    fields: Optional[str] = None,
) -> Dict[str, Any]:
    """Query the events feed — typed, evidence-backed SEC business-change events."""
    return clous_get(
        "/v1/events",
        {
            "event_type": event_type,
            "cik": cik,
            "ticker": ticker,
            "importance": importance,
            "date_from": date_from,
            "limit": limit,
            "cursor": cursor,
            "fields": fields,
        },
    )


def answer(
    q: str,
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    accession: Optional[str] = None,
    forms: Optional[str] = None,
    max_sources: Optional[int] = None,
) -> Dict[str, Any]:
    """Ask a grounded natural-language question; returns an answer with citations."""
    return clous_post(
        "/v1/answer",
        {
            "q": q,
            "cik": cik,
            "ticker": ticker,
            "accession": accession,
            "forms": forms,
            "max_sources": max_sources,
        },
    )


def _dumps(obj: Any) -> str:
    """Compact JSON string suitable for handing a tool result to an LLM."""
    return json.dumps(obj, ensure_ascii=False, default=str)
