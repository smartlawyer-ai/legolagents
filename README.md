<div align="center">
  <img src="assets/legolagents.svg" alt="legolagents" width="800"/>
</div>

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Python](https://img.shields.io/pypi/pyversions/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Licence Apache 2.0](https://img.shields.io/badge/licence-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-51%20passed-brightgreen.svg)]()
[![Basé sur smolagents](https://img.shields.io/badge/basé%20sur-smolagents-orange.svg)](https://github.com/huggingface/smolagents)

**Assemblez des agents juridiques comme des briques — extension de [smolagents](https://github.com/huggingface/smolagents) pour le droit français**

</div>

---

## Qu'est-ce que legolagents ?

`legolagents` est un framework Python pour construire des agents IA spécialisés en droit français, en empilant des briques sur [smolagents](https://github.com/huggingface/smolagents).

**Ce que le framework apporte :**
- **Agents spécialisés** avec stratégies de raisonnement juridique FR intégrées (YAML configurable)
- **Interfaces d'outils abstraites** — branchez votre propre base de données jurisprudentielle
- **Outils documentaires concrets** — dont le suivi des modifications Word natif (`<w:ins>`/`<w:del>`)
- **Bibliothèque de playbooks** — workflows structurés pour les documents juridiques courants
- **Agnostique du backend** — Qdrant, Elasticsearch, API REST, MCP : tout fonctionne

```bash
pip install legolagents
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        smolagents                            │
│           ToolCallingAgent · Tool · Memory · Models          │
└──────────────────────────┬───────────────────────────────────┘
                           │  étend
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                       legolagents                            │
│                                                              │
│  ┌──────────────────┐  ┌─────────────────┐  ┌────────────┐  │
│  │     Agents       │  │  Outils         │  │ Playbooks  │  │
│  │ ──────────────── │  │ ─────────────── │  │ ────────── │  │
│  │ LegalAgent       │  │ Jurisprudence   │  │ Bail comm. │  │
│  │ LegalResearch    │  │ Graphe légal    │  │ Contrat    │  │
│  │ FicheAnalyst     │  │ Articles de loi │  │ travail    │  │
│  │ LegalDocument    │  │ Documents (*)   │  │ SHA, crédit│  │
│  └──────────────────┘  └─────────────────┘  └────────────┘  │
│  (*) ReadDocument · GenerateDocx · TrackedChanges · Tabular  │
│                                                              │
│  Stratégies de raisonnement en YAML — base_legal_fr.yaml     │
└──────────────────────────┬───────────────────────────────────┘
                           │  les outils abstraits sont implémentés par
             ┌─────────────┴──────────────┐
             │                            │
  ┌──────────▼──────────┐    ┌────────────▼───────────┐
  │   Votre backend     │    │  MCP SmartLawyer        │
  │   (Qdrant, ES, API) │    │  13 outils Legal Graph  │
  │   class MonOutil(   │    │  1M+ arrêts français    │
  │     JurisTool):     │    │  mcp.smartlawyer.ai     │
  │     def forward():  │    │  → voir section Données │
  └─────────────────────┘    └────────────────────────┘
```

---

## Démarrage rapide

### 1 — Recherche jurisprudentielle (question libre)

```python
from legolagents import LegalResearchAgent
from legolagents.tools.retrieval import JurisprudenceSearchTool
from smolagents import LiteLLMModel

# Implémenter l'outil pour votre source de données
class MonOutilRecherche(JurisprudenceSearchTool):
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        resultats = ma_base.rechercher(query, domaine=domaine)
        return self.format_results(resultats)   # formatage FR intégré

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
agent = LegalResearchAgent(
    tools        = [MonOutilRecherche()],
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

fiche = {
    "id": "abc-123", "jurisdiction": "cc", "chamber": "soc",
    "decision_date": "2022-09-11", "number": "21-14.027",
    "solution": "Rejet", "domaine": "droit social",
    "importance_score": 92,
}

agent = FicheAnalystAgent(
    tools = [MonOutilRecherche(), MonOutilGraphe()],
    model = model,
    fiche = fiche,   # contexte injecté automatiquement dans le prompt
)

result = agent.run("Cet arrêt a-t-il été renversé ? Quelle est sa portée réelle ?")
```

### 3 — Révision de contrat avec suivi des modifications Word

```python
from legolagents import LegalDocumentAgent

# Les outils documentaires sont concrets — aucune implémentation requise
agent = LegalDocumentAgent(model=model, legal_domain="droit social")

# Révision → fichier Word avec Accept/Rejeter natif (Word & LibreOffice)
agent.review(
    "contrat.docx",
    "Réduire la clause de non-concurrence à 12 mois "
    "et ajouter une contrepartie financière obligatoire",
    output_path="contrat_révisé.docx",
)

# Comparaison de N contrats sur M critères → tableau + rapport DOCX
agent.compare(
    ["bail_A.docx", "bail_B.docx", "bail_C.docx"],
    criteres=["Durée", "Indexation loyer", "Clause résolutoire"],
    output_path="comparaison.docx",
)
```

### 4 — Playbooks (analyse structurée)

```python
from legolagents.playbooks import PlaybookLibrary

playbook = PlaybookLibrary.get("bail_commercial")   # 14 points L145 C.com.
agent.run(f"Document : bail.docx\n\n{playbook.to_prompt()}")
```

---

## Agents

| Agent | Point d'entrée | Workflow de raisonnement |
|---|---|---|
| `LegalAgent` | N'importe quelle tâche | Raisonnement juridique FR de base |
| `LegalResearchAgent` | Question juridique | Grands arrêts → Recherche → Validité → Graphe → Articles |
| `FicheAnalystAgent` | Dict d'un arrêt | Situer → Valider → Traverser → Comparer |
| `LegalDocumentAgent` | Fichier document | Lire → Analyser/Réviser → Vérifier |

Tous les agents : `planning_interval=2`, stratégie YAML, injection `legal_domain` automatique.

---

## Outils

### Abstraits — à implémenter pour votre backend

```python
from legolagents.tools.retrieval import JurisprudenceSearchTool

class MonOutil(JurisprudenceSearchTool):
    def forward(self, query: str, domaine: str = "", limit: int = 5) -> str:
        # votre logique ici
        return self.format_results(resultats)  # format FR intégré
```

| Outil | Interface |
|---|---|
| `JurisprudenceSearchTool` | Recherche sémantique |
| `FindLandmarkCasesTool` | Grands arrêts par importance |
| `FindRelatedCasesTool` | Navigation citant/cité |
| `CheckDecisionValidityTool` | Vérification superseded |
| `GetLegalGraphTool` | Graphe légal complet |
| `TraverseGraphTool` | Traversal N niveaux |
| `FindRevirementsTool` | Détection revirements |
| `GetArticleTool` | Article de loi |
| `SearchArticlesTool` | Recherche dans les codes |

### Concrets — prêts à l'emploi

| Outil | Ce qu'il fait |
|---|---|
| `ReadDocumentTool` | Lecture PDF / DOCX → texte (tableaux inclus) |
| `GenerateDocxTool` | Génération Word structurée |
| `TrackedChangesTool` | Suivi des modifications natif Word (`<w:del>`/`<w:ins>`) |
| `TabularAnalysisTool` | Matrice N documents × M critères |

---

## TrackedChangesTool — le bijou

Injecte directement `<w:del>` / `<w:ins>` dans le XML du DOCX — sans Word, sans service externe. L'utilisateur voit Accept/Rejeter dans Word ou LibreOffice.

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
```

---

## Playbooks

| Identifiant | Document | Points |
|---|---|---|
| `bail_commercial` | Bail commercial (L145-1 C.com.) | 14 |
| `contrat_travail` | Contrat CDI/CDD | 12 |
| `pacte_associes` | Pacte d'associés / actionnaires | 15 |
| `convention_credit` | Convention de crédit | 18 |

```python
from legolagents.playbooks.base import Playbook, PlaybookLibrary, PlaybookPoint

# Créer et enregistrer un playbook personnalisé
PlaybookLibrary.register(Playbook(
    id="cgv", title="Analyse de CGV",
    document_type="conditions générales de vente",
    legal_domain="droit de la consommation",
    points=[
        PlaybookPoint(1, "Identification du vendeur",
            "Dénomination, SIREN, adresse — L111-1 C.conso.",
            flag_conditions=["informations manquantes"]),
    ],
))
```

---

## Stratégie de raisonnement

Tous les agents suivent ce protocole (configurable dans `prompts/base_legal_fr.yaml`) :

```
1. Qualification juridique    Identifier le vrai problème de droit
2. Validité temporelle        L'arrêt est-il superseded ? (OBLIGATOIRE)
3. Hiérarchie                 Arrêt de principe / d'espèce / isolé
4. Traversal du graphe        Remonter les citations sur 2+ niveaux
5. Tensions inter-chambres    Signaler toute divergence
6. Fondement textuel          Relier jurisprudence → article applicable
```

Niveau de certitude sur chaque citation :

| Marqueur | Signification |
|---|---|
| `✅ Droit établi` | Jurisprudence constante, publiée, non superseded |
| `⚡ Tendance` | Arrêts récents, doctrine pas encore fixée |
| `⚠️ Isolé` | Arrêt unique ou minoritaire |
| `❌ Superseded` | Renversé — ne pas citer comme droit positif |

---

## Obtenir des données jurisprudentielles

Si vous n'avez pas de backend jurisprudentiel, le [MCP SmartLawyer](https://mcp.smartlawyer.ai) expose **1M+ arrêts français** et **13 outils Legal Graph** directement utilisables avec legolagents.

**Mode développeur gratuit** — [obtenir une clé API](https://smartlawyer.ai)

```bash
pip install 'legolagents[mcp]'
```

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerMCP
from smolagents import LiteLLMModel

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")

with SmartLawyerMCP(api_key="sk-sl-votre-cle") as outils:
    # 13 outils Legal Graph disponibles immédiatement
    agent  = LegalResearchAgent(tools=outils, model=model)
    result = agent.run("Quels sont les arrêts de principe sur le licenciement pour faute grave ?")
```

Les 13 outils : `search_jurisprudences`, `get_fiche`, `get_legal_graph`, `find_arrets_de_principe`, `find_revirements`, `superseded_chain`, `get_procedure_lineage`, `find_related_by_graph`, `search_by_article`, `get_cited_by`, `get_article`, `search_articles`, `get_filters`.

---

## Tests

```bash
pytest tests/   # 51 tests, ~0.3s
```

---

## Dépendances

| Paquet | Version |
|---|---|
| `smolagents` | ≥ 1.14 |
| `pyyaml` | ≥ 6.0 |
| `pdfplumber` | ≥ 0.11 |
| `python-docx` | ≥ 1.1 |
| `lxml` | ≥ 5.0 |
| `diff-match-patch` | ≥ 20230430 |

---

## Contribuer

Issues et PR bienvenus.

- Nouveaux playbooks (CGV, PV d'AG, protocole d'accord, RGPD…)
- Nouvelles interfaces d'outils (notarial, fiscal…)
- Juridictions francophones : Belgique, Suisse, Québec
- Tests edge cases `TrackedChangesTool`

---

## Licence

Apache 2.0 — voir [LICENSE](LICENSE)

---

*Construit par [SmartLawyer AI](https://smartlawyer.ai)*
