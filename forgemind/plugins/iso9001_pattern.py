"""
ISO 9001:2015 Reverse State Pattern.

Reference implementation for QMS (Quality Management System) document reversals,
based on ISO 9001:2015 §8.5.6 (Control of changes) and §7.5 (Documented information).

This plugin is grounded in a production-validated reference implementation:

    iso-gestion (Sistema de Gestión ISO 9001/2015)
    https://github.com/Desarrollo-CeSPI/iso-gestion
    Author: CeSPI UNLP (Centro Superior para el Procesamiento de la Información,
            Universidad Nacional de La Plata, Argentina)
    License: MIT
    In production since 2014, supporting two ISO 9001:2015 certified scopes,
    30+ active users and ~3000 managed records.

The 8-state machine below mirrors the workflow used by CeSPI's production QMS
(translated from Spanish), extended with explicit reversibility, audit-trail
requirements and approval gates aligned to ISO 9001:2015 normative clauses.

ForgeMind does NOT redistribute iso-gestion code. It codifies the *patterns*
the iso-gestion authors validated through real audits and certifications.

CLASSIFICATION: STOCHASTIC (Empirical) — based on one production-validated
QMS implementation. Confidence ~0.85. Verify against your organization's
own QMS procedures before relying on these reversals.
"""

from typing import Any, Optional

from forgemind.schemas.project import ProjectAnalysis

from .reverse_state_pattern import (
    ReversalPlan,
    ReverseStateDefinition,
    ReverseStatePattern,
    ReverseStep,
)


