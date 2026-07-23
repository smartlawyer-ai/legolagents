"""
Tests — legolagents.ontology
"""

import pytest

from legolagents.ontology import (
    Authority,
    LegalRelation,
    LegalSource,
    RelationType,
    SourceType,
)


class TestSourceTypeAndAuthority:
    def test_source_types_exist(self):
        assert SourceType.STATUTE == "statute"
        assert SourceType.CASE_LAW == "case_law"
        assert SourceType.CONSTITUTION == "constitution"
        assert SourceType.TREATY == "treaty"
        assert SourceType.REGULATION == "regulation"
        assert SourceType.ADMINISTRATIVE == "administrative"
        assert SourceType.DOCTRINE == "doctrine"

    def test_authority_levels_exist(self):
        assert Authority.BINDING == "binding"
        assert Authority.PERSUASIVE == "persuasive"
        assert Authority.INFORMATIVE == "informative"


class TestLegalSource:
    def test_minimal_construction(self):
        src = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        assert src.ref == "L1235-3"
        assert src.type == SourceType.STATUTE
        assert src.authority == Authority.BINDING
        assert src.relations == []

    def test_civil_law_vs_common_law_authority(self):
        """The same case_law type flips authority depending on the legal tradition."""
        civil_law_case = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        common_law_case = LegalSource(ref="Roe v. Wade", type=SourceType.CASE_LAW, authority=Authority.BINDING)
        assert civil_law_case.type == common_law_case.type
        assert civil_law_case.authority != common_law_case.authority

    def test_relates_to_with_enum(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        case = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        result = case.relates_to(statute, how=RelationType.INTERPRETS)
        assert result is case  # chainable
        assert len(case.relations) == 1
        assert case.relations[0].type == RelationType.INTERPRETS
        assert case.relations[0].target_ref == "L1235-3"

    def test_relates_to_with_string(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        case = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        case.relates_to(statute, how="interprets")
        assert case.relations[0].type == RelationType.INTERPRETS

    def test_relates_to_invalid_string_raises(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        case = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        with pytest.raises(ValueError):
            case.relates_to(statute, how="not_a_real_relation")

    def test_chained_relations(self):
        old_case = LegalSource(ref="17-19.860", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        new_case = (
            LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
            .relates_to(old_case, how="overturns")
        )
        assert len(new_case.relations) == 1
        assert new_case.relations[0].type == RelationType.OVERTURNS

    def test_to_markdown_includes_authority_badge(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING, title="Severance cap")
        md = statute.to_markdown()
        assert "L1235-3" in md
        assert "statute" in md
        assert "binding" in md
        assert "Severance cap" in md

    def test_to_markdown_includes_relations(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        case = LegalSource(ref="21-14.027", type=SourceType.CASE_LAW, authority=Authority.PERSUASIVE)
        case.relates_to(statute, how="interprets")
        md = case.to_markdown()
        assert "interprets" in md
        assert "L1235-3" in md

    def test_to_markdown_no_relations(self):
        statute = LegalSource(ref="L1235-3", type=SourceType.STATUTE, authority=Authority.BINDING)
        md = statute.to_markdown()
        assert "↳" not in md
