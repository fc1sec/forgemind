# AI Backend Automation Project

> **Example Type**: Complete AI/ML Project  
> **Domain**: `ai_project`  
> **How to use**: Run `forgemind intake examples/ai_agent_project.md` to generate analysis  
> **Time to analyze**: ~2 seconds  
> **Generated outputs location**: `forgemind_outputs/ai-backend-automation-project/`

---

## What ForgeMind Will Generate

When you analyze this project, ForgeMind will create 17 documents:

**Core Analysis Documents:**
- `PROJECT_CHARTER.md` — Clear objective, scope, success criteria, stakeholders
- `RISK_REGISTER.md` — Detailed risk analysis for AI/ML (security, hallucination, scope creep risks)
- `ASSUMPTION_LOG.md` — Critical assumptions (about model quality, API availability, etc.)
- `ACCEPTANCE_CRITERIA.md` — Testable success metrics
- `CONTROL_PLAN.md` — How to prevent scope creep and maintain boundaries

**Framework Lenses:**
- `RDMAICSI_MATRIX.md` — Eight-phase improvement cycle (Recognize→Integrate)
- `SENGE_LENS.md` — Five disciplines for learning organizations
- `LEAN_WASTE_SCAN.md` — Where time/money could be wasted
- `DECISION_LOG.md` — Key decisions and reasoning

**AI/ML Specific Documents:**
- `AI_RISK_CHECKLIST.md` — Hallucination, safety, security concerns
- `TOOL_PERMISSION_MATRIX.md` — What the agent can and cannot do
- `AGENT_HANDOFF.md` — Complete context for Claude Code or other AI agents
- `AGENT_PR_TEMPLATE.md` — PR submission requirements for agent-generated code
- `AGENT_ISSUE_TEMPLATE.md` — Feedback template for issues

**Reference & Navigation:**
- `{project-slug}.context.md` — Rich agent instruction context with all risks, assumptions, gates
- `README_OUTPUT_INDEX.md` — Guide to all 17 outputs

**Plus: Reversal Plan** (if supported)
- Enhanced context.md includes rollback strategy if agent fails or produces unsafe code

---

## Domain-Specific Notes for AI/ML Projects

For AI/ML projects, **ForgeMind will:**
- ✅ Identify safety and security risks (hallucination, data leaks, scope creep)
- ✅ Flag human review gates (security team, engineering lead approval)
- ✅ Create agent handoff with clear boundaries and constraints
- ✅ Suggest testing gates and validation strategies
- ✅ Highlight assumptions about model behavior

**ForgeMind will NOT:**
- ❌ Design your agent's architecture
- ❌ Guarantee the agent will be safe (you provide domain expertise)
- ❌ Write agent code
- ❌ Certify compliance with AI safety standards

**What you need to do:**
- Validate ForgeMind's risk assessment with your ML/Security team
- Define exact agent boundaries and permissions (ForgeMind creates a template)
- Run comprehensive tests before production
- Monitor agent behavior post-deployment
- Document failures and iterate

---

## The Project

## Objective
Develop an AI-powered agent that can autonomously generate and deploy backend microservices based on specifications, accelerating development velocity while ensuring code quality and security standards.

## Context
Our engineering team spends 4-6 hours per service on boilerplate setup, API scaffolding, and basic testing. This is repetitive work that could be accelerated by an AI agent. A successful agent could reduce this to 30 minutes of AI work plus 1-2 hours of human review, effectively 10x faster.

## Scope
The agent will:
- Read service specifications in Markdown format
- Generate Python/FastAPI boilerplate code
- Create database models with validation
- Generate unit tests with basic coverage
- Validate output against internal patterns
- Create a GitHub PR for human review

## Out of Scope
- Database schema design (requires human expertise)
- Production deployment (requires security approval)
- Security fixes (require security team review)
- Performance optimization beyond basics
- Documentation generation beyond docstrings

## Constraints
- Agent must work without external LLM API calls (local or company-approved only)
- All agent decisions must be logged and auditable
- Agent cannot modify production code directly
- All outputs must go to PR for human approval first
- Must maintain existing code style and patterns

## Stakeholders
- **Engineering Lead:** Reviews and approves all agent-generated PRs; final decision on merge
- **Security Team:** Reviews outputs for vulnerabilities; approves security patterns
- **Platform Team:** Integrates agent with CI/CD; ensures tool governance
- **Data Engineering:** Defines database model standards

## Current State
Manual service scaffolding takes:
- 2-3 hours for models and routes
- 1-2 hours for test setup
- 1 hour for code review and fixes
- Total: 4-6 hours per service

## Desired State
AI-assisted workflow:
- Agent generates 80% of boilerplate in <30 minutes
- Human review adds 1-2 hours for customization and approval
- Zero security issues from agent output
- Code passes CI/CD on first merge

## Risks
- Agent generates insecure patterns or code
- Agent hallucinates non-existent libraries or APIs
- Agent scope creeps to dangerous operations (deletes, auth changes)
- PR review becomes a bottleneck if agent output is low quality
- Team loses control over generated code

## Success Criteria
- Generated code passes linter without modifications
- Generated tests pass without modifications
- Security team approves outputs with <1 hour review
- First 5 agents ship to production successfully
- Velocity improvement measurable in sprint velocity

## Systems
- GitHub for version control and PR workflow
- Local Claude (or similar) running agent
- Company CI/CD pipeline for testing
- Internal code quality tools (linter, type checker)

## Timeline
- **Week 1:** Define agent boundaries, test harness, safety gates
- **Week 2:** Agent MVP development and iterative testing
- **Week 3:** Production pilot with 2-3 services and monitoring

## Notes
This is a governance-first approach. We are not rushing the agent live. We will establish clear boundaries, comprehensive testing, and human review gates before any agent code touches production.
