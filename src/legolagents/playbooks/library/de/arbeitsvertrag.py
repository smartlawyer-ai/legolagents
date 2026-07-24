"""Playbook: Arbeitsvertrag-Prüfung (deutsches Recht)."""

from ...base import Playbook, PlaybookLibrary, PlaybookPoint

ARBEITSVERTRAG = Playbook(
    id            = "de_arbeitsvertrag",
    title         = "Prüfung Arbeitsvertrag",
    document_type = "Arbeitsvertrag",
    legal_domain  = "Arbeitsrecht",
    jurisdiction  = "de",
    output_format = "both",
    points=[
        PlaybookPoint(1, "Nachweisgesetz-Pflichtangaben",
            "Alle wesentlichen Vertragsbedingungen (Parteien, Beginn, bei Befristung: Dauer, "
            "Arbeitsort, Tätigkeitsbeschreibung, Vergütungsbestandteile, Arbeitszeit, "
            "Urlaubsanspruch, Kündigungsfristen, anwendbare Tarifverträge) gemäß NachwG in der "
            "seit 1. August 2022 geltenden, erweiterten Fassung (ca. 15 Pflichtangaben); "
            "Verstöße sind seither bußgeldbewehrt (bis zu 2.000 € je Verstoß und Arbeitnehmer).",
            flag_conditions=["fehlende Pflichtangaben, insbesondere Kündigungsfrist oder genaue Vergütungszusammensetzung"]),
        PlaybookPoint(2, "Form des Nachweises",
            "Seit 1. Januar 2025 (4. Bürokratieentlastungsgesetz) genügt für den "
            "Nachweisgesetz-Nachweis die Textform (§ 126b BGB), sofern zugänglich, "
            "speicherbar, ausdruckbar und eine Empfangsbestätigung angefordert wird; der "
            "Arbeitnehmer kann dennoch eine Papierform verlangen.",
            flag_conditions=["rein elektronischer Nachweis ohne Erfüllung der Zugänglichkeits-/Speicherbarkeitsvoraussetzungen"]),
        PlaybookPoint(3, "Befristung (Sachgrund vs. sachgrundlos)",
            "§ 14 TzBfG: sachgrundlose Befristung max. 2 Jahre mit max. 3 Verlängerungen, nur "
            "ohne vorheriges Beschäftigungsverhältnis mit demselben Arbeitgeber "
            "(Zuvorbeschäftigungsverbot); § 14 Abs. 4 TzBfG verlangt Schriftform für die "
            "Befristungsabrede selbst.",
            flag_conditions=["sachgrundlose Befristung über 2 Jahre oder mehr als 3 Verlängerungen",
                              "fehlende Schriftform der Befristungsabrede (Befristung fällt weg, Vertrag wird unbefristet)"]),
        PlaybookPoint(4, "Kündigungsfristen",
            "§ 622 BGB: Grundfrist 4 Wochen zum 15. oder Monatsende; für Arbeitgeberkündigungen "
            "gestaffelt nach Betriebszugehörigkeit (§ 622 Abs. 2: ab 2 Jahren 1 Monat, ab "
            "5 Jahren 2 Monate, bis 20 Jahre 7 Monate zum Monatsende).",
            flag_conditions=["Arbeitgeberkündigungsfrist kürzer als die gesetzliche Staffel",
                              "Arbeitnehmerkündigungsfrist länger als die des Arbeitgebers (§ 622 Abs. 6 BGB)"]),
        PlaybookPoint(5, "Kündigungsschutz (KSchG-Anwendbarkeit)",
            "§ 23 Abs. 1 KSchG: allgemeiner Kündigungsschutz nur bei regelmäßig mehr als 10 "
            "Arbeitnehmern (Teilzeitkräfte anteilig gewichtet: ≤20h = 0,5, ≤30h = 0,75, "
            ">30h = 1,0; Azubis zählen nicht mit).",
            flag_conditions=["Annahme der Nicht-Anwendbarkeit des KSchG ohne korrekte gewichtete Kopfzahl-Berechnung"]),
        PlaybookPoint(6, "Schriftform der Kündigung",
            "§ 623 BGB: Kündigung und Aufhebungsvertrag bedürfen der Schriftform (§ 126 BGB); "
            "die elektronische Form (§ 126a BGB) genügt ausdrücklich NICHT.",
            flag_conditions=["Vertragsklausel, die eine Kündigung per E-Mail/Textform zulässt (wäre nichtig)"]),
        PlaybookPoint(7, "Nachvertragliches Wettbewerbsverbot",
            "§§ 74 ff. HGB (analog auf alle Arbeitnehmer angewandt): § 74 Abs. 2 HGB verlangt "
            "eine Karenzentschädigung von mindestens 50% der zuletzt bezogenen "
            "Vergütung; max. Dauer i.d.R. 2 Jahre (§ 74a Abs. 1 S. 3 HGB); Schriftform und "
            "Aushändigung einer unterzeichneten Urkunde (§ 74 Abs. 1 HGB).",
            flag_conditions=["keine Karenzentschädigung zugesagt (Wettbewerbsverbot ist dann nichtig)",
                              "Karenzentschädigung unter der 50%-Grenze (Verbot ist dann unverbindlich, Arbeitnehmer hat ein Wahlrecht)",
                              "Dauer über 2 Jahre"]),
        PlaybookPoint(8, "Vertragsstrafeklauseln",
            "Als AGB unterliegen sie § 307 Abs. 1 BGB (Transparenzgebot); nach BAG-Rechtsprechung "
            "ist eine Vertragsstrafe, die die Vergütung während der Kündigungsfrist deutlich "
            "übersteigt, nur ausnahmsweise angemessen.",
            flag_conditions=["Vertragsstrafe deutlich über der Vergütung der Kündigungsfrist",
                              "unklare oder pauschale Auslöser-Formulierung"]),
        PlaybookPoint(9, "Ausschlussfristen (Verfallklauseln)",
            "§ 307 BGB: eine einstufige Ausschlussfrist unter 3 Monaten ist regelmäßig "
            "unwirksam; § 3 MiLoG schließt Mindestlohnansprüche generell von "
            "Verfallklauseln aus; Vorsatzhaftung kann nicht ausgeschlossen werden (§ 202 "
            "Abs. 1, § 276 Abs. 3 BGB).",
            flag_conditions=["Ausschlussfrist kürzer als 3 Monate",
                              "Klausel erfasst auch Mindestlohnansprüche (insoweit unwirksam)"]),
        PlaybookPoint(10, "Mindestlohn-Konformität",
            "MiLoG; nach Beschluss der Mindestlohnkommission vom 27. Juni 2025 steigt der "
            "gesetzliche Mindestlohn zum 1. Januar 2026 auf 13,90 €/Stunde und zum "
            "1. Januar 2027 auf 14,60 €/Stunde.",
            flag_conditions=["Monatsgehalt geteilt durch vereinbarte Arbeitsstunden unterschreitet den jeweils gültigen Mindestlohn"]),
        PlaybookPoint(11, "AGG-Konformität",
            "Allgemeines Gleichbehandlungsgesetz: Diskriminierungsverbot wegen ethnischer "
            "Herkunft, Geschlecht, Religion, Behinderung, Alter, sexueller Identität; "
            "AGG-Ansprüche verjähren regelmäßig binnen 2 Monaten nach Zugang einer Ablehnung.",
            flag_conditions=["Anforderungen ohne objektive Rechtfertigung, die mittelbar diskriminieren (z.B. 'Muttersprache Deutsch')"]),
        PlaybookPoint(12, "Betriebsrat-Mitbestimmungsrechte",
            "BetrVG § 99 (Zustimmungserfordernis bei Einstellung/Versetzung/Ein-Umgruppierung), "
            "§ 87 (Mitbestimmung bei Arbeitszeit, Vergütungsgrundsätzen), § 102 (Anhörung vor "
            "jeder Kündigung — ohne diese ist die Kündigung unheilbar unwirksam)."),
        PlaybookPoint(13, "Nebentätigkeit",
            "Ein pauschales Verbot jeder Nebentätigkeit ist regelmäßig unwirksam (§ 307 BGB) — "
            "zulässig ist nur die Beschränkung konkurrierender oder leistungsbeeinträchtigender "
            "Tätigkeiten.",
            flag_conditions=["absolutes Verbot jeder Nebentätigkeit ohne Bezug zu Konkurrenz/Leistungsfähigkeit"]),
    ],
    instructions=(
        "Zwei Fallstricke verdienen besondere Aufmerksamkeit: erstens die Unterscheidung zwischen "
        "Nachweisgesetz (seit 2025 Textform genügt) und § 623 BGB-Kündigung (weiterhin zwingend "
        "Schriftform) — beides wird in der Praxis häufig verwechselt. Zweitens die zweistufige "
        "Rechtsfolge bei fehlender/unzureichender Karenzentschädigung (§ 74 Abs. 2 HGB): "
        "vollständiges Fehlen macht das Wettbewerbsverbot nichtig, eine zu niedrige Entschädigung "
        "macht es nur unverbindlich (Wahlrecht des Arbeitnehmers) — diese beiden Fälle sollten als "
        "unterschiedlich schwere Warnhinweise behandelt werden."
    ),
)

PlaybookLibrary.register(ARBEITSVERTRAG)
