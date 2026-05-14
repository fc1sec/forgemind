# ForgeMind Compatibility Matrix

**Version:** v1.2.1  
**Updated:** May 2026

---

## Quick Reference

### Can I use this version with my existing projects?

| Project Version | v1.2.1 | v1.2.0 | v1.1.0 |
|---|:---:|:---:|:---:|
| **v1.2.1** | ✅ | ✅ | ✅ |
| **v1.2.0** | ✅ | ✅ | ✅ |
| **v1.1.0** | ✅ | ✅ | ✅ |

All current versions can read all previous versions' projects.

### Can I use this version with previously generated outputs?

| Output Version | v1.2.1 | v1.2.0 | v1.1.0 |
|---|:---:|:---:|:---:|
| **v1.2.1** | ✅ | ✅ | ✅ |
| **v1.2.0** | ✅ | ✅ | ✅ |
| **v1.1.0** | ✅ | ✅ | ✅ |

All outputs from previous versions are compatible.

---

## Detailed Compatibility

### v1.2.1 (Current Release)

**Status:** ✅ Recommended, fully supported

```yaml
version: 1.2.1
released: 2026-05-13

works_with:
  projects:
    - 1.2.1   # ✅ Native
    - 1.2.0   # ✅ Full backward compatibility
    - 1.1.0   # ✅ Full backward compatibility
  outputs:
    - 1.2.1   # ✅ Native
    - 1.2.0   # ✅ Full backward compatibility
    - 1.1.0   # ✅ Full backward compatibility

can_rollback_to:
  - 1.2.0     # ✅ Safe anytime
  - 1.1.0     # ✅ Safe anytime

backward_compatible: true
breaking_changes: false
schema_changes: none
```

**What changed from v1.2.0:**
- Version detection system added
- Update notifications implemented
- Non-breaking infrastructure improvements
- Performance optimizations
- Bug fixes

**Migration needed:** No

### v1.2.0 (Previous Release)

**Status:** ✅ Supported (update to v1.2.1 for latest)

```yaml
version: 1.2.0
released: 2026-02-15

works_with:
  projects:
    - 1.2.0   # ✅ Native
    - 1.1.0   # ✅ Full backward compatibility
  outputs:
    - 1.2.0   # ✅ Native
    - 1.1.0   # ✅ Full backward compatibility

can_rollback_to:
  - 1.1.0     # ✅ Safe anytime

backward_compatible: true
breaking_changes: false
schema_changes: Added optional "governance" field (never required)
```

**What changed from v1.1.0:**
- Reverse pattern plugin system added
- ISO 9001 reference pattern included
- Software and AI/ML patterns added
- Epistemic validator implemented
- ReverseContextGenerator added
- 28 new tests for plugin system

**Migration needed:** No (all new features are opt-in)

### v1.1.0 (Earlier Release)

**Status:** ⚠️ Supported (recommend upgrading to v1.2.1)

```yaml
version: 1.1.0
released: 2025-11-20

works_with:
  projects:
    - 1.1.0   # ✅ Native
  outputs:
    - 1.1.0   # ✅ Native

can_rollback_to: []   # Oldest supported version

backward_compatible: false   # Cannot upgrade from v1.0.x
breaking_changes: true       # Breaking from v1.0.x
schema_changes: All context generators new
```

**What's different:**
- 5 new generators (context, risk checklist, tool matrix, PR template, issue template)
- Automatic integration into all outputs
- 17 outputs instead of 12
- Requires Python 3.9+

**Migration needed:** If upgrading from v1.0.x, yes

---

## Scenario: What Do I Do?

### Scenario 1: I'm on v1.1.0, can I update to v1.2.1?

✅ **YES, safely.**

```bash
pip install --upgrade forgemind

# Your existing v1.1.0 projects work unchanged
forgemind intake forgemind_projects/my_project.md

# Output will be generated with v1.2.1 enhancements
```

**No action needed.** Existing projects are fully compatible.

### Scenario 2: I'm on v1.2.0, should I update to v1.2.1?

✅ **YES, recommended.**

v1.2.1 adds version checking and safety features:

```bash
pip install --upgrade forgemind

# Everything works exactly as before
forgemind intake forgemind_projects/my_project.md
```

**Benefits:**
- Version availability notifications
- Better error messages
- Non-blocking safety checks
- Same API, zero breakage

### Scenario 3: I created a project on v1.2.0, can I use it with v1.1.0?

❌ **NO, not recommended.**

v1.2.0 projects may contain the "governance" field which v1.1.0 doesn't understand.

**Solution:** Stay on v1.2.x or use v1.2.0+

```bash
# Check what version you're using
forgemind version

# If v1.1.0:
pip install forgemind==1.2.1
```

