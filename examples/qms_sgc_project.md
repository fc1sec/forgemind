# QMS Document Control Stabilization Project

> **Example Type**: Complete ISO 9001 QMS Project  
> **Domain**: `qms_iso`  
> **How to use**: Run `forgemind intake examples/qms_sgc_project.md` to generate analysis  
> **Time to analyze**: ~2 seconds  
> **Generated outputs location**: `forgemind_outputs/qms-document-control-stabilization-project/`

---

## What ForgeMind Will Generate

When you analyze this project, ForgeMind will create 17 documents including:

**Core QMS Documents:**
- `PROJECT_CHARTER.md` — Objective, scope, success criteria aligned to ISO 9001:2015 §8.5.6
- `RISK_REGISTER.md` — Compliance risks, audit findings, control failures
- `ASSUMPTION_LOG.md` — Assumptions about approval authorities, document scope
- `CONTROL_PLAN.md` — How to maintain document control discipline
- `DECISION_LOG.md` — Decisions about document lifecycle states, access controls

**QMS-Specific Documents:**
- Enhanced `context.md` includes reversal plans for document state machines
- `ACCEPTANCE_CRITERIA.md` — Audit-ready success criteria
- `TOOL_PERMISSION_MATRIX.md` — Who can create, review, approve, publish documents

---

## Domain-Specific Notes for QMS/ISO 9001 Projects

For QMS projects, **ForgeMind will:**
- ✅ Map ISO 9001 requirements to your project
- ✅ Identify compliance gaps and risks
- ✅ Create audit-ready documentation
- ✅ Define document control workflows (Draft → Review → Approved → Active → Obsolete)
- ✅ Suggest approval gates and record-keeping procedures

**ForgeMind will NOT:**
- ❌ Certify ISO 9001 compliance (auditor certifies)
- ❌ Design your DMS system
- ❌ Conduct the audit

**What you need to do:**
- Have QMS Lead validate workflows match your organization
- Implement document management system
- Train team on new procedures
- Run internal audit before external audit

---

## The Project

## Objective
Establish a controlled, auditable document management process for ISO 9001:2015 compliance, eliminating version confusion and ensuring all documents are current, approved, and traceable.

## Context
Our team operates under ISO 9001 requirements. Currently, documents live in shared drives with inconsistent versioning. Auditors noted this as a gap. We need to implement document control with version tracking, approval workflows, and clear ownership.

## Scope
- Implement document management system (DMS) for controlled documents
- Define document lifecycle: draft → review → approved → archived
- Establish version control with clear approval signatures
- Create evidence trail for all document changes
- Train team on document control process

## Out of Scope
- Email archiving (separate project)
- Knowledge base or wiki (not controlled documents)
- Compliance certification (we support compliance discipline, not certify)

## Constraints
- Must maintain audit trail for regulatory purposes
- Changes require approval from QMS Lead before publishing
- Rollback capability required for accidental changes
- All changes must be recorded and timestamped

## Stakeholders
- **QMS Lead:** Defines standards and approval process
- **Auditor Representative:** Verifies compliance readiness
- **Process Owners:** Maintain documents for their areas
- **IT:** Implements and manages the DMS

## Current State
Documents scattered across shared drives. Multiple versions exist. Unclear which is current. No approval history.

## Desired State
Single document repository with clear versioning, approval history, and controlled access. All changes auditable.

## Success Criteria
- All controlled documents in DMS
- Version history complete
- Approval history recorded for all documents
- Audit trail shows who changed what and when
- Team completes training

## Timeline
- **Week 1:** DMS setup and configuration
- **Week 2:** Migrate existing documents; establish controls
- **Week 3:** Team training and validation
- **Week 4:** Audit readiness review

## Notes
This is foundational for compliance. Quality and completeness matter more than speed. We must establish discipline here or audits will flag us.
