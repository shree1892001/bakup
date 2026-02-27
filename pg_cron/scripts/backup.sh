#!/bin/bash

DATE=$(date +"%Y%m%d_%H%M%S")

echo "Running Full Backup at $DATE"

PGPASSWORD=your_postgres_pass \
pg_dump -h host.docker.internal \
-p 5432 \
-U postgres \
-d SnapHack \
-F c \
-f /backups/full/snahack_full_$DATE.dump

echo "Full Backup Completed"