"""
Tests — legolagents.tools
"""

import io
import zipfile
from pathlib import Path

import pytest

from legolagents.tools.base import Certainty, LegalCitation, LegalTool
from legolagents.tools.articles import normalize_code_name
from legolagents.tools.document import (
    EditInput,
    GenerateDocxTool,
    ReadDocumentTool,
    TabularAnalysisTool,
    TrackedChangesTool,
    _para_flat_text,
    _para_char_map,
)


# ── Certainty ─────────────────────────────────────────────────────────────────

class TestCertainty:
    def test_labels(self):
        assert Certainty.ESTABLISHED.label() == "✅ Established law"
        assert Certainty.TRENDING.label()    == "⚡ Trending"
        assert Certainty.ISOLATED.label()    == "⚠️ Isolated"
        assert Certainty.SUPERSEDED.label()  == "❌ Superseded"

    def test_from_payload_superseded(self):
        payload = {"superseded_by": {"number": "22-11111"}, "importance_score": 90}
        assert LegalTool.certainty_from_payload(payload) == Certainty.SUPERSEDED

    def test_from_payload_established(self):
        payload = {"importance_score": 75, "cited_by_count": 30, "publication": ["B"]}
        assert LegalTool.certainty_from_payload(payload) == Certainty.ESTABLISHED

    def test_from_payload_trending(self):
        payload = {"importance_score": 40, "cited_by_count": 8}
        assert LegalTool.certainty_from_payload(payload) == Certainty.TRENDING

    def test_from_payload_isolated(self):
        payload = {"importance_score": 5, "cited_by_count": 1}
        assert LegalTool.certainty_from_payload(payload) == Certainty.ISOLATED


# ── LegalCitation ─────────────────────────────────────────────────────────────

class TestLegalCitation:
    def test_markdown_with_url(self):
        c = LegalCitation(
            number="21-12345",
            date="2022-03-15",
            jurisdiction="Cour de cassation",
            chamber="Chambre sociale",
            solution="Cassation",
            url="https://smartlawyer.ai/jurisprudence/soc-2022-03-15",
        )
        md = c.to_markdown()
        assert "[Cour de cassation · Chambre sociale" in md
        assert "21-12345" in md
        assert "Cassation" in md
        assert "https://smartlawyer.ai" in md

    def test_markdown_without_url(self):
        c = LegalCitation(
            number="20-99999", date="2021-01-01",
            jurisdiction="CA Paris", chamber="Pôle 5",
        )
        md = c.to_markdown()
        assert "**CA Paris" in md
        assert "[" not in md.split("—")[0]   # pas de lien Markdown


# ── LegalTool helpers ─────────────────────────────────────────────────────────

class TestLegalToolHelpers:
    def setup_method(self):
        class _Concrete(LegalTool):
            name = "test"
            description = "test"
            inputs = {}
            output_type = "string"
            def forward(self): return ""
        self.tool = _Concrete()

    def test_fmt_decision_with_url(self):
        result = self.tool.fmt_decision(
            number="21-12345", date="2022-03-15T00:00:00Z",
            jurisdiction="Cour de cassation", chamber="Chambre sociale",
            url="https://example.com/arrêt", solution="Cassation",
        )
        assert "[Cour de cassation" in result
        assert "Cassation" in result
        assert "https://example.com" in result

    def test_fmt_decision_without_url(self):
        result = self.tool.fmt_decision(
            number="20-11111", date="2021-06-01",
            jurisdiction="CA Paris", chamber="Pôle 5",
        )
        assert "**CA Paris" in result
        assert "[" not in result

    def test_fmt_article_with_url(self):
        result = self.tool.fmt_article(code="Code du travail", number="L1235-3", url="https://x.fr")
        assert "[Art. L1235-3" in result

    def test_fmt_article_without_url(self):
        result = self.tool.fmt_article(code="Code civil", number="1240")
        assert "**Art. 1240" in result

    def test_fmt_date(self):
        assert self.tool.fmt_date("2022-03-15") == "15/03/2022"
        assert self.tool.fmt_date("") == ""
        assert self.tool.fmt_date("bad") == "bad"


# ── Code alias normalization ──────────────────────────────────────────────────

class TestNormalizeCode:
    def test_alias_travail(self):
        assert normalize_code_name("travail") == "Code du travail"

    def test_alias_civil(self):
        assert normalize_code_name("civil") == "Code civil"

    def test_full_name_passthrough(self):
        assert normalize_code_name("Code de commerce") == "Code de commerce"

    def test_case_insensitive(self):
        assert normalize_code_name("CIVIL") == "Code civil"


# ── ReadDocumentTool ──────────────────────────────────────────────────────────

class TestReadDocumentTool:
    def test_file_not_found(self):
        tool   = ReadDocumentTool()
        result = tool.forward("/tmp/does_not_exist_xyz.pdf")
        assert "❌" in result
        assert "not found" in result.lower()

    def test_unsupported_format(self, tmp_path):
        f = tmp_path / "file.xls"
        f.write_bytes(b"fake")
        result = ReadDocumentTool().forward(str(f))
        assert "❌" in result
        assert "unsupported" in result.lower()

    def test_read_txt(self, tmp_path):
        f = tmp_path / "doc.txt"
        f.write_text("Bonjour le monde juridique", encoding="utf-8")
        result = ReadDocumentTool().forward(str(f))
        assert "Bonjour" in result


# ── GenerateDocxTool ──────────────────────────────────────────────────────────

