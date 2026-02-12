#!/usr/bin/env python3
"""
Test Claude Engineer Integration - Verification script to test Claude Engineer
integration with the multi-agent system.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

def test_claude_engineer_startup():
    """Test Claude Engineer startup sequence"""
    print("🧪 Testing Claude Engineer startup sequence...")
    
    project_root = "/Users/studio/hardcard"
    startup_script = os.path.join(project_root, "scripts", "claude-engineer-startup-sequence.py")
    
    if not os.path.exists(startup_script):
        print("❌ Claude Engineer startup script not found")
        return False
    
    try:
        # Run startup sequence with dry-run or test mode
        result = subprocess.run(
            [sys.executable, startup_script, "--project-root", project_root, "--verbose"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ Claude Engineer startup sequence completed successfully")
            return True
        else:
            print(f"❌ Claude Engineer startup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Claude Engineer startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude Engineer startup: {e}")
        return False

def test_integration_setup():
    """Test Claude Engineer integration setup"""
    print("🧪 Testing Claude Engineer integration setup...")
    
    project_root = "/Users/studio/hardcard"
    integration_script = os.path.join(project_root, "scripts", "claude-engineer-integration.py")
    
    if not os.path.exists(integration_script):
        print("❌ Claude Engineer integration script not found")
        return False
    
    try:
        # Run integration setup
        result = subprocess.run(
            [sys.executable, integration_script, "--project-root", project_root, "--verbose"],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            print("✅ Claude Engineer integration setup completed successfully")
            return True
        else:
            print(f"❌ Claude Engineer integration failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Claude Engineer integration timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Claude Engineer integration: {e}")
        return False

def test_unified_startup():
    """Test unified startup orchestrator with Claude Engineer"""
    print("🧪 Testing unified startup orchestrator with Claude Engineer...")
    
    project_root = "/Users/studio/hardcard"
    orchestrator_script = os.path.join(project_root, "scripts", "unified-startup-orchestrator.py")
    
    if not os.path.exists(orchestrator_script):
        print("❌ Unified startup orchestrator not found")
        return False
    
    try:
        # Run unified startup (this might take a while)
        result = subprocess.run(
            [sys.executable, orchestrator_script, "--project-root", project_root, "--timeout-multiplier", "0.5"],
            capture_output=True,
            text=True,
            timeout=600
        )
        
        if result.returncode == 0:
            print("✅ Unified startup with Claude Engineer completed successfully")
            
            # Check if Claude Engineer system was included
            if "Claude Engineer" in result.stdout:
                print("✅ Claude Engineer was included in unified startup")
                return True
            else:
                print("⚠️ Claude Engineer may not have been properly included")
                return False
        else:
            print(f"❌ Unified startup failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Unified startup timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing unified startup: {e}")
        return False

def check_file_structure():
    """Check if required files and directories exist"""
    print("🧪 Checking Claude Engineer file structure...")
    
    project_root = "/Users/studio/hardcard"
    required_files = [
        "scripts/claude-engineer-startup-sequence.py",
        "scripts/claude-engineer-integration.py",
        "scripts/unified-startup-orchestrator.py"
    ]
    
    required_dirs = [
        ".claude-engineer",
        "logs",
        "monitoring",
        "reports",
        "moex-workspace"
    ]
    
    all_good = True
    
    # Check files
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    # Check directories (create if missing)
    for dir_path in required_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️ {dir_path}/ - Creating...")
            os.makedirs(full_path, exist_ok=True)
    
    return all_good

def test_configuration_files():
    """Test if configuration files can be created and read"""
    print("🧪 Testing Claude Engineer configuration files...")
    
    project_root = "/Users/studio/hardcard"
    claude_engineer_dir = os.path.join(project_root, ".claude-engineer")
    
    # Test config file creation
    test_config = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "integration_test": "claude_engineer_verification"
    }
    
    try:
        config_file = os.path.join(claude_engineer_dir, "test-config.json")
        with open(config_file, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Test reading
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        if loaded_config.get("test") and loaded_config.get("integration_test") == "claude_engineer_verification":
            print("✅ Configuration file operations working")
            
            # Clean up test file
            os.remove(config_file)
            return True
        else:
            print("❌ Configuration file data mismatch")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration files: {e}")
        return False

def main():
    """Main test execution"""
    print("=" * 80)
    print("🤖 CLAUDE ENGINEER INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"🕐 Started at: {datetime.now().isoformat()}")
    print()
    
    tests = [
        ("File Structure Check", check_file_structure),
        ("Configuration Files Test", test_configuration_files),
        ("Claude Engineer Startup Test", test_claude_engineer_startup),
        ("Integration Setup Test", test_integration_setup),
        ("Unified Startup Test", test_unified_startup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print()
    print(f"📈 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Claude Engineer integration is ready.")
        return True
    else:
        print(f"⚠️ {total - passed} test(s) failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)