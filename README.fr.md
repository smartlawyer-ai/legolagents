<div align="center">
  <img src="assets/legolagents_banner.png" alt="legolagents" width="800"/>

[![PyPI](https://img.shields.io/pypi/v/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Licence Apache 2.0](https://img.shields.io/badge/licence-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)]()
[![Basé sur smolagents](https://img.shields.io/badge/basé%20sur-smolagents-orange.svg)](https://github.com/huggingface/smolagents)

[English version](README.md)

</div>

---

**legolagents** étend [smolagents](https://github.com/huggingface/smolagents) avec un raisonnement juridique structuré — agnostique de juridiction par défaut.

Vous avez déjà smolagents. Ajoutez legolagents et vos agents appliquent le protocole d'un juriste, quel que soit le droit applicable : ils vérifient si une décision est toujours valide avant de la citer, remontent la lignée jurisprudentielle, détectent les revirements, et révisent vos contrats avec le suivi des modifications Word natif. Précisez une juridiction (`jurisdiction="France"`, `"Belgique"`…) pour l'ancrer dans un droit donné — ou laissez l'agent générique si vous branchez votre propre base multi-juridictions.

```bash
pip install legolagents
```

---

## Ce que ça change concrètement

**Sans legolagents**, un agent smolagents répond à une question juridique en cherchant des mots-clés. Il peut citer une décision renversée depuis 3 ans sans le savoir.

**Avec legolagents**, l'agent applique automatiquement le protocole d'un juriste :
vérifie la validité de chaque décision, distingue les décisions de principe des décisions d'espèce, remonte les citations sur plusieurs niveaux, et signale les divergences entre chambres ou juridictions.

---

## Démarrage rapide (n'importe quelle juridiction)

legolagents ne présuppose aucune base de données ni aucun droit — vous branchez vos propres outils :

```python
from legolagents import LegalResearchAgent
from legolagents.tools.retrieval import JurisprudenceSearchTool
from smolagents import LiteLLMModel

class MonOutilDeRecherche(JurisprudenceSearchTool):
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        resultats = ma_base.rechercher(query)
        return self.format_results(resultats)

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
agent = LegalResearchAgent(
    tools=[MonOutilDeRecherche()],
    model=model,
    jurisdiction="France",   # ou "Belgique", "Québec"… ou vide (générique)
)
print(agent.run("Quelle est la jurisprudence sur la rupture abusive de promesse de vente ?"))
```

L'agent vérifie automatiquement la validité des décisions, remonte le graphe de citations, et répond avec un niveau de certitude : `✅ Droit établi`, `⚡ Tendance`, `⚠️ Isolé`, ou `❌ Superseded`.

Pas encore de base jurisprudentielle ? Voir la section [Exemple : démarrer sur le marché français](#exemple--démarrer-sur-le-marché-français-smartlawyer-mcp) plus bas — un connecteur MCP prêt à l'emploi pour tester le framework sans rien construire.

---

## Autres exemples

### Révision de contrat avec Accept / Rejeter dans Word

```python
from legolagents import LegalDocumentAgent

agent = LegalDocumentAgent(model=model, jurisdiction="France", legal_domain="droit social")
agent.review(
    "contrat.docx",
    "La clause de non-concurrence n'a pas de contrepartie financière — la corriger",
    output_path="contrat_révisé.docx",
)
# → ouvrir dans Word ou LibreOffice → Accept / Rejeter chaque modification
```

Pas de régénération du document entier. L'agent modifie chirurgicalement les clauses concernées et injecte les balises Word natives (`<w:del>` / `<w:ins>`).

### Analyse structurée d'un bail commercial (exemple droit français)

```python
from legolagents import LegalDocumentAgent
from legolagents.playbooks import PlaybookLibrary

agent    = LegalDocumentAgent(model=model, jurisdiction="France")
playbook = PlaybookLibrary.get("bail_commercial")  # 14 points L145 C.com.
agent.run(f"Document : bail.docx\n\n{playbook.to_prompt(output_path='analyse.docx')}")
# → rapport Word : clause résolutoire sans mise en demeure ⚠️, taxe foncière illégale ⚠️…
```

### Comparaison de N contrats sur M critères

```python
agent.compare(
    ["bail_A.docx", "bail_B.docx", "bail_C.docx"],
    criteres=["Durée", "Indexation", "Clause résolutoire", "Charges locataires"],
    output_path="due_diligence.docx",
)
# → matrice avec signalement automatique des clauses à risque
```

---

## Brancher votre propre base de données

legolagents définit des interfaces — vous implémentez le `forward()` pour votre backend, dans n'importe quelle langue ou juridiction :

```python
from legolagents.tools.retrieval import JurisprudenceSearchTool

class MonOutil(JurisprudenceSearchTool):
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        resultats = ma_base.rechercher(query)
        return self.format_results(resultats)
```

Fonctionne avec Qdrant, Elasticsearch, une API REST, ou n'importe quel MCP juridique.

---

## Exemple : démarrer sur le marché français (SmartLawyer MCP)

Pas encore de base jurisprudentielle ? Le [MCP SmartLawyer](https://mcp.smartlawyer.ai) donne accès à **1M+ décisions françaises** et **13 outils Legal Graph** — pratique pour prototyper un projet legolagents sans rien construire. **Mode développeur gratuit.**

```bash
pip install 'legolagents[mcp]'
```

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerMCP

with SmartLawyerMCP(api_key="sk-sl-votre-cle") as outils:
    agent = LegalResearchAgent(tools=outils, model=model, jurisdiction="France")
    agent.run("L'arrêt 17-19.860 est-il toujours valide ?")
```

→ [Obtenir une clé gratuite](https://smartlawyer.ai) · [Documentation MCP](https://smartlawyer.ai/mcp/)

Ce connecteur est un exemple parmi d'autres MCP juridiques possibles (voir "Brancher votre propre base" ci-dessus) — le cœur du framework n'en dépend pas.

---

## Playbooks disponibles (exemples droit français)

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `bail_commercial` | Bail commercial | 14 (L145-1 C.com.) |
| `contrat_travail` | Contrat CDI/CDD | 12 (Code du travail) |
| `pacte_associes` | Pacte d'associés | 15 |
| `convention_credit` | Convention de crédit | 18 |

Ces playbooks sont fournis prêts à l'emploi pour le marché français ; écrivez les vôtres avec `Playbook`/`PlaybookLibrary` pour toute autre juridiction ou type de document.

---

## Contribuer

Issues et PR bienvenus — playbooks supplémentaires, nouvelles interfaces d'outils, support d'autres juridictions (Belgique, Suisse, Québec, common law…).

---

## Licence

Apache 2.0 · Construit par [SmartLawyer AI](https://smartlawyer.ai)
