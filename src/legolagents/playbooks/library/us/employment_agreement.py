"""Playbook: Employment Agreement review (US law, at-will context)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

US_EMPLOYMENT_AGREEMENT = Playbook(
    id            = "us_employment_agreement",
    title         = "Employment Agreement Review (US)",
    document_type = "employment agreement (at-will)",
    legal_domain  = "employment law",
    jurisdiction  = "us",
    output_format = "both",
    points=[
        PlaybookPoint(1, "At-will statement and its real enforceability",
            "At-will is the default rule in nearly all states, but three common-law exceptions "
            "vary by state: public policy, implied contract (recognized in most states, often "
            "from handbook language), and implied covenant of good faith (a minority rule, e.g. "
            "CA, DE, MA). Montana requires good cause after a statutory probation period — not "
            "truly at-will. Florida recognizes none of the three exceptions.",
            flag_conditions=["at-will disclaimer contradicted by handbook/policy promises elsewhere"]),
        PlaybookPoint(2, "Compensation and wage-hour classification",
            "Base pay, bonus discretion, and exempt/non-exempt classification under the FLSA "
            "(29 U.S.C. §201 et seq.). Misclassification is a major and common exposure.",
            flag_conditions=["exemption test not clearly satisfied for the stated exempt classification"]),
        PlaybookPoint(3, "Post-employment non-compete",
            "Enforceability is entirely state-dependent since the FTC's 2024 noncompete rule was "
            "vacated (Ryan LLC v. FTC) and the FTC formally withdrew its appeals in Sept. 2025. "
            "California/North Dakota/Oklahoma/Minnesota ban or heavily restrict employee "
            "noncompetes; Massachusetts requires 'garden leave' pay (≥50% of highest annualized "
            "base salary) or other real consideration; Colorado/Illinois impose minimum-earnings "
            "thresholds; several states ban noncompetes for healthcare or low-wage workers.",
            flag_conditions=["noncompete against a low-wage or healthcare worker",
                              "no independent consideration for a restriction signed mid-employment"]),
        PlaybookPoint(4, "Non-solicitation (customer / employee)",
            "Narrower than a noncompete but still state-regulated under the same matrix "
            "(e.g. Massachusetts' garden-leave rule expressly excludes non-solicits)."),
        PlaybookPoint(5, "Invention assignment / IP ownership",
            "At least seven states (California Labor Code §2870, Delaware, Illinois, Kansas, "
            "Minnesota, North Carolina, Washington RCW 49.44.140) require a carve-out for "
            "inventions developed entirely on the employee's own time, without employer "
            "resources, unrelated to the employer's business — assignment clauses without this "
            "carve-out are void as to those inventions in those states.",
            flag_conditions=["invention-assignment clause with no statutory personal-invention carve-out"]),
        PlaybookPoint(6, "Confidentiality / trade secrets + DTSA notice",
            "18 U.S.C. §1833(b)(3) whistleblower-immunity notice — frequently missing from "
            "offer letters and employment agreements.",
            flag_conditions=["no DTSA §1833(b) notice"]),
        PlaybookPoint(7, "Arbitration clause / class-action waiver",
            "Generally enforceable under the FAA (Concepcion, Italian Colors) subject to "
            "generally applicable contract defenses. The Ending Forced Arbitration of Sexual "
            "Assault and Sexual Harassment Act (EFAA, 2022) voids pre-dispute arbitration and "
            "class/collective waivers specifically for those claims, retroactively.",
            flag_conditions=["arbitration clause with no EFAA carve-out for sexual assault/harassment claims"]),
        PlaybookPoint(8, "Termination, notice, and severance",
            "No general federal severance mandate. WARN Act (29 U.S.C. §2101) requires 60 days' "
            "notice for covered employers (100+ employees) on qualifying plant closings or mass "
            "layoffs; many states have 'mini-WARN' acts with lower thresholds (e.g. NY, CA)."),
        PlaybookPoint(9, "Non-disparagement / confidentiality of terms",
            "Overbroad clauses restricting discussion of wages/working conditions can violate "
            "NLRA Section 7 regardless of union status.",
            flag_conditions=["non-disparagement clause with no carve-out for protected concerted activity"]),
        PlaybookPoint(10, "Wage payment / expense reimbursement",
            "Check against state wage payment and collection acts, which vary significantly "
            "(e.g. California's specific final-pay-timing rules and penalties)."),
        PlaybookPoint(11, "Benefits / ERISA cross-references",
            "ERISA (29 U.S.C. §1001 et seq.) preempts conflicting state benefit-plan terms.",
            flag_conditions=["clause purporting to unilaterally modify ERISA plan terms"]),
        PlaybookPoint(12, "Governing law / dispute forum",
            "A foreign choice-of-law clause doesn't necessarily displace mandatory local "
            "employment protections (wage statutes, notice rules)."),
    ],
    instructions=(
        "Noncompete and non-solicit enforceability is the highest-variance item in US employment "
        "agreements — always identify the governing-law state before assessing enforceability, and "
        "flag explicitly where the law is state-dependent rather than asserting a single national rule."
    ),
)

PlaybookLibrary.register(US_EMPLOYMENT_AGREEMENT)
