#!/bin/bash
# Test runner script for the server
# Usage: ./scripts/test.sh [command]

cd "$(dirname "$0")/.."

case "$1" in
  "all")
    echo "Running all tests..."
    npm test
    ;;
  "coverage")
    echo "Running tests with coverage..."
    npm test -- --coverage
    ;;
  "watch")
    echo "Running tests in watch mode..."
    npm test -- --watch
    ;;
  "auth")
    echo "Running auth tests only..."
    npm test auth.test.ts
    ;;
  "app")
    echo "Running app tests only..."
    npm test app.test.ts
    ;;
  "verbose")
    echo "Running tests with verbose output..."
    npm test -- --verbose
    ;;
  "open-coverage")
    echo "Opening coverage report..."
    if [ -f "coverage/lcov-report/index.html" ]; then
      xdg-open coverage/lcov-report/index.html 2>/dev/null || \
      open coverage/lcov-report/index.html 2>/dev/null || \
      echo "Coverage report not found. Run: npm test -- --coverage"
    else
      echo "Coverage report not found. Run: npm test -- --coverage"
    fi
    ;;
  *)
    echo "Test Runner for Server"
    echo ""
    echo "Usage: ./scripts/test.sh [command]"
    echo ""
    echo "Commands:"
    echo "  all            - Run all tests"
    echo "  coverage       - Run tests with coverage report"
    echo "  watch          - Run tests in watch mode"
    echo "  auth           - Run auth tests only"
    echo "  app            - Run app tests only"
    echo "  verbose        - Run tests with detailed output"
    echo "  open-coverage  - Open coverage report in browser"
    echo ""
    echo "Examples:"
    echo "  ./scripts/test.sh all"
    echo "  ./scripts/test.sh coverage"
    echo "  npm test"
    ;;
esac
