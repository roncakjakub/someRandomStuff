#!/usr/bin/env python3
"""
Master Test Runner - Systematické testovanie všetkých komponentov
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test results storage
results = {
    "timestamp": datetime.now().isoformat(),
    "tools": {},
    "agents": {},
    "workflow": {},
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
}

def save_results():
    """Save test results to JSON file."""
    results_file = project_root / "tests" / "results" / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file}")

def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {results['summary']['total']}")
    print(f"✅ Passed: {results['summary']['passed']}")
    print(f"❌ Failed: {results['summary']['failed']}")
    print(f"⏭️  Skipped: {results['summary']['skipped']}")
    print("="*60)

def run_tool_tests():
    """Run all tool tests."""
    print("\n" + "="*60)
    print("PHASE 1: TESTING TOOLS")
    print("="*60)
    
    # Import test modules
    try:
        from tests import test_image_tools, test_video_tools, test_utility_tools
        
        # Run image tool tests
        print("\n📸 Testing Image Generation Tools...")
        image_results = test_image_tools.run_all()
        results["tools"]["image"] = image_results
        
        # Run video tool tests
        print("\n🎬 Testing Video Generation Tools...")
        video_results = test_video_tools.run_all()
        results["tools"]["video"] = video_results
        
        # Run utility tool tests
        print("\n🔧 Testing Utility Tools...")
        utility_results = test_utility_tools.run_all()
        results["tools"]["utility"] = utility_results
        
    except ImportError as e:
        print(f"⚠️  Could not import test modules: {e}")
        print("Creating test modules...")
        create_test_modules()

def run_agent_tests():
    """Run all agent tests."""
    print("\n" + "="*60)
    print("PHASE 2: TESTING AGENTS")
    print("="*60)
    
    try:
        from tests import test_agents
        
        agent_results = test_agents.run_all()
        results["agents"] = agent_results
        
    except ImportError as e:
        print(f"⚠️  Could not import agent tests: {e}")

def run_workflow_tests():
    """Run workflow tests."""
    print("\n" + "="*60)
    print("PHASE 3: TESTING WORKFLOW")
    print("="*60)
    
    try:
        from tests import test_workflow
        
        workflow_results = test_workflow.run_all()
        results["workflow"] = workflow_results
        
    except ImportError as e:
        print(f"⚠️  Could not import workflow tests: {e}")

def create_test_modules():
    """Create test module files if they don't exist."""
    print("\n📝 Creating test modules...")
    
    # This will be implemented in next step
    pass

def main():
    """Main test runner."""
    print("="*60)
    print("SOCIAL VIDEO AGENT - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Phase 1: Tools
    run_tool_tests()
    
    # Phase 2: Agents
    # run_agent_tests()  # Uncomment when ready
    
    # Phase 3: Workflow
    # run_workflow_tests()  # Uncomment when ready
    
    # Print summary and save results
    print_summary()
    save_results()
    
    print(f"\n✅ Testing completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        save_results()
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        save_results()
        sys.exit(1)
