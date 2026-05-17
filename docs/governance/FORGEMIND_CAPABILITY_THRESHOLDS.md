# ForgeMind — Capability Thresholds

> Seven actions ForgeMind **NEVER auto-executes** — regardless of CLI
> flags, environment variables, configuration, or what the user types.
>
> Anchor: [D41 Capability Thresholds](../../forgemind/data/doctrines.yaml)
> ([source](https://github.com/fc1sec/CertOS-SAGA/blob/main/doctrines/41-capability-thresholds.md)).
>
> These are not opinions about defaults. They are absolute thresholds.
> Implementing any of them — even behind a flag — requires a
> Constitution amendment (see [FORGEMIND_CONSTITUTION.md](FORGEMIND_CONSTITUTION.md)).

---

## T1 — Compliance certification or legal claim

ForgeMind never declares that a project / system / organisation **is
compliant** with any standard. Outputs may say *"helps you structure
work toward ISO 9001 readiness"*; outputs never say *"this project is
ISO 9001 conformant"*. ForgeMind never issues a certificate, a
conformity declaration, or a regulatory submission.

**Required substitute:** licensed auditor / regulatory affairs
specialist for the actual certification.

## T2 — Decisions on the user's behalf

ForgeMind never selects a variant, accepts a risk, signs off on a
decision, or closes a CAPA on the user's behalf. The consultant
calibration always presents choices; the user picks. The `--auto-accept`
flag advances *defaults* — it does not invent choices the user did not
configure.

**Required substitute:** the human owner of the project.

## T3 — Network or external-API calls

ForgeMind never opens a socket, never reads from a URL, never sends
telemetry, never phones home. The dependency graph excludes any cloud
SDK or HTTP client. This is checked by `forgemind self-audit` against
[`pyproject.toml`](../../pyproject.toml).

**Required substitute:** if data has to leave the user's machine, the
user does it themselves with tools they audited.

## T4 — Speculation in not_covered / out-of-scope domains

ForgeMind never improvises advice in domains marked `not_covered` or
`out_of_scope_by_design` in
[`forgemind/data/disciplines.yaml`](../../forgemind/data/disciplines.yaml).
The consultant refuses with exit code 2 and an escalation contact.

**Required substitute:** the domain-specific human expert listed in
the taxonomy's `escalate_to` field.

## T5 — Modifying user code, data, or infrastructure

ForgeMind never edits files outside the user-specified output
directory. It never deletes files. It never runs shell commands. It
never modifies git history. It writes plain Markdown + JSON into the
directory the user pointed at.

**Required substitute:** the user, in their own editor / shell.

## T6 — Acting as an agent runtime

ForgeMind is pre-execution readiness, not runtime orchestration. It
does not invoke LLMs, does not coordinate sub-agents, does not stream
tool calls, does not maintain conversation state across sessions.

**Required substitute:** Claude Code, Codex, Cursor, GitHub Copilot
agent, or whatever runtime the user chose. ForgeMind hands off; it
does not run.

## T7 — Signing, approving, or representing the user externally

ForgeMind never signs an artefact, never approves a document, never
posts to a channel, never represents the user to a third party. Skill
Card templates and AIIA outputs *prompt for* a human signature; they
never *forge* one.

**Required substitute:** the named human in the project's approval
matrix.

---

## Agent behaviour when a threshold is detected

If a future contribution attempts to cross one of T1–T7:

1. The pull request **must not merge** until the threshold is either
   (a) honoured by the implementation or (b) the Constitution is
   amended through the formal revision process.
2. `forgemind self-audit` should grow a check that detects the
   specific bypass attempt; the check is itself part of the patch.
3. The contributor opens a Constitution amendment PR before the
   feature PR, not after.

## Override policy

The 7 thresholds admit **no operational exceptions**. The only path to
modification is:

1. A pull request that explicitly amends
   [FORGEMIND_CONSTITUTION.md](FORGEMIND_CONSTITUTION.md).
2. A minor or major version bump in [pyproject.toml](../../pyproject.toml).
3. A CHANGELOG entry calling out the threshold change.

## Normative anchors

- Anthropic Responsible Scaling Policy v3.0
- EU AI Act Art. 14 (Human oversight)
- NIST AI RMF 1.0 — GOVERN function
- UNESCO Recommendation on the Ethics of AI (2021) — Human supervision
- ISO/IEC 42001:2023 §5.3 (Roles, responsibilities, authorities)

## Bitácora

- **v1.0 · 2026-05-16** — initial declaration as part of v1.3.0 release.
