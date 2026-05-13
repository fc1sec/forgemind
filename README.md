# ForgeMind

**The readiness layer before AI agents build.**

ForgeMind turns vague ideas, issues, and project notes into structured, governed, agent-ready work packages. It helps teams ensure work is worth executing before agents (or humans) build it.

**Core Positioning:** AI agents can execute fast. ForgeMind helps teams make sure the work is worth executing before agents build.

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
12 Structured Outputs
(risk, assumptions, criteria, etc.)
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

---

## Status

| Badge | Info |
|-------|------|
| **Version** | v1.0.0 (Foundation Release) |
| **Maturity** | Beta — Ready for early adopters |
| **Python** | 3.9+ |
| **License** | MIT |
| **CI/CD** | Tests + Linting required |

---

## Demo (60 seconds)

```bash
# 1. Initialize workspace
forgemind init

# 2. Analyze a project
forgemind intake forgemind_projects/sample_ai_project.md

# 3. Check readiness
forgemind diagnose forgemind_projects/sample_ai_project.md

# Output: 12 analysis documents in forgemind_outputs/sample-ai-project/
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

This generates 12 analysis documents in `forgemind_outputs/your-project/`.

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

### `forgemind intake <project_file>`
Analyze project and generate 12 structured output documents:
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

### v1.0.1 (Current)
- Positioning polish
- README improvements
- Foundation release refinement

### v1.1 (Near term) — Context Engineering
- Context file generator (prep agent instruction context)
- AI risk checklist (agent-specific risk patterns)
- Tool permission matrix (what your agent can/cannot do)
- PR readiness template (submission requirements before agent executes)

### v1.2 (Medium term) — Pre-AgentOps Layer
- GitHub Action readiness gate (check before merge)
- Slack/Teams integration for readiness alerts
- Integration with GitHub/GitLab for repo-based analysis
- Custom domain templates

### v2.0 (Future) — MethodOps Platform
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

## Roadmap Issues to Open

Community interest in these features? Open an issue to discuss:

1. **Context file generator** — Generate `.context` file from project analysis for agent instructions
2. **AI risk checklist** — Domain-specific risk patterns for Claude Code, Codex, Cursor
3. **Tool permission matrix** — Define what tools/APIs your agent can use
4. **PR readiness template** — Acceptance criteria for PRs generated by agents
5. **GitHub Action readiness gate** — Fail CI if project doesn't pass readiness checks

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
**Philosophy:** Structure work rigorously before execution.  
**Status:** v1.0.0 foundation release • Beta maturity • Looking for early adopters
