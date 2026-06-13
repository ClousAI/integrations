"""Clous SEC data tools for LlamaIndex.

Usage (2 lines):

    from clous_tools import clous_tools
    agent = ReActAgent.from_tools(clous_tools(), llm=llm)

Each entry is a ``FunctionTool`` wrapping one Clous endpoint. LlamaIndex builds
the JSON schema automatically from the wrapped function's type hints and
docstring, so the thin wrappers below simply forward to ``_clous`` and serialize
the JSON envelope to a string for the model.
"""

from __future__ import annotations

from typing import List, Optional

from llama_index.core.tools import FunctionTool

import _clous as clous


def _search_filings(
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
) -> str:
    """Search the EDGAR filing index across all form types, filterable by
    company CIK, form_type (e.g. "10-K", "8-K", "4"), date range
    (filed_from/filed_to as YYYY-MM-DD), SIC code, and keyword q."""
    return clous._dumps(
        clous.search_filings(
            cik=cik, form_type=form_type, q=q, filed_from=filed_from,
            filed_to=filed_to, sic=sic, state_of_incorp=state_of_incorp,
            is_xbrl=is_xbrl, limit=limit, cursor=cursor,
        )
    )


def _full_text_search(
    q: str,
    forms: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    ciks: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> str:
    """Full-text search across the body of every EDGAR filing since 2001. q is a
    keyword or "exact phrase"; forms/ciks are comma-separated filters."""
    return clous._dumps(
        clous.full_text_search(
            q=q, forms=forms, date_from=date_from, date_to=date_to,
            ciks=ciks, limit=limit, cursor=cursor,
        )
    )


def _resolve_entity(
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    q: Optional[str] = None,
    sic: Optional[str] = None,
    entity_type: Optional[str] = None,
    state_of_incorp: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> str:
    """Resolve and look up companies in the entity directory by CIK, ticker, or
    name (q). Use this to turn a ticker or company name into a CIK."""
    return clous._dumps(
        clous.resolve_entity(
            cik=cik, ticker=ticker, q=q, sic=sic, entity_type=entity_type,
            state_of_incorp=state_of_incorp, limit=limit, cursor=cursor,
        )
    )


def _get_company_financials(cik: str, concept: Optional[str] = None) -> str:
    """Structured XBRL financial facts (every reported concept) for one company
    by CIK. Optionally filter to a single concept, e.g. "us-gaap:Revenues"."""
    return clous._dumps(clous.get_company_financials(cik=cik, concept=concept))


def _search_insider_transactions(
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
) -> str:
    """Search Form 3/4/5 insider transactions by issuer, owner, transaction code
    (P, S, A, M, F), acquired_disposed ("A"/"D"), date range, and min value."""
    return clous._dumps(
        clous.search_insider_transactions(
            ticker=ticker, issuer=issuer, owner=owner, issuer_cik=issuer_cik,
            owner_cik=owner_cik, trans_code=trans_code,
            acquired_disposed=acquired_disposed, derivative=derivative,
            date_from=date_from, date_to=date_to, min_value_usd=min_value_usd,
            limit=limit, cursor=cursor,
        )
    )


def _search_13f_holdings(
    manager: Optional[str] = None,
    issuer: Optional[str] = None,
    cusip: Optional[str] = None,
    min_value: Optional[float] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> str:
    """Search 13F institutional holdings (manager -> security positions) by
    manager name, held issuer, CUSIP, and minimum position value."""
    return clous._dumps(
        clous.search_13f_holdings(
            manager=manager, issuer=issuer, cusip=cusip,
            min_value=min_value, limit=limit, cursor=cursor,
        )
    )


def _search_form_d_raises(
    state: Optional[str] = None,
    industry: Optional[str] = None,
    min_amount: Optional[float] = None,
    q: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> str:
    """Search Form D private-placement capital raises by state, industry,
    minimum amount raised, and issuer name (q)."""
    return clous._dumps(
        clous.search_form_d_raises(
            state=state, industry=industry, min_amount=min_amount,
            q=q, limit=limit, cursor=cursor,
        )
    )


def _get_8k_events(accession: str) -> str:
    """Classify the numbered items an 8-K reports (5.02 leadership, 4.01 auditor,
    2.02 earnings) with excerpts, given the filing accession number."""
    return clous._dumps(clous.get_8k_events(accession=accession))


def _get_filing_briefing(accession: str) -> str:
    """Get an on-demand AI briefing (plain-language summary) of a single filing
    by accession number."""
    return clous._dumps(clous.get_filing_briefing(accession=accession))


def _list_events(
    event_type: Optional[str] = None,
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    importance: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> str:
    """Query the Clous events feed — typed, evidence-backed SEC business-change
    events (e.g. sec.8k.executive_change). Filter by event_type, cik, ticker,
    importance ("high"/"medium"/"low"), and date_from."""
    return clous._dumps(
        clous.list_events(
            event_type=event_type, cik=cik, ticker=ticker,
            importance=importance, date_from=date_from, limit=limit, cursor=cursor,
        )
    )


def _answer(
    q: str,
    cik: Optional[str] = None,
    ticker: Optional[str] = None,
    accession: Optional[str] = None,
    forms: Optional[str] = None,
    max_sources: Optional[int] = None,
) -> str:
    """Ask a grounded natural-language question over SEC filings; returns an
    answer with citations. Optionally scope by cik, ticker, accession, or forms."""
    return clous._dumps(
        clous.answer(
            q=q, cik=cik, ticker=ticker, accession=accession,
            forms=forms, max_sources=max_sources,
        )
    )


_FUNCS = [
    ("search_filings", _search_filings),
    ("full_text_search", _full_text_search),
    ("resolve_entity", _resolve_entity),
    ("get_company_financials", _get_company_financials),
    ("search_insider_transactions", _search_insider_transactions),
    ("search_13f_holdings", _search_13f_holdings),
    ("search_form_d_raises", _search_form_d_raises),
    ("get_8k_events", _get_8k_events),
    ("get_filing_briefing", _get_filing_briefing),
    ("list_events", _list_events),
    ("answer", _answer),
]


def clous_tools() -> List[FunctionTool]:
    """Return the list of Clous FunctionTools, ready to hand to a LlamaIndex agent."""
    return [FunctionTool.from_defaults(fn=fn, name=name) for name, fn in _FUNCS]


__all__ = ["clous_tools"]
