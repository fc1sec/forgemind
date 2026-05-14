"""Tests for the disciplines taxonomy and its integration with the validator.

The taxonomy is ForgeMind's self-knowledge — these tests guard against:
  - Drift between coverage claims and what plugins actually implement
  - Schema breakage (malformed YAML, missing fields)
  - Silent regressions in the can_advise_on / must_escalate API
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from forgemind.cli.main import app
from forgemind.disciplines import (
    Coverage,
    DisciplineTaxonomy,
    get_taxonomy,
)
from forgemind.disciplines.taxonomy import load_taxonomy
from forgemind.epistemics import EpistemicValidator
from forgemind.plugins import PluginRegistry
from forgemind.plugins.ai_ml_pattern import AIMLReversePattern
from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern
from forgemind.plugins.software_pattern import SoftwareReversePattern

# ----------------------------------------------------------------------
# Loading + schema integrity
# ----------------------------------------------------------------------


class TestTaxonomyLoading:
    """Verify the bundled YAML loads and parses cleanly."""

    def test_default_taxonomy_loads(self):
        taxonomy = get_taxonomy()
        assert isinstance(taxonomy, DisciplineTaxonomy)
        assert taxonomy.version
        assert taxonomy.disciplines, "Taxonomy must declare at least one discipline"

    def test_taxonomy_has_expected_disciplines(self):
        taxonomy = get_taxonomy()
        expected = {
            "quality_management",
            "software_engineering",
            "ai_ml",
            "operations_methodops",
            "risk_management",
            "business_analysis",
        }
        missing = expected - set(taxonomy.disciplines.keys())
        assert not missing, f"Missing disciplines: {missing}"

    def test_taxonomy_has_out_of_scope_entries(self):
        taxonomy = get_taxonomy()
        assert taxonomy.out_of_scope, (
            "Taxonomy must declare at least one out-of-scope domain — "
            "honest disclosure of limitations is required"
        )
        # Sanity check on a few flagship out-of-scope entries
        ids = set(taxonomy.out_of_scope.keys())
        assert "nuclear_systems" in ids
        assert "medical_diagnosis" in ids
        assert "legal_advice" in ids

    def test_every_out_of_scope_has_rationale_and_escalation(self):
        taxonomy = get_taxonomy()
        for entry in taxonomy.list_out_of_scope():
            assert entry.reason, f"{entry.id} missing reason"
            assert entry.rationale, f"{entry.id} missing rationale"
            assert entry.escalate_to, f"{entry.id} missing escalate_to"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_taxonomy(tmp_path / "does_not_exist.yaml")


# ----------------------------------------------------------------------
# Coverage queries
# ----------------------------------------------------------------------


class TestCoverageQueries:
    """The questions other modules ask the taxonomy."""

    def test_iso9001_is_partial_with_cespi_variant(self):
        taxonomy = get_taxonomy()
        domain = taxonomy.get_domain("iso9001")
        assert domain is not None
        assert domain.coverage == Coverage.PARTIAL
        assert any(v.id == "cespi_unlp_8state" for v in domain.variants)

    def test_can_advise_on_partial_domain(self):
        taxonomy = get_taxonomy()
        assert taxonomy.can_advise_on("iso9001") is True

    def test_can_advise_on_unknown_domain_is_false(self):
        taxonomy = get_taxonomy()
        assert taxonomy.can_advise_on("totally_made_up_domain") is False

    def test_must_escalate_on_unknown_domain(self):
        taxonomy = get_taxonomy()
        assert taxonomy.must_escalate("totally_made_up_domain") is True

    def test_must_escalate_on_out_of_scope_domain(self):
        taxonomy = get_taxonomy()
        assert taxonomy.must_escalate("nuclear_systems") is True

    def test_must_escalate_false_for_partial_domain(self):
        """A partial domain is advice-eligible (with confidence label), not must-escalate."""
        taxonomy = get_taxonomy()
        assert taxonomy.must_escalate("iso9001") is False

    def test_escalation_contact_for_known_domain(self):
        taxonomy = get_taxonomy()
        contact = taxonomy.escalation_contact("iso9001")
        assert "ISO" in contact or "QMS" in contact

    def test_escalation_contact_fallback_for_unknown(self):
        taxonomy = get_taxonomy()
        contact = taxonomy.escalation_contact("totally_made_up_domain")
        assert contact == "Domain expert"

    def test_confidence_for_partial_domain(self):
        taxonomy = get_taxonomy()
        conf = taxonomy.confidence_for("iso9001")
        assert 0.0 < conf <= 1.0

    def test_confidence_for_unknown_domain_is_zero(self):
        taxonomy = get_taxonomy()
        assert taxonomy.confidence_for("totally_made_up_domain") == 0.0


# ----------------------------------------------------------------------
# Coverage-claim integrity — taxonomy must not lie about what we ship
# ----------------------------------------------------------------------


class TestCoverageClaimsMatchCode:
    """Guard against the taxonomy claiming expertise the code doesn't have."""

    def test_covered_or_partial_iso9001_has_plugin(self):
        """If taxonomy claims (partial) ISO 9001 coverage, the plugin must exist."""
        taxonomy = get_taxonomy()
        if taxonomy.can_advise_on("iso9001"):
            registry = PluginRegistry()
            registry.register(ISO9001ReversePattern)
            assert registry.has_pattern("iso9001")

    def test_covered_or_partial_software_has_plugin(self):
        taxonomy = get_taxonomy()
        if taxonomy.can_advise_on("software"):
            registry = PluginRegistry()
            registry.register(SoftwareReversePattern)
            assert registry.has_pattern("software")

    def test_covered_or_partial_ai_ml_has_plugin(self):
        taxonomy = get_taxonomy()
        if taxonomy.can_advise_on("ai_ml"):
            registry = PluginRegistry()
            registry.register(AIMLReversePattern)
            assert registry.has_pattern("ai_ml")


