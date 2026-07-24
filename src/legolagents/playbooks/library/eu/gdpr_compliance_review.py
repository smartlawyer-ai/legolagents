"""Playbook: GDPR Compliance Review for a product launch (EU-level)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

GDPR_COMPLIANCE_REVIEW = Playbook(
    id            = "eu_gdpr_compliance_review",
    title         = "GDPR Compliance Review",
    document_type = "product/feature launch compliance review",
    legal_domain  = "data protection",
    jurisdiction  = "eu",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Lawful basis per processing purpose",
            "Every data flow must map to one of the six Art 6(1) bases; reliance on "
            "legitimate interests requires a documented balancing test (LIA).",
            flag_conditions=["legitimate interests asserted for everything with no LIA on file"]),
        PlaybookPoint(2, "Special category data check",
            "If the product processes health, biometric, genetic, racial/ethnic, political, "
            "religious, trade-union, or sex-life/orientation data, an Art 9(2) exception must "
            "apply in addition to an Art 6 basis.",
            flag_conditions=["special category data processed with only a generic Art 6 basis"]),
        PlaybookPoint(3, "Data minimisation and purpose limitation",
            "Art 5(1)(b)-(c): verify the product only collects data necessary for stated "
            "purposes — scope creep ('collecting for future features') is a common failure mode."),
        PlaybookPoint(4, "Data protection by design and by default",
            "Art 25: technical/organisational measures embedded at design and processing time; "
            "by default, only data necessary for each specific purpose is processed (relevant "
            "to default privacy settings, opt-out vs. opt-in).",
            flag_conditions=["default settings maximize data collection/sharing (opt-out rather than opt-in)"]),
        PlaybookPoint(5, "Transparency notices",
            "Art 13/14: identity/contact of controller (and DPO if any), purposes and legal "
            "basis, legitimate interests pursued, recipients, transfer intentions and "
            "safeguards, retention period/criteria, data subject rights — delivered at the "
            "time of collection.",
            flag_conditions=["privacy notice silent on international transfers, retention periods, "
                              "or automated decision-making"]),
        PlaybookPoint(6, "Data subject rights operational readiness",
            "Arts 15-22: access, rectification, erasure, restriction, portability, objection, "
            "and automated-decision rights need a functioning intake/response process within "
            "the one-month statutory window (Art 12(3)).",
            flag_conditions=["no process to action rights requests within the one-month window"]),
        PlaybookPoint(7, "Automated decision-making / profiling",
            "Art 22(1) prohibits solely-automated decisions with legal/similarly significant "
            "effect unless an Art 22(2) exception applies (contract necessity, authorising "
            "law, explicit consent), and Art 22(3) requires the right to human intervention, "
            "to express a view, and to contest.",
            flag_conditions=["automated decision with legal/significant effect and no human-review/contest mechanism",
                              "'human-in-the-loop' reviewer with no genuine authority to change the automated output"]),
        PlaybookPoint(8, "Data Protection Impact Assessment",
            "Art 35: required for systematic/extensive profiling with legal effects, "
            "large-scale special-category/criminal data processing, or systematic large-scale "
            "public monitoring (Art 35(3)); WP29/EDPB's nine-criteria approach generally "
            "triggers a DPIA where two or more criteria are met.",
            flag_conditions=["high-risk processing launched without a completed DPIA",
                              "DPIA completed only pro forma after launch"]),
        PlaybookPoint(9, "Records of Processing Activities",
            "Art 30: required for controllers/processors above 250 employees, or those "
            "processing regularly, or processing special category/criminal data, or presenting "
            "risk to rights and freedoms.",
            flag_conditions=["no Art 30 records maintained despite qualifying criteria"]),
        PlaybookPoint(10, "DPO designation assessment",
            "Art 37: mandatory for public authorities, core activities requiring regular/"
            "systematic large-scale monitoring, or large-scale special category/criminal data "
            "processing (large scale assessed per WP29 volume/duration/extent criteria).",
            flag_conditions=["no DPO appointed despite meeting an Art 37(1) mandatory trigger"]),
        PlaybookPoint(11, "Security measures proportionate to risk",
            "Art 32: pseudonymisation/encryption, confidentiality/integrity/availability/"
            "resilience, restoration after incident, regular testing."),
        PlaybookPoint(12, "Breach response plan",
            "Arts 33/34: documented process to detect/assess/notify the supervisory authority "
            "within 72 hours of controller awareness, and affected data subjects without undue "
            "delay where high risk exists.",
            flag_conditions=["no breach-response plan, or no assigned owner/escalation path"]),
        PlaybookPoint(13, "International transfer mapping",
            "Identify every vendor/sub-processor/affiliate outside the EEA in the product's "
            "data flow and confirm a Chapter V mechanism is in place for each."),
        PlaybookPoint(14, "AI Act overlap",
            "Regulation (EU) 2024/1689: if the product uses AI to process personal data, check "
            "risk-tier classification (prohibited practices already in force since 2 February "
            "2025; most high-risk obligations, including Annex III systems, apply from "
            "2 August 2026, subject to any formally adopted deferral). Systems making Art 22 "
            "GDPR-scoped automated decisions are frequently also Annex III high-risk AI "
            "(employment/HR, creditworthiness, essential services) — obligations are "
            "cumulative, not substitutable.",
            flag_conditions=["AI feature (scoring, recommendation, chatbot) launched with no AI Act risk-tier assessment"]),
    ],
    instructions=(
        "A valid Art 6 lawful basis does not substitute for Art 22 compliance where automated "
        "decision-making applies, and neither substitutes for AI Act conformity where the system is "
        "also a high-risk AI system — these are cumulative, independent obligations layered on the "
        "same processing activity. Treat the AI Act's 2 August 2026 high-risk deadline as subject to "
        "verification at publication time, given pending deferral discussions for Annex III systems."
    ),
)

PlaybookLibrary.register(GDPR_COMPLIANCE_REVIEW)
