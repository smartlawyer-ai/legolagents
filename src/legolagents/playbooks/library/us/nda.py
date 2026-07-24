"""Playbook: Mutual / One-Way NDA review (US law)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

US_NDA = Playbook(
    id            = "us_nda",
    title         = "NDA Review (US)",
    document_type = "non-disclosure agreement (mutual or one-way)",
    legal_domain  = "trade secrets / confidentiality",
    jurisdiction  = "us",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Definition of Confidential Information",
            "Scope and marking requirements; oral-disclosure treatment. Note that labeling "
            "something 'confidential' does not by itself confer trade-secret status — DTSA "
            "(18 U.S.C. §1836) and state UTSA statutes still require the info to have "
            "independent economic value from secrecy plus reasonable protective measures.",
            flag_conditions=["catch-all definition with no scope limit", "no marking/identification requirement"]),
        PlaybookPoint(2, "Standard exclusions / carve-outs",
            "Public domain, independently developed, rightfully received from a third party, "
            "legally compelled disclosure. Their absence is the single most common overreach.",
            flag_conditions=["missing one or more standard carve-outs"]),
        PlaybookPoint(3, "DTSA whistleblower immunity notice",
            "18 U.S.C. §1833(b)(3): any agreement governing trade secrets/confidential "
            "information (entered or updated after May 2016) must give notice of immunity for "
            "disclosure to a government official or attorney solely to report a suspected legal "
            "violation, or in a sealed court filing. Missing notice bars recovery of exemplary "
            "damages/fees against that signatory under DTSA.",
            flag_conditions=["no DTSA §1833(b) notice included"]),
        PlaybookPoint(4, "Purpose / permitted-use limitation",
            "A narrow 'Purpose' definition prevents information being used outside the stated "
            "evaluation or negotiation."),
        PlaybookPoint(5, "Term of the confidentiality obligation",
            "Market norm for ordinary confidential info: 1-5 years post-disclosure/termination. "
            "Genuine trade secrets may be protected indefinitely provided secrecy is maintained.",
            flag_conditions=["perpetual/indefinite term applied to all information, not just genuine trade secrets"]),
        PlaybookPoint(6, "Residuals clause",
            "Allows the recipient to use retained 'residual' knowledge from unaided memory. "
            "Can gut confidentiality protection if drafted too broadly.",
            flag_conditions=["residuals clause broad enough to license use of any retained idea or know-how"]),
        PlaybookPoint(7, "Return / destruction of materials",
            "Obligation to return or destroy disclosed materials, with reasonable carve-outs for "
            "backups and litigation-hold/preservation duties."),
        PlaybookPoint(8, "Hidden non-solicit / no-hire / non-compete",
            "Naked no-poach or wage-fixing terms between employers can be treated as per se "
            "Sherman Act §1 violations; a non-compete disguised as a confidentiality restriction "
            "is void under California Bus. & Prof. Code §16600 (expanded by AB 1076/SB 699, "
            "eff. 1/1/2024, with extraterritorial reach) if California law governs.",
            flag_conditions=["non-solicit/no-hire/non-compete terms embedded in an NDA",
                              "restraint likely void under CA §16600 if CA-governed"]),
        PlaybookPoint(9, "Mutuality of obligations",
            "In a 'mutual' NDA, verify both parties actually have symmetric obligations, "
            "remedies, and carve-outs — not just symmetric labeling.",
            flag_conditions=["one-sided obligations mislabeled as mutual"]),
        PlaybookPoint(10, "Remedies — injunctive relief / bond waiver",
            "Stipulated irreparable-harm language is common but doesn't guarantee a court will "
            "grant injunctive relief (a discretionary equitable remedy).",
            flag_conditions=["bond waiver or injunctive-relief clause benefiting only the disclosing party"]),
        PlaybookPoint(11, "Governing law / venue",
            "Delaware courts strongly enforce chosen governing law/forum where it bears 'some "
            "material relationship' to the transaction; such clauses generally bind only "
            "signatories, not non-signatory affiliates absent direct-benefit/alter-ego facts."),
        PlaybookPoint(12, "Assignment / affiliates",
            "Does confidentiality bind/benefit affiliates and successors; is assignment "
            "permitted on a change of control."),
        PlaybookPoint(13, "No license / no warranty of accuracy",
            "Standard boilerplate disclaiming that disclosure grants any IP license or "
            "warrants the accuracy of disclosed information."),
    ],
    instructions=(
        "Flag state-law variance explicitly rather than assuming a single national rule: "
        "California (B&P §16600) voids almost all employee noncompetes and reaches extraterritorially; "
        "New York has no UTSA — trade secret claims proceed under common law only, with no statutory "
        "whistleblower fee-shifting beyond federal DTSA and no inevitable-disclosure doctrine. "
        "This playbook is grounded in general US federal law (DTSA) plus commonly-cited state variance "
        "(Delaware, California, New York) — always confirm the actual governing-law clause before applying "
        "state-specific conclusions."
    ),
)

PlaybookLibrary.register(US_NDA)
