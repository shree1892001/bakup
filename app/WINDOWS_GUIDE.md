# Running pg_cron on Windows

While the project is designed for Docker/Linux, you can run the services directly on Windows.

## Prerequisites

1.  **Python 3**: Ensure Python is installed (`python --version`).
2.  **PostgreSQL Tools**: 
    - Install PostgreSQL for Windows.
    - Add the `bin` folder (e.g., `C:\Program Files\PostgreSQL\16\bin`) to your **System PATH**.
    - Verify with `pg_dump --version`.
3.  **Rsync** (Optional): 
    - The scripts now include a native Python fallback if `rsync` is not found.
    - Having `rsync` is still recommended for performance with very large archives, but not required for basic operation.

## Setup

1.  **Environment Variables**:
    - Set the password in your terminal:
      ```powershell
      $env:PGPASSWORD="postgres"
      ```
2.  **Configuration**:
    - Update `app\src\etc\config.properties` with your database details.

## Execution Commands

Navigate to `app\src` and run:

### 1. Full Backup
```powershell
python services\backup_service.py
```

### 2. Restore Database
```powershell
python services\restore_service.py
```

## Logs
Check `app\src\log\app.log` for execution details.
