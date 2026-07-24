"""Playbook: Geheimhaltungsvereinbarung / NDA-Prüfung (deutsches Recht)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

GEHEIMHALTUNGSVEREINBARUNG = Playbook(
    id            = "de_geheimhaltungsvereinbarung",
    title         = "Prüfung Geheimhaltungsvereinbarung (NDA)",
    document_type = "Geheimhaltungsvereinbarung (NDA)",
    legal_domain  = "Geschäftsgeheimnisschutz",
    jurisdiction  = "de",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Definition des Geschäftsgeheimnisses",
            "Reichweite der als vertraulich definierten Informationen; Bezug zu tatsächlichen "
            "Geheimhaltungsmaßnahmen. Ein Geschäftsgeheimnis muss geheim, von wirtschaftlichem "
            "Wert und Gegenstand angemessener Geheimhaltungsmaßnahmen sein (§ 2 Nr. 1 GeschGehG).",
            flag_conditions=["pauschale Definition ohne jede Eingrenzung", "kein Bezug zu Geheimhaltungsmaßnahmen"]),
        PlaybookPoint(2, "Gegenseitigkeit",
            "Ob die Pflichten wechselseitig (bei tatsächlichem gegenseitigen Informationsaustausch) "
            "oder einseitig ausgestaltet sind.",
            flag_conditions=["einseitige NDA trotz faktisch gegenseitigem Informationsaustausch"]),
        PlaybookPoint(3, "Ausnahmen vom Geheimnisschutz",
            "Gesetzliche Ausnahmen müssen erhalten bleiben: Meinungsfreiheit, Aufdeckung "
            "rechtswidriger Handlungen im öffentlichen Interesse, Offenlegung gegenüber "
            "Arbeitnehmervertretungen (§ 5 GeschGehG); Hinweisgeberschutzgesetz (HinSchG, "
            "in Kraft seit 2. Juli 2023).",
            flag_conditions=["keine Ausnahme für Whistleblowing, gesetzliche Offenlegungspflichten oder Betriebsratsbeteiligung"]),
        PlaybookPoint(4, "Vertragsstrafe",
            "Höhe und auslösendes Verhalten. §§ 339, 343 BGB (richterliche Herabsetzung "
            "überhöhter Vertragsstrafen); bei AGB-Charakter: § 307 Abs. 1 BGB "
            "(Transparenzgebot).",
            flag_conditions=["pauschale Vertragsstrafe für 'jeden Verstoß' ohne Differenzierung",
                              "keine Obergrenze der Vertragsstrafe"]),
        PlaybookPoint(5, "Einordnung als AGB",
            "Wird die NDA als Formularvertrag für mehrere Geschäftsvorfälle verwendet? "
            "§§ 305 ff. BGB greifen dann auch im B2B-Verhältnis (§ 310 Abs. 1 BGB schließt "
            "nur die Kataloge der §§ 308, 309 BGB aus, nicht die Generalklausel des § 307 BGB).",
            flag_conditions=["einseitige Formularklausel ohne Aushandlung, die vom gesetzlichen Interessenausgleich abweicht"]),
        PlaybookPoint(6, "Laufzeit der Geheimhaltungspflicht",
            "Kein gesetzliches Höchstmaß, aber eine unbefristete Pflicht in einer "
            "Formularklausel kann als unangemessene Benachteiligung (§ 307 BGB) gewertet "
            "werden. Marktüblich: 2-5 Jahre nach Offenlegung/Vertragsende.",
            flag_conditions=["unbefristete Geheimhaltungspflicht ohne Bezug zu einem echten Geschäftsgeheimnis"]),
        PlaybookPoint(7, "Rückgabe- und Löschungspflichten",
            "Pflicht zur Rückgabe/Vernichtung vertraulicher Unterlagen und Datenträger bei "
            "Vertragsende, inkl. Nachweis-/Bestätigungsmechanismus."),
        PlaybookPoint(8, "Datenschutzrechtliche Klauseln",
            "Bei Weitergabe personenbezogener Daten: kein Widerspruch zu DSGVO-Grundlagen; "
            "ggf. separater Auftragsverarbeitungsvertrag (AVV) erforderlich."),
        PlaybookPoint(9, "Versteckte Wettbewerbsklauseln",
            "Abwerbeverbote oder Wettbewerbsverbote innerhalb der NDA. Bei Bindung "
            "individueller Arbeitnehmer gelten die Anforderungen der §§ 74 ff. HGB "
            "(Karenzentschädigung, siehe Arbeitsvertrags-Playbook); zwischen Unternehmen "
            "allgemeine Sittenwidrigkeitsgrenze (§ 138 BGB).",
            flag_conditions=["Abwerbe-/Wettbewerbsverbot ohne zeitliche oder räumliche Begrenzung"]),
        PlaybookPoint(10, "Haftungsbegrenzung",
            "§ 307 Abs. 2 BGB: Haftungsausschluss für Kardinalpflichten oder für Vorsatz/grobe "
            "Fahrlässigkeit ist unwirksam; § 276 Abs. 3 BGB (Vorsatzhaftung nicht im Voraus "
            "ausschließbar).",
            flag_conditions=["pauschaler Haftungsausschluss, der auch Vorsatz oder Kardinalpflichten erfasst"]),
        PlaybookPoint(11, "Anwendbares Recht und Gerichtsstand",
            "Rom I-VO für die Rechtswahl; § 38 ZPO für Gerichtsstandsvereinbarungen "
            "(nur zwischen Kaufleuten wirksam).",
            flag_conditions=["Gerichtsstandsklausel trotz Beteiligung eines Verbrauchers oder Nicht-Kaufmanns"]),
        PlaybookPoint(12, "Ausnahmen für öffentlich bekannte/unabhängig entwickelte Informationen",
            "Standardmäßige Freistellungsklauseln; Bezug zur GeschGehG-Definition (Information "
            "muss tatsächlich geheim sein).",
            flag_conditions=["keine Ausnahme für öffentlich bekannte oder unabhängig entwickelte Informationen"]),
    ],
    instructions=(
        "Die AGB-Kontrolle nach §§ 305 ff. BGB gilt für vorformulierte NDAs auch im reinen "
        "B2B-Verhältnis — ein wesentlicher Unterschied zur angelsächsischen Vertragsfreiheit. "
        "Der Whistleblower-Vorbehalt ist seit Inkrafttreten des HinSchG (2. Juli 2023) keine "
        "Kür mehr, sondern eine gesetzliche Notwendigkeit."
    ),
)

PlaybookLibrary.register(GEHEIMHALTUNGSVEREINBARUNG)
