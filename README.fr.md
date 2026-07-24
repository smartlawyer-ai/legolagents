<div align="center">
  <img src="assets/legolagents_banner.png" alt="legolagents" width="800"/>

[![PyPI](https://img.shields.io/pypi/v/legolagents.svg)](https://pypi.org/project/legolagents/)
[![Licence Apache 2.0](https://img.shields.io/badge/licence-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-106%20passed-brightgreen.svg)]()
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

## Le pattern

```python
from legolagents import SourceType, Authority, LegalSource

statute = LegalSource(ref="L1235-3", kind=SourceType.STATUTE, authority=Authority.BINDING)
case    = LegalSource.from_payload(
    {"number": "21-14.027", "cited_by_count": 42, "importance_score": 90},
    kind=SourceType.CASE_LAW, authority=Authority.PERSUASIVE,
)
case.relates_to(statute, how="interprets")

print(case.to_markdown())
# **[case_law] 21-14.027** (💬 persuasive) ✅ Droit établi
#   ↳ interprets L1235-3
```

Tous les systèmes juridiques du monde combinent des sources codifiées (lois, règlements, traités) et de la jurisprudence — ce qui change réellement d'une juridiction à l'autre, c'est l'**autorité**, pas le **type**. Une décision de justice est `PERSUASIVE` en droit civil, `BINDING` en common law — même `SourceType.CASE_LAW` dans les deux cas.

En usage réel, on ne construit pas `LegalSource` un par un comme ici — une vraie intégration en a des milliers. `LegalSource.from_payload()` / `from_payloads()` mappent les enregistrements bruts de votre source de données en masse, et l'autorité/la certitude/les relations viennent des métadonnées de vos données elles-mêmes (contraignant ou persuasif, `cited_by_count`, `superseded_by`…), pas d'une étape séparée qu'on exécute après coup. Voir [`legolagents.ontology`](src/legolagents/ontology.py) pour le modèle complet (types de sources, niveaux d'autorité, et les types de relations — cite, interprète, applique, distingue, renverse, supersède, met en œuvre).

---

## Démarrage rapide (n'importe quelle juridiction)

Un agent juridique travaille sur un **corpus** — un corps de droit (ex : "RGPD", "Code du travail français", "droit des sociétés du Delaware"). Branchez le vôtre en implémentant quatre méthodes — `get_law`, `search_law`, `get_jp`, `search_jp` — et les tools de l'agent sont construits pour vous, sans classe `Tool` à écrire :

```python
from legolagents import LegalResearchAgent, LegalCorpus, LegalSource, SourceType, Authority
from smolagents import LiteLLMModel

class MonCorpus(LegalCorpus):
    name         = "RGPD"
    jurisdiction = "UE"

    def get_law(self, ref):
        payload = ma_base.recuperer_article(ref)
        return LegalSource.from_payload(payload, kind=SourceType.REGULATION, authority=Authority.BINDING)

    def search_law(self, query, limit=5):
        return LegalSource.from_payloads(ma_base.rechercher_articles(query, limit),
                                          kind=SourceType.REGULATION, authority=Authority.BINDING)

    def get_jp(self, ref): ...             # même principe, kind=SourceType.CASE_LAW
    def search_jp(self, query, limit=5): ...

model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-5")
agent = LegalResearchAgent(corpus=MonCorpus(), model=model)   # jurisdiction/legal_domain déduits du corpus
print(agent.run("Quelles sont les obligations d'un sous-traitant au titre de l'article 28 du RGPD ?"))
```

C'est toute la surface d'intégration. L'agent vérifie automatiquement la validité des décisions, remonte le graphe de citations, et répond avec un niveau de certitude : `✅ Droit établi`, `⚡ Tendance`, `⚠️ Isolé`, ou `❌ Superseded`.

Pas encore de base jurisprudentielle ? Voir la section [Exemple : démarrer sur le marché français](#exemple--démarrer-sur-le-marché-français-smartlawyer-mcp) plus bas — un `LegalCorpus` prêt à l'emploi pour tester le framework sans rien construire.

---

## Playbooks — un workflow en une ligne

```python
from legolagents.playbooks import Playbook

Playbook.quick("Revue de NDA", points=[
    "Parties — qui sont les parties contractantes ?",
    "Durée — combien de temps dure l'obligation de confidentialité ?",
    "Exceptions — quelles informations sont exclues de la confidentialité ?",
]).register()
```

`Playbook.quick(...).register()` construit et enregistre un workflow d'analyse structuré en un seul appel — les points acceptent de simples chaînes `"Label — description"`, l'`id` et le type de document sont déduits du titre. Il suffit ensuite de le passer à n'importe quel agent documentaire :

```python
from legolagents import LegalDocumentAgent
from legolagents.playbooks import PlaybookLibrary

agent    = LegalDocumentAgent(model=model)
playbook = PlaybookLibrary.get("revue_de_nda")
agent.run(f"Document : mon_nda.docx\n\n{playbook.to_prompt()}")
```

Pour un contrôle complet (conditions de signalement, format de sortie personnalisé, instructions supplémentaires), `Playbook` et `PlaybookPoint` restent disponibles directement — voir les playbooks droit français ci-dessous en exemple.

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

`LegalCorpus` ne se préoccupe pas de ce qu'il y a derrière — Qdrant, Elasticsearch, une API REST, une base SQL, ou n'importe quel MCP juridique. Implémentez les quatre méthodes contre votre backend et retournez des `LegalSource` (construits en masse avec `from_payload`/`from_payloads`, voir ci-dessus).

Si vous préférez ne pas implémenter de corpus, `tools=[...]` accepte toujours n'importe quelle liste de `Tool` smolagents directement — `corpus=` et `tools=` peuvent aussi se combiner (par ex. un corpus pour la recherche plus des tools documentaires supplémentaires).

---

## Exemple : démarrer sur le marché français (SmartLawyer MCP)

Pas encore de base jurisprudentielle ? Le [MCP SmartLawyer](https://mcp.smartlawyer.ai) donne accès à **1M+ décisions françaises** et **13 outils Legal Graph** — pratique pour prototyper un projet legolagents sans rien construire. **Mode développeur gratuit.**

```bash
pip install 'legolagents[mcp]'
```

```python
from legolagents import LegalResearchAgent
from legolagents.mcp import SmartLawyerCorpus

with SmartLawyerCorpus(api_key="sk-sl-votre-cle") as corpus:   # jurisdiction="France" par défaut
    agent = LegalResearchAgent(corpus=corpus, model=model)
    agent.run("L'arrêt 17-19.860 est-il toujours valide ?")
```

`SmartLawyerCorpus` implémente `LegalCorpus` par-dessus les tools MCP de SmartLawyer, et expose aussi ses tools de graphe/détection de revirements (`find_revirements`, `superseded_chain`, `get_legal_graph`…) en plus des quatre standards. Préférez `SmartLawyerMCP` (liste brute de tools MCP, `tools=` au lieu de `corpus=`) si vous voulez les tools non mappés vers `LegalSource`.

→ [Obtenir une clé gratuite](https://smartlawyer.ai) · [Documentation MCP](https://smartlawyer.ai/mcp/)

Ce connecteur est un exemple parmi d'autres MCP juridiques possibles (voir "Brancher votre propre base" ci-dessus) — le cœur du framework n'en dépend pas.

Envie d'une vraie interface de chat plutôt qu'un script ? [`examples/06_chainlit_smartlawyer_chatbot.py`](examples/06_chainlit_smartlawyer_chatbot.py) branche le même agent dans un chatbot [Chainlit](https://chainlit.io) fonctionnel en une quinzaine de lignes.

---

## Playbooks disponibles (18, sur 5 juridictions)

Les playbooks sont organisés par **juridiction, pas par langue** — le français est parlé en France, en Belgique, en Suisse, au Québec… chacun avec son propre droit ; les regrouper par système juridique (`playbooks/library/fr/`, `us/`, `uk/`, `de/`, `eu/`) garde le contenu de chaque playbook cohérent. Filtrez-les avec `PlaybookLibrary.list(jurisdiction="us")` / `PlaybookLibrary.jurisdictions()`.

**France** (`fr`) — Code du travail / Code de commerce / Code civil :

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `bail_commercial` | Bail commercial | 14 (L145-1 C.com.) |
| `contrat_travail` | Contrat CDI/CDD | 12 (Code du travail) |
| `pacte_associes` | Pacte d'associés | 15 |
| `convention_credit` | Convention de crédit | 18 |

**États-Unis** (`us`) — droit fédéral + variations Delaware/Californie/New York :

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `us_nda` | NDA (mutuel ou unilatéral) | 13 (DTSA, clauses de non-concurrence selon l'État) |
| `us_employment_agreement` | Contrat de travail (at-will) | 12 (FLSA, non-concurrence selon l'État) |
| `us_commercial_lease` | Bail commercial | 13 (droit locatif selon l'État) |
| `us_saas_msa` | Contrat SaaS / MSA | 13 (UCC, lois de confidentialité des États, clauses IA) |

**Royaume-Uni** (`uk`) — droit anglais (England & Wales) :

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `uk_nda` | NDA / accord de confidentialité | 12 (Coco v Clark, Trade Secrets Regs 2018) |
| `uk_employment_contract` | Contrat de travail | 13 (Employment Rights Act 1996/2025) |
| `uk_commercial_lease` | Bail commercial | 13 (Landlord and Tenant Act 1954 Part II) |
| `uk_saas_msa` | Contrat SaaS / MSA | 13 (UCTA 1977, UK GDPR) |

**Allemagne** (`de`) — Bundesrepublik Deutschland, contenu en allemand :

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `de_geheimhaltungsvereinbarung` | NDA | 12 (GeschGehG, § 307 BGB) |
| `de_arbeitsvertrag` | Contrat de travail | 13 (§ 622 BGB, § 74 HGB, KSchG) |
| `de_gewerbemietvertrag` | Bail commercial | 13 (§ 550 BGB Schriftform) |

**UE** (`eu`) — contenu réglementaire supranational, transfrontalier :

| Identifiant | Document | Points d'analyse |
|---|---|---|
| `eu_data_processing_agreement` | Convention de traitement de données | 13 (RGPD Art. 28) |
| `eu_gdpr_compliance_review` | Revue de conformité RGPD | 14 (RGPD + interaction AI Act) |
| `eu_distribution_agreement` | Accord de distribution / vertical | 13 (VBER 2022/720) |

Ces playbooks sont fournis prêts à l'emploi ; écrivez les vôtres avec `Playbook.quick(...)` (voir ci-dessus) pour toute autre juridiction ou type de document. Les références légales reflètent le droit tel qu'il a été recherché au moment de la rédaction — vérifiez toujours leur statut actuel avant de vous y fier pour un cas réel.

---

## Contribuer

Issues et PR bienvenus — playbooks supplémentaires, nouvelles interfaces d'outils, support d'autres juridictions (Belgique, Suisse, Québec, common law…).

---

## Licence

Apache 2.0 · Construit par [SmartLawyer AI](https://smartlawyer.ai)
