# Contributing Domain-Specific Reverse Patterns to ForgeMind

## Philosophy

ForgeMind does **NOT invent patterns**—it **codifies expert knowledge**.

When something goes wrong in a project, teams ask: *"How do we go backward?"* The answer is deeply domain-specific and often constrained by regulation, governance, or technical limitations.

- **ISO 9001 QMS**: Signed documents cannot be "unsigned" per audit compliance. Reversal = issue new version + obsolete old.
- **Software Deployments**: Blue-green deployments enable 5-minute rollbacks; database migrations may require 1+ hours.
- **ML Models**: Model versioning + feature flags enable near-instant rollback, but drift detection is continuous.
- **Government Contracts**: Tender reversals often impossible due to compliance freezes.

Each domain has **real constraints** that must be **documented honestly**.

ForgeMind's job is to codify these constraints into plugins so users understand:
- ✅ What IS reversible (and why)
- ❌ What ISN'T reversible (and why not)
- 🔒 What governance applies
- ⏱️ What time windows are realistic
- 📊 What data loss implications exist

---

## v1.2.x Architecture: Variants, Taxonomy, Attribution

The guide below (Phases 1–6) still applies. This section adds the three
v1.2.x concepts every modern contribution must address.

### 1. Variants within a domain

A single domain can hold multiple **validated variants**. ISO 9001 ships
two today (CeSPI UNLP 8-state from production; industry-common
minimalist 5-state). The consultant offers the user a choice; the
plugin selects the right state machine at construction time.

```python
class ISO9001ReversePattern(ReverseStatePattern):
    VARIANT_CESPI_8STATE = "cespi_unlp_8state"
    VARIANT_MINIMALIST_5STATE = "iso9001_minimalist_5state"

    STATE_MACHINE = {...}              # CeSPI 8-state
    MINIMALIST_STATE_MACHINE = {...}    # minimalist 5-state

    VARIANTS = {
        VARIANT_CESPI_8STATE: STATE_MACHINE,
        VARIANT_MINIMALIST_5STATE: MINIMALIST_STATE_MACHINE,
    }

    def __init__(self, variant_id: str | None = None):
        self.variant_id = variant_id or VARIANT_CESPI_8STATE
        self.STATE_MACHINE = self.VARIANTS[self.variant_id]
```

**A domain is `partial` until 1+ variants ship with tests, `covered` once
2+ ship.** Never claim `covered` from a single source.

### 2. Declarative coverage in `disciplines.yaml`

Every plugin contribution MUST update `forgemind/data/disciplines.yaml`.
This file is the single source of truth for ForgeMind's coverage and
drives `forgemind capabilities`, `forgemind explain-limits`,
`forgemind compare-variants` and the consultant's calibration dialog.

```yaml
quality_management:
  domains:
    iso9001:
      name: ISO 9001:2015 — General QMS
      coverage: partial                    # never claim 'covered' with 1 variant
      confidence: 0.85
      variants:
        - id: cespi_unlp_8state
          name: CeSPI UNLP 8-state document lifecycle
          source: iso-gestion (CeSPI UNLP)
          url: https://github.com/Desarrollo-CeSPI/iso-gestion
          license: MIT
          confidence: 0.85
          production_validated: true
          since: "2014"
          scope_evidence: Two ISO 9001:2015 certified scopes, 30+ users
          when_to_choose:              # required for compare-variants
            - Medium-to-large organization with multiple stakeholders
            - Distinct authorities for reviewer vs approver required
          pros:                        # required for compare-variants
            - Stronger audit trail (more discrete state transitions)
            - Distinct role responsibilities per phase
          cons:                        # required for compare-variants
            - Higher ceremony — slower flow for small teams
      boundary_conditions:
        - Industry-specific extensions (pharma, aerospace) NOT modeled
      escalate_to: ISO 9001 lead auditor / QMS consultant
```

Required fields per variant: `id`, `name`, `confidence`, `when_to_choose`,
`pros`, `cons`. The decision-support fields drive
`forgemind compare-variants` and the consultant's variant question — a
variant without them cannot guide users.

### 3. Attribution (ATTRIBUTIONS.md)

If your pattern is derived from a real external source (and most should
be), you MUST update `ATTRIBUTIONS.md` with:

