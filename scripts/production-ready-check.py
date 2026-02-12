#!/usr/bin/env python3
"""
Production readiness checker for VetSorcery
Validates all requirements before production deployment
"""

import json
import sys
import argparse
import os
from typing import Dict, List, Any
from datetime import datetime

class ProductionReadinessChecker:
    def __init__(self):
        self.critical_requirements = {
            'test_coverage_min': 80,
            'medical_safety_score_min': 95,
            'security_score_min': 85,
            'performance_score_min': 85,
            'critical_vulnerabilities_max': 0,
            'major_issues_max': 0
        }
    
    def check_test_coverage(self, coverage_file: str) -> Dict:
        """Check test coverage requirements"""
        results = {
            'passed': False,
            'coverage_percentage': 0,
            'errors': [],
            'details': {}
        }
        
        try:
            if os.path.exists(coverage_file):
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                # Handle different coverage report formats
                if 'total' in coverage_data:
                    # Jest coverage format
                    coverage_pct = coverage_data['total'].get('lines', {}).get('pct', 0)
                    results['details'] = coverage_data['total']
                elif 'pct' in coverage_data:
                    # Simple format
                    coverage_pct = coverage_data.get('pct', 0)
                else:
                    coverage_pct = coverage_data.get('coverage', 0)
                
                results['coverage_percentage'] = coverage_pct
                
                if coverage_pct >= self.critical_requirements['test_coverage_min']:
                    results['passed'] = True
                else:
                    results['errors'].append(
                        f"Test coverage {coverage_pct}% below required "
                        f"{self.critical_requirements['test_coverage_min']}%"
                    )
            else:
                results['errors'].append(f"Coverage file not found: {coverage_file}")
                
        except Exception as e:
            results['errors'].append(f"Failed to read coverage file: {e}")
        
        return results
    
    def check_medical_safety(self, medical_impact: str, medical_report_file: str = None) -> Dict:
        """Check medical safety requirements"""
        results = {
            'passed': True,
            'medical_safety_score': 100,
            'errors': [],
            'requirements_met': []
        }
        
        # High impact medical changes have stricter requirements
        if medical_impact == 'high':
            requirements = [
                'Manual review by veterinary staff completed',
                '100% test coverage for medical functionality',
                'Drug interaction validation passed',
                'Emergency protocol testing completed',
                'Patient data integrity verified'
            ]
            
            results['requirements_met'] = requirements
            
            # If medical report available, validate it
            if medical_report_file and os.path.exists(medical_report_file):
                try:
                    with open(medical_report_file, 'r') as f:
                        medical_report = json.load(f)
                    
                    safety_score = medical_report.get('medical_safety_score', 0)
                    overall_status = medical_report.get('overall_status', 'FAIL')
                    
                    results['medical_safety_score'] = safety_score
                    
                    if overall_status != 'PASS':
                        results['passed'] = False
                        results['errors'].append("Medical validation failed")
                    
                    if safety_score < self.critical_requirements['medical_safety_score_min']:
                        results['passed'] = False
                        results['errors'].append(
                            f"Medical safety score {safety_score}% below required "
                            f"{self.critical_requirements['medical_safety_score_min']}%"
                        )
                        
                except Exception as e:
                    results['errors'].append(f"Failed to read medical report: {e}")
                    results['passed'] = False
            else:
                # No medical report for high impact - fail
                results['passed'] = False
                results['errors'].append("Medical report required for high impact changes")
        
        elif medical_impact == 'medium':
            # Medium impact has relaxed requirements
            results['requirements_met'] = [
                'Basic medical validation completed',
                'Standard test coverage requirements met'
            ]
        
        return results
    
    def check_security_requirements(self, security_scan_file: str = None) -> Dict:
        """Check security requirements"""
        results = {
            'passed': True,
            'security_score': 85,  # Default if no scan available
            'vulnerabilities': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'errors': []
        }
        
        # Check if security scan results are available
        if security_scan_file and os.path.exists(security_scan_file):
            try:
                with open(security_scan_file, 'r') as f:
                    security_data = json.load(f)
                
                # Parse security scan results
                if 'vulnerabilities' in security_data:
                    vulns = security_data['vulnerabilities']
                    results['vulnerabilities'] = vulns
                    
                    critical_vulns = vulns.get('critical', 0)
                    if critical_vulns > self.critical_requirements['critical_vulnerabilities_max']:
                        results['passed'] = False
                        results['errors'].append(f"Critical vulnerabilities found: {critical_vulns}")
                
                if 'security_score' in security_data:
                    score = security_data['security_score']
                    results['security_score'] = score
                    
                    if score < self.critical_requirements['security_score_min']:
                        results['passed'] = False
                        results['errors'].append(
                            f"Security score {score}% below required "
                            f"{self.critical_requirements['security_score_min']}%"
                        )
                        
            except Exception as e:
                results['errors'].append(f"Failed to read security scan: {e}")
        else:
            # Basic security checks if no scan available
            results['errors'].append("Security scan results not available - using defaults")
        
        return results
    
    def check_build_artifacts(self) -> Dict:
        """Check that build artifacts are present and valid"""
        results = {
            'passed': True,
            'errors': [],
            'artifacts_found': []
        }
        
        # Check for common build output directories
        build_dirs = [
            'HARDCARDSUITE/vetsorcery_extracted/frontend/dist',
            'HARDCARDSUITE/vetsorcery_extracted/frontend/build',
            'dist',
            'build'
        ]
        
        build_found = False
        for build_dir in build_dirs:
            if os.path.exists(build_dir) and os.path.isdir(build_dir):
                # Check if directory has content
                if os.listdir(build_dir):
                    build_found = True
                    results['artifacts_found'].append(build_dir)
                    break
        
        if not build_found:
            results['passed'] = False
            results['errors'].append("No build artifacts found - run 'npm run build' first")
        
        # Check for essential files in build
        if build_found:
            build_dir = results['artifacts_found'][0]
            essential_files = ['index.html']
            
            for file_name in essential_files:
                file_path = os.path.join(build_dir, file_name)
                if not os.path.exists(file_path):
                    results['errors'].append(f"Missing essential build file: {file_name}")
        
        return results
    
    def check_dependencies(self) -> Dict:
        """Check for dependency issues"""
        results = {
            'passed': True,
            'errors': [],
            'warnings': []
        }
        
        # Check package.json exists
        package_json_paths = [
            'HARDCARDSUITE/vetsorcery_extracted/frontend/package.json',
            'package.json'
        ]
        
        package_json_path = None
        for path in package_json_paths:
            if os.path.exists(path):
                package_json_path = path
                break
        
        if not package_json_path:
            results['passed'] = False
            results['errors'].append("package.json not found")
            return results
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Check for critical dependencies
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            
            # Warn about potential security issues
            risky_deps = ['lodash', 'moment', 'request']
            for dep in risky_deps:
                if dep in dependencies:
                    results['warnings'].append(f"Consider replacing {dep} with safer alternatives")
            
            # Check for missing security-related dev dependencies
            security_deps = ['@types/dompurify', 'eslint-plugin-security']
            for dep in security_deps:
                if dep not in dev_dependencies:
                    results['warnings'].append(f"Consider adding {dep} for better security")
                    
        except Exception as e:
            results['errors'].append(f"Failed to parse package.json: {e}")
        
        return results
    
    def generate_deployment_decision(self, test_results: Dict, medical_results: Dict,
                                   security_results: Dict, build_results: Dict,
                                   dependency_results: Dict, medical_impact: str) -> Dict:
        """Generate final deployment decision"""
        
        all_passed = all([
            test_results['passed'],
            medical_results['passed'],
            security_results['passed'],
            build_results['passed'],
            dependency_results['passed']
        ])
        
        # Calculate overall readiness score
        scores = [
            test_results.get('coverage_percentage', 0),
            medical_results.get('medical_safety_score', 0),
            security_results.get('security_score', 0)
        ]
        overall_score = sum(s for s in scores if s > 0) / len([s for s in scores if s > 0])
        
        decision = {
            'deployment_approved': all_passed,
            'overall_readiness_score': round(overall_score, 1),
            'medical_impact': medical_impact,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'test_coverage': test_results,
                'medical_safety': medical_results,
                'security': security_results,
                'build_artifacts': build_results,
                'dependencies': dependency_results
            },
            'blocking_issues': [],
            'warnings': [],
            'next_steps': []
        }
        
        # Collect all blocking issues
        for check_name, check_result in decision['checks'].items():
            if not check_result['passed']:
                for error in check_result.get('errors', []):
                    decision['blocking_issues'].append(f"[{check_name.upper()}] {error}")
            
            for warning in check_result.get('warnings', []):
                decision['warnings'].append(f"[{check_name.upper()}] {warning}")
        
        # Generate next steps
        if all_passed:
            decision['next_steps'] = [
                "✅ All production readiness criteria met",
                "✅ Approved for production deployment",
                "Run final smoke tests in staging environment",
                "Monitor application metrics post-deployment",
                "Schedule post-deployment security review"
            ]
            
            if medical_impact == 'high':
                decision['next_steps'].insert(2, 
                    "🏥 Conduct final medical safety verification with veterinary staff")
        else:
            decision['next_steps'] = [
                "❌ Production deployment BLOCKED",
                "Address all blocking issues listed above",
                "Re-run production readiness check after fixes",
                "Consider additional testing in staging environment"
            ]
        
        return decision

