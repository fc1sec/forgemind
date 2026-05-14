# ForgeMind: Supported Domains

This document describes ForgeMind's capabilities and limitations across different project domains.

---

## Support Matrix

| Domain | Support Level | Coverage | Confidence | Notes |
|--------|---------------|----------|-----------|-------|
| **Software Engineering** | ✅ Full | Requirements, risks, architecture, deployment | 95%+ | Git-based projects, microservices, APIs |
| **AI/ML Projects** | ✅ Full | Safety risks, model versioning, agent handoff | 95%+ | LLMs, ML models, autonomous agents |
| **ISO 9001 QMS** | ✅ Full | Document lifecycle, controls, audit trail | 95%+ | Quality management systems |
| **Operations** | 🟡 Partial | Process mapping, control points | 70% | Can plan, may need domain expert validation |
| **ERP (Odoo)** | 🟡 Partial | Configuration planning, data migration | 70% | Specific to Odoo; other ERP systems may vary |
| **Tenders/Government** | 🟡 Partial | Planning structure, compliance checklist | 60% | Regulatory requirements vary by jurisdiction |
| **Biomedical/Medical Devices** | ❌ Not Supported | — | — | Requires FDA expertise; out of scope |
| **Nuclear Systems** | ❌ Not Supported | — | — | Requires NRC expertise; out of scope |
| **Defense/Classified** | ❌ Not Supported | — | — | Requires security clearance; out of scope |

---

## Full Support (✅ Software, AI/ML, ISO 9001)

**What ForgeMind can do:**
- ✅ Identify risks specific to your domain
- ✅ Generate domain-specific templates and checklists
- ✅ Suggest best-practice validation gates
- ✅ Create domain-aware documentation

**What you still need to do:**
- ✅ Make final decisions (ForgeMind structures, you decide)
- ✅ Validate with domain experts
- ✅ Implement recommendations
- ✅ Monitor outcomes

**Example**: For an AI/ML project, ForgeMind will identify safety risks, hallucination concerns, and model versioning needs. You review these with your ML team and decide which to address.

---

## Partial Support (🟡 Operations, ERP, Tenders)

**What ForgeMind can do:**
- ✅ Structure your planning
- ✅ Identify common risks for this domain
- ✅ Create initial checklists and templates

**What you MUST do:**
- ✅ Validate ForgeMind's output with domain expert
- ✅ Adjust templates for your specific context
- ✅ Ensure regulatory/compliance alignment
- ✅ Make critical domain-specific decisions

**When to escalate to expert:**
- You're uncertain if ForgeMind captured your full domain context
- You're making decisions with regulatory implications
- This is your first time using ForgeMind in this domain
- ForgeMind's output seems generic or misaligned with your needs

**Example**: For a government tender, ForgeMind can structure your planning and create compliance checklists. But you must validate with legal/compliance team because tender requirements vary significantly by jurisdiction and agency.

---

## Not Supported (❌ Biomedical, Nuclear, Defense)

**Why not supported:**
- ❌ Regulatory expertise required (FDA, NRC, DoD)
- ❌ High consequence of errors
- ❌ Specialized knowledge not generalizable
- ❌ Liability and safety concerns

**What to do instead:**
1. Consult domain-specific regulatory specialists
2. Use domain-specific planning tools (e.g., FDA design control software for medical devices)
3. Consider contributing domain expertise via [CONTRIBUTING_REVERSE_PATTERNS.md](CONTRIBUTING_REVERSE_PATTERNS.md) once established

**Note**: We make the deliberate choice NOT to support these domains. Better to be honest about limitations than to speculate and risk harm.

---

## How to Know Which Domain Applies

When you run `forgemind intake`, ForgeMind detects your domain automatically:

```bash
$ forgemind intake my_project.md

[Analyzing project: my_project.md]
[Detected domain: ai_project]

AI/ML PROJECT Analysis
ForgeMind helps you surface safety risks, model versioning strategies, and agent handoff context.
```

The detected domain appears in your output. If ForgeMind gets it wrong:

1. **Review the domain detection**: Check your project description—does it mention AI/ML concepts?
2. **Adjust your project description**: Add more context about what you're building
3. **Re-run analysis**: `forgemind intake my_project.md` (takes ~2 seconds)

If the detected domain seems wrong, you can:
- Specify domain explicitly in your project file (future feature)
- Ask on GitHub [issues](https://github.com/forgemind/issues)

---

## Contributing Domain Expertise

If you have expertise in an unsupported or partial domain, consider contributing a **reverse pattern** to help future users:

- **Supported domain**: Improve existing patterns with edge cases
- **Partial domain**: Submit domain-specific guidelines based on your experience
- **Unsupported domain**: Only contribute if you can back up claims with official standards/references

See [CONTRIBUTING_REVERSE_PATTERNS.md](CONTRIBUTING_REVERSE_PATTERNS.md) for how to contribute.

---

## FAQ

### Q: Can I use ForgeMind for [domain]?

**A**: Check the support matrix above.
- **✅ Full Support**: Yes, use ForgeMind directly
- **🟡 Partial Support**: Yes, but validate with domain expert
- **❌ Not Supported**: No; consult domain specialists instead

### Q: What if ForgeMind detects the wrong domain?

**A**: This can happen if your project description is vague. Add more context:
- What technology/framework are you using?
- What industry are you in?
- What regulatory framework applies?

Then re-run: `forgemind intake your_project.md`

### Q: Can I trust ForgeMind's output for [regulated domain]?

**A**: ForgeMind **structures** planning but doesn't **certify** compliance. For regulated work:
1. Use ForgeMind to structure your thinking
2. Have a qualified person (MD for medical, QA for ISO 9001, etc.) validate outputs
3. Document their approval in your DECISION_LOG
4. ForgeMind output becomes supporting evidence, not the decision itself

### Q: Why isn't ForgeMind more AI-powered?

**A**: ForgeMind is deliberately rule-based, not statistical. This means:
- ✅ No hallucinations (deterministic output)
- ✅ Predictable, auditable behavior
- ✅ Works without internet or API keys
- ❌ Requires more manual domain contribution

We chose certainty over magic.

---

## Support Levels Over Time

As community experts contribute domain patterns, support levels may increase:

- **v1.2.1**: Full support for Software, AI/ML, ISO 9001; Partial for Operations, ERP, Tenders
- **v1.2.2+**: May add patterns based on community feedback
- **v1.3.0+**: Learning system may improve confidence in partial domains
- **Future**: If biomedical expertise is contributed + validated, may move to Partial support

---

**Philosophy**: Be honest about what we know. Be explicit about limitations. Build expertise through community contribution.

*ForgeMind: Structured planning with domain expertise.*
