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

## Reporting attribution issues

If you are an author of a project whose patterns appear in ForgeMind and you
would like the attribution updated, corrected, or expanded, please open an
issue at https://github.com/fc1sec/forgemind/issues.
