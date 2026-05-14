# ForgeMind: Updates, Rollback, and Safety Guide

**Last Updated:** May 2026  
**Version Coverage:** v1.1.0 → v1.2.1

---

## Quick Answer: Will Updates Destroy My Work?

**No.** ForgeMind is designed to be upgrade-safe:

✅ **v1.2.1 is fully backward compatible** with v1.1.0 and v1.2.0 projects  
✅ Your projects and outputs work unchanged with newer versions  
✅ You can always rollback to the previous version  
✅ Version checks are non-blocking (won't interrupt your work)  

---

## Version Safety Guarantees

### Backward Compatibility Matrix

| Installed | Works with v1.2.1 Projects | Works with v1.1.0 Projects | Works with Outputs |
|-----------|---------------------------|---------------------------|-------------------|
| **v1.2.1** | ✅ Yes | ✅ Yes | ✅ Yes (all versions) |
| **v1.2.0** | ✅ Yes | ✅ Yes | ✅ Yes (v1.2.0, v1.1.0) |
| **v1.1.0** | ❌ No* | ✅ Yes | ✅ Yes (v1.1.0 only) |

*v1.1.0 cannot read v1.2.0+ projects (projects with "governance" field). See migration below.

### What Version Am I Running?

```bash
forgemind version
# Output: ForgeMind v1.2.1
```

---

## Safe Update Procedures

### Option 1: Minor/Patch Updates (Recommended)

Minor and patch updates (v1.2.0 → v1.2.1, v1.1.0 → v1.1.1) are **always safe**. These updates:
- ✅ Never change project schema
- ✅ Never break existing outputs
- ✅ Add features without removing functionality
- ✅ Fix bugs and improve performance

**To update:**
```bash
pip install --upgrade forgemind
# Your projects continue to work without changes
```

**No action needed.** Existing projects are fully compatible.

### Option 2: Major Updates (v1.x → v2.0+)

Major version updates contain breaking changes and require careful handling.

#### Before updating to v2.0+:

1. **Backup your projects directory** (if project files are invaluable):
   ```bash
   cp -r forgemind_projects forgemind_projects.backup
   ```

2. **Read the breaking changes document**:
   ```bash
   # Check what's changing in the new version
   cat BREAKING_CHANGES.md
   ```

3. **Test in a non-critical project first**:
   ```bash
   # Don't update your entire codebase immediately
   # Test v2.0 on a new test project first
   pip install forgemind==2.0.0
   forgemind init --test-project
   forgemind intake test_project.md
   # Verify outputs are as expected
   ```

4. **Migrate your existing projects** (if needed):
   ```bash
   pip install forgemind==2.0.0
   forgemind migrate --from 1.2.x --to 2.0.0
   ```

5. **Roll back if problems occur**:
   ```bash
   pip install forgemind==1.2.1
   # Your projects and outputs remain unchanged
   ```

---

## Rolling Back to Previous Version

Rollback is always safe and takes 10 seconds:

```bash
# List installed versions
pip show forgemind | grep Version

# Rollback to v1.2.0
pip install forgemind==1.2.0

# Rollback to v1.1.0
pip install forgemind==1.1.0

# Verify rollback
forgemind version
# Output: ForgeMind v1.1.0
```

**Your projects and outputs are unchanged.** All data is safe during rollback.

---

## Version Check Notifications

ForgeMind automatically checks for new versions **once per day**:

```
✓ Update available: v1.2.0 → v1.2.1

Backward compatible. Safe to update anytime.
Update: pip install --upgrade forgemind
```

**OR for major updates:**

```
⚠️  Major Update Available: v1.2.1 → v2.0.0

This is a MAJOR version update with breaking changes.

Before updating:
  1. Backup your .forgemind/ directory
  2. Read BREAKING_CHANGES.md
  3. Test in non-critical project first
  4. Update: pip install --upgrade forgemind

ℹ️  See UPDATES_AND_SAFETY.md for safe upgrade procedures
💾 Don't worry: Your projects are safe. See COMPATIBILITY_MATRIX.md
```

### Skip the Version Check

If you want to skip the automatic version check:

```bash
forgemind intake my_project.md --skip-version-check
forgemind diagnose my_project.md --skip-version-check
```

Or disable it globally:
```bash
# Add to your shell profile (.zshrc, .bashrc, etc.)
export FORGEMIND_SKIP_VERSION_CHECK=1
```

---

## FAQ: Updates and Safety

### Q: Will updating ForgeMind change my existing projects?

**A:** No. Your project files (`.md`) are independent of ForgeMind version. New versions can read old projects.

Only v1.1.0 → v1.2.0+ adds an optional "governance" field to the project schema (never required). This is backward compatible.

### Q: What if I'm stuck on v1.1.0?

**A:** You can stay on v1.1.0 forever—it's a stable release. But we recommend updating to v1.2.1 because:
- ✅ Better error messages and performance
- ✅ Safer backward compatibility tracking
- ✅ Automatic version notifications (helpful reminder to update)
- ✅ All v1.1.0 projects work unchanged on v1.2.1

To update:
```bash
pip install --upgrade forgemind
# Takes 10 seconds, your projects work unchanged
```

### Q: What if a new version breaks my workflow?

**A:** Report it on GitHub, then rollback immediately:

```bash
# Rollback to stable version
pip install forgemind==1.2.0

# Your work continues
forgemind intake my_project.md
```

We support rollback paths for exactly this reason.

### Q: Can I run multiple ForgeMind versions simultaneously?

**A:** Yes, using virtual environments:

```bash
# Create isolated environments
python3 -m venv env_v121
python3 -m venv env_v110

# Activate and install specific versions
source env_v121/bin/activate
pip install forgemind==1.2.1

source env_v110/bin/activate
pip install forgemind==1.1.0

# Switch between versions as needed
```

This is useful for testing compatibility.

### Q: How do I report update issues?

**A:** Open an issue on GitHub with:
1. Current ForgeMind version: `forgemind version`
2. Error message or behavior that's unexpected
3. What version you're upgrading from/to
4. Which Python version: `python --version`

Include the full error traceback if available.

### Q: When will v2.0 be released?

**A:** No date yet. Current plan is ~2026 Q4. We'll announce 3 months in advance with:
- Clear breaking changes documentation
- Migration guide for existing projects
- Safe upgrade paths and rollback support

You'll have plenty of notice.

### Q: Is there a version pinning strategy?

**A:** Yes, if you want stability:

```bash
# Pin to specific version in requirements.txt
echo "forgemind==1.2.1" >> requirements.txt

# Or use version constraints
echo "forgemind>=1.2.0,<2.0.0" >> requirements.txt

# Install from requirements
pip install -r requirements.txt
```

This ensures all team members use the same version.

---

## Compatibility Matrix (Detailed)

### v1.2.1 (Current)

```
installed_version: 1.2.1

can_read_projects: [1.2.1, 1.2.0, 1.1.0]
can_read_outputs: [1.2.1, 1.2.0, 1.1.0]
can_rollback_to: [1.2.0, 1.1.0]
backward_compatible: YES
```

You can safely run `forgemind intake` on v1.1.0 or v1.2.0 projects.

### v1.2.0

```
installed_version: 1.2.0

can_read_projects: [1.2.0, 1.1.0]
can_read_outputs: [1.2.0, 1.1.0]
can_rollback_to: [1.1.0]
backward_compatible: YES
```

v1.2.0 can read v1.1.0 projects. v1.1.0 cannot read v1.2.0 projects (missing "governance" field).

### v1.1.0

```
installed_version: 1.1.0

can_read_projects: [1.1.0]
can_read_outputs: [1.1.0]
can_rollback_to: []
backward_compatible: NO
```

v1.1.0 cannot read v1.2.0+ projects. Upgrade to read newer projects.

### v1.0.x

End of support. Upgrade to v1.1.0 or later.

---

## Breaking Changes by Version

### v2.0.0 (Future)

**Status:** Not yet released. Planned for ~2026 Q4.

Anticipated breaking changes (subject to change):
- ProjectAnalysis schema will add "governance" field (required)
- Decision log format will change
- Legacy CLI parameters will be removed

Migration path:
```bash
forgemind migrate --from 1.2.x --to 2.0.0
```

### v1.2.0 (Released)

No breaking changes from v1.1.0. Fully backward compatible.

Minor enhancement: ProjectAnalysis now includes optional "governance" field (never required).

### v1.1.0 (Released)

Breaking changes from v1.0:
- New context generators included
- Risk checklist now domain-specific
- Tool permission matrix required for agent handoffs

Requires project migration if upgrading from v1.0.

---

## Support

### Getting Help

If you encounter update issues:

1. **Check this document first** for common Q&A
2. **Check GitHub Issues** for similar reports
3. **Open a new issue** with:
   - ForgeMind version: `forgemind version`
   - Python version: `python --version`
   - Error message with full traceback
   - What you were trying to do

### Reporting Security Issues

If you discover a security vulnerability:
1. **Do NOT open a public GitHub issue**
2. Email fc1sec@hotmail.com with details
3. We'll respond within 48 hours

---

## Summary: Safe Update Checklist

- ✅ **Minor/Patch updates** (v1.2.0 → v1.2.1): Always safe, update anytime
- ✅ **Check version**: `forgemind version`
- ✅ **Automatic checks** run once per day (non-blocking)
- ✅ **Backward compatibility** verified for each release
- ✅ **Rollback always safe**: `pip install forgemind==X.Y.Z`
- ✅ **Your data is safe**: Projects and outputs never modified by updates
- ✅ **No action required** after updating (for existing projects)

**Your work is protected. Update confidently.**

---

*ForgeMind versioning follows Semantic Versioning (SemVer 2.0.0)*  
*For more info: https://semver.org/*
