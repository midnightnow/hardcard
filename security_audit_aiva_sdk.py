#!/usr/bin/env python3
"""
AIVA SDK Security Audit and Code Review Tool
Comprehensive security analysis and code quality assessment
"""

import os
import re
import json
import hashlib
import subprocess
import ast
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

class AIVASecurityAuditor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.findings = []
        self.security_issues = []
        self.code_quality_issues = []
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('aiva_security_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def audit_javascript_security(self, file_path: Path) -> List[Dict]:
        """Audit JavaScript files for security issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Security patterns to check
            security_patterns = {
                'eval_usage': r'\beval\s*\(',
                'innerhtml_usage': r'\.innerHTML\s*=',
                'document_write': r'document\.write\s*\(',
                'global_vars': r'window\.\w+\s*=',
                'unsafe_regex': r'new\s+RegExp\s*\([^)]*\$.*\)',
                'prototype_pollution': r'__proto__|\bconstructor\b.*\bprototype\b',
                'xss_vectors': r'(javascript:|data:|vbscript:)',
                'hardcoded_secrets': r'(api_?key|secret|password|token)\s*[:=]\s*["\'][^"\']{10,}["\']',
                'unsafe_cors': r'Access-Control-Allow-Origin.*\*',
                'local_storage_sensitive': r'localStorage\.setItem.*(?:password|token|secret)',
                'console_log_sensitive': r'console\.log.*(?:password|token|secret|key)',
                'weak_crypto': r'Math\.random\(\)',
                'dom_clobbering': r'document\.getElementById.*user',
                'unsafe_redirect': r'window\.location.*=.*user',
                'postmessage_origin': r'postMessage.*\*'
            }
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in security_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_js_severity(pattern_name)
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'issue': pattern_name,
                            'severity': severity,
                            'description': self._get_js_description(pattern_name),
                            'code': line.strip(),
                            'recommendation': self._get_js_recommendation(pattern_name)
                        })
            
            # Check for specific AIVA SDK security concerns
            aiva_specific_issues = self._check_aiva_js_security(content, file_path)
            issues.extend(aiva_specific_issues)
            
        except Exception as e:
            self.logger.error(f"Error auditing JavaScript file {file_path}: {e}")
            
        return issues

    def audit_python_security(self, file_path: Path) -> List[Dict]:
        """Audit Python files for security issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                ast_issues = self._analyze_python_ast(tree, file_path)
                issues.extend(ast_issues)
            except SyntaxError as e:
                issues.append({
                    'file': str(file_path),
                    'line': e.lineno or 0,
                    'issue': 'syntax_error',
                    'severity': 'high',
                    'description': f'Syntax error: {e.msg}',
                    'code': '',
                    'recommendation': 'Fix syntax error'
                })
            
            # Security patterns for Python
            security_patterns = {
                'eval_usage': r'\beval\s*\(',
                'exec_usage': r'\bexec\s*\(',
                'input_usage': r'\binput\s*\(',  # Dangerous in Python 2
                'pickle_usage': r'\bpickle\.loads?\s*\(',
                'yaml_unsafe': r'yaml\.load\s*\(',
                'sql_injection': r'(execute|query).*%.*%',
                'path_traversal': r'open\s*\(.*\+',
                'hardcoded_secrets': r'(api_?key|secret|password|token)\s*=\s*["\'][^"\']{10,}["\']',
                'shell_injection': r'(os\.system|subprocess\.call|subprocess\.run).*shell\s*=\s*True',
                'assert_usage': r'\bassert\b(?!\s+\w+\s*==)',
                'random_weak': r'random\.random\(\)',
                'temp_file_insecure': r'tempfile\.mktemp\(',
                'urllib_unverified': r'urllib.*verify\s*=\s*False',
                'requests_unverified': r'requests.*verify\s*=\s*False',
                'debug_mode': r'debug\s*=\s*True',
                'logging_sensitive': r'log.*(?:password|token|secret|key)'
            }
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in security_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_python_severity(pattern_name)
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'issue': pattern_name,
                            'severity': severity,
                            'description': self._get_python_description(pattern_name),
                            'code': line.strip(),
                            'recommendation': self._get_python_recommendation(pattern_name)
                        })
            
            # Check AIVA-specific Python security concerns
            aiva_specific_issues = self._check_aiva_python_security(content, file_path)
            issues.extend(aiva_specific_issues)
            
        except Exception as e:
            self.logger.error(f"Error auditing Python file {file_path}: {e}")
            
        return issues

    def _analyze_python_ast(self, tree: ast.AST, file_path: Path) -> List[Dict]:
        """Analyze Python AST for security issues"""
        issues = []
        
        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []
                
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile']:
                        self.issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'issue': f'dangerous_function_{node.func.id}',
                            'severity': 'critical',
                            'description': f'Use of dangerous function: {node.func.id}',
                            'code': f'{node.func.id}(...)',
                            'recommendation': f'Avoid using {node.func.id}. Use safer alternatives.'
                        })
                
                # Check for subprocess with shell=True
                if isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'subprocess' and 
                        node.func.attr in ['call', 'run', 'Popen']):
                        
                        for keyword in node.keywords:
                            if (keyword.arg == 'shell' and 
                                isinstance(keyword.value, ast.Constant) and 
                                keyword.value.value is True):
                                
                                self.issues.append({
                                    'file': str(file_path),
                                    'line': node.lineno,
                                    'issue': 'subprocess_shell_injection',
                                    'severity': 'high',
                                    'description': 'subprocess call with shell=True can lead to injection',
                                    'code': 'subprocess.call(..., shell=True)',
                                    'recommendation': 'Use shell=False and pass command as list'
                                })
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for imports of dangerous modules
                dangerous_modules = ['pickle', 'marshal', 'shelve']
                for alias in node.names:
                    if alias.name in dangerous_modules:
                        self.issues.append({
                            'file': str(file_path),
                            'line': node.lineno,
                            'issue': f'dangerous_import_{alias.name}',
                            'severity': 'medium',
                            'description': f'Import of potentially dangerous module: {alias.name}',
                            'code': f'import {alias.name}',
                            'recommendation': f'Be cautious when using {alias.name}. Validate all input.'
                        })
                
                self.generic_visit(node)
        
        visitor = SecurityVisitor()
        visitor.visit(tree)
        return visitor.issues

    def _check_aiva_js_security(self, content: str, file_path: Path) -> List[Dict]:
        """Check AIVA-specific JavaScript security issues"""
        issues = []
        
        # Check for API key exposure
        if 'apiKey:' in content and ('your-api-key' in content or 'sk-' in content):
            # Look for hardcoded API keys in examples
            api_key_matches = re.finditer(r'apiKey\s*:\s*[\'"]([^\'"]+)[\'"]', content)
            for match in api_key_matches:
                if 'your-api-key' not in match.group(1) and 'demo' not in match.group(1):
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': 'hardcoded_api_key',
                        'severity': 'critical',
                        'description': 'Hardcoded API key found in code',
                        'code': match.group(0),
                        'recommendation': 'Use environment variables or secure configuration'
                    })
        
        # Check for insecure WebSocket connections
        if 'ws://' in content:
            issues.append({
                'file': str(file_path),
                'line': content.find('ws://'),
                'issue': 'insecure_websocket',
                'severity': 'medium',
                'description': 'Insecure WebSocket connection (ws:// instead of wss://)',
                'code': 'ws://',
                'recommendation': 'Use secure WebSocket connections (wss://)'
            })
        
        # Check for missing input validation
        if 'sendMessage' in content and 'trim()' not in content:
            issues.append({
                'file': str(file_path),
                'line': 0,
                'issue': 'missing_input_validation',
                'severity': 'medium',
                'description': 'Potential missing input validation in message handling',
                'code': 'sendMessage',
                'recommendation': 'Validate and sanitize all user input'
            })
        
        return issues

    def _check_aiva_python_security(self, content: str, file_path: Path) -> List[Dict]:
        """Check AIVA-specific Python security issues"""
        issues = []
        
        # Check for API key exposure
        if 'api_key' in content and ('your-api-key' in content or 'sk-' in content):
            api_key_matches = re.finditer(r'api_key\s*=\s*[\'"]([^\'"]+)[\'"]', content)
            for match in api_key_matches:
                if 'your-api-key' not in match.group(1) and 'demo' not in match.group(1):
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'issue': 'hardcoded_api_key',
                        'severity': 'critical',
                        'description': 'Hardcoded API key found in code',
                        'code': match.group(0),
                        'recommendation': 'Use environment variables or secure configuration'
                    })
        
        # Check for insecure HTTP usage
        if 'http://' in content and 'https://' not in content.replace('http://', ''):
            issues.append({
                'file': str(file_path),
                'line': content.find('http://'),
                'issue': 'insecure_http',
                'severity': 'medium',
                'description': 'Insecure HTTP connection found',
                'code': 'http://',
                'recommendation': 'Use HTTPS for all API communications'
            })
        
        # Check for missing SSL verification
        if 'verify=False' in content:
            issues.append({
                'file': str(file_path),
                'line': content.find('verify=False'),
                'issue': 'ssl_verification_disabled',
                'severity': 'high',
                'description': 'SSL certificate verification disabled',
                'code': 'verify=False',
                'recommendation': 'Enable SSL certificate verification for security'
            })
        
        return issues

    def check_code_quality(self, file_path: Path) -> List[Dict]:
        """Check code quality issues"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Check for code quality issues
            quality_patterns = {
                'long_line': (r'.{120,}', 'Line too long (>120 characters)'),
                'trailing_whitespace': (r'[ \t]+$', 'Trailing whitespace'),
                'todo_comment': (r'(TODO|FIXME|HACK)', 'TODO/FIXME comment found'),
                'magic_number': (r'\b\d{4,}\b', 'Magic number (consider using constants)'),
                'console_log': (r'console\.log', 'Console.log statement (remove in production)'),
                'print_statement': (r'\bprint\s*\(', 'Print statement (consider using logging)'),
                'global_var': (r'^[A-Z_]{2,}\s*=', 'Global variable (consider encapsulation)'),
            }
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, (pattern, description) in quality_patterns.items():
                    if re.search(pattern, line):
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'issue': pattern_name,
                            'severity': 'low',
                            'description': description,
                            'code': line.strip(),
                            'recommendation': self._get_quality_recommendation(pattern_name)
                        })
        
        except Exception as e:
            self.logger.error(f"Error checking code quality for {file_path}: {e}")
        
        return issues

    def run_static_analysis(self) -> Dict[str, Any]:
        """Run comprehensive static analysis"""
        self.logger.info("Starting AIVA SDK security audit...")
        
        # Find all relevant files
        js_files = list(self.base_path.glob("**/*.js"))
        py_files = list(self.base_path.glob("**/*.py"))
        md_files = list(self.base_path.glob("**/*.md"))
        
        results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_files_scanned': len(js_files) + len(py_files),
            'javascript_files': len(js_files),
            'python_files': len(py_files),
            'security_issues': [],
            'code_quality_issues': [],
            'summary': {}
        }
        
        # Audit JavaScript files
        for js_file in js_files:
            self.logger.info(f"Auditing JavaScript file: {js_file}")
            security_issues = self.audit_javascript_security(js_file)
            quality_issues = self.check_code_quality(js_file)
            
            results['security_issues'].extend(security_issues)
            results['code_quality_issues'].extend(quality_issues)
        
        # Audit Python files
        for py_file in py_files:
            self.logger.info(f"Auditing Python file: {py_file}")
            security_issues = self.audit_python_security(py_file)
            quality_issues = self.check_code_quality(py_file)
            
            results['security_issues'].extend(security_issues)
            results['code_quality_issues'].extend(quality_issues)
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results

    def _generate_summary(self, results: Dict) -> Dict:
        """Generate audit summary"""
        security_by_severity = {}
        quality_by_severity = {}
        
        for issue in results['security_issues']:
            severity = issue['severity']
            security_by_severity[severity] = security_by_severity.get(severity, 0) + 1
        
        for issue in results['code_quality_issues']:
            severity = issue['severity']
            quality_by_severity[severity] = quality_by_severity.get(severity, 0) + 1
        
        total_issues = len(results['security_issues']) + len(results['code_quality_issues'])
        
        return {
            'total_issues': total_issues,
            'security_issues_count': len(results['security_issues']),
            'code_quality_issues_count': len(results['code_quality_issues']),
            'security_by_severity': security_by_severity,
            'quality_by_severity': quality_by_severity,
            'risk_level': self._calculate_risk_level(security_by_severity),
            'recommendations': self._generate_recommendations(security_by_severity, quality_by_severity)
        }

    def _calculate_risk_level(self, security_by_severity: Dict) -> str:
        """Calculate overall risk level"""
        if security_by_severity.get('critical', 0) > 0:
            return 'CRITICAL'
        elif security_by_severity.get('high', 0) > 2:
            return 'HIGH'
        elif security_by_severity.get('medium', 0) > 5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_recommendations(self, security_by_severity: Dict, quality_by_severity: Dict) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []
        
        if security_by_severity.get('critical', 0) > 0:
            recommendations.append("🚨 CRITICAL: Address all critical security issues immediately")
        
        if security_by_severity.get('high', 0) > 0:
            recommendations.append("🔴 HIGH: Review and fix high-severity security issues")
        
        if security_by_severity.get('medium', 0) > 3:
            recommendations.append("🟡 MEDIUM: Address medium-severity security issues")
        
        if quality_by_severity.get('low', 0) > 10:
            recommendations.append("📝 Consider addressing code quality issues for maintainability")
        
        # General recommendations
        recommendations.extend([
            "🔐 Implement secure secret management",
            "🛡️ Add input validation and sanitization",
            "📊 Set up security monitoring and logging",
            "🔄 Establish regular security review process",
            "📚 Provide security training for developers"
        ])
        
        return recommendations

    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive security report"""
        report = f"""
# AIVA SDK Security Audit Report

**Generated:** {results['timestamp']}
**Risk Level:** {results['summary']['risk_level']}

## Executive Summary

Total files scanned: {results['total_files_scanned']}
- JavaScript files: {results['javascript_files']}
- Python files: {results['python_files']}

Total issues found: {results['summary']['total_issues']}
- Security issues: {results['summary']['security_issues_count']}
- Code quality issues: {results['summary']['code_quality_issues_count']}

## Security Issues by Severity

"""
        
        for severity, count in results['summary']['security_by_severity'].items():
            report += f"- **{severity.upper()}**: {count} issues\n"
        
        report += "\n## Critical Security Issues\n\n"
        
        critical_issues = [issue for issue in results['security_issues'] if issue['severity'] == 'critical']
        if critical_issues:
            for issue in critical_issues:
                report += f"### {issue['issue']} - {issue['file']}:{issue['line']}\n"
                report += f"**Description:** {issue['description']}\n"
                report += f"**Code:** `{issue['code']}`\n"
                report += f"**Recommendation:** {issue['recommendation']}\n\n"
        else:
            report += "✅ No critical security issues found.\n\n"
        
        report += "## High Priority Recommendations\n\n"
        for rec in results['summary']['recommendations'][:5]:
            report += f"- {rec}\n"
        
        report += f"\n## Detailed Findings\n\n"
        report += f"See full audit log for complete details of all {results['summary']['total_issues']} issues found.\n"
        
        return report

    def save_results(self, results: Dict, output_dir: str = "."):
        """Save audit results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save JSON results
        json_file = output_path / "aiva_security_audit_results.json"
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save report
        report = self.generate_report(results)
        report_file = output_path / "aiva_security_audit_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        self.logger.info(f"Results saved to {json_file}")
        self.logger.info(f"Report saved to {report_file}")

    def _get_js_severity(self, pattern_name: str) -> str:
        severity_map = {
            'eval_usage': 'critical',
            'hardcoded_secrets': 'critical',
            'innerhtml_usage': 'high',
            'document_write': 'high',
            'prototype_pollution': 'high',
            'xss_vectors': 'high',
            'unsafe_cors': 'medium',
            'local_storage_sensitive': 'medium',
            'console_log_sensitive': 'medium',
            'weak_crypto': 'medium',
            'global_vars': 'low'
        }
        return severity_map.get(pattern_name, 'medium')

    def _get_python_severity(self, pattern_name: str) -> str:
        severity_map = {
            'eval_usage': 'critical',
            'exec_usage': 'critical',
            'hardcoded_secrets': 'critical',
            'shell_injection': 'high',
            'sql_injection': 'high',
            'pickle_usage': 'high',
            'yaml_unsafe': 'high',
            'path_traversal': 'medium',
            'requests_unverified': 'medium',
            'debug_mode': 'medium',
            'logging_sensitive': 'medium',
            'random_weak': 'low'
        }
        return severity_map.get(pattern_name, 'medium')

    def _get_js_description(self, pattern_name: str) -> str:
        descriptions = {
            'eval_usage': 'Use of eval() can lead to code injection vulnerabilities',
            'hardcoded_secrets': 'Hardcoded secrets expose sensitive information',
            'innerhtml_usage': 'innerHTML usage can lead to XSS vulnerabilities',
            'document_write': 'document.write can be exploited for XSS',
            'prototype_pollution': 'Prototype pollution can lead to security issues',
            'xss_vectors': 'Potential XSS vector detected',
            'unsafe_cors': 'Wildcard CORS policy allows any origin',
            'local_storage_sensitive': 'Sensitive data stored in localStorage',
            'console_log_sensitive': 'Sensitive data logged to console',
            'weak_crypto': 'Math.random() is not cryptographically secure',
            'global_vars': 'Global variables can be accessed/modified by any script'
        }
        return descriptions.get(pattern_name, 'Security issue detected')

    def _get_python_description(self, pattern_name: str) -> str:
        descriptions = {
            'eval_usage': 'Use of eval() can execute arbitrary code',
            'exec_usage': 'Use of exec() can execute arbitrary code',
            'hardcoded_secrets': 'Hardcoded secrets expose sensitive information',
            'shell_injection': 'Shell injection vulnerability with shell=True',
            'sql_injection': 'Potential SQL injection vulnerability',
            'pickle_usage': 'Pickle can execute arbitrary code when deserializing',
            'yaml_unsafe': 'yaml.load() without Loader can execute arbitrary code',
            'path_traversal': 'Potential path traversal vulnerability',
            'requests_unverified': 'SSL verification disabled in requests',
            'debug_mode': 'Debug mode enabled in production code',
            'logging_sensitive': 'Sensitive data logged',
            'random_weak': 'random.random() is not cryptographically secure'
        }
        return descriptions.get(pattern_name, 'Security issue detected')

    def _get_js_recommendation(self, pattern_name: str) -> str:
        recommendations = {
            'eval_usage': 'Avoid eval(). Use JSON.parse() or other safe alternatives',
            'hardcoded_secrets': 'Use environment variables or secure configuration',
            'innerhtml_usage': 'Use textContent or sanitize HTML input',
            'document_write': 'Use DOM manipulation methods instead',
            'prototype_pollution': 'Validate object properties and use Object.create(null)',
            'xss_vectors': 'Sanitize and validate all user input',
            'unsafe_cors': 'Specify allowed origins explicitly',
            'local_storage_sensitive': 'Use secure storage or encrypt sensitive data',
            'console_log_sensitive': 'Remove sensitive data from logs',
            'weak_crypto': 'Use crypto.getRandomValues() for cryptographic purposes',
            'global_vars': 'Encapsulate variables in modules or namespaces'
        }
        return recommendations.get(pattern_name, 'Review and fix security issue')

    def _get_python_recommendation(self, pattern_name: str) -> str:
        recommendations = {
            'eval_usage': 'Avoid eval(). Use ast.literal_eval() for safe evaluation',
            'exec_usage': 'Avoid exec(). Use safer alternatives',
            'hardcoded_secrets': 'Use environment variables or secure configuration',
            'shell_injection': 'Use shell=False and pass commands as lists',
            'sql_injection': 'Use parameterized queries or ORM',
            'pickle_usage': 'Use JSON or other safe serialization formats',
            'yaml_unsafe': 'Use yaml.safe_load() instead of yaml.load()',
            'path_traversal': 'Validate file paths and use os.path.join()',
            'requests_unverified': 'Enable SSL verification for security',
            'debug_mode': 'Disable debug mode in production',
            'logging_sensitive': 'Remove sensitive data from logs',
            'random_weak': 'Use secrets module for cryptographic randomness'
        }
        return recommendations.get(pattern_name, 'Review and fix security issue')

    def _get_quality_recommendation(self, pattern_name: str) -> str:
        recommendations = {
            'long_line': 'Break long lines for better readability',
            'trailing_whitespace': 'Remove trailing whitespace',
            'todo_comment': 'Address TODO/FIXME comments',
            'magic_number': 'Define constants for magic numbers',
            'console_log': 'Remove console.log statements',
            'print_statement': 'Use logging instead of print statements',
            'global_var': 'Encapsulate global variables'
        }
        return recommendations.get(pattern_name, 'Improve code quality')


def main():
    """Main function to run the security audit"""
    base_path = "/Users/studio/hardcard/HARDCARDSUITE/vetsorcery_extracted/frontend"
    
    auditor = AIVASecurityAuditor(base_path)
    results = auditor.run_static_analysis()
    
    # Save results
    auditor.save_results(results, "/Users/studio/hardcard")
    
    # Print summary
    print(f"\n{'='*60}")
    print("AIVA SDK SECURITY AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"Risk Level: {results['summary']['risk_level']}")
    print(f"Total Issues: {results['summary']['total_issues']}")
    print(f"Security Issues: {results['summary']['security_issues_count']}")
    print(f"Code Quality Issues: {results['summary']['code_quality_issues_count']}")
    print(f"\nSecurity Issues by Severity:")
    for severity, count in results['summary']['security_by_severity'].items():
        print(f"  {severity.upper()}: {count}")
    
    print(f"\nTop Recommendations:")
    for i, rec in enumerate(results['summary']['recommendations'][:3], 1):
        print(f"  {i}. {rec}")
    
    print(f"\nDetailed results saved to aiva_security_audit_results.json")
    print(f"Report saved to aiva_security_audit_report.md")


if __name__ == "__main__":
    main()