### Scenario 4: I want to stay on v1.1.0

✅ **You can, but v1.2.1 is recommended.**

v1.1.0 is stable, but if you need:
- Version checking notifications
- Safer update paths
- Better error handling

→ Update to v1.2.1 (fully backward compatible)

### Scenario 5: I want to test v2.0 (when released)

✅ **Use virtual environments.**

```bash
# Keep v1.2.1 in main environment
python3 -m venv env_v2

# Test v2.0 in isolated environment
source env_v2/bin/activate
pip install forgemind==2.0.0

# Test projects
forgemind intake test_project.md

# Switch back when done
deactivate
```

Your main installation stays unchanged.

---

## Migration Scenarios

### From v1.0.x → v1.1.0+

Breaking changes exist (context generators added, schema changed).

**Required steps:**
1. Backup your projects: `cp -r forgemind_projects forgemind_projects.backup`
2. Run migration: `forgemind migrate --from 1.0.x --to 1.1.0`
3. Test: `forgemind intake forgemind_projects/my_project.md`

### From v1.1.0 → v1.2.0+

No breaking changes. Opt-in new features.

**No migration needed:**
```bash
pip install --upgrade forgemind
# Existing projects work unchanged
```

### From v1.2.x → v2.0+ (Future)

Breaking changes anticipated.

**Steps:**
1. Backup: `cp -r forgemind_projects forgemind_projects.backup`
2. Read `BREAKING_CHANGES.md`
3. Test in non-critical project first
4. Run migration: `forgemind migrate --from 1.2.x --to 2.0.0`
5. Verify: `forgemind intake forgemind_projects/my_project.md`

---

## Feature Availability by Version

| Feature | v1.0.x | v1.1.0 | v1.2.0 | v1.2.1 |
|---------|:------:|:------:|:------:|:------:|
| Basic analysis | ✅ | ✅ | ✅ | ✅ |
| RDMAICSI matrix | ✅ | ✅ | ✅ | ✅ |
| Risk register | ✅ | ✅ | ✅ | ✅ |
| Project charter | ✅ | ✅ | ✅ | ✅ |
| **Context generator** | ❌ | ✅ | ✅ | ✅ |
| **AI risk checklist** | ❌ | ✅ | ✅ | ✅ |
| **Tool permission matrix** | ❌ | ✅ | ✅ | ✅ |
| **PR template** | ❌ | ✅ | ✅ | ✅ |
| **Reverse patterns** | ❌ | ❌ | ✅ | ✅ |
| **Plugin system** | ❌ | ❌ | ✅ | ✅ |
| **Version checking** | ❌ | ❌ | ❌ | ✅ |

---

## Unsupported Versions

- **v1.0.x and earlier** — End of life, upgrade to v1.1.0+
- **Unreleased versions** — Not supported until officially released

---

## Support Policy

| Version | Release Date | End of Support | Status |
|---------|-------------|:----------:|---------|
| v1.2.1+ | Current | 2027-05-13 | ✅ Fully supported |
| v1.2.0 | 2026-02-15 | 2026-08-15 | ✅ Supported |
| v1.1.0 | 2025-11-20 | 2026-05-20 | ⚠️ Update recommended |
| v1.0.x | ~2025 | 2025-12-01 | ❌ Unsupported |

---

## How to Check Your Version

```bash
# Check installed version
forgemind version

# Check what version a project was created with
# (stored in project metadata)
head -5 forgemind_projects/my_project.md
```

---

## Frequently Asked Questions

### Q: If I update, will my old projects break?

**A:** No. All versions are backward compatible within their major version line.

- v1.1.0 → v1.2.0 → v1.2.1: Fully compatible
- Projects created with v1.1.0 work unchanged on v1.2.1

### Q: What if v1.2.1 has a bug?

**A:** Rollback immediately (takes 10 seconds):

```bash
pip install forgemind==1.2.0
# Your projects and work are unaffected
```

### Q: Can I mix versions?

**A:** Yes, using virtual environments:

```bash
python3 -m venv env_v121
python3 -m venv env_v110

source env_v121/bin/activate
pip install forgemind==1.2.1

source env_v110/bin/activate
pip install forgemind==1.1.0
```

Switch between them as needed.

### Q: When's v2.0 coming?

**A:** Planned for ~2026 Q4. We'll announce 3 months in advance with clear migration guides.

---

## Summary

✅ **All v1.x versions are backward compatible within their line**  
✅ **You can safely update from v1.1.0 → v1.2.1**  
✅ **Rollback is always safe**  
✅ **Your projects and outputs are never destroyed by updates**

**For details on safe update procedures, see:** [UPDATES_AND_SAFETY.md](UPDATES_AND_SAFETY.md)
