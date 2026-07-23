"""
legolagents.tools.articles
──────────────────────────
Abstract tools for statutes and legal codes.

Any case law analysis must be cross-referenced with the legal text.
These tools give access to the applicable codes and articles.
"""

from __future__ import annotations

from abc import abstractmethod

from .base import LegalTool


# Common aliases for French legal code names
# (kept in French: these are the actual proper names of French codes)
CODE_ALIASES: dict[str, str] = {
    "travail":        "Code du travail",
    "civil":          "Code civil",
    "commerce":       "Code de commerce",
    "pénal":          "Code pénal",
    "procedure":      "Code de procédure civile",
    "cpc":            "Code de procédure civile",
    "cpi":            "Code de la propriété intellectuelle",
    "css":            "Code de la sécurité sociale",
    "urbanisme":      "Code de l'urbanisme",
    "construction":   "Code de la construction et de l'habitation",
    "consommation":   "Code de la consommation",
    "administratif":  "Code de justice administrative",
}


def normalize_code_name(code: str) -> str:
    """Normalize a legal code name (alias → full name)."""
    return CODE_ALIASES.get(code.strip().lower(), code)


class GetArticleTool(LegalTool):
    """
    Retrieves the content of a specific statute article.
    """

    name = "get_article"
    description = (
        "Retrieves the full text of a statute article. "
        "Essential for cross-referencing case law with the applicable legal text. "
        "Always check the version currently in force."
    )
    inputs = {
        "code": {
            "type": "string",
            "description": (
                "Name of the code (e.g. 'Code du travail', 'Code civil', 'Code de commerce'). "
                "Accepted aliases: 'travail', 'civil', 'commerce', 'pénal'."
            ),
        },
        "article": {
            "type": "string",
            "description": "Article number (e.g. 'L1235-3', '1240', 'R4121-1')",
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, code: str, article: str) -> str:
        raise NotImplementedError

    def format_article(
        self,
        *,
        code: str,
        article: str,
        content: str,
        url: str = "",
        version_date: str = "",
    ) -> str:
        ref = self.fmt_article(code=code, numero=article, url=url)
        lines = [ref]
        if version_date:
            lines.append(f"*Version in force as of {self.fmt_date(version_date)}*")
        lines.append("")
        lines.append(content[:3000])
        if url:
            lines.append(f"\n🔗 [View on SmartLawyer]({url})")
        return "\n".join(lines)


class SearchArticlesTool(LegalTool):
    """
    Searches statute articles by topic (semantic search).
    """

    name = "search_articles"
    description = (
        "Searches statute articles by topic or legal concept. "
        "Returns the most relevant articles with their content. "
        "Use to find the textual basis of a case law rule."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Topic or concept (e.g. 'severance pay Macron scale')",
        },
        "code": {
            "type": "string",
            "description": "Restrict to a specific code (optional)",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Number of results (default 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, query: str, code: str = "", limit: int = 5) -> str:
        raise NotImplementedError

    def format_articles(self, results: list[dict]) -> str:
        if not results:
            return "No article found for this query."
        lines = [f"**{len(results)} article(s) found:**\n"]
        for r in results:
            code    = r.get("code", "")
            numero  = r.get("numero", r.get("article", ""))
            content = (r.get("text") or r.get("contenu") or "")[:300]
            url     = r.get("url", "")
            ref = self.fmt_article(code=code, numero=numero, url=url)
            lines.append(f"- {ref}")
            if content:
                lines.append(f"  {content}…")
        return "\n".join(lines)
