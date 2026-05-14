# ForgeMind Changelog

## v1.2.x — Consultant Role (2026-05-13 → 2026-05-14)

ForgeMind transitions from a one-shot "intake → 17 documents" tool into a
**universal multidisciplinary consultant**. Six new layers ship across this
release line, each independently tested:

### Layer 1 — Disciplines taxonomy (Phase D)
- `forgemind/data/disciplines.yaml` declares ForgeMind's coverage map
  (6 disciplines · 23 domains · 6 out-of-scope-by-design).
- `forgemind/disciplines/` Python module with typed API
  (`Coverage`, `Discipline`, `Domain`, `Variant`, `DisciplineTaxonomy`).
- `forgemind capabilities [--discipline X]` — full coverage report CLI.
- `forgemind explain-limits <domain>` — variants + boundary conditions.
- `EpistemicValidator` now consults the taxonomy for escalation routing.

### Layer 2 — Consultant dialog (Phase C)
- `forgemind consult <project.md>` — adaptive 4-step calibration:
  discipline → domain → variant → confirm, before generating outputs.
- Structured refusal protocol (exit code 2 + escalation contact) for
  out-of-scope-by-design and not-covered domains.
- Writes `CONSULTANT_CALIBRATION.md` (human) and
  `consultant_calibration.json` (machine-readable sidecar) alongside the
  17 standard outputs.
- `--auto-accept` for CI / scripting; `--output-dir` override.

### Layer 3 — Variant pluralism
Three disciplines now ship plural validated variants, all with attribution
and decision criteria (`when_to_choose`, `pros`, `cons`):
- **ISO 9001**: CeSPI UNLP 8-state lifecycle (production since 2014,
  iso-gestion, MIT) + industry-common minimalist 5-state.
- **software**: blue/green (Fowler) + canary (Google SRE Workbook).
- **ai_ml**: feature-flag/checkpoint + shadow deployment
  (Sculley 2015; Sato 2019; Netflix Tech Blog).

### Layer 4 — Variant comparison
- `forgemind compare-variants <domain>` — side-by-side decision card with
  when-to-choose, pros, cons per variant.
- Consultant offers an inline "Show me a side-by-side comparison first"
  option at the variant step when multiple variants are available.

### Layer 5 — Follow-up
- `forgemind followup <output_dir>` — drill into one decision (variant,
  risks, acceptance criteria, escalation) without re-running analysis.
- Three modes: interactive menu, `--topic <key>` single render,
  `--auto-accept` print-and-exit.

### Layer 6 — Persistent memory
- `~/.forgemind/history.jsonl` records each successful consult locally.
- `forgemind history [--limit N] [--clear]` to view or erase.
- Consultant defaults are biased by the user's prior choices (the prior
  variant becomes the default in the variant question, etc.).
- `FORGEMIND_HISTORY_PATH` env var to override the path (used in tests).
- LOCAL ONLY: no network, no telemetry.

### Variant-aware outputs
- `forgemind consult` now writes `REVERSAL_PLAN.md` derived from the
  chosen variant's state machine. Picking CeSPI 8-state vs minimalist
  5-state produces materially different reversal-plan tables.
- The variant-aware reversal generator lives in
  `forgemind/consultant/variant_output.py` and falls back gracefully
  when a domain has no plugin.

### Taxonomy ↔ plugin alignment
- Domain ids `web_services` and `ml_systems` were renamed to `software`
  and `ai_ml` respectively so the calibrated taxonomy domain matches the
  plugin registry domain. This unblocked the variant-aware output flow.

### Attribution
- `ATTRIBUTIONS.md` credits each external source ForgeMind codifies
  patterns from: iso-gestion (CeSPI UNLP), Martin Fowler bliki, Google
  SRE Workbook, Sculley et al. NeurIPS 2015, Sato et al. CD4ML, Netflix
  Tech Blog. No upstream code is redistributed.

### Documentation
- `README.md` updated with the consultant workflow (5-command flow,
  refusal protocol, self-knowledge summary).
- `CONTRIBUTING_REVERSE_PATTERNS.md` extended with the v1.2.x
  architecture (variants, taxonomy YAML, decision criteria, attribution
  + self-test commands).

### Test posture
- 213 tests passing (96 base v1.2.1 + 117 net new across the six layers)
- 85% line coverage
- Python 3.9 / 3.11 / 3.12 green on GitHub Actions
- All ruff checks clean

### Breaking changes
- None for `forgemind intake` (the direct mode is unchanged).
- Taxonomy domain ids renamed: `web_services` → `software`,
  `ml_systems` → `ai_ml`. Anyone reading the YAML programmatically
  should update keys.

---

## v1.1.0 — Context Engineering Release (2026-05-13)

### 🎯 What's New

ForgeMind v1.1 adds 5 new generators focused on preparing work for AI agents. These outputs help teams define agent boundaries, validate readiness, and structure code submission workflows.

### ✨ New Features