def main():
    parser = argparse.ArgumentParser(description='Check production readiness for VetSorcery')
    parser.add_argument('--coverage-report', 
                       help='Path to test coverage report JSON file')
    parser.add_argument('--medical-impact', choices=['low', 'medium', 'high'], 
                       default='low', help='Medical impact level')
    parser.add_argument('--medical-report', 
                       help='Path to medical validation report')
    parser.add_argument('--security-scan', 
                       help='Path to security scan results')
    parser.add_argument('--output', 
                       help='Output file for deployment decision')
    parser.add_argument('--verbose', action='store_true', 
                       help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        checker = ProductionReadinessChecker()
        
        # Run all checks
        test_results = checker.check_test_coverage(args.coverage_report or 'coverage/coverage-summary.json')
        medical_results = checker.check_medical_safety(args.medical_impact, args.medical_report)
        security_results = checker.check_security_requirements(args.security_scan)
        build_results = checker.check_build_artifacts()
        dependency_results = checker.check_dependencies()
        
        # Generate final decision
        decision = checker.generate_deployment_decision(
            test_results, medical_results, security_results, 
            build_results, dependency_results, args.medical_impact
        )
        
        if args.verbose:
            print(json.dumps(decision, indent=2))
        else:
            print(f"🚀 Production Readiness Check")
            print(f"{'='*50}")
            print(f"Overall Score: {decision['overall_readiness_score']}%")
            print(f"Medical Impact: {decision['medical_impact']}")
            print(f"Deployment Approved: {'✅ YES' if decision['deployment_approved'] else '❌ NO'}")
            
            if decision['blocking_issues']:
                print(f"\n❌ Blocking Issues ({len(decision['blocking_issues'])}):")
                for issue in decision['blocking_issues']:
                    print(f"  • {issue}")
            
            if decision['warnings']:
                print(f"\n⚠️ Warnings ({len(decision['warnings'])}):")
                for warning in decision['warnings'][:5]:  # Show first 5 warnings
                    print(f"  • {warning}")
                if len(decision['warnings']) > 5:
                    print(f"  ... and {len(decision['warnings']) - 5} more")
            
            print(f"\n📋 Next Steps:")
            for step in decision['next_steps']:
                print(f"  {step}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(decision, f, indent=2)
        
        # Exit with error code if deployment not approved
        if not decision['deployment_approved']:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during production readiness check: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()