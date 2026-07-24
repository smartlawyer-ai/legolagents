"""Playbook: SaaS Agreement / MSA review (England & Wales law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

UK_SAAS_MSA = Playbook(
    id            = "uk_saas_msa",
    title         = "SaaS Agreement / MSA Review (UK)",
    document_type = "SaaS agreement or master services agreement",
    legal_domain  = "technology / commercial contracts",
    jurisdiction  = "uk",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Limitation and exclusion of liability",
            "Unfair Contract Terms Act 1977: s.2(1) bans excluding liability for death/personal "
            "injury from negligence outright; s.2(2) subjects other negligence liability to a "
            "reasonableness test; s.3 covers a party's own written standard terms. Recent case "
            "law: Last Bus Ltd v Dawsongroup Bus and Coach Ltd [2023] EWCA Civ 1297 (bargaining-"
            "power analysis must be done properly); Pinewood Technologies Asia Pacific Ltd v "
            "Pinewood Technologies plc [2023] EWHC 2506 (TCC) (reasonableness only bites on "
            "'written standard terms' — heavily negotiated MSAs may escape UCTA scrutiny).",
            flag_conditions=["cap below annual contract value with no carve-outs",
                              "exclusion purporting to cover death/personal injury from negligence (void per se)",
                              "one-sided cap (vendor capped, customer uncapped)"]),
        PlaybookPoint(2, "Warranties and implied terms",
            "Supply of Goods and Services Act 1982 implies reasonable care and skill; for B2C "
            "SaaS, Consumer Rights Act 2015 Part 1 Chapter 3 ss.33-47 governs 'digital content' "
            "— satisfactory quality (s.34), fitness for purpose (s.35), match to description "
            "(s.36) — and critically s.47 makes these rights non-excludable.",
            flag_conditions=["blanket 'AS IS' disclaimer applied to a consumer-facing SaaS product"]),
        PlaybookPoint(3, "Unfair terms (B2C only)",
            "Consumer Rights Act 2015 Part 2 ss.61-76: s.62 (significant imbalance test), "
            "Schedule 2 grey list (unilateral variation without valid reason, unreasonably "
            "short auto-renewal cancellation windows, etc.).",
            flag_conditions=["auto-renewal with a narrow cancellation window and no reminder notice",
                              "unilateral price/term variation right with no corresponding termination right"]),
        PlaybookPoint(4, "Data protection / processor obligations",
            "UK GDPR Art 28 (processing only on documented instructions, confidentiality, "
            "security, sub-processor authorization, assistance with data subject rights, "
            "deletion/return of data, audit rights); Art 32 (security); Arts 33-34 (breach "
            "notification — ICO within 72 hours).",
            flag_conditions=["no Art 28-compliant DPA, or one missing the mandatory Art 28(3) content",
                              "vendor claims unilateral right to appoint sub-processors with no objection right"]),
        PlaybookPoint(5, "International data transfers",
            "ICO's International Data Transfer Agreement (IDTA) or the UK Addendum to the EU "
            "SCCs (both in force from 21 March 2022). The Data (Use and Access) Act 2025 "
            "replaces the 'essentially equivalent protection' test with a new statutory 'data "
            "protection test' (main provisions in force from 5 February 2026).",
            flag_conditions=["transfers to a non-adequate jurisdiction with no IDTA/Addendum/SCC in place"]),
        PlaybookPoint(6, "Cookies / PECR compliance",
            "Privacy and Electronic Communications Regulations 2003, as amended by the Data "
            "(Use and Access) Act 2025 — new consent exemptions (including a strict "
            "statistics-only exemption requiring a visible opt-out) and PECR fines now aligned "
            "to UK GDPR maxima.",
            flag_conditions=["analytics relying on the statistics exemption while also profiling/advertising"]),
        PlaybookPoint(7, "IP ownership",
            "Background IP, customer data, and developed IP/feedback must be addressed "
            "contractually — the Copyright, Designs and Patents Act 1988 s.11(2) default only "
            "covers employee works, not vendor/customer relationships.",
            flag_conditions=["vendor claims ownership of customer data or derived improvements",
                              "no license-back to customer of their own uploaded content"]),
        PlaybookPoint(8, "Service levels and termination for persistent failure",
            "An SLA framed as the sole and exclusive remedy for any and all availability "
            "failures is itself subject to UCTA reasonableness scrutiny.",
            flag_conditions=["service credits as sole remedy even for complete outage or data loss"]),
        PlaybookPoint(9, "Termination and data return",
            "UK GDPR Art 28(3)(g): processor must delete or return personal data at the end of "
            "processing.",
            flag_conditions=["no obligation to export customer data in a usable format on termination"]),
        PlaybookPoint(10, "Anti-bribery warranties",
            "Bribery Act 2010 s.7: strict-liability corporate offence for failing to prevent "
            "bribery by 'associated persons,' subject to an 'adequate procedures' defence.",
            flag_conditions=["enterprise MSA with no anti-bribery compliance warranty"]),
        PlaybookPoint(11, "Modern slavery / supply chain warranties",
            "Modern Slavery Act 2015 s.54: mandatory transparency statement for organisations "
            "with global turnover above £36 million."),
        PlaybookPoint(12, "Governing law, jurisdiction, and arbitration",
            "Arbitration Act 1996 as modernised by the Arbitration Act 2025 (codifies an "
            "arbitrator's disclosure duty, clarifies governing law of the arbitration "
            "agreement itself).",
            flag_conditions=["asymmetric jurisdiction clause (vendor can sue anywhere, customer confined to one forum)"]),
        PlaybookPoint(13, "Execution formalities",
            "Law Commission's Electronic Execution of Documents Report (2019) confirms "
            "e-signatures are valid for simple contracts and deeds where intent to authenticate "
            "is shown; click-wrap enforceability follows ordinary offer/acceptance principles.",
            flag_conditions=["click-through execution with no evidence of the signatory's authority to bind the counterparty"]),
    ],
    instructions=(
        "UCTA 1977 imposes a mandatory, judicially enforced reasonableness backstop on limitation "
        "clauses in B2B contracts on standard terms — a fairness check with no single US equivalent. "
        "For B2C SaaS, the Consumer Rights Act 2015 gives non-excludable statutory quality rights for "
        "'digital content.' Data protection runs through UK GDPR (now being actively recalibrated by "
        "the Data (Use and Access) Act 2025) rather than a state-by-state US patchwork."
    ),
)

PlaybookLibrary.register(UK_SAAS_MSA)
