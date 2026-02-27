# PostgreSQL Configuration Requirements

To support the incremental backup feature, PostgreSQL must be configured to archive its Write-Ahead Log (WAL) files.

## How to find your configuration file on Windows

The `postgresql.conf` file is usually located in the `data` directory of your installation.

### 1. Common Default Paths:
- `C:\Program Files\PostgreSQL\16\data\postgresql.conf`
- `C:\Program Files\PostgreSQL\15\data\postgresql.conf`

### 2. Find it via SQL (Most Reliable):
Run this command in a query tool (like pgAdmin or `psql`):
```sql
SHOW config_file;
```
This will return the exact absolute path to your configuration file.

## Required Settings in `postgresql.conf`

The following changes are mandatory for the source database:

1.  **wal_level**: Must be set to `replica` or `logical`.
    ```conf
    wal_level = replica
    ```
2.  **archive_mode**: Must be enabled.
    ```conf
    archive_mode = on
    ```
3.  **archive_command**: This is the command that copies WAL files to the `wal.archive_src` directory defined in your `config.properties`.
    
    **On Windows:**
    ```conf
    archive_command = 'copy "%p" "C:\\path\\to\\archive\\%f"'
    ```
    *(Replace with your actual source path defined in config.properties).*

    **On Linux/Docker:**
    ```conf
    archive_command = 'test ! -f /pg_wal_archive/%f && cp %p /pg_wal_archive/%f'
    ```

## Restart Required
Changing `wal_level` and `archive_mode` requires a **restart** of the PostgreSQL service.

## How to Test if Archiving is Working

If your incremental backup script says it copied **0 files**, it likely means no WAL segments have been closed and archived yet. 

You can force a WAL switch to test your configuration immediately:

1.  Open your SQL tool (pgAdmin/psql).
2.  Run this command:
    ```sql
    SELECT pg_switch_wal();
    ```
3.  Check your `wal.archive_src` folder. A new file (24 characters long, e.g., `00000001000000...`) should appear.
4.  Run the `incremental_service.py` script again. It should now find and copy that file.