class ISO9001ReversePattern(ReverseStatePattern):
    """ISO 9001:2015 QMS document reversal patterns.

    State machine (8 states, ordered):

      Draft  → Created → Under Review → Reviewed
             → Under Approval → Approved → In Force → Obsolete
                                              ↘ Signed (terminal-legal)

    State semantics (mapped from iso-gestion):
      Draft           — "En proceso de edición": author drafting
      Created         — "Creado": draft complete, locked, awaiting reviewer
      Under Review    — "En proceso de revisión": active review in progress
      Reviewed        — "Revisado": review complete, awaiting approval routing
      Under Approval  — "En proceso de aprobación": in approval workflow
      Approved        — "Aprobado": approved but not yet in production use
      In Force        — "Vigente": approved AND active/in-effect (current revision)
      Obsolete        — "Obsoleto": superseded by a newer revision (archived)
      Signed          — Legally executed document (terminal, irreversible)

    Reversibility rules:
      - Draft is the origin; not reversible (no prior state)
      - Created, Under Review, Reviewed, Under Approval, Approved: reversible
        upward (back one step) with audit trail
      - In Force is reversible to Approved only via formal change request
      - Signed and Obsolete are terminal: cannot be reversed; issue a new
        revision instead
    """

    domain = "iso9001"
    framework = "ISO 9001:2015 §8.5.6 (Control of changes), §7.5 (Documented information)"
    description = (
        "Document lifecycle reversals with audit trail for quality management systems. "
        "8-state machine validated against CeSPI UNLP's production iso-gestion QMS "
        "(MIT, github.com/Desarrollo-CeSPI/iso-gestion), in operation since 2014 with "
        "two certified ISO 9001:2015 scopes."
    )

    # State machine definition (8 states, derived from iso-gestion production
    # workflow). Each state declares which prior state(s) it can revert to,
    # whether the reversal is permitted, the role authorized to approve it,
    # and the audit-trail template required by ISO §8.5.2 (traceability).
    STATE_MACHINE = {
        "Draft": {
            "spanish_label": "En proceso de edición",
            "can_revert_to": [],
            "reversible": True,
            "data_loss": "none",
            "reason": "Initial state, no prior state to revert to",
            "audit_entry": None,
        },
        "Created": {
            "spanish_label": "Creado",
            "can_revert_to": ["Draft"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Author may unlock and continue editing",
            "approval_role": "document_author",
            "audit_entry": "Reverted Created → Draft by {actor} on {timestamp}\nReason: {reason}",
        },
        "Under Review": {
            "spanish_label": "En proceso de revisión",
            "can_revert_to": ["Created", "Draft"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Reviewer may return document to author for corrections",
            "approval_role": "document_author",
            "audit_entry": "Returned to Draft by {actor} on {timestamp}\nReason: {reason}",
        },
        "Reviewed": {
            "spanish_label": "Revisado",
            "can_revert_to": ["Under Review"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Reviewer may reopen review if new findings emerge before approval routing",
            "approval_role": "reviewer",
            "audit_entry": "Reopened review (Reviewed → Under Review) by {actor} on {timestamp}\nReason: {reason}",
        },
        "Under Approval": {
            "spanish_label": "En proceso de aprobación",
            "can_revert_to": ["Reviewed", "Under Review"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Approver may return to review if compliance issues are detected during approval",
            "approval_role": "quality_manager",
            "audit_entry": "Returned from approval to review by {actor} on {timestamp}\nReason: {reason}",
        },
        "Approved": {
            "spanish_label": "Aprobado",
            "can_revert_to": ["Under Approval", "Under Review"],
            "reversible": True,
            "data_loss": "none",
            "reason": "Approved but not yet in force — may be returned for revision if errors found",
            "approval_role": "quality_manager",
            "audit_entry": "Reverted from Approved to {target} by {actor} on {timestamp}\nReason: {reason}",
            "mitigation": "Triggers re-review cycle and stakeholder notification",
        },
        "In Force": {
            "spanish_label": "Vigente",
            "can_revert_to": ["Approved"],
            "reversible": True,
            "data_loss": "low",
            "reason": (
                "In-force documents may be returned to 'Approved' only via a formal "
                "change request per §8.5.6; affected stakeholders must be notified."
            ),
            "approval_role": "quality_manager",
            "audit_entry": "In-force document withdrawn (In Force → Approved) by {actor} on {timestamp}\nChange request: {change_id}\nReason: {reason}",
            "mitigation": "Notify all distribution-list recipients; mark old copies as 'pending revision'",
        },
        "Signed": {
            "spanish_label": "Firmado",
            "can_revert_to": [],
            "reversible": False,
            "data_loss": "none",
            "reason": (
                "Signed documents are historical records per §7.5.3.2 and cannot be "
                "unsigned. Legal-equivalent of a notarized record."
            ),
            "mitigation": "Issue a new approved revision; mark old version Obsolete with change notice",
            "audit_entry": "Signed document cannot be reverted",
        },
        "Obsolete": {
            "spanish_label": "Obsoleto",
            "can_revert_to": [],
            "reversible": False,
            "data_loss": "none",
            "reason": "Obsolete documents are archived per §7.5.3.2 — they remain readable but are not active",
            "mitigation": "Re-issue with new revision number instead of reactivating an obsolete document",
            "audit_entry": None,
        },
    }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_supported_states(self) -> list[ReverseStateDefinition]:
        """Return all states in the ISO 9001 document lifecycle."""
        definitions = []
        for state_name, config in self.STATE_MACHINE.items():
            definitions.append(
                ReverseStateDefinition(
                    state_name=state_name,
                    can_revert_to=config["can_revert_to"],
                    reversible=config["reversible"],
                    reason=config.get("reason"),
                    mitigation=config.get("mitigation"),
                    data_loss=config.get("data_loss", "none"),
                    audit_entry_template=config.get("audit_entry"),
                )
            )
        return definitions

    def validate_state_transition(self, from_state: str, to_state: str) -> dict[str, Any]:
        """Check if a state transition is valid per ISO 9001."""
        if from_state not in self.STATE_MACHINE:
            return {"is_valid": False, "reason": f"Unknown source state: {from_state}"}

        if to_state not in self.STATE_MACHINE:
            return {"is_valid": False, "reason": f"Unknown target state: {to_state}"}

        config = self.STATE_MACHINE[from_state]

        if not config["reversible"]:
            return {
                "is_valid": False,
                "reason": config.get("reason", "Reversal not permitted"),
                "mitigation": config.get("mitigation"),
            }

        if to_state not in config["can_revert_to"]:
            return {
                "is_valid": False,
                "reason": f"Cannot revert {from_state} to {to_state}",
                "constraint": config.get("reason", "No reversions defined"),
                "allowed_targets": config["can_revert_to"],
            }

        return {
            "is_valid": True,
            "requires_approval": bool(config.get("approval_role")),
            "approval_role": config.get("approval_role"),
            "data_loss": config.get("data_loss", "none"),
        }

    def generate_reversal_plan(
        self,
        project: ProjectAnalysis,
        current_state: str,
        target_state: Optional[str] = None,
    ) -> ReversalPlan:
        """Generate a concrete reversal plan for this ISO project."""

        # Validate current state
        if current_state not in self.STATE_MACHINE:
            raise ValueError(f"Unknown state: {current_state}")

        # Determine target (defaults to first allowed prior state)
        if target_state is None:
            possible_targets = self.STATE_MACHINE[current_state]["can_revert_to"]
            if not possible_targets:
                raise ValueError(
                    f"Cannot revert from {current_state}: "
                    f"{self.STATE_MACHINE[current_state]['reason']}"
                )
            target_state = possible_targets[0]

        # Validate transition
        validation = self.validate_state_transition(current_state, target_state)
        if not validation["is_valid"]:
            raise ValueError(validation["reason"])

        # Dispatch to the appropriate step generator
        steps = self._steps_for_transition(current_state, target_state, project)

        # Calculate totals
        total_time = sum(s.estimated_time_minutes or 0 for s in steps)
        risks = [s.data_loss_risk for s in steps if s.data_loss_risk != "none"]
        highest_risk = max(risks) if risks else "none"

        approval_gates = [s.approval_role for s in steps if s.approval_required]

        return ReversalPlan(
            current_state=current_state,
            target_state=target_state,
            rollback_path=self._build_rollback_path(current_state, target_state),
            steps=steps,
            total_estimated_time_minutes=total_time,
            highest_data_loss_risk=highest_risk,
            approval_gates=list(set(approval_gates)) if approval_gates else [],
            dependencies=self._get_dependencies(current_state),
            constraints=self._get_constraints(current_state),
            confidence=0.85,  # Empirical (iso-gestion production validation)
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _steps_for_transition(
        self,
        current_state: str,
        target_state: str,
        project: ProjectAnalysis,
    ) -> list[ReverseStep]:
        """Dispatch to the right step generator based on the state pair."""
        if current_state == "Created" and target_state == "Draft":
            return self._steps_created_to_draft(project)
        if current_state == "Under Review" and target_state in ("Draft", "Created"):
            return self._steps_under_review_to_draft(project)
        if current_state == "Reviewed" and target_state == "Under Review":
            return self._steps_reviewed_to_under_review(project)
        if current_state == "Under Approval":
            return self._steps_under_approval_to_review(project, target_state)
        if current_state == "Approved":
            return self._steps_approved_to_under_review(project)
        if current_state == "In Force" and target_state == "Approved":
            return self._steps_in_force_to_approved(project)
        if current_state == "Signed":
            return self._steps_signed_to_approved(project)
        return []

    def _steps_created_to_draft(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Revert from 'Created' (locked draft) back to 'Draft' (editable)."""
        return [
            ReverseStep(
                step_number=1,
                action="Author unlocks document and reverts status to Draft",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Log unlock in audit trail per §8.5.2 with author and reason",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_under_review_to_draft(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Revert from 'Under Review' back to 'Draft' (sent back to author)."""
        return [
            ReverseStep(
                step_number=1,
                action="Reviewer identifies reason for sending document back to author",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=2,
                action="Update document status: Set to Draft, clear review dates and reviewer",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Notify author with specific corrections needed",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=4,
                action="Author makes required edits",
                approval_required=False,
                estimated_time_minutes=20,
                notes="Time varies by change scope",
            ),
            ReverseStep(
                step_number=5,
                action="Log reversal in audit trail per §8.5.2 (actor, reason, timestamp)",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_reviewed_to_under_review(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Revert from 'Reviewed' back to 'Under Review' (reopen review)."""
        return [
            ReverseStep(
                step_number=1,
                action="Reviewer documents new finding that requires reopening the review",
                approval_required=True,
                approval_role="reviewer",
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=2,
                action="Update document status from Reviewed to Under Review",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Log reopening in audit trail per §8.5.2",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_under_approval_to_review(
        self, project: ProjectAnalysis, target_state: str
    ) -> list[ReverseStep]:
        """Revert from 'Under Approval' back to review states."""
        return [
            ReverseStep(
                step_number=1,
                action="Approver documents compliance issue or correction needed",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=15,
                notes="Per §8.5.6 — changes require documented justification",
            ),
            ReverseStep(
                step_number=2,
                action=f"Return document from Under Approval to {target_state}",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=3,
                action="Notify reviewer and author of return-from-approval and the reason",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=4,
                action="Log return in audit trail per §8.5.2 with full context",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_approved_to_under_review(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Revert from 'Approved' back to 'Under Review' or 'Under Approval'."""
        return [
            ReverseStep(
                step_number=1,
                action="Quality manager approves reversal (compliance issue or error found)",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=15,
                notes="Use formal change request process per §8.5.6",
            ),
            ReverseStep(
                step_number=2,
                action="Notify document author and stakeholders of reversal",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=3,
                action="Update document status to 'Under Review' or 'Under Approval'",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=4,
                action="Make required changes (compliance fixes, corrections, etc.)",
                approval_required=False,
                estimated_time_minutes=30,
                notes="Time varies by change scope",
            ),
            ReverseStep(
                step_number=5,
                action="Re-route through full approval workflow (review → approve)",
                approval_required=False,
                estimated_time_minutes=10,
            ),
            ReverseStep(
                step_number=6,
                action="Log reversal in audit trail per §8.5.2 with reason",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_in_force_to_approved(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Revert from 'In Force' (Vigente) back to 'Approved' — withdraw from production."""
        return [
            ReverseStep(
                step_number=1,
                action="File formal change request per §8.5.6 documenting why the in-force document must be withdrawn",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=30,
                data_loss_risk="low",
                notes="Active in-force documents withdrawal must be auditable",
            ),
            ReverseStep(
                step_number=2,
                action="Notify ALL recipients on the distribution list that the document is being withdrawn",
                approval_required=False,
                estimated_time_minutes=20,
                notes="Required by §7.5.3 (controlled distribution)",
            ),
            ReverseStep(
                step_number=3,
                action="Mark physical/digital copies in circulation as 'pending revision'",
                approval_required=False,
                estimated_time_minutes=15,
            ),
            ReverseStep(
                step_number=4,
                action="Change status from In Force to Approved (no longer the active revision)",
                approval_required=False,
                estimated_time_minutes=5,
            ),
            ReverseStep(
                step_number=5,
                action="Log withdrawal in audit trail with change request ID per §8.5.2",
                approval_required=False,
                estimated_time_minutes=5,
            ),
        ]

    def _steps_signed_to_approved(self, project: ProjectAnalysis) -> list[ReverseStep]:
        """Handle 'Signed' reversal (NOT PERMITTED — included for guidance only)."""
        return [
            ReverseStep(
                step_number=1,
                action="CONSTRAINT: Signed documents cannot be reverted per §7.5.3.2",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=30,
                data_loss_risk="high",
                notes="Signed documents are historical/legal records",
            ),
            ReverseStep(
                step_number=2,
                action="Alternative: Issue a new revision with corrections + obsolete the old version",
                approval_required=True,
                approval_role="quality_manager",
                estimated_time_minutes=45,
                notes="Create a change notice documenting why the new version is issued",
            ),
        ]

    def _build_rollback_path(self, from_state: str, to_state: str) -> str:
        """Build a readable path description for the reversal."""
        return f"{from_state} → {to_state}"

    def _get_dependencies(self, current_state: str) -> list[str]:
        """Get dependencies for reversal from this state."""
        deps = {
            "Approved": [
                "Stakeholder notification (documented distribution list)",
                "Approval record (who approved initial version)",
            ],
            "In Force": [
                "Active distribution list per §7.5.3",
                "Change request system",
                "Recipient acknowledgement mechanism",
            ],
            "Signed": [
                "Quality manager approval",
                "Change control board review",
                "Document numbering system for new revision",
            ],
        }
        return deps.get(current_state, [])

    def _get_constraints(self, current_state: str) -> list[str]:
        """Get regulatory/policy constraints for this reversal."""
        constraints = [
            "All reversals must be documented in the audit trail per §8.5.2",
            "Change reason must be recorded",
        ]

        if current_state == "In Force":
            constraints.append(
                "Withdrawing an in-force document requires a formal change request per §8.5.6"
            )
            constraints.append(
                "All distribution-list recipients must be notified per §7.5.3"
            )

        if current_state == "Signed":
            constraints.append("Signed documents cannot be modified — only obsoleted")
            constraints.append("A new revision must be issued if changes are needed")

        return constraints
