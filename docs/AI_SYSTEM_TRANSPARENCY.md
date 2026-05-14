# ForgeMind: System Transparency Statement

**Version**: 1.2.1  
**Last Updated**: May 13, 2026  
**Compliance**: EU AI Act Article 50 (Transparency Obligations)

---

## What ForgeMind Is

ForgeMind is a **structured analysis tool** that:
- Analyzes your project description using pattern matching and templates
- Generates 17 planning documents (not code, not decisions)
- Identifies risks and assumptions you may not have documented
- Prepares context for AI agents or human teams

## Technical Implementation

ForgeMind uses:
- **Pattern Matching**: Keyword detection to identify risks, scope, constraints
- **Template-based Generation**: Fixed templates populated with project data
- **No Machine Learning**: Rules-based system, not statistical model
- **No External APIs**: Runs entirely on your computer (local execution only)
- **No Cloud Storage**: Your project data never leaves your machine
- **No Telemetry**: No data collection (v1.2.1; v1.3+ optional feedback only)

---

## What ForgeMind Is NOT

- ❌ **A decision-maker**. You decide whether to act on ForgeMind's recommendations.
- ❌ **A code generator**. ForgeMind generates documents, not executable code.
- ❌ **A guarantee of success**. Good planning reduces risk but doesn't eliminate it.
- ❌ **A compliance certifier**. ForgeMind documents requirements but doesn't certify compliance.
- ❌ **Domain expert**. ForgeMind structures planning; you provide domain expertise.
- ❌ **A replacement for human review**. All outputs require review by qualified personnel.

---

## Confidence Levels

ForgeMind outputs are labeled with confidence based on source:

| Type | Confidence | Source | Example |
|------|-----------|--------|---------|
| **DETERMINISTIC** | 95%+ | Official standards, project facts | "ISO 9001 requires documented procedure" |
| **STOCHASTIC** | 70% | Knowledge graph outcomes | "70% of teams found this risk critical" |
| **ESCALATE** | <60% | Outside expertise scope | "Tender-specific compliance: consult legal" |

---

## Limitations by Domain

### Supported (Deterministic confidence: 95%+)
- **Software engineering projects** — Requirements, risks, architecture, deployment
- **AI/ML projects** — Safety risks, model versioning, agent handoff
- **ISO 9001 QMS** — Document lifecycle, controls, audit trail
- **Generic organizational projects** — Risk and success criteria planning

### Partial Support (Stochastic confidence: 70%)
- **Operations/process planning** — Can plan, may need domain expert validation
- **ERP configuration planning** — Specific to Odoo; other ERP systems may vary
- **Tender/government contract planning** — Regulatory requirements vary by jurisdiction; escalate for final decisions

### Not Supported (Escalate required)
- **Biomedical/medical devices** — Requires FDA expertise; out of scope
- **Nuclear systems** — Requires NRC expertise; out of scope
- **Defense/classified projects** — Requires security clearance; out of scope

---

## How to Use ForgeMind Safely

1. **Understand ForgeMind's purpose**: Read this statement and [FIRST_TIME_USER_GUIDE.md](FIRST_TIME_USER_GUIDE.md) before your first analysis
2. **Review outputs with domain experts**: All ForgeMind recommendations require validation by someone who understands your domain
3. **Iterate**: Update your project based on ForgeMind's findings, re-run analysis
4. **Document decisions**: DECISION_LOG tracks what you decided and why
5. **Validate compliance**: For regulated work, confirm ForgeMind outputs meet regulatory requirements

---

## Security & Privacy

- **Local-only execution**: All analysis happens on your computer
- **No credentials stored**: ForgeMind never asks for passwords, API keys, or sensitive data
- **No external calls**: ForgeMind cannot send your data anywhere (it has no network access)
- **Open source**: Code is auditable at [github.com/forgemind](https://github.com/forgemind)

---

## Feedback & Reporting

- **Questions**: See [FIRST_TIME_USER_GUIDE.md](FIRST_TIME_USER_GUIDE.md) FAQ section
- **Bugs**: Open issue with project file (redacted), error message, expected behavior
- **Security issues**: Email fc1sec@hotmail.com (48-hour response SLA)

---

## References

- **EU AI Act Article 50**: Transparency Obligations for high-risk AI systems
- **OECD AI Principles**: Transparency, explainability, human agency
- **Research**: Limits of Transparency Policy (arxiv 2601.18127v1)

---

**Philosophy**: Structure work rigorously. Be transparent about limitations. Build trust through honesty.

*ForgeMind v1.2.1 | Delivering version safety and conceptual clarity.*
