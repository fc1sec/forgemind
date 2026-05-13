"""Domain classifier using keyword-based detection."""

from forgemind.schemas.project import ProjectInput

# Keywords for each domain
DOMAIN_KEYWORDS = {
    "ai_project": [
        "agent", "llm", "ai", "model", "prompt", "automation",
        "codex", "claude", "copilot", "autonomous", "ml",
        "machine learning", "neural", "embedding", "vector",
    ],
    "software_project": [
        "repo", "api", "frontend", "backend", "database",
        "tests", "feature", "bug", "pr", "github",
        "deployment", "microservice", "framework",
    ],
    "qms_iso": [
        "iso", "qms", "sgc", "capa", "audit",
        "document control", "nonconformity", "risk",
        "quality", "process", "compliance", "governance",
    ],
    "operations": [
        "process", "workflow", "logistics", "inventory",
        "supplier", "customer", "delivery",
        "operational", "supply chain", "handoff",
    ],
    "odoo_erp": [
        "odoo", "erp", "xml-rpc", "inventory", "purchase",
        "sales", "product", "lot", "serial", "traceability",
        "edi", "picking",
    ],
    "tenders": [
        "tender", "bid", "procurement", "compliance matrix",
        "technical requirement", "licitación", "partida",
        "propuesta", "junta de aclaraciones", "rfi", "rfq",
    ],
}


def classify_domain(project_input: ProjectInput) -> tuple[str, bool]:
    """Classify project domain based on keywords.

    Returns: (domain_name, is_detected)
    is_detected=True means auto-detected, False means fallback to generic.
    """
    # Combine all text for keyword matching
    text_to_search = " ".join([
        project_input.objective,
        project_input.context,
        project_input.scope,
        project_input.constraints,
        project_input.risks or "",
        project_input.systems or "",
        project_input.notes or "",
    ]).lower()

    # Score each domain
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_to_search)
        scores[domain] = score

    # Find best match
    best_domain = max(scores, key=scores.get)
    best_score = scores[best_domain]

    # If no keywords found, return generic
    if best_score == 0:
        return "generic", False

    return best_domain, True
