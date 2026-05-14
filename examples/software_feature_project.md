# Dashboard Feature Project

> **Example Type**: Complete Software Engineering Project  
> **Domain**: `software_project`  
> **How to use**: Run `forgemind intake examples/software_feature_project.md` to generate analysis  
> **Time to analyze**: ~2 seconds  
> **Generated outputs location**: `forgemind_outputs/dashboard-feature-project/`

---

## What ForgeMind Will Generate

When you analyze this project, ForgeMind will create 17 documents including:

**Core Analysis:**
- `PROJECT_CHARTER.md` — Objective, scope, success criteria
- `RISK_REGISTER.md` — Technical risks (performance, concurrency, data staleness)
- `ASSUMPTION_LOG.md` — Assumptions about user load, data freshness, etc.
- `CONTROL_PLAN.md` — How to prevent scope creep and maintain performance SLAs

**Engineering-Specific:**
- `ACCEPTANCE_CRITERIA.md` — Testable success metrics (2s load time, 500 concurrent users, etc.)
- `TOOL_PERMISSION_MATRIX.md` — What systems the dashboard can access
- `AGENT_HANDOFF.md` — Complete handoff for Claude Code or other agents

---

## Domain-Specific Notes for Software Projects

For software features, **ForgeMind will:**
- ✅ Identify architectural and deployment risks
- ✅ Flag integration points and dependencies
- ✅ Define clear acceptance criteria
- ✅ Surface assumptions about performance and scalability

**ForgeMind will NOT:**
- ❌ Design your architecture
- ❌ Guarantee performance targets will be met
- ❌ Write code

---

## The Project

## Objective
Build a real-time analytics dashboard that provides teams with visibility into project metrics, enabling faster decision-making and improved visibility into team performance.

## Context
Leadership and team leads lack real-time visibility into project health. Current reporting is weekly and manual. A dashboard would give instant visibility into sprint progress, blockers, and team capacity, allowing faster intervention when things drift.

## Scope
- Real-time metrics from project management tool
- Key metrics: sprint velocity, cycle time, blockers, team capacity
- Visualizations: burndown, cumulative flow, team load
- Refresh rate: every 15 minutes
- Web-based UI accessible to all engineers

## Out of Scope
- Historical reporting (use existing reports)
- Predictive analytics (future work)
- Mobile app (web-only for v1)
- Custom metric definitions (use standard metrics only)

## Constraints
- Must work with existing data sources (no new systems)
- Dashboard must load in <2 seconds
- Support up to 500 concurrent users
- Accessible on company network only

## Stakeholders
- **Engineering Lead:** Defines success metrics; approves design
- **Frontend Lead:** Reviews UI/UX; manages component library alignment
- **Backend Lead:** Reviews API design; manages data layer
- **DevOps:** Handles deployment and monitoring

## Current State
Teams check status manually via three different tools. Metrics are 1-2 days stale. No unified view of progress.

## Desired State
Single dashboard showing real-time metrics. Teams check dashboard for daily standup. Leadership sees blockers immediately.

## Timeline
- **Week 1:** Design review, API specification
- **Week 2:** Frontend component development
- **Week 3:** Backend integration and testing
- **Week 4:** Deployment and monitoring

## Success Criteria
- Dashboard loads in <2 seconds
- All key metrics display correctly
- 95% uptime in first month
- 80% of team members use it in daily standup
- No data accuracy issues identified

## Notes
This is a high-visibility project. Quality and performance matter. We need strong test coverage and deployment validation.