# ----------------------------------------------------------------------
# EpistemicValidator integration
# ----------------------------------------------------------------------


class TestValidatorUsesTaxonomy:
    """The validator must consult the taxonomy before allowing advice."""

    def test_validator_loads_taxonomy_lazily(self):
        validator = EpistemicValidator()
        # Property access triggers lazy load
        assert validator.taxonomy is not None

    def test_validator_treats_unknown_domain_as_unsupported(self):
        validator = EpistemicValidator()
        assert validator._is_unsupported_domain("totally_made_up_domain") is True

    def test_validator_treats_out_of_scope_as_unsupported(self):
        validator = EpistemicValidator()
        assert validator._is_unsupported_domain("nuclear_systems") is True

    def test_validator_treats_partial_domain_as_supported(self):
        validator = EpistemicValidator()
        # iso9001 is partial in the taxonomy — the validator must NOT reject
        # it as unsupported (otherwise we'd refuse to advise on it).
        assert validator._is_unsupported_domain("iso9001") is False

    def test_validator_escalation_routes_through_taxonomy(self):
        validator = EpistemicValidator()
        contact = validator._get_escalation_contact("iso9001")
        assert "ISO" in contact or "QMS" in contact


# ----------------------------------------------------------------------
# CLI commands
# ----------------------------------------------------------------------


class TestCapabilitiesCLI:
    """`forgemind capabilities` and `forgemind explain-limits`."""

    def test_capabilities_command_runs(self):
        runner = CliRunner()
        result = runner.invoke(app, ["capabilities"])
        assert result.exit_code == 0
        assert "ForgeMind Capabilities" in result.stdout

    def test_capabilities_lists_iso9001(self):
        runner = CliRunner()
        result = runner.invoke(app, ["capabilities"])
        assert result.exit_code == 0
        # Reported under quality_management
        assert "ISO 9001" in result.stdout

    def test_capabilities_filter_by_discipline(self):
        runner = CliRunner()
        result = runner.invoke(app, ["capabilities", "--discipline", "quality_management"])
        assert result.exit_code == 0
        assert "Quality Management" in result.stdout
        # Other disciplines should not appear in the discipline header lines
        assert "Software Engineering" not in result.stdout

    def test_capabilities_unknown_discipline_errors(self):
        runner = CliRunner()
        result = runner.invoke(app, ["capabilities", "--discipline", "made_up"])
        assert result.exit_code == 1

    def test_explain_limits_for_covered_domain(self):
        runner = CliRunner()
        result = runner.invoke(app, ["explain-limits", "iso9001"])
        assert result.exit_code == 0
        # Should mention boundary conditions
        assert "ISO 9001" in result.stdout
        # Either variants or boundary conditions should be reported
        assert "cespi" in result.stdout.lower() or "boundary" in result.stdout.lower() or "gaps" in result.stdout.lower()

    def test_explain_limits_for_out_of_scope_domain(self):
        runner = CliRunner()
        result = runner.invoke(app, ["explain-limits", "nuclear_systems"])
        assert result.exit_code == 0
        assert "out of scope" in result.stdout.lower()

    def test_explain_limits_for_unknown_domain_errors(self):
        runner = CliRunner()
        result = runner.invoke(app, ["explain-limits", "totally_made_up_domain"])
        assert result.exit_code == 1
