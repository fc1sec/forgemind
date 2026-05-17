# ForgeMind — Skill Card

> Machine-readable manual for ForgeMind-the-tool. Re-consult on every
> upgrade or before relying on ForgeMind output in a new domain.
>
> Anchor: [D43 Skill Card mandatory](../../forgemind/data/doctrines.yaml)
> ([source](https://github.com/fc1sec/CertOS-SAGA/blob/main/doctrines/43-skill-card-obligatoria.md)).

---

## 1 · Identification

- **Slug:** `forgemind`
- **Full name:** ForgeMind — universal multidisciplinary consultant
- **Skill version (semver):** v1.3.0
- **AIIA reference + hash:** see [FORGEMIND_AIIA.md](FORGEMIND_AIIA.md); hash via `git log` on the introducing commit.
- **Release date:** 2026-05-16
- **Status:** ☑ PRODUCTION (v1.3.0 stable, backward-compatible with v1.2.x and v1.1.0)

## 2 · Declared purpose (constitutional)

- **Operational problem solved:** Translate raw project notes
  (Markdown) into 17–22 structured planning artefacts that surface
  risks, assumptions, acceptance criteria, control plans, and
  agent-handoff context, with explicit boundary disclosures.
- **How it AMPLIFIES human capacity (D39 reverse-citation):** A senior
  reviewer would author these artefacts manually in hours; ForgeMind
  drafts them in seconds, leaving the human review time intact.
- **Project principle materialised:** D26 SAGA — *"Connect before
  duplicate"* (read user's own project file) and *"Improve without
  breaking"* (zero side-effects).

## 3 · Owners

- **Functional owner (role):** ForgeMind Contributors (open-source maintainers)
- **Technical owner (implementer):** ForgeMind Contributors
- **Escalation:** GitHub Issues at https://github.com/fc1sec/forgemind/issues

## 4 · Underlying model

- **Model name and version:** **NONE.** ForgeMind is deterministic
  Python (no LLM call, no neural model).
- **Choice rationale:** local-only operation; reproducible output;
  zero token cost; constitutional value 3 (local-only) is enforced by
  the dependency graph.
- **Provider safety level at release:** N/A (no model provider).
- **Configuration:** none required. CLI flags listed in `forgemind --help`.
- **Active MCPs:** none — ForgeMind does not consume MCP servers.

## 5 · Declared capabilities

Every capability is a single CLI command; full list at `forgemind --help`.

1. `forgemind capabilities [--discipline X]` → input: optional discipline; output: coverage table.
2. `forgemind explain-limits <domain>` → input: domain id; output: variants + boundary conditions.
3. `forgemind compare-variants <domain>` → input: domain id; output: side-by-side decision card.
4. `forgemind consult <project.md>` → input: project Markdown; output: 17–22 readiness artefacts + calibration log.
5. `forgemind intake <project.md>` → input: project Markdown; output: 17–22 readiness artefacts (no dialog).
6. `forgemind diagnose <project.md>` → input: project Markdown; output: maturity assessment.
7. `forgemind gate <project.md>` → input: project Markdown; output: gate pass / fail summary.
8. `forgemind handoff <project.md>` → input: project Markdown; output: agent handoff file.
9. `forgemind export <project.md>` → input: project Markdown; output: JSON export.
10. `forgemind followup <output_dir>` → input: prior output dir; output: drill-down on one decision.
11. `forgemind history [--limit N] [--clear]` → input: optional limits; output: prior calibration log.
12. `forgemind doctrines [<id|short_id>] [--category]` → input: optional doctrine id; output: registry listing or single doctrine.
13. `forgemind self-audit [--write-report]` → input: none; output: this Skill Card's contract verified against the codebase.

## 6 · Explicit limits

- **Tasks ForgeMind does NOT execute:** see
  [FORGEMIND_CAPABILITY_THRESHOLDS.md](FORGEMIND_CAPABILITY_THRESHOLDS.md)
  for the 7 thresholds (compliance certification, decisions on behalf
  of user, network calls, speculation in not_covered domains,
  modifying user code, agent runtime, signing on behalf of user).
- **Input types rejected:** non-Markdown project files; project files
  that map to `out_of_scope_by_design` domains (refused with exit code 2).
- **Minimum confidence below which ForgeMind escalates HITL:** any
  domain marked `not_covered` (confidence = 0.0) escalates
  immediately. Domains marked `partial` carry a confidence score
  (0.45–0.85 in v1.3.0); outputs are always STOCHASTIC and require
  expert review.

## 7 · Data accessed

- **File sources:** only the project Markdown the user explicitly passes on the CLI.
- **System sources:** none.
- **External sources:** none. No HTTP, no MCP, no socket.
- **PII potentially accessed:** whatever the user wrote in their
  project Markdown — ForgeMind has no PII-detection layer. The user
  is responsible for not feeding ForgeMind anything they would not
  want sitting on their own disk in `forgemind_outputs/`.
- **Retention perimeter:** ForgeMind writes to the user-specified
  output directory plus, optionally, `~/.forgemind/history.jsonl` for
  calibration history (clearable with `forgemind history --clear`).
  No other persistence.

## 8 · Accuracy metrics

- **Expected baseline confidence:** per-domain in `disciplines.yaml`
  (0.45 ≤ partial-domain confidence ≤ 0.85; `covered` future-reserved at ≥ 0.85).
- **Known hallucination rates:** N/A — deterministic. The risk is
  *wrong template chosen* (taxonomy miscalibration), not free-text
  fabrication.
- **Red-team coverage (last date, result, open defects):** 2026-05-16
  · `forgemind self-audit` passes GREEN · open defects listed in
  [SELF_AUDIT_REPORT.md](SELF_AUDIT_REPORT.md).
- **Observed human-rework rate:** not yet measured in the wild; the
  test suite + self-audit are the only feedback loop today.

## 9 · Safe-use assumptions

- **Expected input state:** project Markdown that includes an
  Objective, Context, Scope, and at least one Constraint.
- **Operating conditions:** Python 3.9+; no network needed; runs offline.
- **Cases where ForgeMind silently degrades and the output must not
  be trusted:**
  - Project file domain is `not_covered` and the user passed
    `--auto-accept` (rare but possible): the consultant refuses, but
    `intake` may have already produced a generic-template bundle —
    treat it as a starting outline only.
  - Project file is essentially empty: outputs will be stub-rich and
    risk lists will be sparse.
  - User uses ForgeMind output as evidence of compliance: it is not.

## 10 · Fallback plan

- **If a generator raises:** the test suite (275 tests) is the
  regression gate. Open a GitHub issue with the failing project file.
- **If `self-audit` reports a blocker:** do not cut a release. Fix
  the blocker, re-run, then release.
- **Reactivation approval:** any contributor with merge rights, after
  the self-audit returns GREEN.

## 11 · Version history

| Version | Date | Material changes | AIIA updated? | Approver |
|---|---|---|---|---|
| v1.0.0 | 2025-Q? | Initial 17-document intake pipeline | n/a (pre-AIIA) | ForgeMind Contributors |
| v1.1.0 | 2025-Q? | v1.1 generators (context, AI checklist, tool matrix, PR/issue templates) | n/a | ForgeMind Contributors |
| v1.2.0 | 2026-05-13 | Reverse patterns plugin architecture; ISO 9001 / software / ai_ml plugins | n/a | ForgeMind Contributors |
| v1.2.1 | 2026-05-14 | Update safety + compatibility matrix | n/a | ForgeMind Contributors |
| v1.3.0 | 2026-05-16 | Doctrines registry; Annex SL multi-norm taxonomy upgrade; 5 new generators; self-audit module; this Skill Card | yes ([FORGEMIND_AIIA.md](FORGEMIND_AIIA.md)) | ForgeMind Contributors |

## 12 · Integrity hash & signature

- **SHA-256 of this CARD at approval time:** computed at commit time
  via `git hash-object docs/governance/FORGEMIND_SKILL_CARD.md`.
- **Signature:** the commit that introduces this file in git history;
  contributors sign through their git config.
- **Signature block (auditor-readable):**

  ```
  -----BEGIN SKILL CARD SIGNATURE-----
  signer: ForgeMind Contributors (via git commit author)
  algorithm: git sha-256 (object hash) + optional GPG (if user configured)
  timestamp: 2026-05-16
  hash_sha256: <computed at commit time>
  signature: <git commit hash>
  -----END SKILL CARD SIGNATURE-----
  ```

---

## Runtime presentation

This Skill Card is summarised by `forgemind self-audit` whenever the
audit reports against D43. New users are pointed to it from the README
and from `forgemind doctrines D43`.

Without this CARD published and `self-audit`-verified, no future
release of ForgeMind is allowed to ship.

## Normative anchors

- EU AI Act Art. 13 (Transparency & provision of information to deployers)
- OECD AI Principles (revised 2024) — Transparency & explainability
- NIST AI RMF — MAP + MEASURE functions
- ISO/IEC 42001:2023 §7.5 (Documented information for AIMS)
- ISO 9001:2015 cl. 7.5 (Controlled documented information)
