#!/bin/bash

# Set strict mode and error handling
set -e
trap 'echo "Error occurred. Exiting."; exit 1' ERR

# Global variables
DEPLOY_DIR="/path/to/production/deploy/directory"
BACKUP_DIR="/path/to/backup/directory"
GIT_REPO="https://github.com/your-repo/boston-startup-tracker.git"
BRANCH="main"
LOG_FILE="/var/log/boston-startup-tracker-deployment.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check prerequisites
check_prerequisites() {
    log_message "Checking prerequisites..."
    
    # Check if running with sudo privileges
    if [ "$(id -u)" != "0" ]; then
        log_message "This script must be run with sudo privileges."
        exit 1
    fi
    
    # Verify required tools are installed
    for tool in git docker docker-compose; do
        if ! command -v $tool &> /dev/null; then
            log_message "$tool is not installed. Please install it and try again."
            exit 1
        fi
    done
    
    # Check if production environment variables are set
    if [ -z "$PRODUCTION_DB_PASSWORD" ] || [ -z "$PRODUCTION_SECRET_KEY" ]; then
        log_message "Production environment variables are not set. Please set them and try again."
        exit 1
    fi
    
    log_message "Prerequisites check completed successfully."
}

# Function to backup current version
backup_current_version() {
    log_message "Backing up current version..."
    
    # Stop running containers
    docker-compose -f $DEPLOY_DIR/docker-compose.yml down || true
    
    # Create a timestamped backup directory
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$BACKUP_TIMESTAMP"
    mkdir -p $BACKUP_PATH
    
    # Copy current deployment to backup directory
    cp -R $DEPLOY_DIR/* $BACKUP_PATH/
    
    # Backup the production database
    docker exec boston_startup_tracker_db pg_dump -U postgres boston_startup_tracker > $BACKUP_PATH/database_backup.sql
    
    log_message "Backup completed successfully."
}

# Function to fetch latest code
fetch_latest_code() {
    log_message "Fetching latest code..."
    
    if [ -d "$DEPLOY_DIR/.git" ]; then
        # If deploy directory exists, pull latest changes
        cd $DEPLOY_DIR
        git fetch origin
        git reset --hard origin/$BRANCH
    else
        # If deploy directory doesn't exist, clone the repository
        git clone $GIT_REPO $DEPLOY_DIR
        cd $DEPLOY_DIR
    fi
    
    # Checkout the specified branch
    git checkout $BRANCH
    
    log_message "Latest code fetched successfully."
}

# Function to build and deploy
build_and_deploy() {
    log_message "Building and deploying..."
    
    # Build Docker images
    docker-compose -f $DEPLOY_DIR/docker-compose.yml build
    
    # Run database migrations
    docker-compose -f $DEPLOY_DIR/docker-compose.yml run --rm web python manage.py migrate
    
    # Start new containers
    docker-compose -f $DEPLOY_DIR/docker-compose.yml up -d
    
    log_message "Build and deploy completed successfully."
}

# Function to perform post-deploy checks
post_deploy_checks() {
    log_message "Performing post-deploy checks..."
    
    # Check if all containers are running
    if [ "$(docker-compose -f $DEPLOY_DIR/docker-compose.yml ps --services --filter "status=running" | wc -l)" -ne "$(docker-compose -f $DEPLOY_DIR/docker-compose.yml config --services | wc -l)" ]; then
        log_message "Not all containers are running. Deployment failed."
        return 1
    fi
    
    # Perform health checks on the application
    if ! curl -f http://localhost:8000/health-check; then
        log_message "Health check failed. Deployment failed."
        return 1
    fi
    
    # Run a subset of critical tests
    if ! docker-compose -f $DEPLOY_DIR/docker-compose.yml run --rm web python manage.py test --tag=critical; then
        log_message "Critical tests failed. Deployment failed."
        return 1
    fi
    
    log_message "Post-deploy checks completed successfully."
}

# Function to rollback
rollback() {
    log_message "Rolling back to previous version..."
    
    # Stop and remove new containers
    docker-compose -f $DEPLOY_DIR/docker-compose.yml down
    
    # Restore from the latest backup
    LATEST_BACKUP=$(ls -td $BACKUP_DIR/backup_* | head -1)
    rm -rf $DEPLOY_DIR/*
    cp -R $LATEST_BACKUP/* $DEPLOY_DIR/
    
    # Start containers from the backup
    docker-compose -f $DEPLOY_DIR/docker-compose.yml up -d
    
    log_message "Rollback completed successfully."
}

# Main script
log_message "Starting deployment of Boston Startup Tracker..."

check_prerequisites

backup_current_version

fetch_latest_code

build_and_deploy

if ! post_deploy_checks; then
    log_message "Deployment failed. Initiating rollback..."
    rollback
    log_message "Deployment failed and rolled back to previous version."
    exit 1
fi

log_message "Deployment completed successfully."

# Human tasks (commented)
# TODO: Review and update environment-specific configurations
# TODO: Ensure all necessary secrets and API keys are securely managed
# TODO: Test the deployment script in a staging environment before using in production
# TODO: Set up monitoring and alerting for the production deployment
# TODO: Document the rollback procedure for manual intervention if needed
# TODO: Regularly review and update the deployment script as the project evolves