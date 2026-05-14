"""
Tests for Reverse State Pattern plugins and Epistemic Validator (v1.2.0).

Critical tests:
1. Plugin registration and discovery
2. Reversal plan generation
3. State transition validation
4. Epistemic validation (prevents hallucination)
"""

import pytest
from forgemind.plugins import PluginRegistry
from forgemind.plugins.iso9001_pattern import ISO9001ReversePattern
from forgemind.plugins.software_pattern import SoftwareReversePattern
from forgemind.plugins.ai_ml_pattern import AIMLReversePattern
from forgemind.epistemics import EpistemicValidator, OutputClassification
from forgemind.schemas.project import ProjectAnalysis, ProjectMetadata, ProjectInput


class TestPluginRegistry:
    """Test plugin registration and discovery."""

    def test_register_pattern(self):
        """Test registering a pattern."""
        registry = PluginRegistry()
        registry.register(ISO9001ReversePattern)
        assert registry.has_pattern("iso9001")

    def test_register_duplicate_fails(self):
        """Test that registering same domain twice fails."""
        registry = PluginRegistry()
        registry.register(ISO9001ReversePattern)
        with pytest.raises(ValueError, match="already registered"):
            registry.register(ISO9001ReversePattern)

    def test_list_supported_domains(self):
        """Test listing all supported domains."""
        registry = PluginRegistry()
        registry.register(ISO9001ReversePattern)
        registry.register(SoftwareReversePattern)
        domains = registry.list_supported_domains()
        assert "iso9001" in domains
        assert "software" in domains

    def test_get_pattern_instance(self):
        """Test instantiating a pattern."""
        registry = PluginRegistry()
        registry.register(ISO9001ReversePattern)
        pattern = registry.get_pattern("iso9001")
        assert pattern is not None
        assert pattern.domain == "iso9001"

    def test_get_nonexistent_pattern_returns_none(self):
        """Test getting non-existent pattern returns None."""
        registry = PluginRegistry()
        pattern = registry.get_pattern("nonexistent")
        assert pattern is None


class TestISO9001Pattern:
    """Test ISO 9001 reverse state pattern."""

    def test_supported_states(self):
        """Test that all states are supported."""
        pattern = ISO9001ReversePattern()
        states = pattern.get_supported_states()
        state_names = [s.state_name for s in states]
        assert "Draft" in state_names
        assert "Under Review" in state_names
        assert "Approved" in state_names
        assert "Signed" in state_names

    def test_validate_review_to_draft_transition(self):
        """Test valid transition from Under Review to Draft."""
        pattern = ISO9001ReversePattern()
        result = pattern.validate_state_transition("Under Review", "Draft")
        assert result["is_valid"]

    def test_validate_signed_reversal_fails(self):
        """Test that reverting signed documents is not allowed."""
        pattern = ISO9001ReversePattern()
        result = pattern.validate_state_transition("Signed", "Approved")
        assert not result["is_valid"]
        assert "cannot be modified" in result.get("mitigation", "").lower() or \
               "signed documents" in str(result).lower()

    def test_generate_reversal_plan_under_review(self):
        """Test generating reversal plan from Under Review."""
        pattern = ISO9001ReversePattern()
        project = self._create_mock_project()

        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="Under Review",
            target_state="Draft"
        )

        assert plan.current_state == "Under Review"
        assert plan.target_state == "Draft"
        assert len(plan.steps) > 0
        assert all(hasattr(s, 'step_number') for s in plan.steps)

    def test_generate_reversal_plan_approved(self):
        """Test generating reversal plan from Approved."""
        pattern = ISO9001ReversePattern()
        project = self._create_mock_project()

        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="Approved",
            target_state="Under Review"
        )

        assert plan.current_state == "Approved"
        assert len(plan.approval_gates) > 0
        assert plan.total_estimated_time_minutes > 0

    def test_reversal_plan_has_audit_trail_requirement(self):
        """Test that reversals include audit trail logging."""
        pattern = ISO9001ReversePattern()
        project = self._create_mock_project()

        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="Approved",
            target_state="Under Review"
        )

        # Should have step for audit trail
        has_audit_step = any(
            "audit" in step.action.lower()
            for step in plan.steps
        )
        assert has_audit_step, "Reversal plan should include audit trail step"

    @staticmethod
    def _create_mock_project() -> ProjectAnalysis:
        """Create a mock ProjectAnalysis for testing."""
        return ProjectAnalysis(
            metadata=ProjectMetadata(
                name="Test ISO Project",
                slug="test-iso-project",
                domain="iso9001",
            ),
            input=ProjectInput(
                objective="Test reversing ISO 9001 document states",
                context="QMS document management",
                scope="Document approval workflow",
                constraints="Must maintain audit trail",
                current_state="Approved",
            ),
            risks=[
                {
                    "risk_id": "R1",
                    "category": "Documentation",
                    "description": "Test risk",
                    "probability": "medium",
                    "impact": "high",
                    "owner": "Test Owner"
                }
            ],
            assumptions=[],
            acceptance_criteria=[],
            constraints=[],
            control_plan=[],
            decision_log=[],
        )


