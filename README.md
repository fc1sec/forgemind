# ForgeMind

**A universal multidisciplinary consultant for project readiness.**

ForgeMind acts as a calibrated consultant: it asks targeted questions about
the scope, discipline and variant of your project, discloses what it knows
and what it does NOT cover, then turns your project notes into structured,
governed, agent-ready work packages. It refuses to advise outside its
declared scope rather than improvising.

**Core positioning.** AI agents and human teams can execute fast. ForgeMind
helps you make sure the work is worth executing — *and that the advice you
follow is grounded in real, attributed expertise*, not speculation.

Run `forgemind capabilities` at any time to see exactly which disciplines,
domains and variants ForgeMind covers, and `forgemind explain-limits <domain>`
to read the boundary conditions it discloses.

---

## Why Now?

Coding agents (Claude Code, Codex, GitHub Copilot agent, Cursor) can now:
- Understand your codebase
- Plan changes
- Edit files
- Run commands
- Propose PRs

But agents still execute against vague requirements, unvalidated assumptions, and unclear success criteria.

**The result:** Rework, risk, and confusion—even with smart agents.

ForgeMind bridges that gap. It structures the work *before* the agent starts. Clear objectives. Mapped risks. Validated assumptions. Defined success. Human review gates.

Not runtime monitoring. Pre-execution readiness.

---

## The Consultant Workflow

ForgeMind ships two flows. Use the one that fits your stakes.

### Direct mode — `forgemind intake <project.md>`
One-shot: skip calibration, generate the 17 documents directly. Use this
when you've already calibrated, when scripting in CI, or for low-stakes
exploration.

### Consultant mode — `forgemind consult <project.md>`
A real consultant doesn't dump 17 documents blindly. It calibrates first:

```
1. forgemind capabilities                  ← "what disciplines do you cover?"
2. forgemind compare-variants iso9001      ← "contrast the variants you know"
3. forgemind consult my_project.md         ← calibrated 4-step dialog,
   ├── discipline (e.g. quality_management)    rehúses unsupported domains,
   ├── domain (e.g. iso9001)                   surfaces boundary conditions,
   ├── variant (e.g. CeSPI 8-state)            biases defaults by your history
   └── confirm & generate
4. forgemind followup forgemind_outputs/X  ← "drill into one decision"
5. forgemind history                       ← "what have I calibrated before?"
```

Every successful `consult` writes both `CONSULTANT_CALIBRATION.md` (human)
and `consultant_calibration.json` (machine) alongside the 17 outputs, so a
reviewer can always answer *"what did the consultant calibrate to?"* without
re-running the session.

The consultant refuses (exit code 2 + escalation contact) when:
- the project maps to an out-of-scope-by-design domain (e.g. tenders → legal
  advice, nuclear systems, classified defense, medical diagnosis, …); or
- the user picks a `not_covered` domain (e.g. AS9100, IATF 16949 — patterns
  not yet contributed).

### Self-knowledge

ForgeMind's coverage is **declarative**, sourced from
`forgemind/data/disciplines.yaml`. Today (v1.3.0):

```
6 disciplines · 25 domains · 17 partial · 4 not covered · 6 out-of-scope by design
```

Three domains ship **plural** validated variants (each with full attribution
and decision criteria):

| Domain | Variants |
|--------|----------|
| `iso9001` | CeSPI UNLP 8-state · industry-common minimalist 5-state |
| `software` | blue/green · canary |
| `ai_ml` | feature-flag/checkpoint · shadow deployment |

Six management-system standards now ship HLS Annex SL clause-map variants
(promoted from `not_covered` to `partial` in v1.3.0):

| Domain | Variant | Honest limit |
|---|---|---|
| `iso13485` | HLS clause map | design controls, ISO 14971, FDA QSR / EU MDR still escalate |
| `iso14001` | HLS clause map | aspects/impacts methodology still escalates |
| `iso45001` | HLS clause map | hazard ID + worker consultation still escalate |
| `iso27001` | HLS clause map | Annex A 93 controls + SoA still escalate |
| `iso42001` | HLS + AIIA + Skill Card | external certification still escalates |
| `iso22301` | HLS clause map | BIA + RTO/RPO still escalate |

All other partial domains ship a single validated variant each. See
`ATTRIBUTIONS.md` for upstream credit and `CONTRIBUTING_REVERSE_PATTERNS.md`
for how to contribute new variants.

