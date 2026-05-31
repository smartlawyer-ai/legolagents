# legolagents

**Extension de [smolagents](https://github.com/huggingface/smolagents) pour le droit français**

[![PyPI version](https://img.shields.io/pypi/v/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Python](https://img.shields.io/pypi/pyversions/legolagents.svg)](https://pypi.org/project/legolagents/)
[![License](https://img.shields.io/badge/licence-Apache%202.0-blue.svg)](LICENSE)
[![Basé sur smolagents](https://img.shields.io/badge/basé%20sur-smolagents-orange.svg)](https://github.com/huggingface/smolagents)

---

## Qu'est-ce que legolagents ?

`legolagents` est une extension de [smolagents](https://github.com/huggingface/smolagents) qui ajoute une **couche de raisonnement juridique** pour le droit français. Comme des briques Lego sur smolagents, on assemble des agents spécialisés, des outils juridiques et des playbooks pour construire des assistants légaux.

- **Agents spécialisés** — stratégies de raisonnement juridique FR intégrées (YAML)
- **Interfaces d'outils abstraites** — jurisprudence, graphe légal, articles de loi
- **Outils documentaires concrets** — suivi des modifications Word natif (Accept/Rejeter)
- **Bibliothèque de playbooks** — workflows structurés pour les documents juridiques courants
- **Agnostique du backend** — branchez Qdrant, Elasticsearch, ou n'importe quelle API

---

## Démarrage immédiat avec le MCP SmartLawyer

> **Le chemin le plus court** : branchez directement le [Legal Graph SmartLawyer](https://mcp.smartlawyer.ai) et obtenez **13 outils juridiques** sans rien implémenter.
>
> **Mode développeur gratuit** — obtenez votre clé sur [smartlawyer.ai](https://smartlawyer.ai) → Paramètres → Clés API

```bash
pip install legolagents 'smolagents[mcp]'
```

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")

with SmartLawyerMCP(api_key="sk-sl-votre-cle") as outils:
    agent  = LegalResearchAgent(tools=outils, model=model)
    result = agent.run(
        "L'arrêt 17-19.860 est-il toujours valide ? "
        "Y a-t-il eu un revirement depuis ?"
    )
    print(result)
```

Le MCP SmartLawyer expose **13 outils Legal Graph** : `search_jurisprudences`, `get_fiche`, `get_legal_graph`, `find_arrets_de_principe`, `find_revirements`, `superseded_chain`, `get_procedure_lineage`, `find_related_by_graph`, `search_by_article`, `get_cited_by`, `get_article`, `search_articles`, `get_filters`.

→ Documentation complète : [mcp.smartlawyer.ai](https://mcp.smartlawyer.ai)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         smolagents                              │
│              (HuggingFace — ToolCallingAgent, Tool…)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │  étend
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        legolagents                              │
│   ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│   │   Agents        │  │  Outils          │  │  Playbooks   │  │
│   │  ─────────────  │  │  ─────────────   │  │  ─────────── │  │
│   │  LegalAgent     │  │  Jurisprudence   │  │  bail comm.  │  │
│   │  Research       │  │  Graphe légal    │  │  contrat     │  │
│   │  FicheAnalyst   │  │  Articles        │  │  travail     │  │
│   │  Document       │  │  Documents (*)   │  │  SHA, crédit │  │
│   └─────────────────┘  └──────────────────┘  └──────────────┘  │
│   (*) LireDocument · GénérerDocx · SuiviModifs · Tabulaire     │
│                                                                 │
│   Stratégies de raisonnement en YAML (base_legal_fr, …)        │
└───────────────────────────┬─────────────────────────────────────┘
                            │  implémentent les outils abstraits
              ┌─────────────┴──────────────┐
              │                            │
   ┌──────────▼──────────┐    ┌────────────▼────────────┐
   │  MCP SmartLawyer    │    │    Votre projet          │
   │  13 outils Legal    │    │  class MonOutilRecherche(│
   │  Graph — GRATUIT    │    │    JurisprudenceTool):   │
   │  mcp.smartlawyer.ai │    │    def forward(…): …    │
   └─────────────────────┘    └─────────────────────────┘
```

---

## Installation

```bash
pip install legolagents
```

Avec support MCP (recommandé) :

```bash
pip install 'legolagents[mcp]'
```

---

## Démarrage rapide

### 1 — Recherche jurisprudentielle (question libre)

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")

with SmartLawyerMCP(api_key="sk-sl-votre-cle") as outils:
    agent  = LegalResearchAgent(
        tools        = outils,
        model        = model,
        legal_domain = "droit social",
        depth        = "standard",   # "shallow" | "standard" | "deep"
    )
    result = agent.run(
        "Quelle est la jurisprudence actuelle sur le barème Macron "
        "et sa compatibilité avec la Convention 158 de l'OIT ?"
    )
```

### 2 — Analyse d'un arrêt précis

```python
from legolagents import FicheAnalystAgent
from legolagents.mcp import SmartLawyerMCP

fiche = {
    "id": "abc-123", "jurisdiction": "cc", "chamber": "soc",
    "decision_date": "2022-09-11", "number": "21-14.027",
    "solution": "Rejet", "domaine": "droit social",
    "probleme": "Le barème Macron est-il compatible avec la Convention 158 OIT ?",
    "importance_score": 92,
}

with SmartLawyerMCP(api_key="sk-sl-votre-cle") as outils:
    agent = FicheAnalystAgent(
        tools = outils,
        model = model,
        fiche = fiche,   # contexte injecté automatiquement dans le prompt
    )
    result = agent.run(
        "Cet arrêt a-t-il été renversé ? "
        "Quels arrêts postérieurs s'y réfèrent ?"
    )
```

### 3 — Révision de contrat avec suivi des modifications Word

```python
from legolagents import LegalDocumentAgent

agent = LegalDocumentAgent(model=model, legal_domain="droit social")

# Révision avec Accept/Rejeter dans Word ou LibreOffice
agent.review(
    "contrat.docx",
    "Réduire la clause de non-concurrence à 12 mois "
    "et ajouter une contrepartie financière obligatoire "
    "(Soc. 10 juill. 2002, n°00-45135)",
    output_path="contrat_révisé.docx",
)

# Comparaison de N contrats sur M critères
agent.compare(
    ["bail_A.docx", "bail_B.docx", "bail_C.docx"],
    criteres=["Durée", "Indexation loyer", "Clause résolutoire"],
    output_path="comparaison.docx",
)
```

### 4 — Playbooks (analyse structurée de documents)

```python
from legolagents.playbooks import PlaybookLibrary

playbook = PlaybookLibrary.get("bail_commercial")   # 14 points d'analyse
prompt   = playbook.to_prompt(output_path="analyse.docx")

agent = LegalDocumentAgent(model=model)
agent.run(f"Document : bail.docx\n\n{prompt}")
```

### 5 — Brancher votre propre backend

```python
from legolagents.tools.retrieval import JurisprudenceSearchTool

class MonOutilRecherche(JurisprudenceSearchTool):
    def __init__(self, client_es, index: str):
        super().__init__()
        self.es    = client_es
        self.index = index

    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        hits    = self.es.search(index=self.index, body={"query": {"match": {"texte": query}}})
        results = [h["_source"] for h in hits["hits"]["hits"]]
        return self.format_results(results)   # formatage FR intégré
```

---

## Agents

| Agent | Point d'entrée | Workflow de raisonnement |
|---|---|---|
| `LegalAgent` | N'importe quelle tâche | Raisonnement juridique FR de base |
| `LegalResearchAgent` | Question juridique libre | Grands arrêts → Recherche → Validité → Graphe → Articles → Synthèse |
| `FicheAnalystAgent` | Données d'un arrêt | Situer → Valider → Traverser → Comparer |
| `LegalDocumentAgent` | Fichier document | Lire → Analyser/Réviser → Vérifier |

Tous les agents :
- Re-planifient toutes les 2 étapes (`planning_interval=2`)
- Chargent leur stratégie depuis YAML (`prompts/`)
- Injectent automatiquement `legal_domain` dans le contexte

---

## Outils

### Abstraits (à implémenter pour votre backend)

| Outil | Rôle |
|---|---|
| `JurisprudenceSearchTool` | Recherche sémantique dans la jurisprudence |
| `FindLandmarkCasesTool` | Grands arrêts par score d'importance |
| `FindRelatedCasesTool` | Navigation citant / cité par |
| `CheckDecisionValidityTool` | Vérification validité (superseded ?) |
| `SearchByArticleTool` | Arrêts appliquant un article précis |
| `GetLegalGraphTool` | Graphe légal complet d'un arrêt |
| `TraverseGraphTool` | Traversal en profondeur (N niveaux) |
| `FindRevirementsTool` | Détection des revirements jurisprudentiels |
| `GetArticleTool` | Texte d'un article de loi |
| `SearchArticlesTool` | Recherche sémantique dans les codes |

### Concrets (prêts à l'emploi, sans implémentation)

| Outil | Ce qu'il fait |
|---|---|
| `ReadDocumentTool` | Lecture PDF / DOCX → texte (tableaux inclus) |
| `GenerateDocxTool` | Génération de document Word structuré |
| `TrackedChangesTool` | Suivi des modifications Word natif (Accept/Rejeter) |
| `TabularAnalysisTool` | Matrice N documents × M critères |

---

## TrackedChangesTool — le bijou

Injecte directement des balises `<w:del>` / `<w:ins>` dans le XML du DOCX — sans service externe, sans installation de Word.

```python
from legolagents import TrackedChangesTool

TrackedChangesTool().forward(
    input_path  = "contrat.docx",
    edits = [{
        "find":           "dans un délai de 30 jours",
        "replace":        "dans un délai de 15 jours ouvrés",
        "context_before": "le prestataire s'engage à livrer",
        "reason":         "Alignement pratique de marché",
    }],
    output_path = "contrat_suivi.docx",
)
# → Ouvrir dans Word ou LibreOffice → Accept / Rejeter chaque modification
```

---

## Playbooks

Workflows d'analyse structurée pour les documents juridiques français :

| Identifiant | Type de document | Points |
|---|---|---|
| `bail_commercial` | Bail commercial (L145-1 C.com.) | 14 |
| `contrat_travail` | Contrat de travail CDI/CDD | 12 |
| `pacte_associes` | Pacte d'associés / actionnaires | 15 |
| `convention_credit` | Convention de crédit | 18 |

```python
from legolagents.playbooks import PlaybookLibrary

# Lister les playbooks disponibles
print(PlaybookLibrary.list())

# Créer un playbook personnalisé
from legolagents.playbooks.base import Playbook, PlaybookPoint

PlaybookLibrary.register(Playbook(
    id            = "cgv",
    title         = "Analyse de CGV",
    document_type = "conditions générales de vente",
    legal_domain  = "droit de la consommation",
    points=[
        PlaybookPoint(1, "Identification du vendeur",
            "Dénomination, SIREN, adresse — L111-1 C.conso.",
            flag_conditions=["informations manquantes"]),
    ],
))
```

---

## Stratégie de raisonnement

Tous les agents suivent ce protocole obligatoire (configurable en YAML dans `prompts/`) :

```
1. Qualification juridique    Identifier le vrai problème de droit
2. Validité temporelle        L'arrêt est-il toujours en vigueur ? (superseded OBLIGATOIRE)
3. Hiérarchie                 Arrêt de principe / arrêt d'espèce / arrêt isolé
4. Traversal du graphe légal  Remonter les citations sur au moins 2 niveaux
5. Tensions inter-chambres    Signaler toute divergence entre chambres
6. Fondement textuel          Toujours relier la jurisprudence à l'article applicable
```

Niveau de certitude systématique sur chaque citation :
- `✅ Droit établi` — jurisprudence constante, publiée, non superseded
- `⚡ Tendance` — arrêts récents, doctrine pas encore fixée
- `⚠️ Isolé` — arrêt unique ou minoritaire
- `❌ Superseded` — renversé, ne plus citer comme droit positif

---

## Dépendances

| Paquet | Version | Rôle |
|---|---|---|
| `smolagents` | ≥ 1.14 | Framework agent de base |
| `pyyaml` | ≥ 6.0 | Chargement des stratégies YAML |
| `pdfplumber` | ≥ 0.11 | Extraction PDF |
| `python-docx` | ≥ 1.1 | Lecture / génération DOCX |
| `lxml` | ≥ 5.0 | Suivi des modifications XML |
| `diff-match-patch` | ≥ 20230430 | Diff au niveau du mot |

---

## Contribuer

Issues et PR bienvenus.

Axes prioritaires :
- Nouveaux playbooks (CGV, PV d'AG, protocole d'accord, RGPD…)
- Nouvelles interfaces d'outils (notarial, fiscal…)
- Support d'autres juridictions francophones (Belgique, Suisse, Québec)
- Tests `TrackedChangesTool` sur des cas complexes (runs imbriqués)

---

## Licence

Apache 2.0 — voir [LICENSE](LICENSE)

---

*Construit par [SmartLawyer AI](https://smartlawyer.ai) — la plateforme d'IA juridique française.*
