"""JSON export for project analysis."""

import json
from pathlib import Path

from forgemind.schemas.project import ProjectAnalysis


def export_json(analysis: ProjectAnalysis, output_dir: Path) -> Path:
    """Export analysis to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create exportable dict
    export_data = {
        "metadata": analysis.metadata.model_dump(),
        "input": analysis.input.model_dump(),
        "rdmaicsi": analysis.rdmaicsi_phases,
        "senge": analysis.senge_disciplines,
        "lean": analysis.lean_findings,
        "six_sigma": analysis.six_sigma_tools,
        "risks": analysis.risks,
        "assumptions": analysis.assumptions,
        "acceptance_criteria": analysis.acceptance_criteria,
        "backlog": analysis.backlog,
        "control_plan": analysis.control_plan,
        "decision_log": analysis.decision_log,
        "maturity_estimate": analysis.maturity_estimate,
        "summary": {
            "project_name": analysis.metadata.name,
            "domain": analysis.metadata.domain,
            "domain_detected": analysis.metadata.detected_domain,
            "maturity": analysis.maturity_estimate,
            "risk_count": len(analysis.risks),
            "assumption_count": len(analysis.assumptions),
            "acceptance_criteria_count": len(analysis.acceptance_criteria),
            "backlog_item_count": len(analysis.backlog),
            "control_item_count": len(analysis.control_plan),
            "decision_count": len(analysis.decision_log),
        }
    }

    output_file = output_dir / f"{analysis.metadata.slug}_analysis.json"
    output_file.write_text(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return output_file
