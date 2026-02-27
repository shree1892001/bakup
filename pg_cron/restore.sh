#!/bin/sh

export PGPASSWORD=your_postgres_pass

LATEST_FILE=$(ls -t /backups/*.sql | head -1)

echo "Restoring from $LATEST_FILE"

psql -h my_postgres -p 5432 -U postgres SnapHack < $LATEST_FILE