#### 1. **Context File Generator** (`{project-slug}.context.md`)
- Extracts agent instruction context from project analysis
- Includes: Objective, Constraints, Acceptance Criteria, Top Risks, Key Assumptions
- Adds: Human Review Gates, Definition of Done, Rollback Plan
- Domain-aware: Content adapts to project type (AI, software, QMS, etc.)
- **Use case:** Share with Claude Code, Codex, or other agents before execution

#### 2. **AI Risk Readiness Checklist** (`AI_RISK_CHECKLIST.md`)
- Domain-specific risk patterns with domain-aware scoring
- Patterns for: AI Projects, Software Projects, QMS/ISO, Generic fallback
- Example AI patterns: Agent boundaries, unsafe operations, permission matrix, rollback capability, human review gates, test harness, audit trail, stakeholder alignment
- Progress indicator showing % of checklist addressed by project controls
- **Use case:** Verify readiness before handing off work to agents

#### 3. **Tool Permission Matrix** (`TOOL_PERMISSION_MATRIX.md`)
- Defines what tools/operations agents can execute
- Supports: Allowed ✅, Conditional ⚠️, Denied ❌
- Domain-specific policies (AI projects, software, QMS, generic)
- Example AI policies: Read files (Allowed), Modify code (Conditional), External APIs (Denied), Database writes (Denied), Shell execution (Conditional), PRs (Conditional), Delete operations (Denied)
- Implementation guidance for each policy
- **Use case:** Set boundaries before agents execute

#### 4. **PR Template Generator** (`AGENT_PR_TEMPLATE.md`)
- GitHub-compatible PR template for agent-generated code
- Sections: Description, Pre-Review Checklist, Acceptance Criteria, Security Review
- Includes: Key Risks, Merge Requirements (Code Owner, Security, Tests), Rollback Plan
- Extracted from project analysis (high-severity risks, review gates)
- **Use case:** Enforce submission standards for agent-generated PRs

#### 5. **Issue Template Generator** (`AGENT_ISSUE_TEMPLATE.md`)
- Standardized feedback template for agent-generated code issues
- Sections: Issue Type, Description, Steps to Reproduce, Environment
- Captures: ForgeMind version, Project Domain, Agent Used, OS, Python Version
- **Use case:** Collect structured feedback on agent outputs

### 📊 Impact

- **Total output documents:** 12 → 17 (5 new)
- **Automatic generation:** All new outputs are auto-generated during `intake` command
- **Test coverage:** 16 new tests, 35/35 passing, 81% coverage
- **Integration:** Seamless into existing markdown exporter, zero breaking changes

### 🔄 How It Works

```
forgemind intake project.md
  ↓
Analyzes project using 5 methodologies
  ↓
Generates 12 core documents
  ↓
NEW: Generates 5 context engineering documents
  ↓
Output: forgemind_outputs/project-slug/
  - PROJECT_CHARTER.md
  - RISK_REGISTER.md
  - ... (12 core docs)
  - project-slug.context.md         ← NEW
  - AI_RISK_CHECKLIST.md            ← NEW
  - TOOL_PERMISSION_MATRIX.md       ← NEW
  - AGENT_PR_TEMPLATE.md            ← NEW
  - AGENT_ISSUE_TEMPLATE.md         ← NEW
```

### 🎓 Architecture

- **BaseGenerator** abstract class enforces consistent interface across all generators
- **Domain-specific logic** in DOMAIN_PATTERNS and DOMAIN_POLICIES dictionaries
- **Keyword-based scoring** for checklist items (evaluates if keywords appear in project risks/controls)
- **Minimal dependencies** — all logic is local, no external API calls

### 🧪 Testing

- 16 new test cases covering all generators
- Tests verify: markdown output, content inclusion, domain-specificity, minimal project handling
- Coverage: 100% for 5 new generators (except base class abstractness)
- All original v1.0.0 tests (19) continue to pass

### 📝 Breaking Changes

**None.** v1.1 is backward compatible:
- All v1.0 commands work unchanged
- v1.0 output documents unchanged
- New outputs are additions, not replacements
- No CLI changes required

### 🚀 Upgrade Path

```bash
# No special upgrade steps needed
pip install -e ".[dev]"  # Reinstall if needed
forgemind intake project.md  # Automatically generates all 17 outputs
```

### 📚 Documentation Updates

- README.md: Updated version, output count, new features
- Command documentation: Intake command now lists all 17 outputs
- Roadmap: v1.1 marked complete, v1.2 targets pre-AgentOps GitHub integration

### 🔮 What's Next (v1.2)

- GitHub Action readiness gate (fail CI if not ready)
- Slack/Teams integration for alerts
- Custom domain templates
- Repository-based analysis (analyze multiple projects)

### 🙏 Contributors

ForgeMind v1.1 development by: AI-assisted code generation + human review + rigorous testing

---

## v1.0.0 — Foundation Release (2026-04)

Initial release with:
- 5 methodological engines (RDMAICSI, Senge, Lean, Six Sigma, QMS)
- 7 domain classifiers
- 12 core output documents
- 7 CLI commands
- 19 tests at 75% coverage
