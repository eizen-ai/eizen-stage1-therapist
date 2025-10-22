# Backup and Restore Scripts

This directory contains scripts to backup and restore the Therapist2 project.

## Quick Start

### Create a Backup (with .git directory)
```bash
./backup.sh
```

### Create a Backup (without .git directory)
```bash
./backup.sh --no-git
```

### Restore from Backup
```bash
./restore.sh
```

---

## Backup Script (`backup.sh`)

Creates a compressed `.tar.gz` backup of the entire project.

### Features
- **Includes .git directory by default** (full version control history)
- Excludes common temporary files (`__pycache__`, `.pytest_cache`, etc.)
- Timestamped backup files for easy identification
- Shows backup size and compression statistics
- Stores backups in `../backups/` directory

### Usage

**Basic backup (recommended):**
```bash
./backup.sh
```

**Backup without .git directory:**
```bash
./backup.sh --no-git
```

**Include all files (even cache files):**
```bash
./backup.sh --include-all
```

**Custom backup directory:**
```bash
./backup.sh --backup-dir /path/to/backup/location
```

**Combine options:**
```bash
./backup.sh --no-git --backup-dir ~/my-backups
```

### Options
- `--no-git` - Exclude .git directory (smaller backup, no git history)
- `--include-all` - Include cache files (__pycache__, .pytest_cache, etc.)
- `--backup-dir DIR` - Specify custom backup directory (default: ../backups)
- `--help` - Show help message

---

## Restore Script (`restore.sh`)

Restores the project from a backup archive.

### Features
- Interactive backup selection
- Automatic backup of current state before restore
- Safety confirmations before overwriting
- Lists all available backups with timestamps

### Usage

**Interactive restore (recommended):**
```bash
./restore.sh
```

This will:
1. Show all available backups
2. Let you choose which one to restore
3. Ask for confirmation
4. Backup current directory before restoring
5. Extract the selected backup

**List available backups:**
```bash
./restore.sh --list
```

**Restore specific backup:**
```bash
./restore.sh --backup ../backups/Therapist2_backup_20251021_124019.tar.gz
```

**Auto-confirm (skip prompts):**
```bash
./restore.sh --backup ../backups/Therapist2_backup_20251021_124019.tar.gz --yes
```

### Options
- `--list` - List all available backups
- `--backup FILE` - Specify backup file to restore
- `--backup-dir DIR` - Specify backup directory (default: ../backups)
- `--yes, -y` - Auto-confirm restoration (skip prompts)
- `--help` - Show help message

---

## Backup Location

By default, backups are stored in:
```
/media/eizen-4/2TB/gaurav/AI Therapist/backups/
```

Backup files are named:
```
Therapist2_backup_YYYYMMDD_HHMMSS.tar.gz
```

Example: `Therapist2_backup_20251021_124019.tar.gz`

---

## What Gets Backed Up

### Included by default:
- All source code
- Configuration files
- **.git directory** (complete version control history)
- Data files
- Documentation

### Excluded by default:
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- `.pytest_cache/` - Pytest cache
- `node_modules/` - Node.js dependencies
- `*.egg-info/` - Python package metadata
- `.venv/`, `venv/` - Virtual environments

Use `--include-all` to include cache files, or `--no-git` to exclude the .git directory.

---

## Examples

### Example 1: Create a full backup
```bash
./backup.sh
```
Output:
```
=====================================
  Therapist2 Backup Script
=====================================

Configuration:
  Backup name: Therapist2_backup_20251021_124019.tar.gz
  Backup location: ../backups/Therapist2_backup_20251021_124019.tar.gz
  Include .git: true
  Exclude common files: true

Calculating directory size...
  Current directory size: 5.5G

Creating backup...

=====================================
  Backup completed successfully!
=====================================

Backup details:
  Location: ../backups/Therapist2_backup_20251021_124019.tar.gz
  Size: 2.8G (compressed from 5.5G)
```

### Example 2: Restore from backup interactively
```bash
./restore.sh
```
Output:
```
=====================================
  Therapist2 Restore Script
=====================================

Available backups:

  1. Therapist2_backup_20251021_124019.tar.gz (2.8G, Oct 21 12:40)
  2. Therapist2_backup_20251021_100530.tar.gz (2.7G, Oct 21 10:05)
  3. Therapist2_backup_20251020_183245.tar.gz (2.6G, Oct 20 18:32)

Enter backup number to restore (or 'q' to quit): 1

Restore Configuration:
  Backup file: Therapist2_backup_20251021_124019.tar.gz
  Backup size: 2.8G
  Current directory will be backed up to: Therapist2_pre_restore_20251021_130215

WARNING: This will replace the current project directory!

Are you sure you want to continue? (yes/no): yes
```

### Example 3: Create lightweight backup without git
```bash
./backup.sh --no-git
```

---

## Safety Features

### Backup Script
- Non-destructive: only creates new files
- Shows size estimates before creating backup
- Validates backup creation success

### Restore Script
- Always backs up current directory before restoring
- Requires explicit confirmation (unless using `--yes`)
- Rollback on failure: restores previous version if extraction fails
- Shows backup details before restoring

---

## Tips

1. **Regular backups**: Run `./backup.sh` before making major changes
2. **Keep multiple backups**: The script automatically timestamps backups
3. **Git integration**: Backups include .git by default, so you get the full repository history
4. **Test restores**: Periodically test the restore process to ensure backups work
5. **Clean old backups**: Remove old backups manually to save disk space

---

## Troubleshooting

**Problem**: Backup is too large
- **Solution**: Use `--no-git` to exclude git history, or clean up large files first

**Problem**: Restore failed
- **Solution**: The script automatically restores your previous version. Check disk space and file permissions.

**Problem**: Can't find backups
- **Solution**: Use `./restore.sh --list` to see all backups, or check the backup directory manually

**Problem**: Permission denied
- **Solution**: Ensure scripts are executable: `chmod +x backup.sh restore.sh`

---

## Manual Backup/Restore

If you prefer manual commands:

**Manual Backup:**
```bash
tar -czf ../backups/manual_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
  --exclude=__pycache__ --exclude=*.pyc -C .. Therapist2
```

**Manual Restore:**
```bash
cd "/media/eizen-4/2TB/gaurav/AI Therapist"
mv Therapist2 Therapist2_old
tar -xzf backups/Therapist2_backup_YYYYMMDD_HHMMSS.tar.gz
```