### Citable doctrines (new in v1.3.0)

ForgeMind anchors its outputs in named, attributed doctrines from
[fc1sec/CertOS-SAGA](https://github.com/fc1sec/CertOS-SAGA):

```
forgemind doctrines                       # list all 11
forgemind doctrines --category constitutional
forgemind doctrines D41                   # show capability thresholds
forgemind doctrines aiia_pre_deployment   # show AIIA gate
```

The registry ships **11 doctrines** across three categories:

- **Constitutional** (D39–D45): Agentic Constitution, AIIA, Capability
  Thresholds, Skill Card, AIMS-integrated-SGC.
- **Operational** (D06, D17, D22, D37, D38): agnostic routing, evidence
  scoring, token governance, evidence integrity, multi-norm Annex SL.
- **Methodological** (D02, D05): agentic RDMAICSI, integral speed.

### Constitutional governance outputs (new in v1.3.0)

The standard output bundle grows from 17 → **19** (universal) or **22**
(AI/ML domains):

| File | Universal? | Anchor |
|---|---|---|
| `EVIDENCE_SCORING.md` | yes | D17 + D37 |
| `TOKEN_COST_GOVERNANCE.md` | yes | D22 + D06 |
| `AIIA_PRE_DEPLOYMENT.md` | AI/ML only | D40 (ISO/IEC 42001 §6.1.4) |
| `CAPABILITY_THRESHOLDS.md` | AI/ML only | D41 (Anthropic RSP, EU AI Act Art. 14) |
| `SKILL_CARD.md` | AI/ML only | D43 (EU AI Act Art. 13) |

### Self-audit — ForgeMind applies its own doctrines to itself

ForgeMind eats its own dog food. The same doctrines it cites for users
are enforced against the ForgeMind codebase by:

```bash
forgemind self-audit                  # print findings, exit non-zero on blocker
forgemind self-audit --write-report   # also regenerate docs/governance/SELF_AUDIT_REPORT.md
forgemind self-audit --quiet          # counts only (suited for CI)
```

The audit is wired into CI ([.github/workflows/tests.yml](.github/workflows/tests.yml));
a blocker finding fails the build. The current report and ForgeMind's
own governance artefacts live in [`docs/governance/`](docs/governance/):

| Artefact | Anchor doctrine |
|---|---|
| [FORGEMIND_CONSTITUTION.md](docs/governance/FORGEMIND_CONSTITUTION.md) | D39 |
| [FORGEMIND_AIIA.md](docs/governance/FORGEMIND_AIIA.md) | D40 |
| [FORGEMIND_CAPABILITY_THRESHOLDS.md](docs/governance/FORGEMIND_CAPABILITY_THRESHOLDS.md) | D41 |
| [FORGEMIND_SKILL_CARD.md](docs/governance/FORGEMIND_SKILL_CARD.md) | D43 |
| [SELF_AUDIT_REPORT.md](docs/governance/SELF_AUDIT_REPORT.md) | regenerated by `self-audit` |

---

## Works Before

ForgeMind prepares work for:

- **Claude Code** — Structured context for autonomous code execution
- **Codex** — Clear boundaries and acceptance criteria
- **GitHub Copilot agent** — Risk-aware task handoff
- **Cursor** — Agent-ready work packages
- **Generic AI agents** — Local readiness without external APIs
- **Human implementation teams** — Same structured governance

---

## Pre-AgentOps

**What ForgeMind is:**
- Pre-execution readiness (before your agent starts)
- Structured planning with governance gates
- Risk, assumption, and success criteria mapping
- Handoff preparation with human review

**What ForgeMind is NOT:**
- Runtime monitoring (doesn't watch agents work)
- Production observability (doesn't track deployed systems)
- Compliance certification (readiness aid, not guarantee)
- Agent orchestration (doesn't manage agent execution)

ForgeMind is the layer *before* AgentOps—before your agent runs, you need readiness.

---

## New to ForgeMind? Start Here

[**→ First-Time User Guide** (15 minutes)](docs/FIRST_TIME_USER_GUIDE.md)

A guided walkthrough covering:
- Installation and your first project analysis
- Understanding ForgeMind's capabilities and limitations
- Deciding if ForgeMind matches your needs

**Also read:**
- [**What ForgeMind Is (and Is Not)**](#what-forgemind-is-and-is-not-2)
- [**System Transparency Statement**](docs/AI_SYSTEM_TRANSPARENCY.md) (EU AI Act compliance)
- [**Supported Domains**](docs/SUPPORTED_DOMAINS.md) (domain coverage matrix)

---

## What ForgeMind Is (and Is Not)

### ✅ ForgeMind Is:
- A **structured planning tool** that surfaces risks, assumptions, and gaps
- **Analysis before execution** — helps you decide if work is worth doing
- **Local and private** — runs on your computer, never goes to the cloud
- **Domain-aware** — generates guidance specific to software, AI/ML, QMS, and other domains
- **Honest about limitations** — tells you what it can and cannot do

### ❌ ForgeMind Is NOT:
- A decision-maker (you decide what to do with its analysis)
- A code generator (it generates documents, not executable code)
- A guarantee of success (good planning reduces risk, doesn't eliminate it)
- A compliance certifier (it structures planning, you validate with experts)
- A replacement for human review (all outputs require validation by qualified personnel)

**[Full transparency statement →](docs/AI_SYSTEM_TRANSPARENCY.md)**

---

## Why ForgeMind?

### The Problem

Your team has great ideas. But translating ideas into work that's actually ready for execution is hard:

- **Unclear objectives** lead to rework
- **Unvalidated assumptions** cause surprises  
- **Missing acceptance criteria** make success unclear
- **Unmanaged risks** blow up mid-project
- **Agents execute fast, but wrong work wastes time**

ForgeMind helps you structure work rigorously before execution starts.

### The Solution

ForgeMind reads your Markdown project notes and generates:

1. **Structured analysis** using proven methodologies (RDMAICSI, Senge, Lean, Six Sigma)
2. **Risk registers and assumption logs** to surface vulnerabilities
3. **Acceptance criteria and control plans** to define success and prevent drift
4. **Prioritized backlog** with governance gates
5. **Agent-ready handoffs** with all context, constraints, and human review gates

No external AI API calls. No database. Pure local analysis and structured output.

---

## Method Foundations

ForgeMind is inspired by:

- **RDMAICSI** — Eight-phase continuous improvement (Recognize → Integrate)
- **Peter Senge** — Five disciplines of learning organizations
- **Lean Thinking** — Waste reduction and flow
- **Six Sigma** — Root cause analysis and measurement discipline
- **ISO/QMS Discipline** — Evidence, traceability, documented decisions, human accountability

**Important:** ForgeMind is NOT a certification tool. It supports governance and readiness, not compliance certification. Use language like "helps structure" not "guarantees."

---

## How It Works

```
Project Note (Markdown)
         ↓
    ForgeMind
         ↓
17 Structured Outputs
(risk, assumptions, criteria, agent context, etc.)
         ↓
    AI Agent or Human Team
```

---

## Installation

### From source (recommended for v1.0.0)

```bash
git clone https://github.com/fc1sec/forgemind.git
cd forgemind
pip install -e ".[dev]"
```

### From PyPI (when available)

```bash
pip install forgemind
```

### First-Time Setup

When you run `forgemind init` for the first time, ForgeMind will show you:
- A 2-minute orientation explaining what ForgeMind does
- What ForgeMind does NOT do (limitations)
- An option to run the demo analysis

See [First-Time User Guide](docs/FIRST_TIME_USER_GUIDE.md) for step-by-step walkthrough.

---

## Status

| Badge | Info |
|-------|------|
| **Version** | v1.2.1 (Update Safety + Version Checking) |
| **Maturity** | Beta — Ready for early adopters |
| **Python** | 3.9+ |
| **License** | MIT |
| **CI/CD** | Tests + Linting required |
| **Backward Compat** | ✅ Full (v1.1.0 projects work unchanged) |

### Version Safety Guarantee

✅ **All ForgeMind updates are non-blocking and safe**

- Version checks run once daily (fail silently, won't interrupt work)
- Updates never modify existing projects
- Easy rollback anytime: `pip install forgemind==1.2.0`
- Backward compatible with all v1.x projects

See [UPDATES_AND_SAFETY.md](docs/UPDATES_AND_SAFETY.md) for detailed safety procedures.

---

## Demo (60 seconds)

```bash
# 1. Initialize workspace
forgemind init

# 2. Analyze a project
forgemind intake forgemind_projects/sample_ai_project.md

# 3. Check readiness
forgemind diagnose forgemind_projects/sample_ai_project.md

# Output: 17 analysis documents in forgemind_outputs/sample-ai-project/
```

**Sample output preview:**
- `PROJECT_CHARTER.md` — Objective, scope, constraints
- `RISK_REGISTER.md` — Threats, impact, mitigation, owners
- `ASSUMPTION_LOG.md` — Bets, validation criteria
- `ACCEPTANCE_CRITERIA.md` — Definition of done
- `CONTROL_PLAN.md` — Prevent drift, maintain scope
- + 7 more methodology lenses and governance documents

---

## Quick Start

### 1. Initialize workspace

```bash
forgemind init
```

This creates:
- `forgemind_projects/` — Your project input files
- `forgemind_outputs/` — Generated analyses
- `forgemind_projects/sample_ai_project.md` — Example project

### 2. Create or edit a project file

Edit `forgemind_projects/your_project.md`:

```markdown
# Your Project Name

## Objective
What are we trying to accomplish?

## Context
Why is this important? What's the background?

## Scope
What's in scope? What's out?

## Constraints
Timeline, budget, technical limitations?

## Risks
What could go wrong?

## Success Criteria
How do we know we succeeded?
```

### 3. Analyze the project

```bash
forgemind intake forgemind_projects/your_project.md
```

This generates 17 analysis documents in `forgemind_outputs/your-project/`, including 5 new v1.1 context engineering outputs.

### 4. Quick readiness check

```bash
forgemind diagnose forgemind_projects/your_project.md
```

Prints a summary: domain, maturity, top risks, critical gaps.

### 5. Check readiness gates

```bash
forgemind gate forgemind_projects/your_project.md
```

Returns exit code 0 if ready, 1 if critical items are missing.

### 6. Generate agent handoff

```bash
forgemind handoff forgemind_projects/your_project.md --target codex
```

Targets: `codex`, `claude-code`, `generic-agent`

### 7. Export as JSON

```bash
forgemind export forgemind_projects/your_project.md --format json
```

---

## Commands

### `forgemind init`
Initialize workspace with sample project and directories.

### `forgemind capabilities [--discipline X]`
Show ForgeMind's declared coverage map: 6 disciplines, 23 domains, with
per-domain coverage tier (`covered` / `partial` / `not_covered`), confidence,
and escalation contact. Filter to a single discipline with `--discipline`.

### `forgemind explain-limits <domain>`
Honest disclosure for one domain: validated variants ForgeMind knows about
(with sources and confidence), known gaps within those variants, and the
domain's escalation contact. Use BEFORE relying on ForgeMind's advice in
regulated or high-stakes contexts.

### `forgemind compare-variants <domain>`
Side-by-side decision support card across the variants ForgeMind knows for
a domain: when to choose each variant, what you gain, what you give up.
Sources and confidence per variant are surfaced. Returns exit 0 with a
"nothing to compare" message for single-variant domains.

### `forgemind consult <project_file>`
**The consultant mode** — calibrate before generating. Walks the user through
a 4-step adaptive dialog (discipline → domain → variant → confirm), refuses
unsupported domains with exit code 2 + escalation contact, and only then
generates the 17 outputs. Writes both `CONSULTANT_CALIBRATION.md` and
`consultant_calibration.json` alongside the documents.

Defaults are biased by your `forgemind history` so steady-state workflows
become "press Enter" while remaining fully overridable.

Flags:
- `--auto-accept` — pick defaults without prompting (CI / scripting)
- `--output-dir <path>` — override the default output directory

### `forgemind followup <output_dir>`
Revisit specific decisions in depth after a `consult` session. Loads the
calibration sidecar and lets you drill into one topic without re-running
analysis.

Modes:
- interactive (default) — menu loop
- `--topic <key>` — render one topic and exit (`variant`, `risks`,
  `acceptance`, `escalation`)
- `--auto-accept` — print menu and exit (CI-friendly)

### `forgemind history [--limit N] [--clear]`
View or erase ForgeMind's calibration memory. Each successful `consult`
appends one entry to a local JSONL file (`~/.forgemind/history.jsonl`,
overridable via `FORGEMIND_HISTORY_PATH`). The store is LOCAL ONLY — no
telemetry is collected or transmitted.

### `forgemind intake <project_file>`
Analyze project and generate 17 structured output documents:

**Core Governance (12 documents):**
1. PROJECT_CHARTER.md
2. RDMAICSI_MATRIX.md
3. SENGE_LENS.md
4. LEAN_WASTE_SCAN.md
5. RISK_REGISTER.md
6. ASSUMPTION_LOG.md
7. ACCEPTANCE_CRITERIA.md
8. BACKLOG.md
9. CONTROL_PLAN.md
10. DECISION_LOG.md
11. AGENT_HANDOFF.md
12. README_OUTPUT_INDEX.md

**v1.1 Context Engineering (5 new documents):**
13. `{project-slug}.context.md` — Agent instruction context with risks, assumptions, review gates
14. AI_RISK_CHECKLIST.md — Domain-specific readiness checklist
15. TOOL_PERMISSION_MATRIX.md — Agent execution constraints and permissions
16. AGENT_PR_TEMPLATE.md — PR submission requirements for agent-generated code
17. AGENT_ISSUE_TEMPLATE.md — Issue reporting template for feedback

**v1.2 Reverse Patterns (automatic if domain supported):**
- Enhanced `{project-slug}.context.md` now includes reversal/rollback plans from domain-specific plugins
- Automatic discovery: If project domain has registered pattern (ISO 9001, Software, AI/ML), reversal plan generated
- Includes: rollback path, time estimates, data loss risk, approval gates, reversal steps, dependencies, constraints
- Epistemic classification: DETERMINISTIC (standard-based), STOCHASTIC (empirical), or ESCALATE (domain not supported)
- Escalation info if pattern not available: suggests domain expert contact, contribution guide

### `forgemind diagnose <project_file>`
Quick terminal summary: project name, domain, maturity, top risks, critical gaps.

### `forgemind gate <project_file>`
Check minimum readiness gates. Returns exit code 0 (ready) or 1 (not ready).

Validates:
- Objective exists
- Context exists
- Scope exists
- Risks generated
- Assumptions generated
- Acceptance criteria generated
- Control plan exists
- Human review gates defined
- Outputs can be generated

### `forgemind handoff <project_file> --target <target>`
Generate agent-ready handoff for codex, claude-code, or generic-agent.

### `forgemind export <project_file> --format json`
Export analysis as JSON with all structured data.

---

## Example Input

```markdown
# AI Backend Automation Agent

## Objective
Develop an AI agent that generates backend microservice boilerplate autonomously, 10x faster than manual setup while maintaining code quality and security standards.

## Context
Our team spends 4-6 hours per service on boilerplate setup. An agent could reduce this to 30 minutes of AI work + 1-2 hours of human review.

## Scope
- Agent reads service specs
- Generates models, routes, tests
- Validates against patterns
- Submits PR for human review

## Out of Scope
- Database schema design
- Production deployment
- Security fixes (all require human review)

## Constraints
- No external API calls
- All decisions must be auditable
- Cannot modify production code directly
- All outputs go to PR for approval first

## Stakeholders
- Engineering Lead (review & approve PRs)
- Security Team (review for vulnerabilities)
- Platform Team (CI/CD integration)

## Risks
- Agent generates insecure patterns
- Agent hallucinates non-existent APIs
- Scope creeps to dangerous operations

## Success Criteria
- Generated code passes linter without edits
- Security review completes in <1 hour
- First 5 agents ship successfully to production
```

---

## Example Output

ForgeMind generates structured Markdown and JSON:

### PROJECT_CHARTER.md
High-level project definition with objective, scope, constraints, success criteria.

### RISK_REGISTER.md
Identified risks with cause, impact, probability, severity, mitigation, owner.

### ACCEPTANCE_CRITERIA.md
Specific, testable criteria for project success.

### BACKLOG.md
Prioritized work items (P0 = critical, P1 = important, P2 = useful, P3 = polish).

### AGENT_HANDOFF.md
Agent-ready handoff with objective, context, constraints, assumptions, risks, acceptance criteria, human review gates, definition of done, rollback notes.

### And 7 more documents...

All files include the ForgeMind header:
```
Generated by ForgeMind
This output is a readiness aid, not a certification or compliance guarantee.
```

---

## When to Use ForgeMind

✅ **Use ForgeMind when:**
- You're handing work to an AI agent or team (need clarity before execution)
- You've shipped things you shouldn't have (want upfront rigor)
- You face analysis paralysis (need structure to move forward)
- You need audit-ready documentation (compliance-sensitive work)
- You want to prevent scope creep (control during execution)
- You're designing processes (operations, QMS, ERP)

❌ **Don't use ForgeMind for:**
- Tactical/daily firefighting (this is strategic)
- Replacing domain expertise (you still need that)
- Automated compliance certification (it's a readiness aid)
- Projects where requirements are already crystal clear
- Real-time operational decisions (analysis, not runtime)

---

## Use Cases

### 🤖 AI Project Readiness
Before agents execute:
- Define autonomy boundaries clearly
- Identify unsafe execution scope
- Create test harness for boundary validation
- Establish human review gates

### 🔗 Agent Handoff
Prepare work for Codex, Claude Code, or other agents:
- Structured context
- Clear constraints
- Listed assumptions
- Risk awareness
- Rollback notes

### 🚀 Software Feature Planning
Before engineering starts:
- Clear requirements
- Test strategy
- Deployment plan with rollback
- Acceptance criteria
- Risk mitigation

### 📋 QMS/ISO-Inspired Readiness
For compliance-sensitive work:
- Document control
- Evidence requirements
- Process clarity
- Audit readiness checklist

### 🏭 Operations & ERP Process Mapping
For process improvement:
- Workflow clarity
- Handoff points defined
- Metrics and SLAs
- Control mechanisms

---

## Safety and Limitations

### What ForgeMind IS
- A readiness aid that structures work before execution
- A methodology framework for thinking rigorously about projects
- A generator of checklists, registers, and work packages
- A tool for surfacing risks and assumptions

### What ForgeMind IS NOT
- A replacement for human judgment or review
- An ISO/QMS certification tool
- A guarantee of safe execution
- A replacement for domain expertise
- A tool for automated compliance validation
- An external API caller (all logic is local in v1)

### Important Notes

1. **Not a certification engine** — ForgeMind helps you structure work. It does not certify ISO, compliance, or safe AI execution. That's your responsibility.

2. **Human review is required** — Every project should have human review gates before execution. ForgeMind highlights where these are needed; you implement them.

3. **Assumptions must be validated** — ForgeMind generates assumption logs. You must validate critical assumptions before proceeding.

4. **Risks are starting points** — ForgeMind identifies common risks for your domain. Your team must complete risk analysis and mitigation.

5. **Local execution** — ForgeMind does not call external AI APIs. All analysis is local using keyword rules and templates. (Future versions may integrate with AI services with explicit user approval.)

---

## Roadmap

### v1.1 (Current) — Context Engineering ✅
- ✅ Context file generator (prep agent instruction context)
- ✅ AI risk checklist (agent-specific risk patterns)
- ✅ Tool permission matrix (what your agent can/cannot do)
- ✅ PR readiness template (submission requirements before agent executes)
- ✅ Issue template generator (feedback collection for agent-generated code)

### v1.2 (Current) — Reverse Patterns + Plugin System ✅
- ✅ Extensible plugin architecture for domain-specific patterns (ReverseStatePattern ABC)
- ✅ Plugin registry system with automatic pattern discovery
- ✅ Built-in patterns: ISO 9001 QMS, Software Deployments, AI/ML Models
- ✅ YAML template system for reverse pattern documentation
- ✅ ReverseContextGenerator for automatic reversal plan generation
- ✅ EpistemicValidator (prevents hallucination: DETERMINISTIC/STOCHASTIC/ESCALATE)
- ✅ Confidence scoring and scope validation guardrails
- ✅ Community contribution guide (CONTRIBUTING_REVERSE_PATTERNS.md)
- ✅ 28 new tests for plugin system (90%+ coverage)
- ✅ ISO 9001 plugin upgraded to 8-state CeSPI UNLP production variant (attributed)
- ✅ Second ISO 9001 variant: minimalist 5-state (industry-common pattern)

### v1.2.x (Current) — Consultant role ✅
Six-layer consultant model, all delivered and tested:
- ✅ **Phase D — Disciplines taxonomy**: declarative coverage map in
  `forgemind/data/disciplines.yaml`; 6 disciplines · 23 domains · 6
  out-of-scope-by-design. Exposed via `forgemind capabilities` and
  `forgemind explain-limits`.
- ✅ **Phase C — Consult dialog**: `forgemind consult` walks an adaptive
  4-step calibration (discipline → domain → variant → confirm) before
  generating, with a structured refusal protocol.
- ✅ **Variant pluralism**: a domain can declare multiple validated
  variants; the consultant offers each with attribution and confidence.
- ✅ **Variant comparison**: `forgemind compare-variants` renders a
  side-by-side decision card (when-to-choose, pros, cons).
- ✅ **Follow-up**: `forgemind followup` reads the calibration sidecar
  and drills into one decision (variant, risks, acceptance, escalation)
  without re-running analysis.
- ✅ **Persistent memory**: `forgemind history` records each calibration
  locally and biases future defaults toward prior choices.

### v1.3 (Medium term) — MethodOps Learning Layer
- Knowledge graph schema for capturing project outcomes
- GitHub/Jira integration for automatic outcome capture
- Recommendation engine (what succeeded for similar projects?)
- Feedback loop system (`forgemind feedback` command)
- Aggregated lessons dashboard

### v2.0 (Future) — Full MethodOps Platform
- Optional integration with Claude API for AI-assisted risk analysis
- Multi-project portfolio tracking
- Historical project metrics
- Readiness trend analysis
- Custom assessment rules per organization

### Anti-patterns (What we will NOT do)
- Build a SaaS platform (ForgeMind stays local-first)
- Add external AI API dependency without explicit opt-in
- Claim to certify compliance or safety
- Build a marketplace of plugins (keep it simple)
- Implement database dependencies (stay portable)
- Replace human judgment with automated decisions
- Become a runtime agent monitor (that's AgentOps, not PreAgentOps)

---

## Examples

Three example projects included:

1. `examples/ai_agent_project.md` — AI backend automation agent
2. `examples/software_feature_project.md` — Dashboard feature implementation
3. `examples/qms_sgc_project.md` — QMS document control stabilization
4. `examples/odoo_process_project.md` — ERP lot/serial traceability
5. `examples/tender_analysis_project.md` — Government tender compliance

Run analysis on any:
```bash
forgemind intake examples/ai_agent_project.md
forgemind diagnose examples/ai_agent_project.md
forgemind gate examples/ai_agent_project.md
```

---

## Plugin Contributions

ForgeMind's reverse pattern system is extensible. Community experts can contribute domain-specific patterns without modifying core code.

**Want to contribute a pattern for your domain?**
- **See:** `CONTRIBUTING_REVERSE_PATTERNS.md` for contributor guide
- **Reference:** `forgemind/templates/reverse_patterns/` for examples (ISO 9001, Software, AI/ML)
- **Process:** Research domain → Create plugin → Add YAML template → Write tests → Submit PR
- **Examples:** Government procurement reversals, biomedical device workflows, hardware firmware rollback, infrastructure-as-code patterns

**v1.3 Roadmap Issues to Open**

Community interest in these features? Open an issue to discuss:

1. **Knowledge graph for project outcomes** — Learn which mitigations succeeded across projects
2. **GitHub/Jira integration** — Auto-capture project success/failure outcomes
3. **Multi-project portfolio tracking** — Analyze readiness trends across projects
4. **Recommendation engine** — "What mitigations worked for projects like yours?"
5. **Custom assessment rules** — Organization-specific patterns and gates

---

## Contributing

Contributions welcome. Please:

1. Run tests: `pytest`
2. Check lint: `ruff check .`
3. Keep dependencies minimal
4. Follow existing patterns
5. Test new domains or methodologies thoroughly

---

## License

MIT License. See LICENSE file.

---

## Support

For issues, feature requests, or feedback:
- Open an issue on GitHub
- Check existing documentation
- Review example projects for usage patterns

---

**Built with:** Python 3.9+, Typer, Pydantic, Jinja2, Rich
**Inspired by:** RDMAICSI, Peter Senge, Lean, Six Sigma, ISO/QMS
**Grounded in (attributed):** iso-gestion (CeSPI UNLP, MIT) — see `ATTRIBUTIONS.md`
**Philosophy:** Structure work rigorously. Refuse cleanly. Calibrate before generating.
**Status:** v1.2.x consultant role • Beta maturity • 213 tests passing • CI green on Python 3.9 / 3.11 / 3.12
**Safety:** ✅ Backward compatible · Local-only · No telemetry · Refuses out-of-scope domains