class TestSoftwarePattern:
    """Test Software reverse state pattern."""

    def test_production_reversal_requires_approval(self):
        """Test that production rollback requires approval."""
        pattern = SoftwareReversePattern()
        result = pattern.validate_state_transition("Production", "Staging")
        assert result["is_valid"]
        assert result.get("requires_approval")

    def test_blue_green_steps_included(self):
        """Test that blue-green deployment steps are included."""
        pattern = SoftwareReversePattern()
        project = self._create_mock_project()

        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="Production",
            target_state="Staging"
        )

        # Should mention load balancer switching
        has_blue_green = any(
            "load balancer" in step.action.lower() or "environment" in step.action.lower()
            for step in plan.steps
        )
        assert has_blue_green, "Production rollback should mention blue-green/load balancer"

    @staticmethod
    def _create_mock_project() -> ProjectAnalysis:
        """Create mock project for testing."""
        return ProjectAnalysis(
            metadata=ProjectMetadata(
                name="Test Software Project",
                slug="test-software-project",
                domain="software",
            ),
            input=ProjectInput(
                objective="Test software deployment reversals",
                context="DevOps environment",
                scope="Blue-green deployment",
                constraints="15-minute SLA for rollbacks",
                current_state="Production",
            ),
            risks=[],
            assumptions=[],
            acceptance_criteria=[],
            control_plan=[],
            decision_log=[],
        )


class TestEpistemicValidator:
    """Test the Epistemic Validator (hallucination prevention)."""

    def test_deterministic_output_accepted(self):
        """Test that deterministic (fact-based) output is accepted."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="ISO 9001:2015 §8.5.6 requires documented control of changes.",
            confidence=0.95,
            domain="iso9001",
            sources=["official_standard"]
        )

        assert result.is_valid
        assert result.classification == OutputClassification.DETERMINISTIC

    def test_stochastic_output_labeled(self):
        """Test that empirical patterns are labeled with confidence."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="Based on 50 similar projects, this approach succeeds 70% of the time.",
            confidence=0.70,
            domain="iso9001",
            sources=["knowledge_graph_high_n"]
        )

        assert result.is_valid
        assert result.classification == OutputClassification.STOCHASTIC
        assert result.requires_label

    def test_speculative_output_rejected(self):
        """Test that speculative output is rejected."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="We think you should probably use the best practice approach in our experience.",
            confidence=0.50,
            domain="iso9001",
            sources=[]
        )

        assert not result.is_valid
        assert result.classification == OutputClassification.SPECULATIVE
        assert result.escalation_needed

    def test_unsupported_domain_escalates(self):
        """Test that unsupported domains escalate to experts."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="Some advice about firmware.",
            confidence=0.70,
            domain="hardware_firmware",
            sources=["knowledge_graph_high_n"]
        )

        assert not result.is_valid
        assert result.classification == OutputClassification.ESCALATE
        assert result.escalation_needed

    def test_low_confidence_escalates(self):
        """Test that low confidence outputs escalate."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="This might work based on limited data.",
            confidence=0.45,
            domain="iso9001",
            sources=["knowledge_graph_low_n"]
        )

        assert not result.is_valid
        assert result.escalation_needed

    def test_speculative_phrases_detected(self):
        """Test detection of speculative language patterns."""
        validator = EpistemicValidator()

        speculative_outputs = [
            "In our experience, you should probably",
            "We think you should consider",
            "Most teams do this",
            "The best practice would be",
        ]

        for output in speculative_outputs:
            result = validator.validate_output(
                output_text=output,
                confidence=0.70,
                domain="iso9001",
                sources=[]  # No sources = no grounding
            )
            assert not result.is_valid, f"Should reject: {output}"
            assert result.classification == OutputClassification.SPECULATIVE

    def test_no_sources_rejected(self):
        """Test that output without sources is rejected."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="Here is some recommendation.",
            confidence=0.80,
            domain="iso9001",
            sources=[]
        )

        assert not result.is_valid
        assert not result.sources

    def test_confidence_label_formatting(self):
        """Test that confidence labels are properly formatted."""
        validator = EpistemicValidator()
        result = validator.validate_output(
            output_text="Based on pattern X, outcome Y occurs 65% of the time.",
            confidence=0.65,
            domain="iso9001",
            sources=["knowledge_graph_medium_n"]
        )

        assert result.requires_label
        assert "STOCHASTIC" in result.suggested_label
        assert "Confidence" in result.suggested_label

    def test_source_confidence_scoring(self):
        """Test that sources are scored correctly."""
        validator = EpistemicValidator()

        # Standard should be highest confidence
        result_std = validator.validate_output(
            output_text="ISO 9001 requires X.",
            confidence=0.95,
            domain="iso9001",
            sources=["official_standard"]
        )
        assert result_std.is_valid
        assert result_std.classification == OutputClassification.DETERMINISTIC

        # Low sample knowledge graph should require escalation
        result_low_n = validator.validate_output(
            output_text="Some recommendation from few projects.",
            confidence=0.45,
            domain="iso9001",
            sources=["knowledge_graph_low_n"]
        )
        assert not result_low_n.is_valid


