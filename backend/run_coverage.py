#!/usr/bin/env python3
"""Generate test coverage report."""
import subprocess
import sys
import os

def run_coverage():
    """Run test coverage analysis."""
    print("📊 Generating test coverage report...")
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            "python", "-m", "pytest", 
            "tests/", 
            "--cov=app",
            "--cov-report=term",
            "--cov-report=html:htmlcov",
            "--tb=short",
            "-v"
        ], capture_output=True, text=True, cwd="/app")
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Coverage report generated successfully!")
            if os.path.exists("/app/htmlcov/index.html"):
                print("📊 HTML coverage report available at: htmlcov/index.html")
        else:
            print("⚠️  Tests completed with issues but coverage generated")
            
    except Exception as e:
        print(f"❌ Coverage generation failed: {e}")

if __name__ == "__main__":
    run_coverage()