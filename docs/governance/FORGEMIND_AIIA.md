# ForgeMind — AI Impact Assessment (AIIA)

> Pre-deployment gate for ForgeMind-the-tool itself.
> Anchor: [D40 AIIA pre-deployment](../../forgemind/data/doctrines.yaml)
> ([source](https://github.com/fc1sec/CertOS-SAGA/blob/main/doctrines/40-aiia-previo-despliegue-skill.md)).
>
> ForgeMind is **not an LLM** — it is deterministic Python. Many GenAI
> risks therefore do not apply directly. This AIIA addresses the
> *meta-AI risk* that ForgeMind shapes how humans deploy other AI
> systems: bad advice from ForgeMind could degrade governance of
> downstream agents.

---

## 1 · AI system identification

- **System name:** ForgeMind
- **Version / model:** v1.3.0 — deterministic Python, **no LLM**, no model API
- **Functional owner (role):** ForgeMind Contributors (open-source maintainers)
- **Technical owner (implementer):** ForgeMind Contributors
- **Proposed deployment date:** 2026-05-16 (initial v1.3.0)

## 2 · Declared purpose

- **Operational problem solved:** AI agents and human teams ship work
  against vague requirements, unvalidated assumptions, and unclear
  success criteria. ForgeMind structures the work *before* execution
  starts so the human reviewing the agent's PR has a documented basis
  for accept / reject / refine.
- **How this AMPLIFIES human capacity (D39 reverse-citation):**
  ForgeMind drafts the 17–22 readiness artefacts that a senior
  reviewer would otherwise have to author or improvise from memory.
- **Which SAGA / project principle it materialises:** D26 SAGA principle
  *"Connect before duplicate"* (reuse the user's own project notes) and
  *"Improve without breaking"* (no execution side-effects, no network).

## 3 · Affected stakeholders

| Stakeholder | Expected impact | Residual risk |
|---|---|---|
| End user (developer / coordinator) | Direct — receives the 17–22 output bundle | False sense of compliance if user skips human-review gates |
| Downstream AI agent | Indirect — consumes `*.context.md` / `AGENT_HANDOFF.md` | Agent acts on stale or incorrect context if the project file drifts |
| User's organisation | Indirect — receives planning artefacts ostensibly aligned with ISO 9001 / 13485 / 27001 / 42001 / etc. | Audit risk if outputs are treated as evidence of certification — they are NOT |
| Upstream pattern contributors (CeSPI UNLP, CertOS-SAGA, Fowler bliki, Google SRE Workbook, etc.) | Their patterns are cited and re-used | Mis-attribution; outdated source URL |
| Anthropic / model providers | None directly (ForgeMind never calls them) | None |

## 4 · Risk map (NIST AI 600-1 GenAI Profile)

ForgeMind is deterministic and offline. Most GenAI risks do not apply
directly to ForgeMind itself; they apply to the *downstream agent* that
will consume ForgeMind output. We map both layers.

| GenAI risk | Applies to ForgeMind itself? | Applies to downstream agent? | ForgeMind mitigation |
|---|---|---|---|
| Confabulation | No (deterministic) | Yes | Doctrines/taxonomy refusal contract; explicit boundary conditions |
| Data Privacy | No (no data leaves the machine) | Yes | Tool Permission Matrix forbids external API calls by default |
| Harmful Bias | Low (templates are domain-tested) | Yes | Multiple variants per domain; user picks via consultant calibration |
| Information Integrity | Indirect (bad advice) | Yes | EVIDENCE_SCORING.md + every doctrine cites normative anchors |
| Information Security | No (local) | Yes | Local-only operation; no telemetry |
| Intellectual Property | Possible (re-use of upstream patterns) | N/A | ATTRIBUTIONS.md; per-doctrine source URLs; no verbatim copies |
| Value Chain Integration | Yes (depends on upstream corpus, fc1sec/CertOS-SAGA) | Yes | Pin upstream URLs; CHANGELOG records adoptions |
| Environmental Impact | Negligible (local CPU only) | Variable | Token & Cost Governance reports cost = 0 |
| Human-AI Configuration | Yes — shapes how humans configure agents | Yes | Capability Thresholds doctrine + Tool Permission Matrix per domain |
| Dangerous content | No | Variable | Out-of-scope-by-design list refuses defense / nuclear / classified work |
| Obscene / Degrading | No | No | N/A |
| CBRN | No | No | Out-of-scope-by-design refuses nuclear / weapons advice |

## 5 · EU AI Act categorisation (voluntary reference)

- **High-risk per Annex III?** No. ForgeMind does not perform any of
  the regulated functions in Annex III directly. It generates planning
  documents, not decisions.
- **General-purpose AI (GPAI)?** No. ForgeMind contains no general-purpose
  AI model.
- **Voluntary alignment:** ForgeMind voluntarily implements the
  *spirit* of Arts. 13 (transparency to deployers), 14 (human
  oversight), and 17 (quality management) by publishing this
  governance/ folder.

## 6 · Binding controls

- **HITL controls** — see [FORGEMIND_CAPABILITY_THRESHOLDS.md](FORGEMIND_CAPABILITY_THRESHOLDS.md).
- **Reversal plan** — every output bundle is plain Markdown in a
  user-chosen directory. Reversal is `rm -rf <out_dir>`; cost = 0;
  approval = the user alone.
- **Logging** — ForgeMind logs nothing. The user's shell history and
  git working tree are the only audit surface.
- **Skill Card published** — see [FORGEMIND_SKILL_CARD.md](FORGEMIND_SKILL_CARD.md).
- **First red-team exercise** — the `forgemind self-audit` command
  *is* the standing red-team for the doctrine layer. Wider adversarial
  testing of generators is a future contribution.

## 7 · Pilot plan

- **Pilot population:** open-source contributors and early adopters
  via `pip install forgemind`.
- **Success metric:** `forgemind self-audit` returns GREEN; >80% test
  coverage; no contributor-filed issues alleging fabricated coverage
  claims.
- **Abort criteria (kill switch):** if `self-audit` reports blockers
  on D39, D40, D41, or D43 in a tagged release, the release is yanked
  and a patch version is cut.
- **Promotion-to-production criteria:** GREEN self-audit + full test
  suite + CHANGELOG entry documenting any constitutional changes.

## 8 · Approvals

| Role | Signature | Date | Hash of signed artefact |
|---|---|---|---|
| Project lead | ForgeMind Contributors | 2026-05-16 | (computed by `git log` on commit that introduces this file) |
| Doctrine-source attribution check | Per-doctrine `source.url` field | 2026-05-16 | n/a — checked by test_doctrines.py |

---

## Hard limit

**No new ForgeMind generator may be merged to `main` until its impact
on this AIIA is recorded.** Re-run `forgemind self-audit`; a blocker
finding stops the merge.

## Bitácora

- **v1.0 · 2026-05-16** — initial AIIA emitted as part of the
  v1.3.0 release, after the doctrines registry shipped.
