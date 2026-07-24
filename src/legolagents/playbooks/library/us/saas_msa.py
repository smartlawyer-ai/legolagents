"""Playbook: SaaS Agreement / MSA review (US law, software vendor)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

US_SAAS_MSA = Playbook(
    id            = "us_saas_msa",
    title         = "SaaS Agreement / MSA Review (US)",
    document_type = "SaaS agreement or master services agreement",
    legal_domain  = "technology / commercial contracts",
    jurisdiction  = "us",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Goods vs. services characterization",
            "Courts apply a 'predominant purpose' test to decide whether UCC Article 2 applies "
            "(standardized software leans 'goods'; custom development leans common-law "
            "services) — outcomes are genuinely unpredictable across jurisdictions, so the "
            "contract should state its own remedy structure rather than leaving this to a court.",
            flag_conditions=["no express remedy structure, relying entirely on an unresolved goods-vs-services characterization"]),
        PlaybookPoint(2, "IP ownership — background IP vs. custom deliverables",
            "17 U.S.C. §101 'work made for hire' applies automatically to employees, but for "
            "independent contractors ONLY within nine narrow statutory categories — most custom "
            "SaaS development doesn't qualify, so ownership needs an express present-assignment "
            "clause, not just 'work made for hire' language.",
            flag_conditions=["IP ownership relies solely on 'work made for hire' for contractor-created deliverables"]),
        PlaybookPoint(3, "Customer data use and AI/model-training rights",
            "Fast-moving, heavily negotiated area: legacy 'improve the service' language is "
            "increasingly read by vendors as permission to train AI/ML models on customer data. "
            "2020s market practice trends toward requiring opt-in (not silence) for model "
            "training on customer data, source code, or confidential information.",
            flag_conditions=["silence on AI/model-training use of customer data",
                              "one-sided 'improve our services' clause with no training-specific carve-out"]),
        PlaybookPoint(4, "Data privacy / state privacy-law service-provider terms",
            "CCPA/CPRA (California) and the growing list of comprehensive state privacy "
            "statutes require: purpose/data-category description, no sale/use outside the "
            "specified business purpose, support for consumer rights requests, security and "
            "breach-notification obligations, sub-processor disclosure, and data return/deletion "
            "on termination, plus a compliance certification.",
            flag_conditions=["DPA missing the compliance certification or sub-processor flow-down"]),
        PlaybookPoint(5, "Service Level Agreement (SLA) and remedies",
            "If the SLA credit is the sole and exclusive remedy for downtime and the limitation "
            "of liability otherwise bars all other recovery, a court may find the limited remedy "
            "'fails of its essential purpose' under UCC §2-719 if goods characterization applies.",
            flag_conditions=["SLA credit as sole and exclusive remedy paired with a broad liability exclusion"]),
        PlaybookPoint(6, "Limitation of liability and cap structure",
            "Market standard: 1x trailing-12-months fees as the general cap (often 2-3x for "
            "enterprise deals), with a separate higher cap for data breach, confidentiality "
            "breach, and gross negligence/willful misconduct.",
            flag_conditions=["IP infringement indemnity folded into the low general liability cap",
                              "cap denominated on 'fees actually paid' rather than 'fees paid or payable'"]),
        PlaybookPoint(7, "IP infringement indemnification",
            "Vendor's duty to defend/indemnify against third-party IP infringement claims — "
            "typically carved out of the general cap (uncapped or separately capped).",
            flag_conditions=["indemnity conditioned on unreasonably narrow procedural requirements"]),
        PlaybookPoint(8, "Warranty disclaimers",
            "Standard 'AS IS' pattern disclaiming implied warranties, with a limited warranty of "
            "conformance to documentation.",
            flag_conditions=["disclaimer purports to also disclaim liability for fraud or willful misconduct"]),
        PlaybookPoint(9, "Termination, auto-renewal, and cancellation mechanics",
            "California's Automatic Renewal Law (B&P §17600 et seq., amended for contracts from "
            "1 July 2025) requires clear pre-consent disclosure of auto-renewal terms, easy "
            "self-service cancellation via the same medium used to enroll, and advance notice "
            "for promotional pricing rollovers.",
            flag_conditions=["auto-renewal clause with no easy self-service cancellation path"]),
        PlaybookPoint(10, "Data breach notification and security obligations",
            "Check the vendor's notification timeline against the customer's own downstream "
            "statutory notification deadlines to regulators/consumers."),
        PlaybookPoint(11, "Subprocessor / subcontractor flow-down and audit rights",
            "Right to receive SOC 2 (or similar) reports, commission security audits, and flow "
            "down confidentiality/security obligations to subprocessors."),
        PlaybookPoint(12, "Assignment / change of control",
            "One-sided clauses letting the vendor freely assign to any acquirer while requiring "
            "customer consent for its own assignment.",
            flag_conditions=["vendor freely assignable, customer assignment restricted"]),
        PlaybookPoint(13, "Governing law, venue, arbitration",
            "FAA framework generally enforces arbitration/class-action waivers absent "
            "unconscionability; confirm no employee-style restrictive covenants are smuggled "
            "into a B2B customer agreement."),
    ],
    instructions=(
        "AI/model-training contract terms are the most unsettled, fastest-moving area in this "
        "playbook — no comprehensive US federal statute governs this yet; treat any specific "
        "clause language as reflecting current market practice, not settled law, and flag "
        "explicitly that it may shift quickly. Likewise, UCC 'goods vs. services' characterization "
        "of SaaS remains genuinely unresolved across jurisdictions — don't assert a single rule."
    ),
)

PlaybookLibrary.register(US_SAAS_MSA)
