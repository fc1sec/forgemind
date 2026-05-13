# ForgeMind v1.1.0 Release Notes

**Release Date:** May 13, 2026  
**Version:** 1.1.0 Context Engineering Release  
**Status:** Ready for adoption  

---

## Overview

ForgeMind v1.1 adds **5 new context engineering outputs** to help teams prepare work specifically for AI agents. These new documents define agent boundaries, validate readiness, structure code submission workflows, and collect feedback.

**All new features are automatically generated** — no new commands to learn. Just run `forgemind intake` as before, and you'll get 5 additional outputs alongside the 12 core documents.

---

## What's New: 5 New Generators

### 1. Context File Generator
**Output:** `{project-slug}.context.md`

Prepares agent instruction context from your project analysis.

**Contains:**
- Objective (what the agent should accomplish)
- Key Constraints (boundary conditions)
- Acceptance Criteria (definition of done)
- Top 3 Risks & Mitigation (what could go wrong)
- Key Assumptions to Validate (bets the plan makes)
- Human Review Gates (where humans must approve)
- Definition of Done (checklist before completion)
- Rollback Plan (how to undo if things go wrong)

**Use:** Share with Claude Code, Codex, or other agents before they start work.

---

### 2. AI Risk Readiness Checklist
**Output:** `AI_RISK_CHECKLIST.md`

Domain-specific readiness checklist for AI agents.

**Features:**
- 10 items specific to your project type (AI projects, software, QMS, etc.)
- Scored based on your project's risk register and control plan
- Shows % of checklist addressed (Progress indicator)
- Highlights what still needs attention (⚠️ items)
- Next steps guidance

**Example items for AI projects:**
- ✅ Agent execution boundaries clearly defined
- ✅ Unsafe operations prevented by system design
- ✅ Tool permission matrix implemented
- ✅ Rollback capability for agent-generated changes
- ✅ Human review gates before production
- ✅ Test harness validates agent outputs
- ✅ Audit trail captures all agent decisions
- ✅ Stakeholders aligned on autonomy scope

**Use:** Verify agent readiness before execution.

---

### 3. Tool Permission Matrix
**Output:** `TOOL_PERMISSION_MATRIX.md`

Defines what tools and operations your agent can execute.

**Format:** Clear table showing:
- Tool/Operation
- Permission (✅ Allowed, ✅ Conditional, ⚠️ Restricted, ❌ Denied)
- Reason
- Human Review Gate requirement

**Example entries:**
- Read files: ✅ Allowed
- Modify code: ✅ Conditional (requires tests + linter pass)
- Run tests: ✅ Allowed
- Database migrations: ⚠️ Restricted (requires schema review)
- Deploy to production: ❌ Denied (requires manual approval)
- Modify secrets: ❌ Denied

**Includes implementation guidance:**
- Enable only permitted operations
- Log conditional operations
- Implement approval gates
- Review quarterly

**Use:** Set boundaries before deploying agents.

---

### 4. PR Template for Agent-Generated Code
**Output:** `AGENT_PR_TEMPLATE.md`

GitHub-compatible pull request template for agent-generated code submissions.

**Sections:**
- Description (what was generated and why)
- Pre-Review Checklist (linter, tests, no secrets, comments)
- Acceptance Criteria (from your project)
- Security Review (SQL injection, input validation, error handling)
- Key Risks (from project analysis)
- Merge Requirements (who must approve)
- Rollback Plan (how to revert if needed)

**Use:** Standardize submission requirements for agent PRs.

---

### 5. Issue Template for Feedback on Agent Outputs
**Output:** `AGENT_ISSUE_TEMPLATE.md`

Structured issue template for reporting problems with agent-generated code.

**Sections:**
- Issue Type (Bug, Feature Request, Question)
- Description
- Steps to Reproduce
- Expected vs Actual Behavior
- Environment (ForgeMind version, project domain, agent used, OS, Python)
- Screenshots/Code Samples
- Related Issues

**Use:** Collect consistent feedback when agent outputs need fixes.

---

## How to Use v1.1 Features

### Step 1: Upgrade (if needed)
```bash
cd forgemind
pip install -e ".[dev]"
```

### Step 2: Run intake as usual
```bash
forgemind intake forgemind_projects/your_project.md
```

### Step 3: You get 17 outputs instead of 12
```
forgemind_outputs/your-project/
├── PROJECT_CHARTER.md           (v1.0)
├── RDMAICSI_MATRIX.md           (v1.0)
├── SENGE_LENS.md                (v1.0)
├── LEAN_WASTE_SCAN.md           (v1.0)
├── RISK_REGISTER.md             (v1.0)
├── ASSUMPTION_LOG.md            (v1.0)
├── ACCEPTANCE_CRITERIA.md       (v1.0)
├── BACKLOG.md                   (v1.0)
├── CONTROL_PLAN.md              (v1.0)
├── DECISION_LOG.md              (v1.0)
├── AGENT_HANDOFF.md             (v1.0)
├── README_OUTPUT_INDEX.md       (v1.0)
├── your-project.context.md      (v1.1) ← NEW
├── AI_RISK_CHECKLIST.md         (v1.1) ← NEW
├── TOOL_PERMISSION_MATRIX.md    (v1.1) ← NEW
├── AGENT_PR_TEMPLATE.md         (v1.1) ← NEW
└── AGENT_ISSUE_TEMPLATE.md      (v1.1) ← NEW
```

