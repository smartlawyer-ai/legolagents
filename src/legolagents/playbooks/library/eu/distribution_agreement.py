"""Playbook: Distribution / Vertical Agreement review (EU competition law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

DISTRIBUTION_AGREEMENT = Playbook(
    id            = "eu_distribution_agreement",
    title         = "Distribution Agreement Review (EU competition law)",
    document_type = "distribution or vertical agreement",
    legal_domain  = "competition law",
    jurisdiction  = "eu",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Market share check (both parties)",
            "Vertical Block Exemption Regulation (VBER), Commission Regulation (EU) 2022/720, "
            "Art 3: the block exemption applies only where both supplier's and buyer's market "
            "shares are each ≤30% on their respective relevant markets. Above that, no "
            "presumption of exemption applies — the agreement needs individual assessment "
            "under Art 101(1)/(3) TFEU.",
            flag_conditions=["either party's market share above 30% with the agreement still assuming automatic block exemption"]),
        PlaybookPoint(2, "Resale price maintenance",
            "VBER Art 4(a): fixing or imposing a minimum resale price is a hardcore "
            "restriction — voids the ENTIRE block exemption, not just the offending clause. "
            "Recommended/maximum resale prices remain permissible if genuinely non-binding.",
            flag_conditions=["fixed or minimum resale price imposed on the buyer",
                              "'recommended' price enforced via rebates/penalties tied to adherence"]),
        PlaybookPoint(3, "Territorial / customer sales restrictions",
            "VBER Art 4(b): a supplier may reserve a territory/customer group exclusively to "
            "itself or up to 5 pre-allocated buyers, and restrict active (but not passive) "
            "sales by other buyers into that reserved territory/group.",
            flag_conditions=["passive-sales restrictions into a non-exclusive territory/customer group (hardcore)"]),
        PlaybookPoint(4, "Cross-supply restrictions in selective distribution",
            "VBER Art 4(d): restricting cross-supplies between authorized distributors within "
            "a selective distribution network is hardcore.",
            flag_conditions=["distributors barred from supplying each other within the selective network"]),
        PlaybookPoint(5, "Online sales restrictions",
            "VBER Art 4(e) (expanded in the 2022 reform): restrictions preventing the "
            "'effective use of the internet' are hardcore — this includes not just outright "
            "online-sales bans but indirect restrictions (banning an entire advertising "
            "channel, imposing online criteria not equivalent to offline criteria). Total bans "
            "on all online sales void the exemption.",
            flag_conditions=["total ban on all online sales", "online-sales criteria stricter than offline criteria with no justification"]),
        PlaybookPoint(6, "Marketplace-specific bans",
            "Per Coty Germany (CJEU C-230/16) and the 2022 Vertical Guidelines §150-208: "
            "banning a specific third-party marketplace while permitting the distributor's own "
            "webstore and other online channels is a non-hardcore, potentially exempted "
            "restraint for qualitative selective distribution, subject to the Metro criteria "
            "(legitimate objective, applied uniformly, proportionate).",
            flag_conditions=["marketplace ban applied non-uniformly/discriminatorily",
                              "marketplace ban leaves the distributor with no viable alternative online channel"]),
        PlaybookPoint(7, "Dual pricing",
            "Under the 2022 VBER, charging a different wholesale price for online vs. offline "
            "resale is no longer automatically hardcore — but becomes one if the "
            "differential makes online sales unprofitable or is used to cap online sale "
            "volumes.",
            flag_conditions=["dual pricing differential large enough to make online resale commercially unviable"]),
        PlaybookPoint(8, "Non-compete duration",
            "VBER Art 5: non-compete obligations exceeding 5 years or of indefinite duration "
            "fall outside the block exemption (an 'excluded restriction,' not hardcore, but "
            "unprotected). Tacit renewal beyond 5 years is permissible under the 2022 VBER only "
            "if the buyer retains a genuine, practical ability to switch suppliers/renegotiate.",
            flag_conditions=["non-compete of indefinite duration or nominally 5 years with automatic renewal and no genuine exit mechanism"]),
        PlaybookPoint(9, "Selective distribution criteria",
            "Confirm the system is based on genuinely qualitative criteria necessary for the "
            "product's nature (outside Art 101(1) altogether per Metro/Coty), or on "
            "quantitative criteria falling within VBER coverage (subject to the Art 4(c)/(d) "
            "hardcore checks).",
            flag_conditions=["quantitative/arbitrary criteria dressed up as 'qualitative' with no genuine link to product nature"]),
        PlaybookPoint(10, "Retail-level active/passive sales restriction",
            "VBER Art 4(c): restricting active or passive sales to end users by members of a "
            "selective distribution system at retail level is hardcore."),
        PlaybookPoint(11, "Most-favoured-nation / parity clauses",
            "Not addressed as hardcore under VBER but subject to individual Art 101(1) "
            "scrutiny, especially 'wide' MFNs referencing third-party platforms.",
            flag_conditions=["wide MFN/price-parity clause tied to third-party platforms with no case-specific efficiency justification"]),
        PlaybookPoint(12, "Agency vs. genuine distribution characterization",
            "Verify whether the arrangement is a genuine commercial agency (largely outside "
            "Art 101(1) per the 2022 Vertical Guidelines' agency test — no or limited "
            "financial/commercial risk assumed by the agent) misclassified as distribution to "
            "evade scrutiny, or vice versa."),
        PlaybookPoint(13, "Post-termination restrictions",
            "Non-compete/non-solicit clauses surviving termination are generally not covered by "
            "VBER at all and are assessed individually — often disfavoured beyond narrow "
            "protection periods.",
            flag_conditions=["post-termination non-compete/non-solicit with no time limit"]),
    ],
    instructions=(
        "The single highest-priority check is whether any hardcore restriction (VBER Art 4) is "
        "present — a single hardcore clause removes the ENTIRE agreement from block-exemption "
        "protection, not just that clause, creating a strong presumption of an Art 101(1) TFEU "
        "infringement. Always run the market-share gate (Art 3) first: above 30% for either party, "
        "the block exemption doesn't apply regardless of the clauses used, and the agreement needs "
        "individual justification under Art 101(3)."
    ),
)

PlaybookLibrary.register(DISTRIBUTION_AGREEMENT)
