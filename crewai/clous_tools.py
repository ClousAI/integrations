"""Clous SEC data tools for CrewAI.

Each tool is a ``crewai.tools.BaseTool`` subclass with a pydantic ``args_schema``.
Returns the Clous JSON envelope as a string so any agent can read it.

Usage (2 lines):

    from clous_tools import clous_tools
    agent = Agent(role="SEC analyst", tools=clous_tools(), llm=llm, ...)
"""

from __future__ import annotations

from typing import List, Optional, Type

from crewai.tools import BaseTool
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
    cursor: Optional[str] = Field(None, description="Pagination cursor.")


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


# ──────────────────────────────────────────────────────────────── tool classes
class SearchFilingsTool(BaseTool):
    name: str = "search_filings"
    description: str = (
        "Search the EDGAR filing index across all form types, filterable by "
        "company CIK, form type, date range, and keyword."
    )
    args_schema: Type[BaseModel] = SearchFilingsArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.search_filings(**kwargs))


class FullTextSearchTool(BaseTool):
    name: str = "full_text_search"
    description: str = "Full-text search across the body of every EDGAR filing since 2001."
    args_schema: Type[BaseModel] = FullTextSearchArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.full_text_search(**kwargs))


class ResolveEntityTool(BaseTool):
    name: str = "resolve_entity"
    description: str = (
        "Resolve and look up companies in the entity directory by CIK, ticker, or name."
    )
    args_schema: Type[BaseModel] = ResolveEntityArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.resolve_entity(**kwargs))


class CompanyFinancialsTool(BaseTool):
    name: str = "get_company_financials"
    description: str = (
        "Structured XBRL financial facts (every reported concept) for one company by CIK."
    )
    args_schema: Type[BaseModel] = CompanyFinancialsArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.get_company_financials(**kwargs))


class InsiderTransactionsTool(BaseTool):
    name: str = "search_insider_transactions"
    description: str = (
        "Search Form 3/4/5 insider transactions by issuer, owner, transaction "
        "code, date, and value."
    )
    args_schema: Type[BaseModel] = InsiderArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.search_insider_transactions(**kwargs))


class Holdings13FTool(BaseTool):
    name: str = "search_13f_holdings"
    description: str = "Search 13F institutional holdings (manager -> security positions)."
    args_schema: Type[BaseModel] = HoldingsArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.search_13f_holdings(**kwargs))


class FormDRaisesTool(BaseTool):
    name: str = "search_form_d_raises"
    description: str = "Search Form D private-placement capital raises."
    args_schema: Type[BaseModel] = RaisesArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.search_form_d_raises(**kwargs))


class Events8KTool(BaseTool):
    name: str = "get_8k_events"
    description: str = (
        "Classify the numbered items an 8-K reports (5.02 leadership, 4.01 "
        "auditor, 2.02 earnings) with excerpts."
    )
    args_schema: Type[BaseModel] = AccessionArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.get_8k_events(**kwargs))


class FilingBriefingTool(BaseTool):
    name: str = "get_filing_briefing"
    description: str = (
        "Get an on-demand AI briefing (plain-language summary) of a single "
        "filing by accession number."
    )
    args_schema: Type[BaseModel] = AccessionArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.get_filing_briefing(**kwargs))


class ListEventsTool(BaseTool):
    name: str = "list_events"
    description: str = (
        "Query the Clous events feed — typed, evidence-backed SEC business-change "
        "events (executive changes, new filings, insider sells)."
    )
    args_schema: Type[BaseModel] = ListEventsArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.list_events(**kwargs))


class AnswerTool(BaseTool):
    name: str = "answer"
    description: str = (
        "Ask a grounded natural-language question over SEC filings; returns an "
        "answer with citations to the source filings."
    )
    args_schema: Type[BaseModel] = AnswerArgs

    def _run(self, **kwargs) -> str:
        return clous._dumps(clous.answer(**kwargs))


def clous_tools() -> List[BaseTool]:
    """Return the list of Clous CrewAI tools, ready to pass to an Agent."""
    return [
        SearchFilingsTool(),
        FullTextSearchTool(),
        ResolveEntityTool(),
        CompanyFinancialsTool(),
        InsiderTransactionsTool(),
        Holdings13FTool(),
        FormDRaisesTool(),
        Events8KTool(),
        FilingBriefingTool(),
        ListEventsTool(),
        AnswerTool(),
    ]


__all__ = ["clous_tools"]
