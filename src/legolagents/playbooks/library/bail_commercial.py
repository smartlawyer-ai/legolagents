"""Playbook : Analyse de Bail Commercial (statut L145-1 et s. C.com.)"""

from ..base import Playbook, PlaybookLibrary, PlaybookPoint

BAIL_COMMERCIAL = Playbook(
    id            = "bail_commercial",
    title         = "Analyse de Bail Commercial",
    document_type = "bail commercial",
    legal_domain  = "droit commercial",
    output_format = "both",
    points=[
        PlaybookPoint(1,  "Parties",
            "Bailleur et preneur : dénomination sociale, forme juridique, SIREN, qualité (propriétaire, mandataire…)"),
        PlaybookPoint(2,  "Bien loué",
            "Désignation précise : adresse, superficie (Loi Pinel : mesure obligatoire), nature des locaux, destination contractuelle"),
        PlaybookPoint(3,  "Durée",
            "Durée du bail (minimum légal 9 ans). Date d'effet, date d'échéance. Renouvellement tacite ou express.",
            flag_conditions=["durée inférieure à 9 ans sans dérogation", "pas de mention de renouvellement"]),
        PlaybookPoint(4,  "Loyer",
            "Montant initial, indexation (ILC ou ILAT selon activité — L145-34 C.com.), périodicité, franchise éventuelle",
            flag_conditions=["indice non conforme à l'activité", "clause d'indexation non plafonnée"]),
        PlaybookPoint(5,  "Charges et travaux",
            "Répartition charges/travaux entre bailleur et preneur. Conformité au décret du 3 novembre 2014 (liste limitative).",
            flag_conditions=["charges exclues par décret 2014 mises à la charge du preneur"]),
        PlaybookPoint(6,  "Destination des locaux",
            "Activité autorisée. Clause de déspécialisation (partielle L145-47, plénière L145-48). Restrictions d'usage.",
            flag_conditions=["destination trop restrictive", "interdiction de sous-location ou cession sans accord"]),
        PlaybookPoint(7,  "Dépôt de garantie",
            "Montant (pratique : 2 à 3 termes). Conditions de restitution. Intérêts si > 2 termes de loyer (L145-15).",
            flag_conditions=["dépôt > 3 termes sans intérêts", "conditions de restitution floues"]),
        PlaybookPoint(8,  "Droit au renouvellement",
            "Conditions L145-8 : exploitation effective, immatriculation RCS, durée minimale. "
            "Congé avec/sans offre de renouvellement. Indemnité d'éviction.",
            flag_conditions=["clause supprimant le droit au renouvellement", "indemnité d'éviction non mentionnée"]),
        PlaybookPoint(9,  "Résiliation",
            "Congé triennal (L145-4 : résiliation à l'expiration de chaque période triennale). "
            "Causes de résiliation anticipée. Clause résolutoire et délai de mise en demeure.",
            flag_conditions=["congé triennal exclu", "clause résolutoire sans mise en demeure préalable"]),
        PlaybookPoint(10, "Cession et sous-location",
            "Conditions de cession du droit au bail ou du fonds de commerce. "
            "Droit de préférence du bailleur. Agrément du cessionnaire.",
            flag_conditions=["interdiction totale de cession", "droit de préférence non prévu par la loi"]),
        PlaybookPoint(11, "Clause d'accession",
            "Sort des améliorations et aménagements en fin de bail. "
            "Remise en état aux frais du preneur ?",
            flag_conditions=["accession sans indemnité pour améliorations importantes"]),
        PlaybookPoint(12, "Assurances",
            "Obligations d'assurance du preneur et du bailleur. Garanties minimales exigées."),
        PlaybookPoint(13, "Droit de préférence (Loi Pinel)",
            "Si vente du local : droit de préférence du preneur (L145-46-1). "
            "Exceptions et modalités de purge.",
            flag_conditions=["clause excluant le droit de préférence légal"]),
        PlaybookPoint(14, "Loi applicable et juridiction",
            "Droit français impératif pour les baux commerciaux. Tribunal de grande instance compétent."),
    ],
    instructions=(
        "Pour chaque clause, vérifier la conformité au statut des baux commerciaux (L145-1 et s. C.com.). "
        "Les clauses contraires à l'ordre public du statut sont nulles de plein droit (L145-15). "
        "Signaler toute clause qui écarte les droits impératifs du preneur."
    ),
)

PlaybookLibrary.register(BAIL_COMMERCIAL)
