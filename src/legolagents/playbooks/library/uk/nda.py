"""Playbook: Confidentiality Agreement / NDA review (England & Wales law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

UK_NDA = Playbook(
    id            = "uk_nda",
    title         = "NDA / Confidentiality Agreement Review (UK)",
    document_type = "confidentiality agreement (mutual or one-way)",
    legal_domain  = "confidentiality / trade secrets",
    jurisdiction  = "uk",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Definition of Confidential Information",
            "Scope and exclusions (public domain, independently developed, already known, "
            "legally compelled disclosure). Grounded in the common-law breach-of-confidence "
            "test from Coco v A N Clark (Engineers) Ltd [1969] RPC 41 — necessary quality of "
            "confidence, imparted in circumstances importing an obligation, unauthorised "
            "use/detriment — plus the Trade Secrets (Enforcement etc.) Regulations 2018 "
            "(SI 2018/597) for genuine trade secrets specifically.",
            flag_conditions=["definition broad enough to cover publicly available information",
                              "one-sided definition in an agreement labeled 'mutual'"]),
        PlaybookPoint(2, "Permitted purpose / permitted disclosees",
            "Must be tightly drafted since a breach-of-confidence claim turns on the scope of "
            "'circumstances importing an obligation' (Coco v Clark).",
            flag_conditions=["no purpose limitation", "sub-disclosees not required to sign equivalent undertakings"]),
        PlaybookPoint(3, "Whistleblowing / protected disclosure carve-out",
            "Employment Rights Act 1996 s.43J voids any provision purporting to preclude a "
            "protected disclosure. Missing carve-out signals an aggressively drafted NDA and "
            "regulatory/reputational risk (cf. the Higher Education (Freedom of Speech) Act "
            "2023's ban on using NDAs to cover up harassment/misconduct complaints).",
            flag_conditions=["no whistleblower/protected-disclosure carve-out",
                              "clause could be read as preventing reports to regulators or police"]),
        PlaybookPoint(4, "Term of the confidentiality obligation",
            "No statutory cap for ordinary commercial confidentiality; trade secrets are "
            "protected indefinitely at common law while secrecy is maintained.",
            flag_conditions=["perpetual/indefinite term for information that is not a genuine trade secret"]),
        PlaybookPoint(5, "Non-solicitation dressed up as confidentiality",
            "Restraint-of-trade doctrine: Nordenfelt v Maxim Nordenfelt [1894] AC 535 (only "
            "reasonable restraints protecting a legitimate interest are enforceable); "
            "Egon Zehnder Ltd v Tillman [2019] UKSC 32 tightened the severance/'blue pencil' "
            "test. A no-poach clause between competing businesses can also raise Competition "
            "Act 1998 Chapter I exposure (the CMA has pursued no-poach agreements as cartel "
            "conduct).",
            flag_conditions=["non-solicitation of employees/customers with no time or scope limit",
                              "NDA used as a disguised non-compete between competitors"]),
        PlaybookPoint(6, "Residuals / retained-knowledge clause",
            "Tension with the Coco v Clark breach-of-confidence test.",
            flag_conditions=["residuals clause broad enough to license use of anything retained in unaided memory"]),
        PlaybookPoint(7, "Data protection carve-out",
            "If personal data is disclosed, reference UK GDPR (as amended by the Data (Use and "
            "Access) Act 2025) — either a data-sharing clause or a separate DPA.",
            flag_conditions=["NDA permits free disclosure of personal data with no data-protection reference"]),
        PlaybookPoint(8, "Return / destruction of information",
            "Relevant to demonstrating 'reasonable steps' to maintain secrecy under the Trade "
            "Secrets Regulations 2018 definition."),
        PlaybookPoint(9, "IP ownership / no licence granted",
            "Confidentiality is not an IP assignment — needs an explicit 'no licence' clause "
            "to avoid implied-licence arguments.",
            flag_conditions=["silence on IP ownership creating ambiguity"]),
        PlaybookPoint(10, "Remedies — injunctive relief",
            "A contractual acknowledgment of irreparable harm cannot oust the court's equitable "
            "discretion (American Cyanamid v Ethicon [1975] AC 396 principles still apply)."),
        PlaybookPoint(11, "Governing law and jurisdiction",
            "For cross-border NDAs, consider Rome I (retained, as amended by SI 2019/834) for "
            "governing law and the Hague Convention on Choice of Court Agreements 2005 (UK "
            "rejoined in its own right from 1 Jan 2021) for jurisdiction."),
        PlaybookPoint(12, "Execution formalities",
            "Simple contracts need no deed; if executed as a deed, formalities under the Law of "
            "Property (Miscellaneous Provisions) Act 1989 s.1 and Companies Act 2006 s.44 apply. "
            "Electronic execution of deeds via video-witnessing remains legally uncertain per "
            "the Law Commission's 2019 report on Electronic Execution of Documents.",
            flag_conditions=["deed execution with a remote/video witness"]),
    ],
    instructions=(
        "UK NDAs rely on the common-law tort/equity of breach of confidence (Coco v Clark) rather "
        "than a single trade-secret statute — the Trade Secrets Regulations 2018 sit alongside, not "
        "instead of, common law. UK courts are notably more cautious about non-solicit/no-poach "
        "language embedded in NDAs than US practice, because of restraint-of-trade scrutiny."
    ),
)

PlaybookLibrary.register(UK_NDA)
