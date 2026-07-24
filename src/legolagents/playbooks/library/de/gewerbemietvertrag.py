"""Playbook: Gewerbemietvertrag-Prüfung (deutsches Recht)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

GEWERBEMIETVERTRAG = Playbook(
    id            = "de_gewerbemietvertrag",
    title         = "Prüfung Gewerbemietvertrag",
    document_type = "Gewerbemietvertrag",
    legal_domain  = "Mietrecht",
    jurisdiction  = "de",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Schriftform des Vertrages",
            "§ 550 BGB: ein auf mehr als ein Jahr angelegter Mietvertrag, der die Schriftform "
            "nicht wahrt, gilt als auf unbestimmte Zeit geschlossen und ist ab dem ersten Jahr "
            "mit gesetzlicher Frist ordentlich kündbar — die gesamte Laufzeitsicherheit entfällt. "
            "Alle Anlagen/Nachträge müssen körperlich/logisch mit der Urkunde verbunden und "
            "unterzeichnet sein.",
            flag_conditions=["langfristiger Vertrag nur formlos vereinbart",
                              "Anlagen/Nachträge (z.B. Grundrisse, Nebenabreden) nicht ordnungsgemäß einbezogen/unterzeichnet"]),
        PlaybookPoint(2, "Mietstruktur (Festmiete, Staffelmiete, Indexmiete, Umsatzmiete)",
            "Indexmiete bei Gewerberaum richtet sich nicht nach § 557b BGB (nur Wohnraum), "
            "sondern nach dem Preisklauselgesetz (PrKG); § 3 PrKG regelt die "
            "Wirksamkeitsvoraussetzungen von Preisgleitklauseln.",
            flag_conditions=["Indexklausel fälschlich auf § 557b BGB gestützt (falsche Rechtsgrundlage für Gewerberaum)",
                              "Staffelmiete mit zusätzlicher Indexklausel ohne klare Vorrangregel"]),
        PlaybookPoint(3, "Betriebskosten",
            "Die BetrKV gilt für Gewerberaum nicht unmittelbar, nur als Auslegungshilfe; "
            "AGB-Kontrolle nach § 307 BGB bleibt bei Formularverträgen anwendbar.",
            flag_conditions=["Auffangklausel 'alle beim Vermieter anfallenden Kosten' ohne Aufzählung (Transparenzgebot)",
                              "Verwaltungskosten des Vermieters als 'Betriebskosten' getarnt"]),
        PlaybookPoint(4, "Schönheitsreparaturen und Instandhaltung",
            "§ 307 BGB-Inhaltskontrolle gilt auch bei Gewerberaum, wenn auch mit geringerem "
            "Schutzbedürfnis als bei Wohnraum; seit 6. März 2024 können echte, individuell "
            "ausgehandelte Quotenabgeltungsklauseln wieder wirksam sein.",
            flag_conditions=["Renovierungspflicht bei unrenoviert übergebenen Räumen ohne Ausgleich",
                              "starre Fristenpläne statt bedarfsabhängiger Formulierung"]),
        PlaybookPoint(5, "Konkurrenzschutz",
            "Nicht kodifiziert — aus dem allgemeinen Grundsatz von Treu und Glauben (§ 242 BGB) "
            "abgeleitet; wirksam nur bei präziser Definition des vertraglichen Mietzwecks.",
            flag_conditions=["vager oder fehlender Mietzweck (untergräbt jeden Konkurrenzschutz)",
                              "kein Konkurrenzschutz in einem Einkaufszentrum/Fachmarktzentrum-Kontext"]),
        PlaybookPoint(6, "Kündigungsfristen, Laufzeit und Optionsrechte",
            "Mangels abweichender Vereinbarung gilt für unbefristete Gewerbemietverhältnisse "
            "die vierteljährliche Kündigungsfrist nach § 580a BGB.",
            flag_conditions=["fehlende ausdrückliche Kündigungsfristregelung", "Optionsrecht ohne handhabbare Ausübungsfrist"]),
        PlaybookPoint(7, "Kündigung aus wichtigem Grund / Zahlungsverzug",
            "§ 543 Abs. 2 Nr. 3 BGB: fristlose Kündigung bei Verzug mit zwei aufeinander "
            "folgenden Terminen in Höhe von mehr als einer Monatsmiete oder anhaltendem "
            "Rückstand über zwei Monatsmieten.",
            flag_conditions=["Klausel erlaubt sofortige Kündigung bereits bei geringfügigem, "
                              "einmaligem Zahlungsverzug unterhalb der gesetzlichen Schwelle"]),
        PlaybookPoint(8, "Kaution / Mietsicherheit",
            "Kein gesetzlicher Höchstbetrag bei Gewerberaum (anders als § 551 BGB bei "
            "Wohnraum, 3 Monatsnettomieten) — grundsätzlich frei verhandelbar.",
            flag_conditions=["überhöhte Kaution kombiniert mit zusätzlicher Vertragsstrafe ohne marktübliche Begründung"]),
        PlaybookPoint(9, "Gewährleistung und Haftungsausschluss",
            "§§ 536 ff. BGB (Sachmängelhaftung) mit größerem vertraglichen Gestaltungsspielraum "
            "als bei Wohnraum; § 307 Abs. 2 BGB verbietet dennoch den Ausschluss der Haftung "
            "für Vorsatz/grobe Fahrlässigkeit oder Kardinalpflichten.",
            flag_conditions=["pauschaler Ausschluss jeder Vermieterhaftung, auch für Vorsatz/grobe Fahrlässigkeit"]),
        PlaybookPoint(10, "Untervermietung / Nutzungsänderung",
            "§ 540 BGB: Untervermietung bedarf der Zustimmung des Vermieters; unberechtigte "
            "Verweigerung kann ein Sonderkündigungsrecht des Mieters auslösen.",
            flag_conditions=["absolutes Untervermietungsverbot ohne Zustimmungsmaßstab"]),
        PlaybookPoint(11, "Instandhaltung von Dach und Fach",
            "Die Verlagerung struktureller Instandhaltung (Dach, Fassade, tragende Teile) auf "
            "den Mieter per AGB ist nach ständiger Rechtsprechung regelmäßig unwirksam "
            "(§ 307 BGB) — nur Instandhaltung im Innenbereich ist übertragbar.",
            flag_conditions=["Formularklausel verlagert Dach-/Fassaden-/Tragwerksinstandhaltung auf den Mieter"]),
        PlaybookPoint(12, "Selbsthilfe- und Räumungsklauseln",
            "Eigenmächtige Besitzentziehung (§ 858 BGB) ist unzulässig — der Vermieter kann "
            "sich kein Selbsthilferecht (Schlösser austauschen, Räumung ohne Titel) "
            "vertraglich einräumen.",
            flag_conditions=["Klausel gestattet dem Vermieter Schlossaustausch/Räumung ohne gerichtlichen Titel (nichtig)"]),
        PlaybookPoint(13, "AGB-Einordnung des gesamten Vertrages",
            "§§ 305 ff. BGB gelten auch für Gewerberaum-Formularverträge; § 310 Abs. 1 BGB "
            "schließt nur die Kataloge der §§ 308, 309 BGB aus, nicht die "
            "Generalklausel des § 307 BGB.",
            flag_conditions=["unveränderte Vermieter-Vorlage mit einseitiger Risikoverteilung (alle Kosten-/Strukturrisiken beim Mieter)"]),
    ],
    instructions=(
        "§ 550 BGB (Schriftform) ist die wichtigste Falle im deutschen Gewerbemietrecht — anders "
        "als im angelsächsischen Recht kann ein Formmangel die gesamte vereinbarte Festlaufzeit "
        "zunichtemachen. Prüfen Sie IMMER zuerst, ob Urkunde und sämtliche Anlagen/Nachträge "
        "vollständig und durchgängig unterzeichnet sind, bevor andere Klauseln bewertet werden."
    ),
)

PlaybookLibrary.register(GEWERBEMIETVERTRAG)