### Step 4: Use the new outputs
- Share `your-project.context.md` with your agent
- Review `AI_RISK_CHECKLIST.md` to verify readiness
- Use `TOOL_PERMISSION_MATRIX.md` to configure agent permissions
- Copy `AGENT_PR_TEMPLATE.md` into your `.github/pull_request_template.md`
- Copy `AGENT_ISSUE_TEMPLATE.md` into your `.github/ISSUE_TEMPLATE/agent-feedback.md`

---

## Technical Details

### Architecture
- **BaseGenerator** abstract class enforces consistent interface
- **Domain-aware patterns** adapt content to AI projects, software, QMS, operations, etc.
- **Keyword-based scoring** for checklist items
- **Zero external dependencies** — all logic local, no API calls

### Testing
- 16 new test cases (all passing)
- 100% coverage on 5 new generators
- All 19 original v1.0.0 tests still passing
- Total: 35/35 tests passing
- Coverage: 81%

### Backward Compatibility
✅ **Fully backward compatible**
- All v1.0 commands work unchanged
- All v1.0 outputs unchanged
- New outputs are additions, not replacements
- No CLI changes required

---

## What's Included in This Release

### New Files
- `forgemind/generators/base.py` — Abstract base class
- `forgemind/generators/context_generator.py` — Context file generator
- `forgemind/generators/ai_risk_checklist.py` — Risk checklist generator
- `forgemind/generators/tool_permission_matrix.py` — Permission matrix generator
- `forgemind/generators/pr_template.py` — PR template generator
- `forgemind/generators/issue_template.py` — Issue template generator
- `forgemind/generators/__init__.py` — Module exports
- `tests/test_generators.py` — 16 comprehensive tests
- `CHANGELOG.md` — Detailed change history
- `RELEASE_NOTES.md` — This file

### Updated Files
- `README.md` — Updated with v1.1 features
- `pyproject.toml` — Version bumped to 1.1.0
- `forgemind/exporters/markdown.py` — Integrated 5 generators

---

## Breaking Changes

**None.** v1.1 is fully backward compatible with v1.0.

---

## Upgrade Instructions

### For Existing Users
```bash
# No breaking changes — just reinstall
pip install -e ".[dev]"  # or your normal install command

# Existing projects work as-is
forgemind intake forgemind_projects/your_project.md

# You'll now get 17 outputs instead of 12
# No configuration needed
```

### For New Users
```bash
git clone https://github.com/fc1sec/forgemind.git
cd forgemind
pip install -e ".[dev]"

# Start using v1.1 immediately
forgemind init
forgemind intake forgemind_projects/sample_ai_project.md
```

---

## Known Limitations

1. **Domain detection is heuristic-based** — ForgeMind may classify your project differently than expected. If so, the checklists and permission matrix will adapt accordingly.

2. **Keyword-based scoring** — The AI Risk Checklist scores items based on whether keywords appear in your project's risks and control plan. If your risk register uses different terminology, items may be marked as unaddressed even if they're handled.

3. **Local analysis only** — ForgeMind does not call external APIs. Future versions may add optional AI-assisted analysis.

4. **Not a compliance tool** — These outputs are readiness aids, not compliance certifications. You still need to validate assumptions and manage risks yourself.

---

## Future Roadmap

### v1.2 (Planned)
- GitHub Action readiness gate (fail CI if project not ready)
- Slack/Teams integration (readiness alerts)
- Custom domain templates
- Multi-project portfolio tracking

### v2.0 (Future)
- Optional Claude API integration for AI-assisted risk analysis
- Historical project metrics and trends
- Organizational readiness dashboards
- Custom assessment rules per organization

---

## Support & Feedback

- **Issues:** Open an issue on GitHub
- **Feature requests:** Discuss in issues or pull requests
- **Questions:** Check the README and example projects
- **Feedback:** We'd love to hear how you're using ForgeMind

---

## Credits

ForgeMind v1.1 development involved:
- 5 new generators with domain-specific logic
- 16 new test cases (all passing)
- Updated documentation and examples
- Automated integration into existing workflow

Built with: Python 3.9+, Typer, Pydantic, Rich  
Inspired by: RDMAICSI, Peter Senge, Lean, Six Sigma, ISO/QMS  

---

**Thank you for using ForgeMind. Happy planning! 🚀**