- Source URL
- Author / organization
- License (MIT/Apache 2.0/BSD/CC-BY/CC0 — copyleft sources are usable
  for pattern *codification* only, not for code redistribution)
- A short description of what ForgeMind uses (the *patterns*) and
  what it does NOT redistribute (the upstream code, UI, schemas)

Mirror the format of the existing iso-gestion entry.

### 4. Self-test commands

After your contribution, run these locally before submitting:

```bash
pytest tests/ -v                          # all tests still pass
ruff check .                              # lint clean
forgemind capabilities                    # your domain appears with right coverage
forgemind explain-limits <your_domain>    # variants + boundary conditions render
forgemind compare-variants <your_domain>  # decision card renders for 2+ variants
```

If any of these fail or produce empty sections, your contribution isn't
ready.

---

## How to Contribute a Reverse Pattern

### Phase 1: Research Your Domain

Before writing any code, document your domain's **actual practices**, not idealized ones.

#### Step 1a: Find Official Standards or Best Practices
- **ISO 9001**: Reference ISO 9001:2015 §8.5.6 (Control of externally provided processes)
- **Software**: DORA metrics, SRE handbook, IEEE practices
- **AI/ML**: MLOps community practices, model governance frameworks
- **Government/Tender**: Procurement regulations (FAR, specific country regulations)
- **Healthcare**: HIPAA compliance, FDA 21 CFR Part 11 (electronic records)

**Your pattern must reference official sources.** If it's not in an official standard or widely-documented best practice, explain why.

#### Step 1b: Document Real Reversibility Constraints
For each state in your domain's workflow:

```markdown
## [State Name]

**Reversible?** Yes/No
**Why?** [Compliance reason, technical reason, business reason]

**If reversible:**
- From which prior states?
- Approval gates required?
- Time estimate?
- Data loss risk?
- Audit trail implications?

**If NOT reversible:**
- Why not (regulation, technical, business)?
- What mitigation strategy exists?
- Can we work around it?

**Example:** Signed documents in ISO 9001 are NOT reversible because §8.5.2 
requires signed documents to be historical records. Mitigation: issue new 
approved version and mark old version as "Superseded."
```

#### Step 1c: Validate with Domain Experts
- Interview 3+ practitioners in your domain
- Get their agreement on constraints
- Document their examples

**Example**: If you're contributing a QMS pattern, talk to:
- ISO 9001 auditor
- QMS document control specialist
- Internal compliance officer

---

### Phase 2: Create the Pattern Plugin

Create your plugin inheriting from `ReverseStatePattern`.

#### Directory Structure

```
forgemind/plugins/
├── __init__.py                    (already exists, no changes)
├── reverse_state_pattern.py       (ABC, already exists)
├── iso9001_pattern.py             (reference implementation)
└── your_domain_pattern.py         (YOUR NEW PATTERN)

forgemind/templates/reverse_patterns/
├── iso9001_reverse_pattern.yaml   (reference template)
└── your_domain_reverse_pattern.yaml (YOUR NEW TEMPLATE)
```

#### Pattern Template

