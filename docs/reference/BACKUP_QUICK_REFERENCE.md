# Backup Quick Reference

## 📦 Latest Backup

**File:** `Therapist2_backup_20251015_134214.tar.gz`
**Location:** `/media/eizen-4/2TB/gaurav/AI Therapist/`
**Size:** 26 MB
**Date:** 2025-10-15 13:42:14

**Includes:** Clean folder structure, hybrid RAG system, loop prevention, all fixes

---

## 🚀 Quick Commands

### Create New Backup
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist
tar -czf "Therapist2_backup_$(date +%Y%m%d_%H%M%S).tar.gz" \
  --exclude='Therapist2/venv' \
  --exclude='Therapist2/.git' \
  --exclude='Therapist2/__pycache__' \
  --exclude='Therapist2/*/__pycache__' \
  --exclude='Therapist2/*/*/__pycache__' \
  --exclude='Therapist2/.bmad-core' \
  --exclude='Therapist2/logs/*.json' \
  Therapist2/
```

### Restore from Backup
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist
tar -xzf Therapist2_backup_20251015_134214.tar.gz
cd Therapist2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
```

### View Backup Contents
```bash
tar -tzf /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2_backup_20251015_134214.tar.gz | less
```

### Extract Single File
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist
tar -xzf Therapist2_backup_20251015_134214.tar.gz Therapist2/src/agents/improved_ollama_dialogue_agent.py
```

---

## 🔄 Emergency Rollback (If Something Breaks)

```bash
# 1. Stop current system
cd /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2
docker compose down

# 2. Rename current directory
cd /media/eizen-4/2TB/gaurav/AI\ Therapist
mv Therapist2 Therapist2_broken_$(date +%Y%m%d_%H%M%S)

# 3. Restore backup
tar -xzf Therapist2_backup_20251015_134214.tar.gz

# 4. Rebuild environment
cd Therapist2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Restart Docker
docker compose build --no-cache
docker compose up -d

# 6. Verify
curl http://localhost:8090/health
```

---

## 📝 What's in This Backup

✅ **Included:**
- All source code
- All documentation (organized in docs/)
- All configuration files
- All data files (embeddings, transcripts)
- Docker files
- Scripts and utilities

❌ **Excluded (to save space):**
- Virtual environment (venv/)
- Git history (.git/)
- Python cache (__pycache__/)
- Session logs (logs/*.json)

---

## 💾 Backup Info

**Full details:** See `/media/eizen-4/2TB/gaurav/AI Therapist/BACKUP_INFO.md`

**Available backups:**
```bash
ls -lh /media/eizen-4/2TB/gaurav/AI\ Therapist/Therapist2_backup_*.tar.gz
```

**Disk space:**
- Available: 210 GB
- Backup size: 26 MB (without venv)
- You can keep many backups!

---

## 🎯 When to Create Backup

- ✅ Before major code changes
- ✅ Before refactoring
- ✅ After completing features
- ✅ Before deployment
- ✅ Before updating dependencies

**Quick backup:**
```bash
cd /media/eizen-4/2TB/gaurav/AI\ Therapist && tar -czf "Therapist2_backup_$(date +%Y%m%d_%H%M%S).tar.gz" --exclude='Therapist2/venv' --exclude='Therapist2/.git' --exclude='Therapist2/__pycache__' --exclude='Therapist2/*/__pycache__' --exclude='Therapist2/*/*/__pycache__' --exclude='Therapist2/.bmad-core' --exclude='Therapist2/logs/*.json' Therapist2/
```

---

**Last Updated:** 2025-10-15 13:42:14