class TestReverseContextGenerator:
    """Test the ReverseContextGenerator (v1.2.0 generator integration)."""

    def test_generator_loads_iso_plugin(self):
        """Test that generator loads ISO 9001 plugin for ISO domain."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_iso_project()
        generator = ReverseContextGenerator()
        data = generator.generate(project)

        assert data["domain"] == "iso9001"
        assert data["plugin_available"] is True

    def test_generator_escalates_unsupported_domain(self):
        """Test that generator escalates when domain not supported."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_project_with_domain("hardware_firmware")
        generator = ReverseContextGenerator()
        data = generator.generate(project)

        assert data["plugin_available"] is False
        assert data["escalation_needed"] is True
        assert "engineer" in data["escalate_to"].lower()

    def test_generator_uses_epistemic_validator(self):
        """Test that generator applies epistemic validation to output."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_iso_project()
        generator = ReverseContextGenerator()
        data = generator.generate(project)

        # Should have epistemic classification
        assert "epistemic_classification" in data
        assert data["epistemic_classification"] in ["DETERMINISTIC", "STOCHASTIC", "ESCALATE"]

    def test_generator_formats_markdown_with_plan(self):
        """Test that generator formats reversal plan as Markdown."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_iso_project()
        generator = ReverseContextGenerator()
        data = generator.generate(project)
        markdown = generator.format_markdown(data)

        # Should include project name in header
        assert project.metadata.name in markdown
        # Should include domain
        assert "iso9001" in markdown.lower()
        # Should include epistemic classification
        assert "DETERMINISTIC" in markdown or "STOCHASTIC" in markdown or "ESCALATE" in markdown

    def test_generator_includes_escalation_in_markdown(self):
        """Test that Markdown includes escalation info when needed."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_project_with_domain("hardware_firmware")
        generator = ReverseContextGenerator()
        data = generator.generate(project)
        markdown = generator.format_markdown(data)

        # Should indicate reversal pattern not available
        assert "not available" in markdown.lower() or "not yet" in markdown.lower()
        # Should include escalation contact
        assert "escalate" in markdown.lower()

    def test_generator_handles_missing_current_state(self):
        """Test that generator handles missing current_state gracefully."""
        from forgemind.generators.reverse_context_generator import ReverseContextGenerator

        project = self._create_iso_project()
        project.input.current_state = None  # Clear current state

        generator = ReverseContextGenerator()
        data = generator.generate(project)

        # Should not crash, should indicate current state missing
        assert data["current_state"] == "Unknown"

    @staticmethod
    def _create_iso_project() -> ProjectAnalysis:
        """Create ISO 9001 test project."""
        return ProjectAnalysis(
            metadata=ProjectMetadata(
                name="Test Generator Project",
                slug="test-gen-project",
                domain="iso9001",
            ),
            input=ProjectInput(
                objective="Test reversal plan generation",
                context="QMS environment",
                scope="Document approval workflow",
                constraints="Maintain audit trail",
                current_state="Approved",
            ),
        )

    @staticmethod
    def _create_project_with_domain(domain: str) -> ProjectAnalysis:
        """Create project with specified domain."""
        return ProjectAnalysis(
            metadata=ProjectMetadata(
                name="Test Domain Project",
                slug="test-domain-project",
                domain=domain,
            ),
            input=ProjectInput(
                objective="Test domain handling",
                context="Test context",
                scope="Test scope",
                constraints="Test constraints",
            ),
        )