```python
"""
[Domain] Reverse State Machine Pattern

Reference: [Official standard or best practice document]
Contributor: [Your name/organization]
Validation: [3+ domain experts who reviewed this]
"""

from forgemind.plugins import ReverseStatePattern
from forgemind.schemas.project import ProjectAnalysis
from dataclasses import dataclass


@dataclass
class ReversalStep:
    """Single step in a reversal plan."""
    step_number: int
    action: str
    approval_required: bool = False
    approval_role: str = None
    estimated_time_minutes: int = 0
    data_loss_risk: str = "none"  # none, low, medium, high
    notes: str = ""


@dataclass
class ReversalPlan:
    """Complete reversal plan for a state transition."""
    current_state: str
    target_state: str
    rollback_path: str  # e.g., "Production → Staging → Code Review"
    steps: list
    approval_gates: list
    total_estimated_time_minutes: int
    highest_data_loss_risk: str
    dependencies: list
    constraints: list
    confidence: float = 0.85  # Based on how well this is documented


class YourDomainReversePattern(ReverseStatePattern):
    """[Domain] reverse state machine."""
    
    domain = "your_domain"  # Lowercase, no spaces
    
    def __init__(self):
        """Initialize pattern with state definitions."""
        self.states = {
            "Draft": {
                "can_revert_to": [],
                "reversible": True,
                "approval_required": False,
                "data_loss": "none",
            },
            # ... more states
        }
    
    def get_supported_states(self) -> list:
        """Return list of supported state objects."""
        return [
            StateInfo(state_name=name, **config) 
            for name, config in self.states.items()
        ]
    
    def validate_state_transition(self, from_state: str, to_state: str) -> dict:
        """
        Validate if reversal is possible.
        
        Args:
            from_state: Current state
            to_state: Target reversal state
        
        Returns:
            {
                "is_valid": bool,
                "reason": str,
                "requires_approval": bool,
                "approval_role": str,
                "mitigation": str (if not valid)
            }
        """
        if from_state not in self.states or to_state not in self.states:
            return {"is_valid": False, "reason": "Unknown state"}
        
        allowed = self.states[from_state]["can_revert_to"]
        is_valid = to_state in allowed
        
        return {
            "is_valid": is_valid,
            "reason": "Reversal allowed" if is_valid else f"Cannot revert {from_state} to {to_state}",
            "requires_approval": self.states[from_state].get("approval_required", False),
            "approval_role": self.states[from_state].get("approval_role", None),
        }
    
    def generate_reversal_plan(self, 
                              project: ProjectAnalysis,
                              current_state: str,
                              target_state: str = None) -> ReversalPlan:
        """
        Generate step-by-step reversal plan.
        
        Args:
            project: ProjectAnalysis with domain context
            current_state: Current state from project
            target_state: Optional target state (default: previous state)
        
        Returns:
            ReversalPlan with steps, time estimates, approval gates
        """
        if target_state is None:
            # Default: revert to first reversible prior state
            target_state = self.states[current_state]["can_revert_to"][0]
        
        # Build steps for reversal
        steps = [
            ReversalStep(
                step_number=1,
                action="...",
                approval_required=False,
            ),
            # ... more steps
        ]
        
        return ReversalPlan(
            current_state=current_state,
            target_state=target_state,
            rollback_path=f"{current_state} → {target_state}",
            steps=steps,
            approval_gates=[...],
            total_estimated_time_minutes=sum(s.estimated_time_minutes for s in steps),
            highest_data_loss_risk="none",  # or low/medium/high
            dependencies=[...],
            constraints=[...],
            confidence=0.85,
        )
```

#### Key Rules for Plugins

1. **No Speculation**: Only document what you know is true.
   - ❌ "Teams probably reverse X way"
   - ✅ "ISO 9001:2015 §8.5.6 requires..."
   - ✅ "In interviews with 3 QMS teams, all use approach X"

2. **Be Honest About Constraints**: If something can't be reversed, say so.
   - ❌ "Signed documents can be unsigned" (false)
   - ✅ "Signed documents cannot be unsigned per audit compliance. Mitigation: issue new version."

3. **Document Approval Gates**: Who must approve the reversal?
   - ❌ No approval specification
   - ✅ "Quality Manager approval required per §8.5.6"

4. **Include Time Estimates**: Realistic, not optimistic.
   - ❌ "1 minute to rollback database"
   - ✅ "5-10 min (blue-green load balancer switch) or 60+ min (database restore)"

5. **Data Loss Implications**: Be explicit about what happens to recent data.
   - ❌ No mention of data impact
   - ✅ "High risk: recent transactions (last 15 min) may be lost"

---

### Phase 3: Create the YAML Template

Create a human-readable reference template documenting your pattern.

**See these examples:**
- `forgemind/templates/reverse_patterns/iso9001_reverse_pattern.yaml` (220 LOC, detailed)
- `forgemind/templates/reverse_patterns/software_reverse_pattern.yaml` (280 LOC, detailed)
- `forgemind/templates/reverse_patterns/ai_ml_reverse_pattern.yaml` (280 LOC, detailed)

**Your YAML should include:**
- Domain and framework reference
- State machine definition (all states, transitions, constraints)
- Reversibility rules (policies governing reversals)
- Approval gates per state
- Time estimates per transition
- Data loss impact assessment
- Dependencies (systems required for reversals)
- Constraints (limitations, regulations)
- Compliance references (standards cited)
- Example scenarios (5+ realistic examples)

---

### Phase 4: Write Tests

**Minimum test coverage: 90% of pattern code.**

```python
# tests/test_your_domain_pattern.py

import pytest
from forgemind.plugins import YourDomainReversePattern


class TestYourDomainPattern:
    """Test [Domain] reverse state pattern."""
    
    def test_supported_states(self):
        """All states are defined and accessible."""
        pattern = YourDomainReversePattern()
        states = pattern.get_supported_states()
        assert len(states) > 0
        assert "State1" in [s.state_name for s in states]
    
    def test_valid_transition(self):
        """Valid transitions are allowed."""
        pattern = YourDomainReversePattern()
        result = pattern.validate_state_transition("State2", "State1")
        assert result["is_valid"]
    
    def test_invalid_transition_fails(self):
        """Invalid transitions are rejected."""
        pattern = YourDomainReversePattern()
        result = pattern.validate_state_transition("State1", "State3")
        assert not result["is_valid"]
        assert "cannot" in result["reason"].lower()
    
    def test_approval_gates_enforced(self):
        """Approval required when specified."""
        pattern = YourDomainReversePattern()
        result = pattern.validate_state_transition("ApprovedState", "ReviewState")
        assert result.get("requires_approval") is True
        assert result.get("approval_role") is not None
    
    def test_generate_reversal_plan_includes_steps(self):
        """Reversal plan includes all necessary steps."""
        pattern = YourDomainReversePattern()
        project = self._create_test_project()
        
        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="State2",
            target_state="State1"
        )
        
        assert plan.current_state == "State2"
        assert plan.target_state == "State1"
        assert len(plan.steps) > 0
        assert all(hasattr(s, 'step_number') for s in plan.steps)
        assert all(hasattr(s, 'action') for s in plan.steps)
        assert plan.total_estimated_time_minutes > 0
    
    def test_unreversible_state_handled(self):
        """Non-reversible states return appropriate error."""
        pattern = YourDomainReversePattern()
        result = pattern.validate_state_transition("FinalState", "PriorState")
        assert not result["is_valid"]
        assert "mitigation" in result or "reason" in result
    
    def test_compliance_references_documented(self):
        """Pattern includes compliance/standard references."""
        pattern = YourDomainReversePattern()
        # Verify pattern has compliance info
        # (implementation depends on your pattern structure)
    
    def test_data_loss_impact_assessed(self):
        """Reversal plan includes data loss assessment."""
        pattern = YourDomainReversePattern()
        project = self._create_test_project()
        
        plan = pattern.generate_reversal_plan(
            project=project,
            current_state="State2",
            target_state="State1"
        )
        
        assert plan.highest_data_loss_risk in ["none", "low", "medium", "high"]
    
    @staticmethod
    def _create_test_project():
        """Create test ProjectAnalysis."""
        from forgemind.schemas.project import ProjectAnalysis, ProjectMetadata, ProjectInput
        
        return ProjectAnalysis(
            metadata=ProjectMetadata(
                name="Test Project",
                slug="test-project",
                domain="your_domain",
            ),
            input=ProjectInput(
                objective="Test pattern",
                context="Test context",
                scope="Pattern validation",
                constraints="Test constraints",
                current_state="State2",
            ),
        )
```

---

### Phase 5: Register Your Pattern

Update `forgemind/plugins/__init__.py` to load your pattern:

```python
# forgemind/plugins/__init__.py

from .reverse_state_pattern import ReverseStatePattern
from .plugin_registry import PluginRegistry, get_plugin_registry, register_builtin_patterns
from .your_domain_pattern import YourDomainReversePattern  # ADD THIS

__all__ = [
    "ReverseStatePattern", 
    "PluginRegistry", 
    "get_plugin_registry", 
    "register_builtin_patterns",
    "YourDomainReversePattern",  # ADD THIS
]
```

Update `forgemind/plugins/plugin_registry.py` `register_builtin_patterns()`:

```python
def register_builtin_patterns():
    """Register built-in reverse state machine patterns."""
    registry = get_plugin_registry()
    registry.register(ISO9001ReversePattern)
    registry.register(SoftwareReversePattern)
    registry.register(AIMLReversePattern)
    registry.register(YourDomainReversePattern)  # ADD THIS
```

---

### Phase 6: Submit Pull Request

**PR Requirements:**

