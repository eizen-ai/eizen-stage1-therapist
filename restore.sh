#!/bin/bash

# Restore script for Therapist2 project
# Restores from a backup archive

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Therapist2"
BACKUP_DIR="../backups"
PARENT_DIR="$(dirname "$PWD")"

# Parse arguments
BACKUP_FILE=""
LIST_BACKUPS=false
AUTO_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --list)
            LIST_BACKUPS=true
            shift
            ;;
        --backup)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        --yes|-y)
            AUTO_CONFIRM=true
            shift
            ;;
        --help)
            echo "Usage: ./restore.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --list            List all available backups"
            echo "  --backup FILE     Specify backup file to restore"
            echo "  --backup-dir DIR  Specify backup directory (default: ../backups)"
            echo "  --yes, -y         Auto-confirm restoration (skip prompt)"
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

# List backups if requested
if [ "$LIST_BACKUPS" = true ]; then
    echo -e "${BLUE}Available backups in $BACKUP_DIR:${NC}"
    echo ""
    if [ -d "$BACKUP_DIR" ]; then
        ls -lht "$BACKUP_DIR"/${PROJECT_NAME}_backup_*.tar.gz 2>/dev/null | awk '{print NR". "$9" ("$5", "$6" "$7" "$8")"}'
        if [ $? -ne 0 ]; then
            echo "No backups found."
        fi
    else
        echo "Backup directory does not exist."
    fi
    exit 0
fi

# If no backup file specified, show available backups and let user choose
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}  Therapist2 Restore Script${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
    echo -e "${YELLOW}Available backups:${NC}"
    echo ""

    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}Backup directory $BACKUP_DIR does not exist!${NC}"
        exit 1
    fi

    # Create array of backup files
    mapfile -t BACKUPS < <(ls -t "$BACKUP_DIR"/${PROJECT_NAME}_backup_*.tar.gz 2>/dev/null)

    if [ ${#BACKUPS[@]} -eq 0 ]; then
        echo -e "${RED}No backups found in $BACKUP_DIR${NC}"
        exit 1
    fi

    # Display backups with numbers
    for i in "${!BACKUPS[@]}"; do
        BACKUP_SIZE=$(ls -lh "${BACKUPS[$i]}" | awk '{print $5}')
        BACKUP_DATE=$(ls -l "${BACKUPS[$i]}" | awk '{print $6" "$7" "$8}')
        echo "  $((i+1)). $(basename "${BACKUPS[$i]}") ($BACKUP_SIZE, $BACKUP_DATE)"
    done

    echo ""
    read -p "Enter backup number to restore (or 'q' to quit): " CHOICE

    if [ "$CHOICE" = "q" ] || [ "$CHOICE" = "Q" ]; then
        echo "Restore cancelled."
        exit 0
    fi

    # Validate choice
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt ${#BACKUPS[@]} ]; then
        echo -e "${RED}Invalid choice!${NC}"
        exit 1
    fi

    BACKUP_FILE="${BACKUPS[$((CHOICE-1))]}"
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Display restore information
echo ""
echo -e "${YELLOW}Restore Configuration:${NC}"
echo "  Backup file: $(basename "$BACKUP_FILE")"
echo "  Backup size: $(ls -lh "$BACKUP_FILE" | awk '{print $5}')"
echo "  Current directory will be backed up to: ${PROJECT_NAME}_pre_restore_$(date +%Y%m%d_%H%M%S)"
echo ""
echo -e "${RED}WARNING: This will replace the current project directory!${NC}"
echo ""

# Confirm restoration
if [ "$AUTO_CONFIRM" = false ]; then
    read -p "Are you sure you want to continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Restore cancelled."
        exit 0
    fi
fi

# Backup current directory
CURRENT_BACKUP="${PROJECT_NAME}_pre_restore_$(date +%Y%m%d_%H%M%S)"
echo ""
echo -e "${YELLOW}Backing up current directory...${NC}"
cd "$PARENT_DIR"
mv "$PROJECT_NAME" "$CURRENT_BACKUP"

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to backup current directory!${NC}"
    exit 1
fi

# Extract backup
echo -e "${YELLOW}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$PARENT_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}  Restore completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "${YELLOW}Details:${NC}"
    echo "  Restored from: $(basename "$BACKUP_FILE")"
    echo "  Previous version saved to: $CURRENT_BACKUP"
    echo ""
    echo -e "${YELLOW}To remove the old backup:${NC}"
    echo "  rm -rf \"$PARENT_DIR/$CURRENT_BACKUP\""
else
    echo -e "${RED}Restore failed!${NC}"
    echo "Restoring previous version..."
    mv "$CURRENT_BACKUP" "$PROJECT_NAME"
    exit 1
fi
