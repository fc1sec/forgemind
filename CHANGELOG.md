# ForgeMind Changelog

## v1.3.0 — Constitutional Governance (2026-05-16)

ForgeMind absorbs the constitutional and operational doctrines of
[fc1sec/CertOS-SAGA](https://github.com/fc1sec/CertOS-SAGA) and turns
them into first-class ForgeMind primitives: a named doctrines registry,
an HLS-Annex-SL multi-norm taxonomy upgrade, and five new output
artefacts. ForgeMind is now able to anchor every recommendation it
emits in a citable, attributed doctrine.

### Layer 7 — Doctrines registry

- New file: `forgemind/data/doctrines.yaml` (11 doctrines · 3 categories
  · all sourced from CertOS-SAGA with normative anchors).
- New module: `forgemind/doctrines/` typed API (`Doctrine`,
  `DoctrineCategory`, `DoctrineSource`, `DoctrineRegistry`).
- New CLI command: `forgemind doctrines [<id|short_id>] [--category]`
  — list every doctrine, or show purpose + summary + normative anchors
  + source URL for a single one.
- Anti-hallucination invariant (test-enforced): every doctrine MUST
  declare a source attribution AND at least one normative anchor.

### Layer 8 — Multi-norm Annex SL coverage upgrade

Six management-system standards move from `not_covered` to `partial`,
each with an `hls_annex_sl_clause_map` variant + honest boundary
conditions about what ForgeMind does **not** model:

- `iso13485` (Medical Devices) — HLS skeleton; design controls / ISO
  14971 / FDA QSR / EU MDR submission packs still escalate.
- `iso14001` (Environmental) — HLS skeleton; aspects/impacts methodology
  + Amd 1:2024 climate-action evidence still escalate.
- `iso45001` (OH&S) — HLS skeleton; hazard identification + worker
  consultation + incident investigation still escalate.
- `iso27001` (Information Security 2022) — HLS skeleton; Annex A (93
  controls) + Statement of Applicability + ISO/IEC 27005 still escalate.
- `iso42001` (AI Management System) — HLS skeleton + AIIA + Skill Card +
  Capability Thresholds; Annex B/C controls + external certification still escalate.
- `iso22301` (Business Continuity) — HLS skeleton; BIA + RTO/RPO +
  exercise programme still escalate.

Two new domains within `operations_methodops`:

- `pokayoke_patterns` — 10-type mistake-proofing taxonomy (Shingo ZQC
  operationalised in CertOS-SAGA D30 for ERP/QMS change discipline).
- `agnostic_task_routing` — 7-tier decision hierarchy (rule → cache →
  small model → strong model → human) from CertOS-SAGA D06.

### Layer 9 — Constitutional-governance outputs

Five new artefacts join the standard output bundle:

**Universal (every project)**:
- `EVIDENCE_SCORING.md` — 5-level confidence scale + penalties +
  3-tier integrity (SHA-256 chain → Ed25519 signature → NOM-151/RFC 3161).
  Anchors: D17 + D37.
- `TOKEN_COST_GOVERNANCE.md` — 5-level routing decision card + 7-step
  agnostic routing hierarchy + per-task routing contract + cost-savings
  rules. Anchors: D22 + D06.

**AI / ML domains** (added when `analysis.metadata.domain` is one of
`ai_project`, `ai_ml`, `llm_agents`, `classical_ml`):
- `AIIA_PRE_DEPLOYMENT.md` — 8-section AI Impact Assessment gate (NIST
  AI 600-1 GenAI Profile 12 risks, EU AI Act Art. 9 categorisation,
  signed approvals). Anchor: D40 (ISO/IEC 42001 §6.1.4).
- `CAPABILITY_THRESHOLDS.md` — 7 hard HITL thresholds + agent behaviour
  protocol + override policy. Anchors: D41 (Anthropic RSP, EU AI Act
  Art. 14, NIST AI RMF GOVERN).
- `SKILL_CARD.md` — 12-section machine-readable manual per AI skill
  (identification → purpose → owners → model → capabilities → limits →
  data accessed → accuracy metrics → safe-use assumptions → fallback →
  version history → signature block). Anchors: D43 (EU AI Act Art. 13,
  OECD AI Principles, ISO/IEC 42001 §7.5).

Output count grows from 17 → **19** (universal) or **22** (AI/ML domains).

### Coverage snapshot

```
6 disciplines · 25 domains · 17 partial · 4 not covered · 6 out-of-scope by design
                                              ↑ up from 9 partial in v1.2.x
```

### Compatibility

- v1.2.x and v1.1.0 projects work unchanged.
- No public-API breaking changes; `forgemind doctrines` is purely additive.
- Output bundle is a strict superset of v1.2.x.

### Attribution

All new doctrines and the multi-norm upgrade draw from
[fc1sec/CertOS-SAGA](https://github.com/fc1sec/CertOS-SAGA) — see
`ATTRIBUTIONS.md` for the per-doctrine source map and
`forgemind doctrines <id>` for inline citations at runtime.

### Layer 10 — Self-audit loop (eat-your-own-dogfood)

After importing the doctrines, ForgeMind applied them **to itself** and
found 4 blockers (no Constitution, no AIIA, no Capability Thresholds,
no Skill Card for ForgeMind-the-tool). All 4 are now closed.

- New module: `forgemind/self_audit/` — one check function per
  registered doctrine; renders a `SelfAuditReport` as Markdown.
- New CLI: `forgemind self-audit [--write-report] [--quiet]` — exits
  non-zero on any blocker so CI can gate releases.
- New CI step: `.github/workflows/tests.yml` runs `forgemind self-audit
  --quiet` after the test suite.
- New governance artefacts in `docs/governance/`:
    · `FORGEMIND_CONSTITUTION.md` (anchored on D39 — mission, 5
      lexicographic values, 3-question pre-invocation test, veto)
    · `FORGEMIND_AIIA.md` (anchored on D40 — 8 sections; addresses the
      meta-AI risk that ForgeMind shapes downstream-agent governance)
    · `FORGEMIND_CAPABILITY_THRESHOLDS.md` (anchored on D41 — the 7
      hard limits ForgeMind itself never crosses)
    · `FORGEMIND_SKILL_CARD.md` (anchored on D43 — 12 sections; declares
      `model = NONE (deterministic Python)` and `token cost = 0`)
    · `SELF_AUDIT_REPORT.md` (regenerated by the CLI; do not hand-edit)
- New tests (14): `tests/test_self_audit.py` enforces that
    (a) every registered doctrine has a corresponding check function,
    (b) no orphan checks exist,
    (c) the governance/ artefacts exist and contain the required sections,
    (d) the CLI exits zero on GREEN and writes a renderable report.

**Outcome:** `forgemind self-audit` returns GREEN with 0 blockers,
0 warnings, 7 info findings. The doctrines registry stops being
decorative — every doctrine carries a check that verifies the codebase
honours it.

This implements **D02 Agentic RDMAICSI** as a closed loop on
ForgeMind itself:
R-recognize · D-define · M-measure (audit) · A-analyze (findings) ·
I-improve (artifacts) · C-control (CI gate) · S-systematize
(governance/ folder) · I-institutionalize (this CHANGELOG entry).

---

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
