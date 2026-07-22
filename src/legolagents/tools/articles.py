"""
legolagents.tools.articles
──────────────────────────
Tools abstraits pour les articles de loi.

Toute analyse jurisprudentielle doit être croisée avec le texte légal.
Ces tools donnent accès aux codes et articles applicables.
"""

from __future__ import annotations

from abc import abstractmethod

from .base import LegalTool


# Aliases courants pour les noms de codes français
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
    """Normalise un nom de code juridique (alias → nom complet)."""
    return CODE_ALIASES.get(code.strip().lower(), code)


class GetArticleTool(LegalTool):
    """
    Récupère le contenu d'un article de loi précis.
    """

    name = "get_article"
    description = (
        "Récupère le texte complet d'un article de loi. "
        "Indispensable pour croiser la jurisprudence avec le texte légal applicable. "
        "Toujours vérifier la version en vigueur."
    )
    inputs = {
        "code": {
            "type": "string",
            "description": (
                "Nom du code (ex: 'Code du travail', 'Code civil', 'Code de commerce'). "
                "Alias acceptés : 'travail', 'civil', 'commerce', 'pénal'."
            ),
        },
        "article": {
            "type": "string",
            "description": "Numéro de l'article (ex: 'L1235-3', '1240', 'R4121-1')",
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
            lines.append(f"*Version en vigueur au {self.fmt_date(version_date)}*")
        lines.append("")
        lines.append(content[:3000])
        if url:
            lines.append(f"\n🔗 [Consulter sur SmartLawyer]({url})")
        return "\n".join(lines)


class SearchArticlesTool(LegalTool):
    """
    Recherche des articles de loi par thème (recherche sémantique).
    """

    name = "search_articles"
    description = (
        "Recherche des articles de loi par thème ou concept juridique. "
        "Retourne les articles les plus pertinents avec leur contenu. "
        "Utiliser pour trouver le fondement textuel d'une règle jurisprudentielle."
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "Thème ou concept (ex: 'indemnité licenciement barème Macron')",
        },
        "code": {
            "type": "string",
            "description": "Restreindre à un code précis (optionnel)",
            "nullable": True,
        },
        "limit": {
            "type": "integer",
            "description": "Nombre de résultats (défaut 5)",
            "nullable": True,
        },
    }
    output_type = "string"

    @abstractmethod
    def forward(self, query: str, code: str = "", limit: int = 5) -> str:
        raise NotImplementedError

    def format_articles(self, results: list[dict]) -> str:
        if not results:
            return "Aucun article trouvé pour cette requête."
        lines = [f"**{len(results)} article(s) trouvé(s) :**\n"]
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
