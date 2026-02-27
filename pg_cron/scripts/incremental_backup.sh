#!/bin/sh

DATE=$(date +"%Y%m%d_%H%M%S")
echo "Running Incremental Backup at $DATE"

SRC="/pg_wal_archive/"
DEST="/backups/incremental/"

# Copy new WAL files
rsync -av $SRC $DEST

# Remove WAL files after copying (VERY IMPORTANT)
rm -f ${SRC}*

echo "Incremental Backup Completed"