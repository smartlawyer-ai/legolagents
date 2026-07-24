"""Playbook: Commercial Lease review (US law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

US_COMMERCIAL_LEASE = Playbook(
    id            = "us_commercial_lease",
    title         = "Commercial Lease Review (US)",
    document_type = "commercial lease agreement",
    legal_domain  = "real property",
    jurisdiction  = "us",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Premises, use clause, exclusivity",
            "Note: UCC Article 2 does NOT apply to real property leases — governed by state "
            "real property/landlord-tenant common law and statutes, not the UCC."),
        PlaybookPoint(2, "Term, renewal options, rent escalation",
            "Fixed steps, CPI-indexed, or fair-market-value resets. Ambiguous FMV-reset "
            "mechanisms are a common source of disputes.",
            flag_conditions=["FMV rent-reset mechanism with no defined process or arbitrator"]),
        PlaybookPoint(3, "CAM (Common Area Maintenance) charges",
            "Definition, caps, and tenant audit rights over the landlord's cost pass-through.",
            flag_conditions=["no cap on controllable CAM increases", "no tenant audit right"]),
        PlaybookPoint(4, "Assignment and subletting — consent standard",
            "Majority modern trend implies consent may not be unreasonably withheld even if the "
            "lease is silent; California codifies this (Civ. Code §1995.260). New York has no "
            "such statute — a silent clause is far less tenant-protective there. Maryland "
            "requires explicit 'sole and absolute discretion' language for unrestricted refusal.",
            flag_conditions=["silent assignment clause (state-dependent outcome)",
                              "unrestricted landlord discretion with no reciprocal tenant protection"]),
        PlaybookPoint(5, "Default, notice, and cure periods",
            "Market practice: 5-10 days' cure for monetary default, ~30 days for non-monetary. "
            "New York gives commercial tenants no statutory cure-period backstop absent contract "
            "language. California prohibits commercial self-help eviction (Civ. Code §789.3); "
            "Texas statutorily permits self-help lockouts subject to procedural conditions "
            "(Prop. Code Ch. 93).",
            flag_conditions=["no cure period specified (high risk under NY law)",
                              "self-help remedy assumed available regardless of governing state"]),
        PlaybookPoint(6, "Estoppel certificates and SNDA",
            "An SNDA (Subordination, Non-Disturbance, and Attornment) protects the tenant's "
            "lease on the landlord's lender's foreclosure in exchange for subordination.",
            flag_conditions=["subordination required with no corresponding non-disturbance protection",
                              "unlimited/unreasonably fast estoppel certification obligation"]),
        PlaybookPoint(7, "Casualty / damage and destruction",
            "Right to terminate or abate rent if the premises are destroyed or unusable — "
            "abatement typically covers actual physical damage only, not e.g. regulatory closures."),
        PlaybookPoint(8, "Force majeure clause",
            "Read narrowly by courts; commonly does NOT excuse rent payment even during a "
            "qualifying event unless expressly stated.",
            flag_conditions=["tenant assumes rent relief from a generic force majeure clause with no express carve-out"]),
        PlaybookPoint(9, "Condemnation / eminent domain",
            "Allocation of the condemnation award and termination rights on a partial or total "
            "taking. Whether a temporary government-ordered closure counts as a compensable "
            "'taking' remains an untested legal theory."),
        PlaybookPoint(10, "Indemnification and insurance",
            "Mutual vs. one-sided indemnity; insurance minimums, additional-insured status, "
            "waiver of subrogation.",
            flag_conditions=["uncapped one-sided tenant indemnity for the landlord's own negligence"]),
        PlaybookPoint(11, "Personal guaranty / good-guy guaranty",
            "Triggers, cap amount, and burn-off conditions (common in smaller retail leases)."),
        PlaybookPoint(12, "Repair/maintenance allocation and compliance with law",
            "Structural vs. non-structural allocation; which party bears ADA (42 U.S.C. §12181 "
            "et seq.) compliance/remediation costs.",
            flag_conditions=["no allocation of ADA/compliance-with-law costs"]),
        PlaybookPoint(13, "Holdover provisions",
            "Holdover rent multiplier (often 150-200% of rent) and consequential-damages exposure "
            "beyond state-law defaults."),
    ],
    instructions=(
        "State variance is the central axis of a US commercial lease review: assignment consent, "
        "default/cure periods, and availability of landlord self-help remedies all depend on the "
        "governing-law state. Identify that state before drawing conclusions, and flag explicitly "
        "when the outcome is state-dependent rather than settled nationally."
    ),
)

PlaybookLibrary.register(US_COMMERCIAL_LEASE)
