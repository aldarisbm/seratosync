#!/bin/bash -e

# Serato Sync - Complete backup with rsync + metadata sync
# Can be run from anywhere

SCRIPT_DIR="/Users/berrio/Develop/seratosync"
ERROR_FILE="/Users/berrio/Desktop/error.txt"

echo "=================================================="
echo "Serato Complete Backup"
echo "=================================================="

# Step 1: Rsync music files (excluding Serato metadata)
echo ""
echo "Step 1: Syncing music files with rsync..."
echo "--------------------------------------------------"
rsync -ahP --exclude '.DS_Store' --exclude '.tmp.driveupload' --exclude '_Serato_' --exclude '_Serato_Backup' /Users/berrio/Music /Volumes/sandisk/ 2> "$ERROR_FILE"

# Check rsync errors
if [ -f "$ERROR_FILE" ]; then
    if [ -s "$ERROR_FILE" ]; then
        echo "⚠ Rsync completed with errors"
        echo "Check errors at ${ERROR_FILE}"
    else
        echo "✓ Rsync completed successfully"
        rm -f "$ERROR_FILE"
    fi
else
    echo "⚠ Error file not created"
fi

# Step 2: Sync Serato metadata
echo ""
echo "Step 2: Syncing Serato metadata..."
echo "--------------------------------------------------"
cd "$SCRIPT_DIR"
poetry run python src/seratosync/main.py

echo ""
echo "=================================================="
echo "✓ Complete backup finished!"
echo "=================================================="
