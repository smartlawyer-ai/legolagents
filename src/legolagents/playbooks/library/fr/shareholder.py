"""Playbook : Analyse de Pacte d'Associés / Pacte d'Actionnaires (droit FR)"""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

SHAREHOLDER_AGREEMENT = Playbook(
    id            = "pacte_associes",
    title         = "Analyse de Pacte d'Associés / Actionnaires",
    document_type = "pacte d'associés ou d'actionnaires",
    legal_domain  = "droit des sociétés",
    jurisdiction  = "fr",
    output_format = "docx",
    points=[
        PlaybookPoint(1,  "Parties et participations",
            "Identité des signataires, nombre d'actions/parts, pourcentage du capital et des droits de vote. "
            "Nature des actions (ordinaires, préférentielles, ADP). Tableau de capitalisation."),
        PlaybookPoint(2,  "Gouvernance",
            "Composition du conseil/comité de direction. Droits de nomination par seuil de détention. "
            "Quorum, majorité qualifiée, droit de veto. Président, DG.",
            flag_conditions=["droit de veto unilatéral", "quorum trop élevé risquant le blocage"]),
        PlaybookPoint(3,  "Décisions réservées",
            "Matières requérant une majorité renforcée ou l'accord de certains associés. "
            "Seuils de déclenchement et conséquences en cas de désaccord.",
            flag_conditions=["liste trop longue créant un risque de blocage permanent"]),
        PlaybookPoint(4,  "Préemption sur cessions",
            "Droit de préemption : bénéficiaires, délai d'exercice, prix (même conditions ou valorisation). "
            "Conformité à l'art. L227-14 C.com. pour les SAS.",
            flag_conditions=["prix de préemption différent du prix de cession", "délai d'exercice trop court"]),
        PlaybookPoint(5,  "Agrément",
            "Mécanisme d'agrément des nouveaux associés. Délai, mode de valorisation en cas de refus. "
            "Exceptions (cessions intra-groupe, succession)."),
        PlaybookPoint(6,  "Incessibilité",
            "Période de lock-up. Durée et bénéficiaires. Exceptions légales et contractuelles. "
            "Conformité : max 10 ans pour SA (L228-23).",
            flag_conditions=["lock-up supérieur à 10 ans pour SA", "pas d'exception pour cessions intra-groupe"]),
        PlaybookPoint(7,  "Drag-Along (entraînement)",
            "Seuil de déclenchement. Conditions de prix (plancher, valorisation indépendante). "
            "Droits des minoritaires (prix minimum garanti).",
            flag_conditions=["drag sans prix minimum", "seuil de déclenchement trop bas"]),
        PlaybookPoint(8,  "Tag-Along (sortie conjointe)",
            "Seuil de déclenchement. Parité de traitement avec les majoritaires. "
            "Procédure et délai d'exercice.",
            flag_conditions=["tag-along limité à une fraction des titres", "conditions moins favorables que le majoritaire"]),
        PlaybookPoint(9,  "Anti-dilution",
            "Mécanisme (ratchet simple ou weighted average). "
            "Déclencheurs : nouvelles émissions à prix inférieur. Exceptions (BSPCE, stock-options).",
            flag_conditions=["full ratchet sans plafond", "exceptions BSPCE non prévues"]),
        PlaybookPoint(10, "Liquidation préférentielle",
            "Rang de priorité en cas de cession ou liquidation. "
            "Multiplicateur, cap, participation au surplus. "
            "Cumulative ou non-cumulative.",
            flag_conditions=["multiplicateur > 1x sans cap", "liquidation préférentielle non plafonnée"]),
        PlaybookPoint(11, "Clause de non-concurrence",
            "Périmètre (géographique, sectoriel), durée, contrepartie financière. "
            "Validité en droit des sociétés : appréciation plus souple qu'en droit du travail.",
            flag_conditions=["durée > 3 ans", "absence de contrepartie pour associés non salariés"]),
        PlaybookPoint(12, "Deadlock",
            "Définition du blocage. Mécanismes de résolution : médiation, arbitrage, "
            "offre d'achat forcée (Texas Shoot-Out, Russian Roulette). Délais.",
            flag_conditions=["absence de mécanisme de déblocage", "mécanisme potentiellement abusif"]),
        PlaybookPoint(13, "Clause de sortie / IPO",
            "Obligation ou option d'introduction en bourse. Délai, conditions de marché. "
            "Droit de co-vente (secondary) en cas d'IPO.",),
        PlaybookPoint(14, "Information et reporting",
            "Informations périodiques dues aux associés (comptes, budget, KPIs). "
            "Droit d'audit. Fréquence et format."),
        PlaybookPoint(15, "Droit applicable et arbitrage",
            "Loi française impérative pour les SAS/SARL françaises. "
            "Clause compromissoire : institution (CCI, CMAP), siège, langue, nombre d'arbitres."),
    ],
    instructions=(
        "Analyser le pacte en distinguant les droits des fondateurs, des investisseurs et des minoritaires. "
        "Vérifier la cohérence entre le pacte et les statuts : en cas de conflit, les statuts prévalent. "
        "Pour les SAS, vérifier la conformité aux clauses obligatoires des statuts (L227-11 à L227-20 C.com.). "
        "Signaler toute clause qui pourrait être qualifiée d'abusive ou de léonine (C.civ. art. 1844-1)."
    ),
)

PlaybookLibrary.register(SHAREHOLDER_AGREEMENT)
