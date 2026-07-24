"""Playbook: Commercial (business tenancy) Lease review (England & Wales law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

UK_COMMERCIAL_LEASE = Playbook(
    id            = "uk_commercial_lease",
    title         = "Commercial Lease Review (UK)",
    document_type = "business tenancy / commercial lease",
    legal_domain  = "real property",
    jurisdiction  = "uk",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Security of tenure — inside or outside the 1954 Act?",
            "Landlord and Tenant Act 1954 Part II, ss.23-46: s.23 defines a 'business tenancy'; "
            "automatic security of tenure applies unless validly excluded. This is the single "
            "most important threshold question.",
            flag_conditions=["ambiguous or absent statement of whether the tenancy is inside or outside the Act"]),
        PlaybookPoint(2, "Contracting-out procedure",
            "LTA 1954 s.38A (introduced by the Regulatory Reform (Business Tenancies) (England "
            "and Wales) Order 2003): landlord must serve a prescribed-form warning notice "
            "(at least 14 days before completion, or a simple statutory declaration with less "
            "notice) and the tenant must make a declaration confirming receipt and understanding.",
            flag_conditions=["contracting-out notice not served in time or in the wrong form",
                              "declaration signed by someone without apparent authority"]),
        PlaybookPoint(3, "Renewal rights and grounds of opposition",
            "LTA 1954 ss.24-28 (renewal mechanics), s.30(1)(a)-(g) (landlord's statutory grounds "
            "to oppose, e.g. persistent disrepair, rent arrears, redevelopment, owner-occupation), "
            "s.37 (compensation for no-fault refusal).",
            flag_conditions=["lease inside the Act but silent on renewal mechanics"]),
        PlaybookPoint(4, "Rent review",
            "No governing statute — a contractual mechanism, but the RICS Code for Leasing "
            "Business Premises 2020 (mandatory for RICS members) recommends clear, "
            "non-obscure formulae.",
            flag_conditions=["upward-only review with an obscure/indexed formula and no caps or collars"]),
        PlaybookPoint(5, "Break clauses",
            "Strict compliance required (Fitzroy House Epworth Street (No.1) Ltd v Financial "
            "Times Ltd [2006] EWCA Civ 329). RICS Code for Leasing 2020 recommends break "
            "conditions be limited to payment of basic rent, vacant possession, and no "
            "subtenants — not full compliance with repair covenants.",
            flag_conditions=["break conditional on full compliance with all lease covenants"]),
        PlaybookPoint(6, "Repairing obligations and dilapidations",
            "FRI (full repairing and insuring) vs. internal-only; Landlord and Tenant Act 1927 "
            "s.18(1) caps dilapidations damages to the diminution in the landlord's reversionary "
            "value.",
            flag_conditions=["FRI obligations disproportionate to a short-term/small tenancy",
                              "no schedule of condition for older or poor-condition premises"]),
        PlaybookPoint(7, "Service charge",
            "Governed by the RICS Professional Statement 'Service Charges in Commercial "
            "Property' (mandatory from 2020) — transparency, no profit element, real-cost "
            "management fees.",
            flag_conditions=["uncapped/undefined service charge with no audit or inspection right"]),
        PlaybookPoint(8, "Alienation (assignment, subletting, charging)",
            "Landlord and Tenant Act 1927 s.19(1)(a) (implied reasonableness where consent is "
            "required); Landlord and Tenant Act 1988 (statutory duty to decide within a "
            "reasonable time, with written reasons); Landlord and Tenant (Covenants) Act 1995 "
            "(post-1995 leases release the original tenant on assignment, subject to Authorised "
            "Guarantee Agreements).",
            flag_conditions=["absolute prohibition on assignment/subletting",
                              "AGA required on every future assignment with no limit"]),
        PlaybookPoint(9, "Insurance",
            "Typical drafting requires the landlord to insure and the tenant to reimburse, with "
            "reinstatement obligations.",
            flag_conditions=["no rent-suspension clause if the premises become unusable due to an insured risk"]),
        PlaybookPoint(10, "User clause / permitted use and planning",
            "Ties to the Town and Country Planning (Use Classes) Order 1987 (as amended)."),
        PlaybookPoint(11, "VAT / option to tax",
            "Value Added Tax Act 1994, Schedule 10.",
            flag_conditions=["lease silent on whether the landlord has opted to tax"]),
        PlaybookPoint(12, "Forfeiture / re-entry",
            "Law of Property Act 1925 s.146 (relief from forfeiture — landlord must serve a "
            "s.146 notice for non-rent breaches, giving the tenant a chance to remedy).",
            flag_conditions=["forfeiture clause drafted to bypass the s.146 notice requirement"]),
        PlaybookPoint(13, "Green lease / MEES (energy efficiency)",
            "Energy Efficiency (Private Rented Property) (England and Wales) Regulations 2015: "
            "minimum EPC rating of E currently required to lawfully let commercial premises.",
            flag_conditions=["lease silent on EPC/MEES compliance responsibility"]),
    ],
    instructions=(
        "The single biggest UK-vs-US quirk is statutory security of tenure under LTA 1954 Part II — "
        "US commercial leases have no equivalent automatic renewal right. Note: the Law Commission is "
        "mid-review of Part II (second consultation open until 16 September 2026) — current ss.24-28/38A "
        "remain in force unchanged, but flag this as an area to monitor for future reform."
    ),
)

PlaybookLibrary.register(UK_COMMERCIAL_LEASE)
