"""Clous SEC data tools for LangChain.

Usage (2 lines):

    from clous_tools import clous_tools
    agent = create_react_agent(llm, clous_tools())   # or .bind_tools(clous_tools())

Each tool is a ``StructuredTool`` whose function returns the raw Clous JSON
envelope serialized to a string, so any LangChain agent can read it.
"""

from __future__ import annotations

from typing import List, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

import _clous as clous


# ─────────────────────────────────────────────────────────── argument schemas
class SearchFilingsArgs(BaseModel):
    cik: Optional[str] = Field(None, description="Company CIK (zero-padded 10-digit).")
    form_type: Optional[str] = Field(None, description='Form type, e.g. "10-K", "8-K", "4".')
    q: Optional[str] = Field(None, description="Keyword match on company name.")
    filed_from: Optional[str] = Field(None, description="Earliest filed date, YYYY-MM-DD.")
    filed_to: Optional[str] = Field(None, description="Latest filed date, YYYY-MM-DD.")
    sic: Optional[str] = Field(None, description="SIC industry code.")
    state_of_incorp: Optional[str] = Field(None, description="State of incorporation.")
    is_xbrl: Optional[bool] = Field(None, description="Restrict to XBRL filings.")
    limit: Optional[int] = Field(None, description="Page size, 1-100 (default 25).")
    cursor: Optional[str] = Field(None, description="Pagination cursor from a prior page.")


class FullTextSearchArgs(BaseModel):
    q: str = Field(..., description='Keyword or "exact phrase" to search filing text.')
    forms: Optional[str] = Field(None, description="Comma-separated form types, e.g. 8-K,10-K.")
    date_from: Optional[str] = Field(None, description="Earliest filed date, YYYY-MM-DD.")
    date_to: Optional[str] = Field(None, description="Latest filed date, YYYY-MM-DD.")
    ciks: Optional[str] = Field(None, description="Comma-separated CIKs.")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class ResolveEntityArgs(BaseModel):
    cik: Optional[str] = Field(None, description="Company CIK.")
    ticker: Optional[str] = Field(None, description="Ticker symbol.")
    q: Optional[str] = Field(None, description="Company name substring.")
    sic: Optional[str] = Field(None, description="SIC industry code.")
    entity_type: Optional[str] = Field(None, description="Entity type filter.")
    state_of_incorp: Optional[str] = Field(None, description="State of incorporation.")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class CompanyFinancialsArgs(BaseModel):
    cik: str = Field(..., description="Company CIK.")
    concept: Optional[str] = Field(None, description='XBRL concept, e.g. "us-gaap:Revenues".')


class InsiderArgs(BaseModel):
    ticker: Optional[str] = Field(None, description="Issuer ticker.")
    issuer: Optional[str] = Field(None, description="Issuer name.")
    owner: Optional[str] = Field(None, description="Insider/owner name.")
    issuer_cik: Optional[str] = Field(None, description="Issuer CIK.")
    owner_cik: Optional[str] = Field(None, description="Owner CIK.")
    trans_code: Optional[str] = Field(None, description="SEC transaction code, e.g. P, S, A, M, F.")
    acquired_disposed: Optional[str] = Field(None, description='"A" (acquired) or "D" (disposed).')
    derivative: Optional[bool] = Field(None, description="Restrict to derivative trades.")
    date_from: Optional[str] = Field(None, description="Earliest date, YYYY-MM-DD.")
    date_to: Optional[str] = Field(None, description="Latest date, YYYY-MM-DD.")
    min_value_usd: Optional[float] = Field(None, description="Minimum transaction value (USD).")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class HoldingsArgs(BaseModel):
    manager: Optional[str] = Field(None, description="13F manager name.")
    issuer: Optional[str] = Field(None, description="Held issuer name.")
    cusip: Optional[str] = Field(None, description="Security CUSIP.")
    min_value: Optional[float] = Field(None, description="Minimum position value (USD).")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class RaisesArgs(BaseModel):
    state: Optional[str] = Field(None, description="Issuer state.")
    industry: Optional[str] = Field(None, description="Industry group.")
    min_amount: Optional[float] = Field(None, description="Minimum total offering amount (USD).")
    q: Optional[str] = Field(None, description="Issuer name substring.")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class AccessionArgs(BaseModel):
    accession: str = Field(..., description="Filing accession number.")


