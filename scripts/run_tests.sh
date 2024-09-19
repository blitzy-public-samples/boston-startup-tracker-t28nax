#!/bin/bash

# Set the project root directory
PROJECT_ROOT=$(pwd)

# Function to run Python backend tests using pytest
run_backend_tests() {
    echo "Running backend tests..."
    
    # Activate the Python virtual environment
    source ${PROJECT_ROOT}/venv/bin/activate
    
    # Navigate to the backend directory
    cd ${PROJECT_ROOT}/backend
    
    # Run pytest with coverage reporting
    pytest --cov=. --cov-report=term-missing
    
    # Display test coverage report
    coverage report
    
    # Deactivate the virtual environment
    deactivate
}

# Function to run JavaScript frontend tests using Jest
run_frontend_tests() {
    echo "Running frontend tests..."
    
    # Navigate to the frontend directory
    cd ${PROJECT_ROOT}/frontend
    
    # Run npm test command
    npm test
    
    # Display test results and coverage report
    # (Jest usually handles this automatically)
}

# Function to run integration tests
run_integration_tests() {
    echo "Running integration tests..."
    
    # Set up test database if needed
    # TODO: Implement database setup for integration tests
    
    # Run integration test suite
    # TODO: Implement integration test runner
    
    # Tear down test database
    # TODO: Implement database teardown after integration tests
}

# Function to run end-to-end tests using Cypress
run_e2e_tests() {
    echo "Running end-to-end tests..."
    
    # Start the backend server in test mode
    cd ${PROJECT_ROOT}/backend
    python manage.py runserver --settings=config.settings.test &
    BACKEND_PID=$!
    
    # Start the frontend development server
    cd ${PROJECT_ROOT}/frontend
    npm run start &
    FRONTEND_PID=$!
    
    # Wait for servers to start
    sleep 10
    
    # Run Cypress tests
    npm run cypress:run
    
    # Shut down servers after tests complete
    kill $BACKEND_PID
    kill $FRONTEND_PID
}

# Main script
main() {
    # Parse command line arguments for specific test suites to run
    RUN_ALL=true
    RUN_BACKEND=false
    RUN_FRONTEND=false
    RUN_INTEGRATION=false
    RUN_E2E=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend) RUN_BACKEND=true; RUN_ALL=false ;;
            --frontend) RUN_FRONTEND=true; RUN_ALL=false ;;
            --integration) RUN_INTEGRATION=true; RUN_ALL=false ;;
            --e2e) RUN_E2E=true; RUN_ALL=false ;;
            *) echo "Unknown option: $1"; exit 1 ;;
        esac
        shift
    done

    # Run test suites based on arguments or run all if no specific suite is specified
    if [ "$RUN_ALL" = true ] || [ "$RUN_BACKEND" = true ]; then
        run_backend_tests
        if [ $? -ne 0 ]; then
            echo "Backend tests failed"
            exit 1
        fi
    fi

    if [ "$RUN_ALL" = true ] || [ "$RUN_FRONTEND" = true ]; then
        run_frontend_tests
        if [ $? -ne 0 ]; then
            echo "Frontend tests failed"
            exit 1
        fi
    fi

    if [ "$RUN_ALL" = true ] || [ "$RUN_INTEGRATION" = true ]; then
        run_integration_tests
        if [ $? -ne 0 ]; then
            echo "Integration tests failed"
            exit 1
        fi
    fi

    if [ "$RUN_ALL" = true ] || [ "$RUN_E2E" = true ]; then
        run_e2e_tests
        if [ $? -ne 0 ]; then
            echo "End-to-end tests failed"
            exit 1
        fi
    fi

    echo "All requested test suites completed successfully"
}

# Run the main script
main "$@"

# Human tasks:
# TODO: Ensure all necessary test dependencies are installed
# TODO: Update the script if new test suites are added to the project
# TODO: Configure CI/CD pipeline to use this script for running tests
# TODO: Optimize test run time by parallelizing test suites if possible
# TODO: Implement test result caching to speed up subsequent test runs