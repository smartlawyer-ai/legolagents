"""Playbook : Analyse de Convention de Crédit (droit FR — adapté de mike)"""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

CREDIT_AGREEMENT = Playbook(
    id            = "convention_credit",
    title         = "Analyse de Convention de Crédit",
    document_type = "convention de crédit ou contrat de prêt",
    legal_domain  = "droit bancaire",
    jurisdiction  = "fr",
    output_format = "docx",
    points=[
        PlaybookPoint(1,  "Prêteurs",
            "Prêteurs ou pool bancaire. Dénomination complète, rôle (arrangeur, chef de file, agent). "
            "Engagements respectifs en cas de syndicat bancaire."),
        PlaybookPoint(2,  "Emprunteurs",
            "Emprunteur(s) et co-emprunteurs. Dénomination, forme juridique, pays d'incorporation."),
        PlaybookPoint(3,  "Garants",
            "Garants, nature de la garantie (cautionnement, garantie autonome, hypothèque). "
            "Étendue et plafond de la garantie. Garantie solidaire ou subsidiaire.",
            flag_conditions=["garantie illimitée sans plafond", "caution disproportionnée"]),
        PlaybookPoint(4,  "Autres parties",
            "Agent de crédit, agent des sûretés, arrangeurs, banques d'investissement."),
        PlaybookPoint(5,  "Date et durée",
            "Date de signature, date de mise en place, date d'échéance finale."),
        PlaybookPoint(6,  "Tranches / Facilités",
            "Nature et nom de chaque tranche (RCF, TLA, TLB…). "
            "Type (amortissable, in fine, revolving). Montant et devise par tranche."),
        PlaybookPoint(7,  "Montant total",
            "Montant global engagé. Devise principale. Possibilité de multi-devises."),
        PlaybookPoint(8,  "Objet",
            "Finalité déclarée du crédit. Restrictions d'utilisation des fonds. "
            "Déclarations d'utilisation périodiques.",
            flag_conditions=["objet trop vague", "restrictions d'utilisation excessives"]),
        PlaybookPoint(9,  "Taux d'intérêt",
            "Taux de référence (EURIBOR, SOFR, taux fixe). Marge applicable. "
            "Mécanisme de ratchet (évolution selon levier). Intérêts de retard.",
            flag_conditions=["absence de plancher sur l'index", "ratchet non plafonné"]),
        PlaybookPoint(10, "Commission d'engagement",
            "Taux, base de calcul (montant non tiré), périodicité."),
        PlaybookPoint(11, "Remboursement",
            "Amortissement par tranche (tableau, linéaire, bullet). Dates et montants. "
            "Remboursements anticipés obligatoires (excess cash flow, cession d'actifs)."),
        PlaybookPoint(12, "Sûretés",
            "Nantissement de parts sociales, gage de comptes, hypothèque, pledge d'actifs. "
            "Parties constitutives, actifs concernés. Agent des sûretés.",
            flag_conditions=["sûretés insuffisantes au regard du risque", "absence d'agent des sûretés en syndicat"]),
        PlaybookPoint(13, "Covenants financiers",
            "Ratio Levier (Dette nette / EBITDA), couverture des intérêts, actif net minimum. "
            "Niveau de déclenchement, fréquence de test, equity cure.",
            flag_conditions=["absence de cure right", "covenant de levier trop serré"]),
        PlaybookPoint(14, "Cas de défaut",
            "Liste exhaustive. Cross-default : seuil, périmètre. "
            "Délais de grâce. Défaut croisé avec les autres dettes du groupe.",
            flag_conditions=["cross-default sans seuil de matérialité", "délais de grâce absents"]),
        PlaybookPoint(15, "Cessions",
            "Conditions de cession de créance (accord emprunteur, liste blanche/noire). "
            "Restrictions à la cession côté emprunteur.",
            flag_conditions=["accord emprunteur non requis pour cession", "liste noire absente"]),
        PlaybookPoint(16, "Changement de contrôle",
            "Définition. Conséquences (remboursement anticipé obligatoire, consentement des prêteurs). "
            "Période de cure éventuelle."),
        PlaybookPoint(17, "Remboursement anticipé",
            "Indemnité de remboursement anticipé (make-whole, call premium, soft-call). "
            "Période d'application. Exceptions (assurance, cessions d'actifs)."),
        PlaybookPoint(18, "Droit applicable et juridiction",
            "Droit français ou anglais. Tribunal compétent (Tribunal de commerce Paris). "
            "Clause compromissoire éventuelle."),
    ],
    instructions=(
        "Analyser la convention sous l'angle du risque pour l'emprunteur et les garants. "
        "Vérifier la cohérence entre les covenants et la capacité financière de l'emprunteur. "
        "Identifier les événements déclencheurs de défaut les plus exposants. "
        "Comparer les conditions aux standards de marché français (LMA ou AFME)."
    ),
)

PlaybookLibrary.register(CREDIT_AGREEMENT)
