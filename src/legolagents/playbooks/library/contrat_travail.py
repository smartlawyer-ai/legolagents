"""Playbook : Analyse de Contrat de Travail (CDI / CDD)"""

from ..base import Playbook, PlaybookLibrary, PlaybookPoint

CONTRAT_TRAVAIL = Playbook(
    id            = "contrat_travail",
    title         = "Analyse de Contrat de Travail",
    document_type = "contrat de travail (CDI ou CDD)",
    legal_domain  = "droit social",
    output_format = "both",
    points=[
        PlaybookPoint(1,  "Parties et qualification",
            "Employeur (dénomination, SIREN, effectif) et salarié. "
            "Nature du contrat : CDI, CDD, CTT, temps partiel. "
            "Qualification réelle (attention au risque de requalification).",
            flag_conditions=["CDD sans motif légal précis", "clause de requalification en CDI risquée"]),
        PlaybookPoint(2,  "Fonction et classification",
            "Intitulé du poste, coefficient, niveau, statut (Cadre/AM/Ouvrier/Employé). "
            "Convention collective applicable et vérification de la classification.",
            flag_conditions=["classification inférieure aux fonctions réelles", "convention collective non identifiée"]),
        PlaybookPoint(3,  "Rémunération",
            "Salaire brut fixe, part variable (conditions d'attribution, objectifs mesurables). "
            "Conformité au SMIC et à la grille conventionnelle. "
            "Avantages en nature, primes contractuelles.",
            flag_conditions=["salaire inférieur au minimum conventionnel", "variable sans objectifs définis"]),
        PlaybookPoint(4,  "Durée du travail",
            "Temps plein (35h) ou temps partiel (mention obligatoire des horaires). "
            "Forfait jours cadres : accord collectif de branche ou d'entreprise requis. "
            "Heures supplémentaires : majoration conventionnelle.",
            flag_conditions=["forfait jours sans accord collectif valide", "temps partiel sans mention des horaires"]),
        PlaybookPoint(5,  "Période d'essai",
            "Durée et possibilité de renouvellement (accord de branche requis). "
            "Délais de prévenance légaux (L1221-25). "
            "Conformité aux maxima légaux (CDI : 2 mois E/O, 3 mois AM, 4 mois cadres).",
            flag_conditions=["durée supérieure au maximum légal", "renouvellement sans accord de branche"]),
        PlaybookPoint(6,  "Lieu de travail",
            "Lieu d'exécution, clause de mobilité géographique (étendue, délai de prévenance). "
            "Télétravail : régime applicable.",
            flag_conditions=["clause de mobilité sans limite géographique", "absence de délai de prévenance"]),
        PlaybookPoint(7,  "Clause de non-concurrence",
            "Validité : limitation dans le temps (max 2 ans), dans l'espace, à l'activité, "
            "contrepartie financière obligatoire (Soc. 10 juill. 2002). "
            "Conditions de levée par l'employeur.",
            flag_conditions=[
                "absence de contrepartie financière",
                "absence de limitation dans l'espace ou le temps",
                "absence de limitation à l'activité",
            ]),
        PlaybookPoint(8,  "Clause de confidentialité",
            "Étendue et durée. Conformité au secret des affaires (L151-1 et s. C.com.). "
            "Sanctions contractuelles.",
            flag_conditions=["durée illimitée", "clause trop large couvrant des informations non confidentielles"]),
        PlaybookPoint(9,  "Clause d'exclusivité",
            "Validité : justifiée par la nature des fonctions, proportionnée. "
            "Interdiction si temps partiel (L3123-8).",
            flag_conditions=["exclusivité pour salarié à temps partiel", "exclusivité non justifiée"]),
        PlaybookPoint(10, "Protection des données",
            "Obligations RGPD du salarié. Politique de traitement des données personnelles. "
            "Charte informatique annexée."),
        PlaybookPoint(11, "Rupture du contrat",
            "Conditions de rupture anticipée (CDD). "
            "Clause de dédit-formation : conditions de validité (engagement préalable, durée limitée). "
            "Indemnité conventionnelle de licenciement.",
            flag_conditions=["dédit-formation sans engagement préalable du salarié", "clause illicite de rupture anticipée CDI"]),
        PlaybookPoint(12, "Convention collective et accords",
            "Identification précise. Documents remis au salarié. "
            "Dispositions plus favorables que la loi."),
    ],
    instructions=(
        "Vérifier systématiquement la conformité au Code du travail et à la convention collective applicable. "
        "Les clauses contraires à l'ordre public social sont nulles. "
        "Pour la clause de non-concurrence, appliquer les critères de la jurisprudence Soc. : "
        "limitation dans le temps, l'espace, à une activité, et contrepartie financière — "
        "les quatre conditions sont cumulatives (Soc. 10 juill. 2002, n°00-45135)."
    ),
)

PlaybookLibrary.register(CONTRAT_TRAVAIL)
