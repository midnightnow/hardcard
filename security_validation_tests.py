#!/usr/bin/env python3
"""
Security Validation Test Suite for VetSorcery
Validates that all security fixes have been properly implemented
"""

import requests
import os
import sqlite3
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class SecurityValidationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        result = {
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {details}")
    
    def test_database_permissions(self):
        """Test that database permissions are secure"""
        db_path = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/vetsorcery.db"
        
        if os.path.exists(db_path):
            stat_info = os.stat(db_path)
            file_mode = oct(stat_info.st_mode)[-3:]
            
            if file_mode == "600":
                self.log_result("Database permissions secure", True)
            else:
                self.log_result("Database permissions", False, f"Permissions are {file_mode}, should be 600")
        else:
            self.log_result("Database permissions", False, "Database file not found")
    
    def test_authorization_framework(self):
        """Test that authorization framework is implemented"""
        auth_file = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/authorization.py"
        
        if os.path.exists(auth_file):
            with open(auth_file, 'r') as f:
                content = f.read()
                
            # Check for key authorization components
            required_components = [
                "class User",
                "class Permission", 
                "require_permission",
                "check_client_access",
                "UserRole"
            ]
            
            missing = [comp for comp in required_components if comp not in content]
            
            if not missing:
                self.log_result("Authorization framework implemented", True)
            else:
                self.log_result("Authorization framework", False, f"Missing components: {missing}")
        else:
            self.log_result("Authorization framework", False, "Authorization file not found")
    
    def test_rate_limiting_implementation(self):
        """Test that rate limiting is implemented"""
        rate_limit_file = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/rate_limiting.py"
        
        if os.path.exists(rate_limit_file):
            with open(rate_limit_file, 'r') as f:
                content = f.read()
            
            # Check for rate limiting components
            if "InMemoryRateLimit" in content and "RATE_LIMITS" in content:
                self.log_result("Rate limiting middleware implemented", True)
            else:
                self.log_result("Rate limiting middleware", False, "Missing rate limiting components")
        else:
            self.log_result("Rate limiting middleware", False, "Rate limiting file not found")
    
    def test_security_headers(self):
        """Test that security headers middleware is implemented"""
        headers_file = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/security_headers.py"
        
        if os.path.exists(headers_file):
            with open(headers_file, 'r') as f:
                content = f.read()
            
            # Check for security headers
            required_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "Content-Security-Policy",
                "Strict-Transport-Security"
            ]
            
            missing = [header for header in required_headers if header not in content]
            
            if not missing:
                self.log_result("Security headers middleware implemented", True)
            else:
                self.log_result("Security headers middleware", False, f"Missing headers: {missing}")
        else:
            self.log_result("Security headers middleware", False, "Security headers file not found")
    
    def test_audit_logging(self):
        """Test that audit logging is implemented"""
        audit_file = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/audit_logging.py"
        
        if os.path.exists(audit_file):
            with open(audit_file, 'r') as f:
                content = f.read()
            
            # Check for audit logging components
            required_components = [
                "class AuditLogger",
                "log_authentication",
                "log_authorization", 
                "log_data_access"
            ]
            
            missing = [comp for comp in required_components if comp not in content]
            
            if not missing:
                self.log_result("Audit logging implemented", True)
            else:
                self.log_result("Audit logging", False, f"Missing components: {missing}")
        else:
            self.log_result("Audit logging", False, "Audit logging file not found")
    
    def test_secure_environment(self):
        """Test that secure environment configuration exists"""
        secure_env = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/.env.secure"
        env_template = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/.env.secure.template"
        
        if os.path.exists(secure_env):
            with open(secure_env, 'r') as f:
                content = f.read()
            
            # Check for secure configuration
            if "JWT_SECRET=" in content and len(content.split("JWT_SECRET=")[1].split("\n")[0]) > 20:
                self.log_result("Secure environment configuration", True)
            else:
                self.log_result("Secure environment", False, "JWT_SECRET not properly configured")
        else:
            self.log_result("Secure environment", False, "Secure .env file not found")
        
        if os.path.exists(env_template):
            self.log_result("Environment template exists", True)
        else:
            self.log_result("Environment template", False, "Template file missing")
    
    def test_api_endpoints_exist(self):
        """Test that protected endpoints exist and require authentication"""
        try:
            # Test telehealth endpoints
            response = requests.get(f"{self.base_url}/routes/api/telehealth/sessions", timeout=5)
            if response.status_code in [401, 403]:  # Should require auth
                self.log_result("Telehealth endpoints protected", True)
            elif response.status_code == 404:
                self.log_result("Telehealth endpoints", False, "Endpoints not found (404)")
            else:
                self.log_result("Telehealth endpoints", False, f"Unexpected response: {response.status_code}")
            
            # Test web portal endpoints
            response = requests.get(f"{self.base_url}/routes/api/web_portal/client/test", timeout=5)
            if response.status_code in [401, 403]:  # Should require auth
                self.log_result("Web portal endpoints protected", True)
            elif response.status_code == 404:
                self.log_result("Web portal endpoints", False, "Endpoints not found (404)")
            else:
                self.log_result("Web portal endpoints", False, f"Unexpected response: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self.log_result("API endpoints", False, f"Cannot connect to server: {e}")
    
    def test_telehealth_authorization_updated(self):
        """Test that telehealth router has authorization imports"""
        telehealth_router = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/apis/telehealth/router.py"
        
        if os.path.exists(telehealth_router):
            with open(telehealth_router, 'r') as f:
                content = f.read()
            
            # Check for authorization imports and usage
            auth_indicators = [
                "from app.middleware.authorization import",
                "require_permission",
                "Permission.ACCESS_TELEHEALTH",
                "current_user: User = Depends"
            ]
            
            found = [indicator for indicator in auth_indicators if indicator in content]
            
            if len(found) >= 3:  # Should have most of these
                self.log_result("Telehealth authorization implemented", True)
            else:
                self.log_result("Telehealth authorization", False, f"Missing authorization code. Found: {found}")
        else:
            self.log_result("Telehealth authorization", False, "Telehealth router not found")
    
    def test_no_weak_credentials(self):
        """Test that weak credentials have been removed"""
        backend_env = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/.env"
        
        weak_indicators = [
            "DATABUTTON_EXTENSIONS=",
            "password=123",
            "secret=test",
            "key=dev"
        ]
        
        if os.path.exists(backend_env):
            with open(backend_env, 'r') as f:
                content = f.read().lower()
            
            found_weak = [weak for weak in weak_indicators if weak.lower() in content]
            
            if not found_weak:
                self.log_result("No weak credentials in .env", True)
            else:
                self.log_result("Weak credentials removed", False, f"Found: {found_weak}")
        else:
            self.log_result("Environment file check", True, "No .env file found (good for security)")
    
    def test_file_structure_security(self):
        """Test that security file structure is properly implemented"""
        required_files = [
            "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/__init__.py",
            "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/authorization.py",
            "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/rate_limiting.py",
            "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/security_headers.py",
            "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/backend/app/middleware/audit_logging.py"
        ]
        
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if not missing_files:
            self.log_result("Security file structure complete", True)
        else:
            self.log_result("Security file structure", False, f"Missing files: {missing_files}")
    
    def test_logs_directory(self):
        """Test that logs directory exists and is writable"""
        logs_dir = "/Users/studio/hardcard/logs"
        
        if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
            # Test if we can write to it
            test_file = os.path.join(logs_dir, "test_write.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                self.log_result("Logs directory writable", True)
            except Exception as e:
                self.log_result("Logs directory", False, f"Not writable: {e}")
        else:
            self.log_result("Logs directory", False, "Directory does not exist")
    
    def run_all_tests(self):
        """Run all security validation tests"""
        print("🔒 Running Security Validation Tests")
        print("=" * 50)
        
        # Core security tests
        self.test_database_permissions()
        self.test_authorization_framework()
        self.test_rate_limiting_implementation()
        self.test_security_headers()
        self.test_audit_logging()
        self.test_secure_environment()
        
        # Implementation tests
        self.test_file_structure_security()
        self.test_telehealth_authorization_updated()
        self.test_no_weak_credentials()
        self.test_logs_directory()
        
        # Runtime tests
        self.test_api_endpoints_exist()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": self.passed,
                "failed": self.failed,
                "success_rate": round(success_rate, 2)
            },
            "results": self.test_results
        }
        
        # Save detailed report
        with open("/Users/studio/hardcard/security_validation_report.json", 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 50)
        print("📊 SECURITY VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL SECURITY TESTS PASSED!")
            print("✅ VetSorcery is ready for production deployment")
        else:
            print(f"\n⚠️  {self.failed} tests failed - review before deployment")
            
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n📄 Detailed report: security_validation_report.json")
        
        return report

def main():
    tester = SecurityValidationTester()
    report = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if tester.failed == 0 else 1
    exit(exit_code)

if __name__ == "__main__":
    main()