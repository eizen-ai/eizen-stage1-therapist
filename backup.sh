#!/bin/bash

# Backup script for Therapist2 project
# Creates a compressed backup of the entire project directory

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Therapist2"
BACKUP_DIR="../backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="${PROJECT_NAME}_backup_${TIMESTAMP}.tar.gz"

# Parse arguments
INCLUDE_GIT=true
EXCLUDE_COMMON=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-git)
            INCLUDE_GIT=false
            shift
            ;;
        --include-all)
            EXCLUDE_COMMON=false
            shift
            ;;
        --backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./backup.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-git          Exclude .git directory from backup"
            echo "  --include-all     Include cache files (__pycache__, .pytest_cache, etc.)"
            echo "  --backup-dir DIR  Specify backup directory (default: ../backups)"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Build exclude options
EXCLUDE_OPTS=""
if [ "$EXCLUDE_COMMON" = true ]; then
    EXCLUDE_OPTS="--exclude=__pycache__ --exclude=*.pyc --exclude=.pytest_cache --exclude=node_modules --exclude=*.egg-info --exclude=.venv --exclude=venv"
fi

if [ "$INCLUDE_GIT" = false ]; then
    EXCLUDE_OPTS="$EXCLUDE_OPTS --exclude=.git"
fi

# Display backup information
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Therapist2 Backup Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Backup name: $BACKUP_NAME"
echo "  Backup location: $BACKUP_DIR/$BACKUP_NAME"
echo "  Include .git: $INCLUDE_GIT"
echo "  Exclude common files: $EXCLUDE_COMMON"
echo ""

# Get current directory size
echo -e "${YELLOW}Calculating directory size...${NC}"
CURRENT_SIZE=$(du -sh . | cut -f1)
echo "  Current directory size: $CURRENT_SIZE"
echo ""

# Create backup
echo -e "${YELLOW}Creating backup...${NC}"
tar -czf "$BACKUP_DIR/$BACKUP_NAME" $EXCLUDE_OPTS -C .. "$(basename "$PWD")"

# Check if backup was successful
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_DIR/$BACKUP_NAME" | awk '{print $5}')
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  Backup completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "${YELLOW}Backup details:${NC}"
    echo "  Location: $BACKUP_DIR/$BACKUP_NAME"
    echo "  Size: $BACKUP_SIZE (compressed from $CURRENT_SIZE)"
    echo ""
    echo -e "${YELLOW}To restore this backup:${NC}"
    echo "  cd \"$(dirname "$PWD")\""
    echo "  mv $PROJECT_NAME ${PROJECT_NAME}_old  # Backup current version"
    echo "  tar -xzf \"$BACKUP_DIR/$BACKUP_NAME\""
    echo ""
    echo -e "${YELLOW}All backups in $BACKUP_DIR:${NC}"
    ls -lht "$BACKUP_DIR" | grep "${PROJECT_NAME}_backup_" | head -5
else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi
