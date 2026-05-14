# Third-Party Attributions

ForgeMind incorporates patterns and templates derived from the following
open-source projects. This file satisfies the attribution requirements of
each upstream license. No upstream code is redistributed inside ForgeMind;
only patterns (state machines, entity schemas, workflow conventions) have
been codified into ForgeMind's plugins and YAML templates.

---

## iso-gestion — ISO 9001:2015 QMS reference patterns

- **Source**: https://github.com/Desarrollo-CeSPI/iso-gestion
- **Author**: CeSPI UNLP — Centro Superior para el Procesamiento de la
  Información, Universidad Nacional de La Plata, Argentina
- **License**: MIT
- **Production track record**: In operation since 2014, supporting two
  ISO 9001:2015 certified scopes, 30+ active users, and ~3000 managed records.

### What ForgeMind uses

The 8-state document lifecycle, the change-control workflow, and the
scope-based RBAC model in the following ForgeMind files are direct
codifications of the patterns iso-gestion validated in production:

- `forgemind/plugins/iso9001_pattern.py`
- `forgemind/templates/reverse_patterns/iso9001_reverse_pattern.yaml`
- `forgemind/templates/qms/documento_lifecycle.yaml`
- `forgemind/templates/qms/control_cambios.yaml`
- `forgemind/templates/qms/alcance_rbac.yaml`

### What ForgeMind does NOT use

ForgeMind does not bundle, redistribute, or depend on iso-gestion's PHP /
Symfony 2.8 codebase, its database schema, its UI, or its Symfony-specific
ACL implementation.

### iso-gestion MIT License (verbatim)

```
Copyright (c) 2004-2013 Fabien Potencier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

---

## Industry-standard deployment patterns — software domain

The two `software` variants ForgeMind ships (`blue_green` and `canary`) codify
industry-standard deployment patterns. ForgeMind does NOT redistribute upstream
code from these sources; it codifies the published patterns into its
state-machine model.

### Blue/Green deployment

- **Pattern documented at**: Martin Fowler — BlueGreenDeployment
  ([martinfowler.com/bliki/BlueGreenDeployment.html](https://martinfowler.com/bliki/BlueGreenDeployment.html))
- **Reference implementations** (open source): Spinnaker, Argo Rollouts
  (BlueGreen strategy), Flagger.
- **What ForgeMind uses**: the canonical blue/green semantics —
  two full production environments with an instantaneous load-balancer
  switch as the rollback primitive.

### Canary release

- **Pattern documented at**: Google SRE Workbook — Canarying Releases
  ([sre.google/workbook/canarying-releases/](https://sre.google/workbook/canarying-releases/))
- **Reference implementations** (open source): Spinnaker Kayenta,
  Argo Rollouts (Canary strategy), Flagger.
- **Additional reference**: Netflix Tech Blog posts on canary analysis.
- **What ForgeMind uses**: progressive traffic shifting (1% → 10% → 50% →
  100%), SLO-based automated rollback gating, the `Canary` tier between
  Staging and Production.

The Google SRE Workbook is licensed CC-BY-4.0; Martin Fowler's bliki is
publicly accessible reference material. ForgeMind credits these sources
because the patterns are theirs even though no upstream code is copied.

---

## Industry-standard deployment patterns — ai_ml domain

The two `ai_ml` variants ForgeMind ships codify documented MLOps patterns.

### Feature-flag + checkpoint rollback

- **Pattern documented at**: MLOps community practice across MLflow,
  Weights & Biases, LaunchDarkly, TensorFlow Serving, KServe.
- **What ForgeMind uses**: canary-style rollout with feature flags routing
  traffic to specific cohorts; checkpoint restore as rollback primitive.

### Shadow deployment

- **Primary references**:
  - D. Sculley et al., *"Hidden Technical Debt in ML Systems"*,
    NeurIPS 2015 (Google).
  - D. Sato, A. Wider, C. Windheuser, *"Continuous Delivery for Machine
    Learning"*, [martinfowler.com/articles/cd4ml.html](https://martinfowler.com/articles/cd4ml.html), 2019.
  - Netflix Tech Blog posts on model shadowing.
- **What ForgeMind uses**: the canonical shadowing semantics — new model
  runs in parallel with the production model on the same input traffic;
  only the production model's predictions reach users; shadow predictions
  are logged for offline analysis. Rollback from the `Shadow` state is
  operationally trivial (turn off the shadow logger); rollback from
  `Production` is a serving-role swap.

ForgeMind credits these sources because the shadow-deployment pattern is
theirs; no upstream code is copied.

---

## Reporting attribution issues

If you are an author of a project whose patterns appear in ForgeMind and you
would like the attribution updated, corrected, or expanded, please open an
issue at https://github.com/fc1sec/forgemind/issues.
