#!/bin/bash

# Set the project root directory
PROJECT_ROOT=$(pwd)

# Function to check if required dependencies are installed
check_dependencies() {
    echo "Checking dependencies..."
    
    # Check if Python 3.8+ is installed
    if ! command -v python3 &> /dev/null || [[ $(python3 --version 2>&1) < "Python 3.8" ]]; then
        echo "Error: Python 3.8 or higher is required but not installed."
        exit 1
    fi
    
    # Check if Node.js 14+ is installed
    if ! command -v node &> /dev/null || [[ $(node --version 2>&1) < "v14" ]]; then
        echo "Error: Node.js 14 or higher is required but not installed."
        exit 1
    fi
    
    # Check if PostgreSQL 12+ is installed
    if ! command -v psql &> /dev/null || [[ $(psql --version | awk '{print $3}' | cut -d. -f1) -lt 12 ]]; then
        echo "Error: PostgreSQL 12 or higher is required but not installed."
        exit 1
    fi
    
    # Check if Redis is installed
    if ! command -v redis-cli &> /dev/null; then
        echo "Error: Redis is required but not installed."
        exit 1
    fi
    
    echo "All dependencies are installed."
}

# Function to set up Python virtual environment and install dependencies
setup_python_environment() {
    echo "Setting up Python environment..."
    
    # Create a Python virtual environment
    python3 -m venv venv
    
    # Activate the virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies from requirements.txt
    pip install -r requirements.txt
    
    echo "Python environment setup complete."
}

# Function to set up Node.js environment and install dependencies
setup_node_environment() {
    echo "Setting up Node.js environment..."
    
    # Navigate to the frontend directory
    cd "$PROJECT_ROOT/frontend"
    
    # Install Node.js dependencies using npm
    npm install
    
    cd "$PROJECT_ROOT"
    
    echo "Node.js environment setup complete."
}

# Function to set up and configure the PostgreSQL database
setup_database() {
    echo "Setting up database..."
    
    # Create a new PostgreSQL database for the project
    createdb boston_startup_tracker
    
    # Run database migrations
    python manage.py db upgrade
    
    # Seed the database with initial data if needed
    python manage.py seed_db
    
    echo "Database setup complete."
}

# Function to set up environment variables for development
configure_environment_variables() {
    echo "Configuring environment variables..."
    
    # Copy .env.example to .env
    cp .env.example .env
    
    # Generate secret keys for JWT and other secure operations
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    
    # Set database connection string
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://localhost/boston_startup_tracker|" .env
    
    # Set API keys for external services (e.g., Crunchbase, LinkedIn)
    echo "Please manually set the API keys for external services in the .env file."
    
    echo "Environment variables configured."
}

# Function to set up Git hooks for pre-commit checks
setup_git_hooks() {
    echo "Setting up Git hooks..."
    
    # Install pre-commit
    pip install pre-commit
    
    # Set up pre-commit hooks for linting and formatting
    pre-commit install
    
    echo "Git hooks setup complete."
}

# Main script
echo "Welcome to the Boston Startup Tracker development environment setup!"

check_dependencies

setup_python_environment
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up Python environment."
    exit 1
fi

setup_node_environment
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up Node.js environment."
    exit 1
fi

setup_database
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up database."
    exit 1
fi

configure_environment_variables
if [ $? -ne 0 ]; then
    echo "Error: Failed to configure environment variables."
    exit 1
fi

setup_git_hooks
if [ $? -ne 0 ]; then
    echo "Error: Failed to set up Git hooks."
    exit 1
fi

echo "Setup complete! You can now start the development server."
echo "To run the backend: python manage.py run"
echo "To run the frontend: cd frontend && npm start"

# Human tasks (commented out):
# TODO: Review and update the list of dependencies if needed
# TODO: Ensure database creation steps are correct for your PostgreSQL setup
# TODO: Update the script if any new setup steps are added to the project
# TODO: Test the script on a clean environment to ensure it works as expected
# TODO: Add any project-specific configuration steps that may be needed