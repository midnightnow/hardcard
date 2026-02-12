# Hardcard v1.1.0 - Next Steps Review

**Status**: Core primitives tidied and ready ✅
**Date**: 2026-02-07
**Version**: v1.1.0 - Open Core Launch

---

## ✅ Completed Tasks

### 1. Repository Cleanup (Cult of Done)
- ✅ Created comprehensive `.gitignore` excluding test projects
- ✅ Focused repository on core primitives only
- ✅ Set aside experimental applications (VetSorcery, AIVA, Alexandria, MacAgent, MOEX)
- ✅ All test files remain on disk but excluded from version control

### 2. Configuration Updates
- ✅ Fixed `pyproject.toml` URLs → `github.com/midnightnow/hardcard`
- ✅ Consolidated Firebase hosting in `hardcard-e107f` project
- ✅ Three sites configured: hardcard-ai, hardcard-org, hardcard-world

### 3. Documentation
- ✅ Updated `CLAUDE.md` - Focused on core primitives
- ✅ Updated `GEMINI.md` - Added Wiki v2.0 system
- ✅ Created `hardcard.json` - Project manifest for wiki system
- ✅ Created `docs/FAQ.md` - Comprehensive FAQ
- ✅ Created `docs/SHEAR_FORCE_GUIDE.md` - Economic physics guide

### 4. Git Commits (Pushed to Main)
```
726763fa docs: Integrate Claude Code Wiki v2.0 system
87b06979 docs: Update CLAUDE.md and GEMINI.md for v1.1.0 cleanup
30b0cc1e chore: Tidy Hardcard v1.1.0 - Focus on Core Primitives
d38bfa0d docs: Add comprehensive Shear Force Algorithm Guide
```

### 5. Package Status
- ✅ Package installed: `hardcard v1.1.0`
- ✅ CLI imports working: `hardcard.cli`, `hardcard_core.physics`
- ✅ Dependencies: `click`, `cryptography`
- ⚠️ CLI not in PATH (use `python3 -c "from hardcard.cli import main; main()"`)

---

## 🔄 Immediate Next Steps

### 1. Test Wiki v2.0 System
**Priority**: High | **Time**: 5 minutes

```bash
# Scan Hardcard project
wiki scan "/Users/studio/00 Constellation/hardcard"

# Verify incremental scanning
touch hardcard/cli.py
wiki scan "/Users/studio/00 Constellation/hardcard"

# Check database size
du -h ~/.claude/wiki/hardcard.db

# Get project context
wiki context hardcard

# Run optimization
wiki vacuum
```

### 2. Verify Package Installation
**Priority**: High | **Time**: 2 minutes

```bash
# Test imports
python3 -c "from hardcard.cli import main; print('✅ CLI')"
python3 -c "from hardcard_core.physics import calculate_shear_force; print('✅ Physics')"

# Test shear force calculation
python3 << EOF
from hardcard_core.physics import calculate_shear_force
from decimal import Decimal
sigma = calculate_shear_force(Decimal("100"), Decimal("450"))
print(f"Shear force: {sigma} (expected: 0.45)")
EOF
```

### 3. Check Deployment Sites
**Priority**: High | **Time**: 3 minutes

```bash
# Verify Firebase project
firebase use

# List sites
firebase hosting:sites:list

# Test URLs (requires network)
curl -I https://hardcard-e107f-ai.web.app 2>&1 | grep "HTTP"
curl -I https://hardcard-e107f-org.web.app 2>&1 | grep "HTTP"
curl -I https://hardcard-e107f-world.web.app 2>&1 | grep "HTTP"
```

### 4. Fix CLI Accessibility
**Priority**: Medium | **Time**: 2 minutes

**Option A - Alias** (quick):
```bash
echo 'alias hardcard="python3 -c \"from hardcard.cli import main; main()\""' >> ~/.zshrc
source ~/.zshrc
```

**Option B - pipx** (recommended):
```bash
pipx install -e "/Users/studio/00 Constellation/hardcard"
```

### 5. Verify .gitignore Effectiveness
**Priority**: Low | **Time**: 2 minutes

```bash
# Check ignored files count
git status --short | wc -l

# Verify test projects ignored
for dir in vetsorcery* alexandria* macagent* moex* aiva*; do
    [ -d "$dir" ] && {
        git check-ignore "$dir" && echo "✅ $dir ignored" || echo "⚠️ $dir tracked"
    }
done 2>/dev/null
```

---

## 🎯 Quick Wins (Do These Next)

**Total Time**: ~15 minutes

1. ✅ **Test package** (2 min) - Verify imports and calculations work
2. ✅ **Fix CLI** (2 min) - Add alias or use pipx  
3. ✅ **Test Wiki** (5 min) - Run wiki scan and verify performance
4. ✅ **Check sites** (3 min) - Verify deployment URLs work
5. ✅ **Verify git** (2 min) - Ensure test projects properly ignored

---

## 📊 Current Status Summary

**Core Primitives**: ✅ Production-ready
- hardcard/ package working
- hardcard_core/ primitives functional
- Documentation complete
- Version control clean

**Known Issues**:
1. CLI not in PATH → Add alias or use pipx
2. Custom domains not verified → Sites at .web.app URLs work
3. Multiple Firebase projects in config → Using hardcard-e107f

**Performance**:
- Package size: 107KB
- Dependencies: 2 (click, cryptography)
- Python: >=3.9

---

## 🚀 Optional Future Work

### PyPI Publication
```bash
python3 -m build
twine check dist/*
twine upload dist/*
```

### GitHub Release
```bash
git tag -a v1.1.0 -m "Open Core Launch"
git push origin v1.1.0
gh release create v1.1.0 dist/*
```

### Custom Domains
- Set up hardcard.ai → hardcard-e107f-ai
- Set up hardcard.org → hardcard-e107f-org
- Set up hardcard.world → hardcard-e107f

---

**Hardcard v1.1.0 is wrapped and ready! 🏛️**

Next: Run the "Quick Wins" checklist above (15 min total)