✅ Plugin code with 90%+ test coverage
✅ YAML template documenting the pattern
✅ Tests passing (run `pytest tests/test_reverse_patterns.py -v`)
✅ 5+ example scenarios in YAML
✅ References to official standards/best practices
✅ Validation from 3+ domain experts (document in PR description)
✅ Updated `CONTRIBUTING_REVERSE_PATTERNS.md` if you expanded guidance
✅ Updated `README.md` listing new supported domain

**PR Template:**

```markdown
## Adds [Domain] Reverse Pattern

### Summary
Reverse state machine pattern for [Domain] based on [Standard/Best Practice].

### Validation
- [x] Reviewed by [Expert Name, Title]
- [x] Reviewed by [Expert Name, Title]
- [x] Reviewed by [Expert Name, Title]

### Compliance References
- [Standard/Document] §X.Y.Z
- [Link to documentation]

### Test Coverage
- [x] 90%+ line coverage
- [x] All state transitions tested
- [x] Approval gates validated
- [x] Data loss implications documented

### Example Scenarios
Pattern includes 5+ realistic examples:
1. [Scenario 1]
2. [Scenario 2]
...

### Checklist
- [x] Plugin code added to `forgemind/plugins/your_domain_pattern.py`
- [x] YAML template added to `forgemind/templates/reverse_patterns/`
- [x] Tests in `tests/test_reverse_patterns.py`
- [x] Pattern registered in `register_builtin_patterns()`
- [x] All tests passing
- [x] README updated with new domain
```

---

## What NOT to Do

### ❌ Don't Speculate
- "I think teams probably should..."
- "The best way would be..."
- "In our experience, this usually works..."

**Do:** Reference official standards, interviews with experts, or knowledge graph data.

### ❌ Don't Ignore Constraints
- "You can always roll back by..."
- "It's easy to reverse if you..."
- "Just delete the data and start over..."

**Do:** Document what CAN'T be reversed and why (compliance, technical, business).

### ❌ Don't Invent New Domains
- Create patterns only for domains with established practices
- If your domain is unique, validate with at least 3 practitioners

**Do:** Stick to well-established domains with documented best practices.

### ❌ Don't Skip Tests
- Low test coverage hides bugs
- Tests document expected behavior

**Do:** Write tests for all state transitions, approval gates, data loss scenarios.

### ❌ Don't Forget the YAML
- YAML templates are discoverable documentation
- They help teams understand reversibility BEFORE they hit a problem

**Do:** Make YAML as detailed as code implementation.

---

## What Happens After You Submit

1. **Community Review** (1-2 weeks)
   - ForgeMind maintainers verify: compliance references, test coverage, expert validation
   - Other users comment on accuracy, missing scenarios

2. **Validation** (1 week)
   - At least 2 domain experts outside your organization review pattern

3. **Merge** (1 week)
   - Pattern merged into main
   - Becomes available in `generate_reverse_context()` automatically

4. **Improvement** (Ongoing)
   - Users submit issues for missing scenarios, unclear steps
   - Pattern is iteratively improved based on real usage

---

## Questions?

See **CONTRIBUTING_PRINCIPLES.md** for philosophy.
See **README.md** for the consultant workflow (`capabilities`, `consult`,
`compare-variants`, `followup`, `history`) that consumes your contribution.
See **ATTRIBUTIONS.md** for the format used to credit upstream sources.
See **forgemind/plugins/iso9001_pattern.py** + the two iso9001 variants
in `disciplines.yaml` for the reference implementation.
Open an issue: `[reverse-pattern] <your domain or question>`.

---

## What's out of scope by design

ForgeMind explicitly will NEVER advise on the following, even if patterns
are contributed:

- `nuclear_systems`               — NRC/IAEA expertise + consequence-of-error
- `defense_classified`            — security clearance required
- `biomedical_clinical_trials`    — bioethics + GCP expertise
- `legal_advice`                  — unauthorized practice of law
- `financial_advice_regulated`    — licensed advisor required
- `medical_diagnosis`             — practice of medicine

These are declared under `out_of_scope_by_design` in `disciplines.yaml`.
Contributions extending the *escalation contact* for these entries are
welcome; contributions trying to make ForgeMind advise on them are not.

Thank you for helping ForgeMind codify domain expertise!
