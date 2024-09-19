#!/bin/bash

# Set strict mode to exit on any command failure
set -e

# Global variables
DB_NAME="boston_startup_tracker"
DB_USER="postgres"
BACKUP_DIR="/path/to/backup/directory"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${DATE}.sql"
LOG_FILE="${BACKUP_DIR}/backup_log.txt"

# Function to check prerequisites
check_prerequisites() {
    # Check if pg_dump is installed
    if ! command -v pg_dump &> /dev/null; then
        echo "Error: pg_dump is not installed. Please install PostgreSQL client tools." | tee -a "$LOG_FILE"
        exit 1
    fi

    # Check if backup directory exists, create if not
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "Created backup directory: $BACKUP_DIR" | tee -a "$LOG_FILE"
    fi

    # Check if user has necessary permissions
    if [ ! -w "$BACKUP_DIR" ]; then
        echo "Error: No write permission for backup directory: $BACKUP_DIR" | tee -a "$LOG_FILE"
        exit 1
    fi
}

# Function to perform the backup
perform_backup() {
    echo "Starting database backup..." | tee -a "$LOG_FILE"
    
    # Use pg_dump to create a SQL dump of the database
    pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
    
    # Compress the SQL dump file
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    # Check if backup was successful
    if [ -f "$BACKUP_FILE" ]; then
        echo "Backup completed successfully: $BACKUP_FILE" | tee -a "$LOG_FILE"
    else
        echo "Error: Backup failed" | tee -a "$LOG_FILE"
        exit 1
    fi
}

# Function to clean up old backups
cleanup_old_backups() {
    echo "Cleaning up old backups..." | tee -a "$LOG_FILE"
    
    # Find and delete backup files older than 30 days
    find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime +30 -delete
    
    echo "Old backups cleaned up" | tee -a "$LOG_FILE"
}

# Main script execution
main() {
    echo "Starting database backup process at $(date)" | tee -a "$LOG_FILE"
    
    check_prerequisites
    perform_backup
    cleanup_old_backups
    
    echo "Backup process completed at $(date)" | tee -a "$LOG_FILE"
    echo "Backup file: $BACKUP_FILE" | tee -a "$LOG_FILE"
}

# Error handling
trap 'echo "Error occurred. Exiting..." | tee -a "$LOG_FILE"; exit 1' ERR

# Execute main function
main

# Human tasks (commented)
# TODO: Ensure database connection details are correctly configured
# TODO: Verify the backup directory path is correct and has sufficient space
# TODO: Consider implementing encryption for sensitive data in backups
# TODO: Set up a cron job to run this script regularly
# TODO: Test the restore process to ensure backups are valid
# TODO: Implement off-site backup storage for disaster recovery