"""
legolagents.tools.base
─────────────────────
LegalTool — base class for all legal tools.

Adds on top of smolagents.Tool:
  - Domain attributes (jurisdiction, legal_domain)
  - Citation formatting helpers
  - run_async() — clean sync/async bridge
  - Certainty level on results
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Coroutine

from smolagents import Tool


class Certainty(str, Enum):
    ESTABLISHED = "established"  # settled, published case law, non-superseded
    TRENDING    = "trending"     # recent decisions, not yet settled
    ISOLATED    = "isolated"     # single or minority decision
    SUPERSEDED  = "superseded"   # no longer citable as positive law

    def label(self) -> str:
        return {
            self.ESTABLISHED: "✅ Established law",
            self.TRENDING:    "⚡ Trending",
            self.ISOLATED:    "⚠️ Isolated",
            self.SUPERSEDED:  "❌ Superseded",
        }[self]


@dataclass
class LegalCitation:
    """
    Normalized representation of a case law citation.

    Case-law-specific (chamber, importance_score…). For reasoning that
    spans multiple kinds of sources — a statute, the cases interpreting
    it, a treaty it implements — see the more general `LegalSource` in
    `legolagents.ontology`.
    """
    number: str
    date: str
    jurisdiction: str
    chamber: str
    solution: str = ""
    url: str = ""
    importance_score: int = 0
    cited_by_count: int = 0
    certainty: Certainty = Certainty.ESTABLISHED

    def to_markdown(self) -> str:
        header = f"{self.jurisdiction} · {self.chamber} · {self.date} · n°{self.number}"
        if self.url:
            link = f"[{header}]({self.url})"
        else:
            link = f"**{header}**"
        parts = [link]
        if self.solution:
            parts.append(f"— {self.solution}")
        parts.append(self.certainty.label())
        return " ".join(parts)


@dataclass
class LegalToolResult:
    """Structured result returned by a LegalTool."""
    content: str
    citations: list[LegalCitation] = field(default_factory=list)
    certainty: Certainty = Certainty.ESTABLISHED
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


class LegalTool(Tool):
    """
    Base class for all legal tools.

    Any subclass that makes network calls must implement forward()
    synchronously and use self.run_async() for coroutines. Do not
    reimplement __call__.
    """

    # Subclasses may override
    jurisdiction: str = ""
    legal_domain: str = ""
    async_timeout: int = 60

    # ── Formatting ─────────────────────────────────────────────────────────────

    @staticmethod
    def fmt_decision(
        *,
        number: str,
        date: str,
        jurisdiction: str,
        chamber: str,
        url: str = "",
        solution: str = "",
    ) -> str:
        """Format a decision as Markdown with an optional link."""
        date_short = (date or "")[:10]
        header = f"{jurisdiction} · {chamber} · {date_short} · n°{number}"
        link = f"[{header}]({url})" if url else f"**{header}**"
        return f"{link} — {solution}" if solution else link

    @staticmethod
    def fmt_article(*, code: str, number: str, url: str = "") -> str:
        """Format a statute reference."""
        ref = f"Art. {number} {code}"
        return f"[{ref}]({url})" if url else f"**{ref}**"

    @staticmethod
    def fmt_date(raw: str) -> str:
        """Normalize a date from YYYY-MM-DD → DD/MM/YYYY."""
        if not raw or len(raw) < 10:
            return raw or ""
        try:
            y, m, d = raw[:10].split("-")
            return f"{d}/{m}/{y}"
        except ValueError:
            return raw[:10]

    @staticmethod
    def certainty_from_payload(payload: dict) -> Certainty:
        """Infer the certainty level from a decision's metadata."""
        if payload.get("superseded_by"):
            return Certainty.SUPERSEDED
        score = payload.get("importance_score") or 0
        cited = payload.get("cited_by_count") or 0
        publication = payload.get("publication") or []
        if publication or score >= 70 or cited >= 20:
            return Certainty.ESTABLISHED
        if score >= 30 or cited >= 5:
            return Certainty.TRENDING
        return Certainty.ISOLATED

    # ── Async bridge ───────────────────────────────────────────────────────────

    def run_async(self, coro: Coroutine) -> Any:
        """
        Run a coroutine from forward() (synchronous context).

        Detects whether an event loop is already running (FastAPI, Chainlit)
        and uses an isolated thread to avoid conflicts.

        IMPORTANT: the coroutine must be created INSIDE the thread to avoid
        cross-loop Futures. So we either pass a coroutine (no-loop case), or
        wrap it directly in asyncio.run.
        """
        try:
            asyncio.get_running_loop()
            # Active event loop → separate thread with its own loop
            # Wrapped in a function so the coroutine is fully executed
            # within the new thread's context
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self._run_in_new_loop, coro)
                return fut.result(timeout=self.async_timeout)
        except RuntimeError:
            # No active loop → can run directly
            return asyncio.run(coro)

    @staticmethod
    def _run_in_new_loop(coro: Coroutine) -> Any:
        """Create a clean loop and run the coroutine inside it."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    # ── Validation ─────────────────────────────────────────────────────────────

    def _require(self, value: Any, name: str) -> Any:
        if value is None:
            raise ValueError(f"[{self.name}] Missing required parameter: {name}")
        return value