class ListEventsArgs(BaseModel):
    event_type: Optional[str] = Field(None, description="Exact event type, e.g. sec.8k.executive_change.")
    cik: Optional[str] = Field(None, description="Issuer CIK (zero-padded 10-digit).")
    ticker: Optional[str] = Field(None, description="Issuer ticker.")
    importance: Optional[str] = Field(None, description='"high", "medium", or "low".')
    date_from: Optional[str] = Field(None, description="Earliest detected date, YYYY-MM-DD.")
    limit: Optional[int] = Field(None, description="Page size, 1-100.")
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


class AnswerArgs(BaseModel):
    q: str = Field(..., description="Natural-language question about SEC filings.")
    cik: Optional[str] = Field(None, description="Scope to a company CIK.")
    ticker: Optional[str] = Field(None, description="Scope to a ticker.")
    accession: Optional[str] = Field(None, description="Scope to a single filing.")
    forms: Optional[str] = Field(None, description="Comma-separated form types to scope to.")
    max_sources: Optional[int] = Field(None, description="Max grounding sources, 1-8 (default 4).")


# ───────────────────────────────────────────────────────── tool factory funcs
def _wrap(fn):
    def runner(**kwargs):
        return clous._dumps(fn(**kwargs))

    return runner


def clous_tools() -> List[StructuredTool]:
    """Return the list of Clous StructuredTools, ready to bind to any agent."""
    return [
        StructuredTool.from_function(
            func=_wrap(clous.search_filings),
            name="search_filings",
            description="Search the EDGAR filing index across all form types, "
            "filterable by company CIK, form type, date range, and keyword.",
            args_schema=SearchFilingsArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.full_text_search),
            name="full_text_search",
            description="Full-text search across the body of every EDGAR filing since 2001.",
            args_schema=FullTextSearchArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.resolve_entity),
            name="resolve_entity",
            description="Resolve and look up companies in the entity directory by "
            "CIK, ticker, or name.",
            args_schema=ResolveEntityArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.get_company_financials),
            name="get_company_financials",
            description="Structured XBRL financial facts (every reported concept) "
            "for one company by CIK.",
            args_schema=CompanyFinancialsArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.search_insider_transactions),
            name="search_insider_transactions",
            description="Search Form 3/4/5 insider transactions by issuer, owner, "
            "transaction code, date, and value.",
            args_schema=InsiderArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.search_13f_holdings),
            name="search_13f_holdings",
            description="Search 13F institutional holdings (manager -> security positions).",
            args_schema=HoldingsArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.search_form_d_raises),
            name="search_form_d_raises",
            description="Search Form D private-placement capital raises.",
            args_schema=RaisesArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.get_8k_events),
            name="get_8k_events",
            description="Classify the numbered items an 8-K reports (5.02 leadership, "
            "4.01 auditor, 2.02 earnings) with excerpts.",
            args_schema=AccessionArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.get_filing_briefing),
            name="get_filing_briefing",
            description="Get an on-demand AI briefing (plain-language summary) of a "
            "single filing by accession number.",
            args_schema=AccessionArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.list_events),
            name="list_events",
            description="Query the Clous events feed — typed, evidence-backed SEC "
            "business-change events (executive changes, new filings, insider sells).",
            args_schema=ListEventsArgs,
        ),
        StructuredTool.from_function(
            func=_wrap(clous.answer),
            name="answer",
            description="Ask a grounded natural-language question over SEC filings; "
            "returns an answer with citations to the source filings.",
            args_schema=AnswerArgs,
        ),
    ]


class ClousToolkit:
    """Convenience toolkit exposing the Clous tools as ``.get_tools()``."""

    def get_tools(self) -> List[StructuredTool]:
        return clous_tools()


__all__ = ["clous_tools", "ClousToolkit"]
