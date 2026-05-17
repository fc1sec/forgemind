# ForgeMind Constitution

> The first reference any ForgeMind module — or any user about to act on
> ForgeMind output — must be able to cite. If a behaviour cannot be
> mapped back to this Constitution, it is out of governance and must stop.

**Anchor:** [D39 — Agentic Constitution](../../forgemind/data/doctrines.yaml)
(sourced from [fc1sec/CertOS-SAGA](https://github.com/fc1sec/CertOS-SAGA/blob/main/doctrines/39-constitucion-agentica.md)).

This file is enforced by `forgemind self-audit`. See
[SELF_AUDIT_REPORT.md](SELF_AUDIT_REPORT.md) for the current state.

---

## Mission

**ForgeMind exists to help humans structure work BEFORE an AI agent or
implementation team executes it — and to refuse advice in domains
ForgeMind cannot honestly cover.**

ForgeMind is a *consultant before execution*. It does not run code,
does not contact networks, does not store data outside the user's
machine, and does not make decisions the user has not approved.

## The three-question test (pre-invocation)

Every ForgeMind generator, CLI command, or doctrine check must be able
to answer **yes** to all three questions before producing an output:

1. Does this output **amplify** the user's capacity to plan and decide
   — rather than *replace* their judgement?
2. Does the **human owner** of the project retain final authority over
   what happens with this output?
3. Does the output feed **live, citable evidence** (a doctrine, a
   normative anchor, a taxonomy entry) — rather than fabrication?

If any answer is "no", the generator must escalate (taxonomy refusal,
explicit caveat, or non-emission) rather than ship the output.

## Lexicographic values

When two values conflict, the **lower-numbered** value wins. There is
no horse-trading across this hierarchy.

1. **Honest disclosure of boundaries.**
   ForgeMind never advises in `not_covered` or `out_of_scope_by_design`
   domains. The taxonomy refusal is binding. Confidence labels are
   conservative.

2. **Human authority is preserved.**
   ForgeMind drafts, structures, surfaces risks; the human reviews,
   decides, signs. Outputs are templates and analyses, never
   instructions to execute.

3. **Local-only operation.**
   No network calls. No telemetry. No cloud SDKs. The
   [Token & Cost Governance](../../forgemind/generators/token_governance.py)
   doctrine reports `cost = 0` because the codebase makes it true.

4. **Transparent attribution.**
   Every doctrine cited in an output declares its source repository,
   path, and URL. Every taxonomy variant declares its production
   evidence. Anti-hallucination invariant: if it isn't upstream, it
   isn't shipped.

5. **Efficiency.**
   Only after values 1–4 hold. Speed of analysis is a means, never a
   licence to lower a guard.

## What ForgeMind is

- A pre-execution readiness layer for AI agents and human teams.
- A declarative consultant — its self-knowledge lives in
  [`forgemind/data/disciplines.yaml`](../../forgemind/data/disciplines.yaml)
  and [`forgemind/data/doctrines.yaml`](../../forgemind/data/doctrines.yaml).
- A deterministic Python tool: same input project, same output bundle.

## What ForgeMind is not

- **Not a decision-maker.** Outputs are drafts; humans sign.
- **Not a code generator.** Outputs are Markdown analyses, not runnable code.
- **Not a compliance certifier.** Helps structure planning; users
  validate with qualified experts.
- **Not an agent runtime.** Doesn't watch agents work; doesn't manage
  agent execution.
- **Not networked.** No API calls leave the user's machine.

## Stakeholders

| Stakeholder | Right under this Constitution | How they exercise it |
|---|---|---|
| End user (developer / coordinator / team) | That outputs amplify their work and never replace their judgement | Read, edit, refuse, or discard any output without ForgeMind retaliation. |
| Upstream pattern contributors | That ForgeMind credits them honestly | See [ATTRIBUTIONS.md](../../ATTRIBUTIONS.md) and per-doctrine `source.url` in `doctrines.yaml`. |
| Contributors | That ForgeMind's claims match its tests | Coverage / variant claims are test-gated; CI rejects unbacked claims. |
| Future users in regulated contexts | That ForgeMind refuses to fake compliance | Out-of-scope-by-design list in `disciplines.yaml` is binding and explicit. |

## Cite-back contract

Any generator added under `forgemind/generators/` SHOULD cite at least
one doctrine from `forgemind/data/doctrines.yaml`, and any doctrine
added to that registry MUST declare a source attribution plus at least
one normative anchor. The `forgemind self-audit` command verifies this.

## Veto

Any contributor or user can invoke this Constitution to halt a
ForgeMind behaviour that violates values 1–3. The invocation is the
opening of an issue or pull request that cites this file and the
specific value at stake.

## Revision

This Constitution is **living** but slow. Changes require:

1. A pull request that explains why a value or commitment must change.
2. A bumped `forgemind` minor or major version reflecting the change.
3. An entry in [CHANGELOG.md](../../CHANGELOG.md) calling out the constitutional change explicitly.

---

**Owner:** ForgeMind Contributors · **Version:** v1.0 (2026-05-16) ·
**Next mandatory review:** any v1.x → v2.x bump, or any time
`forgemind self-audit` reports a blocker against D39.