class TestGenerateDocxTool:
    def test_generates_docx(self, tmp_path):
        out = str(tmp_path / "output.docx")
        result = GenerateDocxTool().forward(
            title="Test Document",
            sections=[
                {"heading": "Section 1", "content": "Contenu de test", "level": 1},
                {"heading": "Tableau", "content": "", "level": 2,
                 "table": {"headers": ["Col A", "Col B"], "rows": [["v1", "v2"]]}},
            ],
            output_path=out,
        )
        assert "✅" in result
        assert Path(out).exists()
        # Vérifier que c'est un vrai DOCX (ZIP valide)
        with zipfile.ZipFile(out) as z:
            assert "word/document.xml" in z.namelist()


# ── TrackedChangesTool ────────────────────────────────────────────────────────

def _make_docx(paragraph_text: str) -> bytes:
    """Crée un DOCX minimal en mémoire avec un seul paragraphe."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t xml:space="preserve">{paragraph_text}</w:t></w:r>
    </w:p>
  </w:body>
</w:document>""".encode("utf-8")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", """<?xml version="1.0"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        z.writestr("_rels/.rels", """<?xml version="1.0"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="word/document.xml"/>
</Relationships>""")
        z.writestr("word/document.xml", doc_xml)
    return buf.getvalue()


class TestTrackedChangesTool:
    def test_file_not_found(self):
        result = TrackedChangesTool().forward(
            input_path="/nonexistent.docx",
            edits=[{"find": "x", "replace": "y"}],
        )
        assert "❌" in result

    def test_wrong_format(self, tmp_path):
        f = tmp_path / "doc.pdf"
        f.write_bytes(b"fake")
        result = TrackedChangesTool().forward(input_path=str(f), edits=[])
        assert "❌" in result

    def test_no_valid_edits(self, tmp_path):
        f = tmp_path / "doc.docx"
        f.write_bytes(_make_docx("Bonjour monde"))
        result = TrackedChangesTool().forward(input_path=str(f), edits=[])
        assert "❌" in result

    def test_apply_tracked_change(self, tmp_path):
        """Test principal : vérifie que w:del et w:ins sont injectés dans le XML."""
        src = tmp_path / "contrat.docx"
        src.write_bytes(_make_docx("dans un délai de 30 jours suivant la commande"))
        out = str(tmp_path / "contrat_tracked.docx")

        result = TrackedChangesTool().forward(
            input_path=str(src),
            edits=[{
                "find":           "30 jours",
                "replace":        "15 jours ouvrés",
                "context_before": "délai de ",
                "context_after":  " suivant",
                "reason":         "Pratique de marché",
            }],
            output_path=out,
            author="TestAgent",
        )

        assert "✅" in result
        assert Path(out).exists()

        # Vérifier le XML modifié
        with zipfile.ZipFile(out) as z:
            xml = z.read("word/document.xml").decode("utf-8")

        assert "w:del" in xml,   "w:del manquant — texte supprimé non marqué"
        assert "w:ins" in xml,   "w:ins manquant — texte inséré non marqué"
        assert "30 jours" in xml, "texte original devrait être dans w:del"
        assert "15 jours ouvrés" in xml, "nouveau texte devrait être dans w:ins"
        assert "TestAgent" in xml, "auteur devrait être dans les attributs"

    def test_text_not_found(self, tmp_path):
        """Une modification dont le texte n'existe pas retourne une erreur partielle, pas un crash."""
        src = tmp_path / "doc.docx"
        src.write_bytes(_make_docx("Texte quelconque"))

        result = TrackedChangesTool().forward(
            input_path=str(src),
            edits=[{"find": "texte inexistant XYZ", "replace": "nouveau"}],
        )
        assert "❌" in result or "non trouvé" in result.lower()

    def test_multiple_edits(self, tmp_path):
        """Plusieurs modifications sur le même document."""
        src = tmp_path / "doc.docx"
        src.write_bytes(_make_docx("Le délai est de 30 jours et le prix est de 100 euros"))
        out = str(tmp_path / "doc_tracked.docx")

        result = TrackedChangesTool().forward(
            input_path=str(src),
            edits=[
                {"find": "30 jours",  "replace": "15 jours ouvrés"},
                {"find": "100 euros", "replace": "120 euros HT"},
            ],
            output_path=out,
        )
        assert "✅" in result

        with zipfile.ZipFile(out) as z:
            xml = z.read("word/document.xml").decode("utf-8")
        assert xml.count("w:del") >= 1


# ── TabularAnalysisTool ───────────────────────────────────────────────────────

class TestTabularAnalysisTool:
    def test_empty_inputs(self):
        result = TabularAnalysisTool().forward(documents=[], columns=[])
        assert "❌" in result

    def test_produces_markdown_table(self, tmp_path):
        f1 = tmp_path / "doc1.txt"
        f2 = tmp_path / "doc2.txt"
        f1.write_text("Durée du bail : 9 ans. Loyer : 1500 euros.", encoding="utf-8")
        f2.write_text("Durée du bail : 6 ans. Loyer : 2000 euros.", encoding="utf-8")

        result = TabularAnalysisTool().forward(
            documents=[
                {"path": str(f1), "label": "Bail A"},
                {"path": str(f2), "label": "Bail B"},
            ],
            columns=[
                {"name": "Durée", "question": "Quelle est la durée du bail ?"},
                {"name": "Loyer", "question": "Quel est le montant du loyer ?"},
            ],
        )
        assert "| Document |" in result
        assert "Bail A" in result
        assert "Bail B" in result
        assert "Durée" in result
        assert "Loyer" in result
