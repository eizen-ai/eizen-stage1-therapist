# GitHub Pre-Push Checklist

> Complete this checklist before pushing to GitHub

**Date:** _______________
**Prepared by:** _______________

---

## ✅ Pre-Push Checklist

### 1. Backup Created
- [ ] Backup created and verified
- [ ] Backup location: `_______________________`
- [ ] Backup size: `_______________________`

### 2. Sensitive Data Removed
- [ ] No `.env` file in git (only `.env.example`)
- [ ] No passwords or API keys in code
- [ ] No personal information in logs
- [ ] No private transcripts (if any)
- [ ] Checked: `git status` shows no sensitive files

**Command to check:**
```bash
git status
git ls-files | grep -E '\.env$|password|secret|key'
```

### 3. Large Files Excluded
- [ ] No large embedding files (.faiss > 100MB)
- [ ] No large model files (.bin, .pt, .pth)
- [ ] No session logs (logs/*.json)
- [ ] venv/ directory excluded
- [ ] __pycache__/ directories excluded

**Command to check:**
```bash
find . -type f -size +50M -not -path "./venv/*" -not -path "./.git/*"
```

### 4. Documentation Complete
- [ ] README.md is up to date
- [ ] GITHUB_SETUP_GUIDE.md exists
- [ ] docs/ARCHITECTURE.md exists
- [ ] docs/PRESENTATION_GUIDE.md exists
- [ ] All doc links work (no broken links)
- [ ] LICENSE file present

**Check links:**
```bash
grep -r "\[.*\](.*\.md)" README.md docs/
```

### 5. Code Quality
- [ ] No debug print statements left in code
- [ ] No commented-out code blocks
- [ ] No TODO comments for critical issues
- [ ] All imports used (no unused imports)
- [ ] Consistent code formatting

**Quick check:**
```bash
grep -r "print(" src/ | grep -v "logger"
grep -r "# TODO" src/
```

### 6. Dependencies
- [ ] requirements.txt is complete and up to date
- [ ] No local file paths in requirements.txt
- [ ] All imports can be installed via pip
- [ ] Tested: `pip install -r requirements.txt` in clean venv

**Test:**
```bash
python3 -m venv test_venv
source test_venv/bin/activate
pip install -r requirements.txt
deactivate
rm -rf test_venv
```

### 7. Configuration Files
- [ ] `.env.example` has all required variables
- [ ] `.env.example` has NO real secrets
- [ ] `.gitignore` is comprehensive
- [ ] `docker-compose.yml` uses environment variables (not hardcoded)
- [ ] `Dockerfile` builds successfully

**Test Docker build:**
```bash
docker compose build
```

### 8. Scripts and Executables
- [ ] `setup.sh` is executable and works
- [ ] `startup.sh` is executable and works
- [ ] `update_docker.sh` is executable
- [ ] All scripts have proper shebang (`#!/bin/bash`)

**Test:**
```bash
chmod +x setup.sh startup.sh update_docker.sh
./setup.sh --help 2>/dev/null || echo "Script exists"
```

### 9. Data Files
- [ ] Only necessary data included
- [ ] Metadata files included (JSON, CSV)
- [ ] Large files documented in README
- [ ] Instructions for downloading large files provided

**Files to include:**
- ✅ `data/embeddings/trt_rag_metadata.json` (small, ~1-2MB)
- ✅ `config/STAGE1_COMPLETE.csv`
- ❌ `data/embeddings/*.faiss` (distribute via releases)
- ❌ `logs/*.json` (not needed)

### 10. Examples and Tests
- [ ] `examples/` directory has working examples
- [ ] `tests/` directory has tests
- [ ] Tests can run independently
- [ ] Example scripts documented

**Run quick test:**
```bash
python tests/test_improved_system.py --help 2>/dev/null || echo "Test exists"
```

### 11. Git Repository
- [ ] `.git` directory exists
- [ ] Remote origin set (GitHub URL)
- [ ] Main branch is `main` or `master`
- [ ] No untracked files that should be committed
- [ ] No staged files with sensitive data

**Check:**
```bash
git remote -v
git branch
git status
```

### 12. README Information
- [ ] Project title clear
- [ ] Description informative
- [ ] Installation instructions complete
- [ ] Usage examples provided
- [ ] Architecture diagram/link included
- [ ] License mentioned
- [ ] Contact/support information

### 13. GitHub-Specific Files
- [ ] LICENSE file exists (MIT, Apache, etc.)
- [ ] .gitignore is comprehensive
- [ ] README.md is GitHub-markdown formatted
- [ ] CONTRIBUTING.md exists (if open source)
- [ ] CODE_OF_CONDUCT.md exists (optional)

### 14. Legal and Licensing
- [ ] All code is your own or properly licensed
- [ ] Third-party code attributed
- [ ] License chosen (e.g., MIT)
- [ ] No proprietary/confidential information

### 15. Final Checks
- [ ] Project name decided: `________________________`
- [ ] GitHub repository created: YES / NO
- [ ] Repository visibility: PUBLIC / PRIVATE
- [ ] Description written: `________________________`
- [ ] Topics/tags added (after push)

---

## 📋 Information Needed

Before pushing, I need to know:

1. **Repository Name**
   - [ ] Decided: `________________________`

2. **Repository URL**
   - [ ] Created: `https://github.com/USERNAME/REPO-NAME`

3. **License**
   - [ ] Chosen: MIT / Apache 2.0 / GPL / Other: `________`

4. **Project Visibility**
   - [ ] Public (anyone can see)
   - [ ] Private (only you and collaborators)

5. **Large Files Distribution**
   - [ ] Will use GitHub Releases for embeddings: YES / NO
   - [ ] Will use Git LFS: YES / NO
   - [ ] Will provide download links: YES / NO

6. **Contact Information**
   - [ ] Email for issues: `________________________`
   - [ ] Maintainer name: `________________________`

---

## 🔍 Pre-Push Commands to Run

Run these commands before pushing:

```bash
# 1. Check git status
git status

# 2. Check for large files
find . -type f -size +50M -not -path "./venv/*" -not -path "./.git/*"

# 3. Check for sensitive files
git ls-files | grep -E '\.env$|password|secret|key|credential'

# 4. Test Docker build
docker compose build --no-cache

# 5. Test setup script
./setup.sh

# 6. Verify .gitignore works
git check-ignore -v data/embeddings/*.faiss
git check-ignore -v .env
git check-ignore -v venv/

# 7. Check documentation links
grep -r "\[.*\](.*\.md)" README.md | head -20

# 8. List what will be pushed
git ls-files | head -50
```

---

## 📦 Files That MUST Be Included

### ✅ Core Application
- [ ] `src/` directory (all source code)
- [ ] `config/` directory (CSV files)
- [ ] `requirements.txt`
- [ ] `README.md`
- [ ] `LICENSE`

### ✅ Docker/Deployment
- [ ] `Dockerfile`
- [ ] `docker-compose.yml`
- [ ] `.dockerignore`
- [ ] `startup.sh`
- [ ] `setup.sh`

### ✅ Documentation
- [ ] `docs/` directory (all documentation)
- [ ] `GITHUB_SETUP_GUIDE.md`
- [ ] `.env.example`

### ✅ Examples and Tests
- [ ] `examples/` directory
- [ ] `tests/` directory

### ✅ Structure
- [ ] `data/` directory structure (empty folders with .gitkeep)
- [ ] `logs/` directory structure (empty with .gitkeep)

---

## ❌ Files That MUST NOT Be Included

### ❌ Sensitive
- [ ] `.env` (real environment file)
- [ ] Any files with passwords/keys
- [ ] Private transcripts
- [ ] Personal notes

### ❌ Large Files
- [ ] `data/embeddings/*.faiss` (> 100MB)
- [ ] `venv/` directory
- [ ] `logs/*.json` (session logs)
- [ ] `*.tar.gz` (backups)

### ❌ Generated Files
- [ ] `__pycache__/` directories
- [ ] `*.pyc` files
- [ ] `.DS_Store` (Mac)
- [ ] `Thumbs.db` (Windows)

---

## 🚀 Push Commands

After completing this checklist:

```bash
# 1. Add all files
git add .

# 2. Check what will be committed
git status

# 3. Commit
git commit -m "Initial commit: TRT AI Therapist System

- Complete Stage 1 implementation
- Docker containerization
- Comprehensive documentation
- RAG-based dialogue system
- All critical bugs fixed"

# 4. Add remote (if not already added)
git remote add origin https://github.com/USERNAME/REPO-NAME.git

# 5. Push to GitHub
git push -u origin main
```

---

## 📝 Post-Push Tasks

After pushing to GitHub:

### Immediate
- [ ] Verify repository is accessible
- [ ] Check README renders correctly
- [ ] Test clone and setup from fresh directory
- [ ] Create first GitHub Release (v1.0)

### Documentation
- [ ] Add topics/tags to repository
- [ ] Enable GitHub Issues
- [ ] Enable GitHub Discussions (optional)
- [ ] Create Wiki (optional)

### Large Files
- [ ] Upload embeddings to GitHub Release
- [ ] Document download instructions in README
- [ ] Update GITHUB_SETUP_GUIDE.md with download link

### Community
- [ ] Add description to repository
- [ ] Add website link (if any)
- [ ] Set up branch protection (optional)
- [ ] Add collaborators (if any)

---

## 🧪 Post-Push Verification

Test that others can use your repository:

```bash
# 1. Clone in a new directory
cd /tmp
git clone https://github.com/USERNAME/REPO-NAME.git
cd REPO-NAME

# 2. Run setup
./setup.sh

# 3. Try to start (without embeddings)
./startup.sh

# 4. Verify documentation is clear
cat README.md
cat GITHUB_SETUP_GUIDE.md
```

---

## ✅ Checklist Complete

- [ ] All items checked
- [ ] Ready to push to GitHub
- [ ] Backup created
- [ ] Information collected

**Signed:** _______________  **Date:** _______________

---

**Next Step:** Run the push commands above!
