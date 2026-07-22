"""
legolagents.tools.base
─────────────────────
LegalTool — base class pour tous les tools juridiques.

Apporte par rapport à smolagents.Tool :
  - Attributs de domaine (jurisdiction, legal_domain)
  - Helpers de formatage citations FR
  - run_async() — bridge sync/async propre
  - Niveau de certitude sur les résultats
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Coroutine

from smolagents import Tool


class Certainty(str, Enum):
    ESTABLISHED = "established"  # jurisprudence constante, publiée, non superseded
    TRENDING    = "trending"     # arrêts récents, pas encore constants
    ISOLATED    = "isolated"     # arrêt unique ou minoritaire
    SUPERSEDED  = "superseded"   # ne plus citer comme droit positif

    def label(self) -> str:
        return {
            self.ESTABLISHED: "✅ Droit établi",
            self.TRENDING:    "⚡ Tendance",
            self.ISOLATED:    "⚠️ Isolé",
            self.SUPERSEDED:  "❌ Superseded",
        }[self]


@dataclass
class LegalCitation:
    """Représentation normalisée d'une citation juridique."""
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
    """Résultat structuré retourné par un LegalTool."""
    content: str
    citations: list[LegalCitation] = field(default_factory=list)
    certainty: Certainty = Certainty.ESTABLISHED
    metadata: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


class LegalTool(Tool):
    """
    Base class pour tous les tools juridiques.

    Toutes les sous-classes qui font des appels réseau doivent implémenter
    forward() de manière synchrone et utiliser self.run_async() pour les
    coroutines. Ne pas réimplémenter __call__.
    """

    # Sous-classes peuvent surcharger
    jurisdiction: str = "FR"
    legal_domain: str = ""
    async_timeout: int = 60

    # ── Formatage ──────────────────────────────────────────────────────────────

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
        """Formate une décision en Markdown avec lien optionnel."""
        date_short = (date or "")[:10]
        header = f"{jurisdiction} · {chamber} · {date_short} · n°{number}"
        link = f"[{header}]({url})" if url else f"**{header}**"
        return f"{link} — {solution}" if solution else link

    @staticmethod
    def fmt_article(*, code: str, numero: str, url: str = "") -> str:
        """Formate une référence d'article de loi."""
        ref = f"Art. {numero} {code}"
        return f"[{ref}]({url})" if url else f"**{ref}**"

    @staticmethod
    def fmt_date(raw: str) -> str:
        """Normalise une date au format YYYY-MM-DD → DD/MM/YYYY."""
        if not raw or len(raw) < 10:
            return raw or ""
        try:
            y, m, d = raw[:10].split("-")
            return f"{d}/{m}/{y}"
        except ValueError:
            return raw[:10]

    @staticmethod
    def certainty_from_payload(payload: dict) -> Certainty:
        """Déduit le niveau de certitude depuis les métadonnées d'un arrêt."""
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
        Exécute une coroutine depuis forward() (contexte synchrone).

        Détecte si une event loop tourne déjà (FastAPI, Chainlit) et
        utilise un thread isolé pour éviter les conflits.

        IMPORTANT : la coroutine doit être créée DANS le thread pour éviter
        les Future cross-loop. On passe donc soit une coroutine (cas sans loop),
        soit on la wrape dans asyncio.run directement.
        """
        try:
            asyncio.get_running_loop()
            # Event loop active → thread séparé avec sa propre loop
            # On wrappe dans une fonction pour que la coroutine soit
            # entièrement exécutée dans le contexte du nouveau thread
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(self._run_in_new_loop, coro)
                return fut.result(timeout=self.async_timeout)
        except RuntimeError:
            # Pas de loop active → on peut lancer directement
            return asyncio.run(coro)

    @staticmethod
    def _run_in_new_loop(coro: Coroutine) -> Any:
        """Crée une loop propre et exécute la coroutine dedans."""
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
            raise ValueError(f"[{self.name}] Paramètre requis manquant : {name}")
        return value
