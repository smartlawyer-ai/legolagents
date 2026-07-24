"""Playbook: Employment Contract review (England & Wales law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

UK_EMPLOYMENT_CONTRACT = Playbook(
    id            = "uk_employment_contract",
    title         = "Employment Contract Review (UK)",
    document_type = "employment contract",
    legal_domain  = "employment law",
    jurisdiction  = "uk",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Written statement of particulars (day 1)",
            "Employment Rights Act 1996 s.1 (as amended by the Good Work Plan reforms, "
            "effective 6 April 2020): must be given no later than the first day of employment "
            "and cover around 15 mandatory particulars (pay, hours, holiday, place of work, "
            "notice, disciplinary/grievance procedures, pension, probation…).",
            flag_conditions=["missing mandatory particulars", "statement provided late"]),
        PlaybookPoint(2, "Notice periods",
            "ERA 1996 s.86 sets statutory minimum notice (scaling from 1 week per year of "
            "service up to 12 weeks employer-to-employee after 2 years). Contractual notice can "
            "exceed but not undercut the statutory minimum.",
            flag_conditions=["contractual notice below the statutory minimum",
                              "grossly asymmetric notice between employer and employee"]),
        PlaybookPoint(3, "Probationary period",
            "No standalone statute, but interacts with the unfair dismissal qualifying period "
            "under ERA 1996 Part X — currently 2 years, reducing to 6 months from 1 January 2027 "
            "under the Employment Rights Act 2025.",
            flag_conditions=["probation drafted only around the old 2-year threshold with no review of the 2027 change"]),
        PlaybookPoint(4, "Unfair dismissal / disciplinary and grievance procedure",
            "ERA 1996 Part X plus the ACAS Code of Practice on Disciplinary and Grievance "
            "Procedures (statutory footing under TULR(C)A 1992 s.207 — tribunals can adjust "
            "awards up to 25% for unreasonable failure to follow it). A clause purporting to "
            "waive unfair dismissal rights is void (ERA 1996 s.203) except via a settlement "
            "agreement or ACAS COT3.",
            flag_conditions=["contract silent on or inconsistent with the ACAS Code procedure",
                              "attempted contracting-out of unfair dismissal rights"]),
        PlaybookPoint(5, "Post-termination restrictive covenants",
            "Common-law restraint of trade: Nordenfelt v Maxim Nordenfelt [1894] AC 535; "
            "Herbert Morris Ltd v Saxelby [1916] AC 688 (no protection for mere competition, "
            "only legitimate interests); Egon Zehnder Ltd v Tillman [2019] UKSC 32 (tightened "
            "severance test). Not currently subject to any statutory cap — a Nov. 2025 "
            "government working paper is consulting on options, but no legislation is in force.",
            flag_conditions=["covenant exceeding roughly 6-12 months with no strong justification",
                              "non-compete applied to a junior/low-paid employee with no client contact or confidential access"]),
        PlaybookPoint(6, "Equality Act 2010 compliance",
            "s.4 (protected characteristics), s.39 (employer duties), ss.13/19 (direct/indirect "
            "discrimination), ss.20-22 (reasonable adjustments for disability).",
            flag_conditions=["contractual term that indirectly discriminates against a protected group"]),
        PlaybookPoint(7, "Working time, holiday, and rest breaks",
            "Working Time Regulations 1998 (SI 1998/1833): reg 4 (48-hour average weekly limit, "
            "opt-out under reg 5 requiring separate written, revocable consent), reg 13/13A "
            "(5.6 weeks statutory annual leave). The 2024 reforms introduced the 12.07% accrual "
            "method for irregular-hours/part-year workers.",
            flag_conditions=["48-hour opt-out buried in the main contract with no standalone revocable consent",
                              "holiday accrual miscalculated for irregular-hours workers under the 2024 rules"]),
        PlaybookPoint(8, "National Minimum/Living Wage compliance",
            "National Minimum Wage Act 1998 and Regulations 2015 (SI 2015/621); rates reviewed "
            "annually.",
            flag_conditions=["deductions (uniforms, training costs) bringing effective pay below NMW/NLW"]),
        PlaybookPoint(9, "TUPE — business transfer provisions",
            "Transfer of Undertakings (Protection of Employment) Regulations 2006 (SI 2006/246): "
            "reg 4 (automatic transfer on a relevant transfer), reg 7 (transfer-connected "
            "dismissal automatically unfair absent an ETO reason), reg 13 (information and "
            "consultation duty).",
            flag_conditions=["contract silent on what happens on a business sale/outsourcing",
                              "term varied 'because of the transfer' with no ETO reason"]),
        PlaybookPoint(10, "Garden leave / PILON",
            "Garden leave is an express contractual right, not implied. Since 2018 all PILON "
            "payments are subject to income tax and Class 1 NIC under the PENP regime "
            "(Income Tax (Earnings and Pensions) Act 2003 ss.402A-402D) regardless of whether a "
            "PILON clause exists.",
            flag_conditions=["no PILON clause at all (forces wrongful-dismissal exposure on immediate termination)"]),
        PlaybookPoint(11, "IP and inventions",
            "Patents Act 1977 ss.39-43 (inventor owns rights unless made in the normal course of "
            "duties, subject to the s.40 compensation regime for outstanding-benefit inventions); "
            "Copyright, Designs and Patents Act 1988 s.11(2) (employer owns copyright in works "
            "created in the course of employment, absent agreement otherwise)."),
        PlaybookPoint(12, "Whistleblowing protection",
            "ERA 1996 Part IVA (inserted by the Public Interest Disclosure Act 1998); s.43J "
            "voids any provision precluding a protected disclosure.",
            flag_conditions=["disciplinary clause allowing dismissal for any third-party disclosure with no carve-out"]),
        PlaybookPoint(13, "Pensions auto-enrolment",
            "Pensions Act 2008 Part 1; opt-out inducements are prohibited (s.54)."),
    ],
    instructions=(
        "UK employment is not 'at-will' — there is always a statutory notice requirement (ERA 1996 "
        "s.86) and, after the qualifying period, substantive unfair dismissal protection through the "
        "Employment Tribunal system. The Employment Rights Act 2025 is being implemented in phases "
        "through 2027 (day-one SSP from April 2026; 6-month unfair dismissal qualifying period and "
        "automatically-unfair fire-and-rehire from 1 January 2027) — date-stamp any clause referencing "
        "these thresholds and flag if it assumes the pre-reform rules."
    ),
)

PlaybookLibrary.register(UK_EMPLOYMENT_CONTRACT)
