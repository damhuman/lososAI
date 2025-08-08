#!/bin/bash

# Unified Test Runner for Seafood Store Project
# Runs all tests: backend (pytest) + frontend (jest)

set -e  # Exit on any error

echo "🧪 Starting Unified Test Suite for Seafood Store"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
BACKEND_RESULT=0
FRONTEND_RESULT=0

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "SUCCESS")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
    esac
}

# Check if Docker Compose is running
check_services() {
    print_status "INFO" "Checking Docker Compose services..."
    if ! docker-compose ps | grep -q "Up"; then
        print_status "WARNING" "Some Docker services are not running"
        print_status "INFO" "Starting Docker services..."
        docker-compose up -d
        sleep 10  # Wait for services to start
    fi
    print_status "SUCCESS" "Docker services are ready"
}

# Run Backend Tests
run_backend_tests() {
    print_status "INFO" "Running Backend Tests (pytest)..."
    echo
    
    if docker-compose exec -T backend pytest tests/ -v --tb=short; then
        print_status "SUCCESS" "Backend tests completed successfully"
        BACKEND_RESULT=0
    else
        print_status "ERROR" "Backend tests failed"
        BACKEND_RESULT=1
    fi
    echo
}

# Run Frontend Tests
run_frontend_tests() {
    print_status "INFO" "Running Frontend Tests (Jest)..."
    echo
    
    cd frontend/webapp
    if npm test -- --watchAll=false; then
        print_status "SUCCESS" "Frontend tests completed successfully"
        FRONTEND_RESULT=0
    else
        print_status "ERROR" "Frontend tests failed"
        FRONTEND_RESULT=1
    fi
    cd ../..
    echo
}

# Run Backend Tests with Coverage
run_backend_tests_coverage() {
    print_status "INFO" "Running Backend Tests with Coverage..."
    echo
    
    docker-compose exec -T backend pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
    print_status "INFO" "Coverage report generated in backend/htmlcov/"
    echo
}

# Run Frontend Tests with Coverage
run_frontend_tests_coverage() {
    print_status "INFO" "Running Frontend Tests with Coverage..."
    echo
    
    cd frontend/webapp
    npm run test:coverage -- --watchAll=false
    print_status "INFO" "Coverage report generated in frontend/webapp/coverage/"
    cd ../..
    echo
}

# Parse command line arguments
COVERAGE=false
BACKEND_ONLY=false
FRONTEND_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --coverage)
            COVERAGE=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --coverage       Run tests with coverage reports"
            echo "  --backend-only   Run only backend tests"
            echo "  --frontend-only  Run only frontend tests"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

# Main execution
main() {
    local start_time=$(date +%s)
    
    # Check services unless frontend-only
    if [[ $FRONTEND_ONLY != true ]]; then
        check_services
    fi
    
    # Run tests based on options
    if [[ $BACKEND_ONLY == true ]]; then
        if [[ $COVERAGE == true ]]; then
            run_backend_tests_coverage
        else
            run_backend_tests
        fi
    elif [[ $FRONTEND_ONLY == true ]]; then
        if [[ $COVERAGE == true ]]; then
            run_frontend_tests_coverage
        else
            run_frontend_tests
        fi
    else
        # Run all tests
        if [[ $COVERAGE == true ]]; then
            run_backend_tests_coverage
            run_frontend_tests_coverage
        else
            run_backend_tests
            run_frontend_tests
        fi
    fi
    
    # Calculate duration
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Final results
    echo "=================================================="
    print_status "INFO" "Test Summary"
    echo
    
    if [[ $BACKEND_ONLY != true && $FRONTEND_ONLY != true ]]; then
        # Full test run
        if [[ $BACKEND_RESULT -eq 0 ]]; then
            print_status "SUCCESS" "Backend Tests: PASSED"
        else
            print_status "ERROR" "Backend Tests: FAILED"
        fi
        
        if [[ $FRONTEND_RESULT -eq 0 ]]; then
            print_status "SUCCESS" "Frontend Tests: PASSED"
        else
            print_status "ERROR" "Frontend Tests: FAILED"
        fi
        
        if [[ $BACKEND_RESULT -eq 0 && $FRONTEND_RESULT -eq 0 ]]; then
            print_status "SUCCESS" "ALL TESTS PASSED! 🎉"
            echo
            print_status "INFO" "Total duration: ${duration}s"
            exit 0
        else
            print_status "ERROR" "SOME TESTS FAILED! 💥"
            echo
            print_status "INFO" "Total duration: ${duration}s"
            exit 1
        fi
    elif [[ $BACKEND_ONLY == true ]]; then
        if [[ $BACKEND_RESULT -eq 0 ]]; then
            print_status "SUCCESS" "BACKEND TESTS PASSED! 🎉"
        else
            print_status "ERROR" "BACKEND TESTS FAILED! 💥"
        fi
        exit $BACKEND_RESULT
    else
        # Frontend only
        if [[ $FRONTEND_RESULT -eq 0 ]]; then
            print_status "SUCCESS" "FRONTEND TESTS PASSED! 🎉"
        else
            print_status "ERROR" "FRONTEND TESTS FAILED! 💥"
        fi
        exit $FRONTEND_RESULT
    fi
}

# Run main function
main