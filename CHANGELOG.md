# ForgeMind Changelog

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
