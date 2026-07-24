"""Playbook: Data Processing Agreement review (GDPR Article 28, EU-level)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

DATA_PROCESSING_AGREEMENT = Playbook(
    id            = "eu_data_processing_agreement",
    title         = "Data Processing Agreement Review (EU / GDPR Art. 28)",
    document_type = "data processing agreement (DPA)",
    legal_domain  = "data protection",
    jurisdiction  = "eu",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Existence of a written contract",
            "GDPR Art 28(3): any controller-processor relationship must be governed by a "
            "binding contract in writing, including electronic form (Art 28(9)).",
            flag_conditions=["no written DPA, or a verbal/informal arrangement"]),
        PlaybookPoint(2, "Subject-matter, duration, nature, purpose, data types, data subjects",
            "Art 28(3) chapeau requires the DPA to specify these five elements precisely — "
            "EDPB Guidelines 07/2020 note the DPA 'must not simply restate the provisions of "
            "the GDPR' but give concrete operational detail.",
            flag_conditions=["generic restatement of GDPR text with no operational specificity"]),
        PlaybookPoint(3, "Processing only on documented instructions",
            "Art 28(3)(a); the processor must also flag to the controller if an instruction "
            "infringes GDPR or other data protection law.",
            flag_conditions=["processor retains a unilateral right to process for its own purposes "
                              "beyond documented instructions (converts it into a de facto controller)"]),
        PlaybookPoint(4, "Confidentiality of authorized persons",
            "Art 28(3)(b): persons authorized to process personal data must be bound by "
            "confidentiality."),
        PlaybookPoint(5, "Security measures",
            "Art 28(3)(c) requires all measures required under Art 32 (pseudonymisation, "
            "encryption, confidentiality/integrity/availability/resilience, restoration after "
            "an incident, regular testing)."),
        PlaybookPoint(6, "Sub-processor authorization",
            "Art 28(2): no sub-processor without the controller's prior specific or general "
            "written authorization (with an objection right if general); Art 28(4): equivalent "
            "obligations must flow down to sub-processors by contract, and the processor "
            "remains fully liable for the sub-processor's performance.",
            flag_conditions=["sub-processor engagement with no controller consent mechanism",
                              "sub-processor contract fails to impose equivalent Art 28(3) obligations"]),
        PlaybookPoint(7, "Assistance with data subject rights",
            "Art 28(3)(e): the processor must assist the controller in responding to access, "
            "rectification, erasure, restriction, portability, and objection requests."),
        PlaybookPoint(8, "Assistance with Art 32/33/34/35/36 obligations",
            "Art 28(3)(f): assistance with security, breach notification, and DPIA/prior "
            "consultation obligations, taking into account the nature of processing."),
        PlaybookPoint(9, "Breach notification timeline",
            "Art 28(3)(f) read with Art 33(2): the processor must notify the controller "
            "'without undue delay.' A DPA should set a concrete SLA (commonly 24-48 hours), "
            "since the controller's own 72-hour clock to the supervisory authority (Art 33(1)) "
            "starts on the controller's awareness.",
            flag_conditions=["no concrete breach-notification timeline from processor to controller"]),
        PlaybookPoint(10, "Deletion or return of data at end of provision of services",
            "Art 28(3)(g): at the controller's choice, delete or return all personal data, "
            "and delete existing copies unless EU/Member State law requires storage.",
            flag_conditions=["no deletion/return clause, or no specified timeframe/treatment of backups"]),
        PlaybookPoint(11, "Audit and inspection rights",
            "Art 28(3)(h): the processor must make available all information necessary to "
            "demonstrate compliance and allow for audits/inspections by the controller or its "
            "mandated auditor.",
            flag_conditions=["audit rights excluded or limited to processor's own self-certifications"]),
        PlaybookPoint(12, "International transfer mechanism",
            "If processing occurs outside the EEA (directly or via a sub-processor), the DPA "
            "must incorporate a valid Chapter V transfer tool: the 2021 SCCs (Commission "
            "Implementing Decision (EU) 2021/914, using the correct module), an adequacy "
            "decision (Art 45), Binding Corporate Rules (Art 47), or an Art 49 derogation. "
            "Post-Schrems II (CJEU C-311/18), SCCs alone are not sufficient — a Transfer Impact "
            "Assessment (per EDPB Recommendations 01/2020) is required.",
            flag_conditions=["transfer to a non-adequate country with no SCCs/BCRs/adequacy/derogation referenced",
                              "no Transfer Impact Assessment documented for SCC-based transfers",
                              "reliance solely on adequacy self-certification (e.g. a data-transfer framework) with no SCC fallback"]),
        PlaybookPoint(13, "Liability and indemnification allocation",
            "Not itself a mandatory Art 28 clause, but standard market practice tied to breach "
            "of the Art 28(3) obligations.",
            flag_conditions=["liability cap disproportionately low relative to plausible GDPR fine exposure"]),
    ],
    instructions=(
        "The official Article 28 Standard Contractual Clauses (Commission Implementing Decision "
        "(EU) 2021/915) automatically satisfy Art 28(3)/(4) — check whether the DPA is bespoke or "
        "the official template, and if bespoke, checklist it against every Art 28(3)(a)-(h) element "
        "above. International-transfer mechanisms are the fastest-moving part of this area — flag "
        "any transfer-framework adequacy reliance as conditional/dated rather than settled, given the "
        "history of successive EU-US transfer mechanisms facing judicial challenge."
    ),
)

PlaybookLibrary.register(DATA_PROCESSING_AGREEMENT)
