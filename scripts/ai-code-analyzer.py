#!/usr/bin/env python3
"""
AI-Powered Code Analyzer for HardCard Multi-Agent System
Provides intelligent code analysis, suggestions, and automated improvements
"""

import os
import json
import re
import ast
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import asyncio
import aiofiles

@dataclass
class CodeIssue:
    severity: str  # critical, major, minor, info
    category: str  # security, performance, maintainability, medical, style
    message: str
    line: int
    column: int
    suggestion: str
    auto_fixable: bool
    medical_impact: bool

@dataclass
class CodeMetrics:
    cyclomatic_complexity: int
    lines_of_code: int
    test_coverage: float
    technical_debt_ratio: float
    maintainability_index: float
    security_score: float
    medical_compliance_score: float

@dataclass
class AIAnalysisResult:
    file_path: str
    completion_score: float
    quality_score: float
    issues: List[CodeIssue]
    metrics: CodeMetrics
    suggestions: List[str]
    auto_fixes: List[Dict[str, Any]]
    estimated_fix_time: int  # minutes

class MedicalCodeAnalyzer:
    """Specialized analyzer for medical/veterinary code compliance"""
    
    def __init__(self):
        self.medical_patterns = {
            'drug_calculation': [
                r'\b(dose|dosage|medication|drug)\b.*\b(calculate|computation|formula)\b',
                r'\b(mg|ml|kg|lb)\b.*[+\-*/]',
                r'\bweight\s*\*\s*dose\b'
            ],
            'patient_data': [
                r'\b(patient|animal|pet)\.?\w*\.(id|name|data|record)\b',
                r'\b(medical_record|patient_info|clinical_data)\b'
            ],
            'emergency_protocols': [
                r'\b(emergency|urgent|critical|stat)\b',
                r'\b(protocol|procedure|emergency_response)\b'
            ],
            'controlled_substances': [
                r'\b(controlled|schedule|narcotic|opioid)\b',
                r'\b(dea|prescription|rx)\b'
            ]
        }
        
        self.required_validations = {
            'drug_calculation': ['error_handling', 'precision_handling', 'range_validation'],
            'patient_data': ['encryption', 'access_control', 'audit_logging'],
            'emergency_protocols': ['timeout_handling', 'fallback_procedures', 'logging'],
            'controlled_substances': ['authentication', 'audit_trail', 'secure_storage']
        }
    
    def analyze_medical_compliance(self, content: str, file_path: str) -> Tuple[float, List[CodeIssue]]:
        """Analyze code for medical compliance"""
        issues = []
        compliance_score = 100.0
        
        # Check for medical patterns
        for pattern_type, patterns in self.medical_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Check if required validations are present
                    missing_validations = self._check_required_validations(
                        content, pattern_type, match.start(), match.end()
                    )
                    
                    for validation in missing_validations:
                        issues.append(CodeIssue(
                            severity="critical" if pattern_type in ['drug_calculation', 'controlled_substances'] else "major",
                            category="medical",
                            message=f"Medical code missing {validation} for {pattern_type}",
                            line=line_num,
                            column=match.start() - content.rfind('\n', 0, match.start()),
                            suggestion=f"Add {validation} validation for medical safety",
                            auto_fixable=False,
                            medical_impact=True
                        ))
                        compliance_score -= 15 if pattern_type in ['drug_calculation', 'controlled_substances'] else 10
        
        return max(0, compliance_score), issues
    
    def _check_required_validations(self, content: str, pattern_type: str, start: int, end: int) -> List[str]:
        """Check if required validations are present near medical code"""
        required = self.required_validations.get(pattern_type, [])
        missing = []
        
        # Check surrounding context (500 characters before and after)
        context_start = max(0, start - 500)
        context_end = min(len(content), end + 500)
        context = content[context_start:context_end]
        
        validation_patterns = {
            'error_handling': [r'\btry\b.*\bcatch\b', r'\bif\s*\(.*error', r'\.catch\s*\('],
            'precision_handling': [r'\btoFixed\b', r'\bMath\.round\b', r'\bprecision\b'],
            'range_validation': [r'\bif\s*\(.*>\s*\d+', r'\bvalidate\b', r'\bmin\b.*\bmax\b'],
            'encryption': [r'\bencrypt\b', r'\bcrypto\b', r'\bhash\b'],
            'access_control': [r'\bauth\b', r'\bpermission\b', r'\brole\b'],
            'audit_logging': [r'\blog\b', r'\baudit\b', r'\btrack\b'],
            'timeout_handling': [r'\btimeout\b', r'\bsetTimeout\b', r'\bdelay\b'],
            'fallback_procedures': [r'\bfallback\b', r'\belse\b', r'\bdefault\b'],
            'authentication': [r'\bauth\b', r'\blogin\b', r'\bverify\b'],
            'audit_trail': [r'\baudit\b', r'\blog\b', r'\bhistory\b'],
            'secure_storage': [r'\bsecure\b', r'\bencrypt\b', r'\bstore\b']
        }
        
        for validation in required:
            patterns = validation_patterns.get(validation, [])
            if not any(re.search(pattern, context, re.IGNORECASE) for pattern in patterns):
                missing.append(validation)
        
        return missing

class SecurityAnalyzer:
    """Advanced security analysis for TypeScript/JavaScript code"""
    
    def __init__(self):
        self.security_patterns = {
            'xss_vulnerabilities': [
                r'innerHTML\s*=\s*[^;]*[+]',
                r'dangerouslySetInnerHTML',
                r'document\.write\s*\(',
                r'eval\s*\('
            ],
            'injection_risks': [
                r'query\s*\+\s*["\']',
                r'execute\s*\(\s*["\'][^"\']*["\']\s*\+',
                r'new\s+Function\s*\('
            ],
            'crypto_issues': [
                r'Math\.random\s*\(\s*\)',
                r'btoa\s*\(',
                r'atob\s*\('
            ],
            'data_exposure': [
                r'console\.(log|info|debug|warn)\s*\(',
                r'alert\s*\(',
                r'localStorage\.',
                r'sessionStorage\.'
            ]
        }
    
    def analyze_security(self, content: str, file_path: str) -> Tuple[float, List[CodeIssue]]:
        """Analyze code for security vulnerabilities"""
        issues = []
        security_score = 100.0
        
        for vuln_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    severity = self._get_security_severity(vuln_type, match.group())
                    
                    issues.append(CodeIssue(
                        severity=severity,
                        category="security",
                        message=f"Potential {vuln_type.replace('_', ' ')}: {match.group()}",
                        line=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        suggestion=self._get_security_suggestion(vuln_type),
                        auto_fixable=vuln_type in ['data_exposure'],
                        medical_impact=any(med in file_path.lower() for med in ['patient', 'medical', 'drug'])
                    ))
                    
                    score_penalty = 20 if severity == "critical" else 10 if severity == "major" else 5
                    security_score -= score_penalty
        
        return max(0, security_score), issues
    
    def _get_security_severity(self, vuln_type: str, match_text: str) -> str:
        """Determine severity of security issue"""
        critical_patterns = ['eval', 'innerHTML.*+', 'dangerouslySetInnerHTML']
        major_patterns = ['console.log', 'localStorage', 'Math.random']
        
        if any(pattern in match_text for pattern in critical_patterns):
            return "critical"
        elif any(pattern in match_text for pattern in major_patterns):
            return "major"
        else:
            return "minor"
    
    def _get_security_suggestion(self, vuln_type: str) -> str:
        """Get security fix suggestion"""
        suggestions = {
            'xss_vulnerabilities': "Use textContent instead of innerHTML, or sanitize input",
            'injection_risks': "Use parameterized queries or prepared statements",
            'crypto_issues': "Use crypto.getRandomValues() for cryptographic randomness",
            'data_exposure': "Remove console.log statements and use secure storage"
        }
        return suggestions.get(vuln_type, "Review security implications")

class PerformanceAnalyzer:
    """Performance analysis for TypeScript/JavaScript code"""
    
    def analyze_performance(self, content: str, file_path: str) -> Tuple[float, List[CodeIssue]]:
        """Analyze code for performance issues"""
        issues = []
        performance_score = 100.0
        
        # Check for performance anti-patterns
        anti_patterns = {
            'inefficient_loops': [
                r'for\s*\([^)]*\.length[^)]*\)',  # length in loop condition
                r'while\s*\([^)]*\.length[^)]*\)'
            ],
            'unnecessary_re_renders': [
                r'useEffect\s*\(\s*\(\s*\)\s*=>\s*{[^}]*}\s*\)',  # useEffect without deps
                r'useState\s*\([^)]*\)\s*\[0\]'  # Unused state setter
            ],
            'memory_leaks': [
                r'setInterval\s*\(',
                r'setTimeout\s*\(',
                r'addEventListener\s*\('
            ],
            'blocking_operations': [
                r'JSON\.parse\s*\([^)]*large',
                r'for\s*\([^)]*1000[^)]*\)',
                r'while\s*\(true\)'
            ]
        }
        
        for pattern_type, patterns in anti_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    
                    issues.append(CodeIssue(
                        severity="major" if pattern_type in ['memory_leaks', 'blocking_operations'] else "minor",
                        category="performance",
                        message=f"Performance issue: {pattern_type.replace('_', ' ')}",
                        line=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        suggestion=self._get_performance_suggestion(pattern_type),
                        auto_fixable=pattern_type in ['inefficient_loops'],
                        medical_impact=False
                    ))
                    
                    performance_score -= 15 if pattern_type in ['memory_leaks', 'blocking_operations'] else 5
        
        return max(0, performance_score), issues
    
    def _get_performance_suggestion(self, pattern_type: str) -> str:
        """Get performance optimization suggestion"""
        suggestions = {
            'inefficient_loops': "Cache array length outside loop",
            'unnecessary_re_renders': "Add dependency array to useEffect",
            'memory_leaks': "Clear intervals/timeouts and remove event listeners",
            'blocking_operations': "Use async/await or web workers for heavy operations"
        }
        return suggestions.get(pattern_type, "Optimize performance")

class CodeComplexityAnalyzer:
    """Analyze code complexity and maintainability"""
    
    def analyze_complexity(self, content: str, file_path: str) -> CodeMetrics:
        """Calculate various code metrics"""
        try:
            # Basic metrics
            lines = content.split('\n')
            lines_of_code = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
            
            # Cyclomatic complexity (simplified)
            complexity_keywords = ['if', 'else', 'for', 'while', 'switch', 'case', 'catch', '&&', '||']
            cyclomatic_complexity = 1  # Base complexity
            for keyword in complexity_keywords:
                cyclomatic_complexity += len(re.findall(rf'\b{keyword}\b', content))
            
            # Technical debt indicators
            debt_indicators = ['TODO', 'FIXME', 'HACK', 'XXX', 'console.log', 'any']
            debt_count = sum(content.lower().count(indicator.lower()) for indicator in debt_indicators)
            technical_debt_ratio = min(100, (debt_count / max(1, lines_of_code / 10)) * 100)
            
            # Maintainability index (simplified calculation)
            avg_line_length = sum(len(line) for line in lines) / max(1, len(lines))
            comment_ratio = len([line for line in lines if line.strip().startswith('//')]) / max(1, len(lines))
            
            maintainability_index = max(0, 100 - (cyclomatic_complexity * 2) - (technical_debt_ratio * 0.5) - 
                                      max(0, avg_line_length - 80) * 0.1 + (comment_ratio * 20))
            
            return CodeMetrics(
                cyclomatic_complexity=cyclomatic_complexity,
                lines_of_code=lines_of_code,
                test_coverage=0.0,  # Would need to integrate with test runner
                technical_debt_ratio=technical_debt_ratio,
                maintainability_index=maintainability_index,
                security_score=0.0,  # Set by security analyzer
                medical_compliance_score=0.0  # Set by medical analyzer
            )
            
        except Exception as e:
            logging.error(f"Error analyzing complexity for {file_path}: {e}")
            return CodeMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)

class AICodeAnalyzer:
    """Main AI-powered code analyzer"""
    
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.medical_analyzer = MedicalCodeAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
        self.complexity_analyzer = CodeComplexityAnalyzer()
        
        # Setup logging
        logging.basicConfig(
            filename=f"{project_root}/logs/ai-code-analysis.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    async def analyze_file(self, file_path: str) -> AIAnalysisResult:
        """Perform comprehensive AI analysis of a single file"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Run all analyzers
            medical_score, medical_issues = self.medical_analyzer.analyze_medical_compliance(content, file_path)
            security_score, security_issues = self.security_analyzer.analyze_security(content, file_path)
            performance_score, performance_issues = self.performance_analyzer.analyze_performance(content, file_path)
            
            # Calculate metrics
            metrics = self.complexity_analyzer.analyze_complexity(content, file_path)
            metrics.security_score = security_score
            metrics.medical_compliance_score = medical_score
            
            # Combine all issues
            all_issues = medical_issues + security_issues + performance_issues
            
            # Calculate overall scores
            completion_score = self._calculate_completion_score(content, all_issues)
            quality_score = self._calculate_quality_score(metrics, all_issues)
            
            # Generate AI suggestions
            suggestions = self._generate_ai_suggestions(content, all_issues, metrics)
            
            # Generate auto-fixes
            auto_fixes = self._generate_auto_fixes(content, all_issues)
            
            # Estimate fix time
            fix_time = self._estimate_fix_time(all_issues)
            
            return AIAnalysisResult(
                file_path=file_path,
                completion_score=completion_score,
                quality_score=quality_score,
                issues=all_issues,
                metrics=metrics,
                suggestions=suggestions,
                auto_fixes=auto_fixes,
                estimated_fix_time=fix_time
            )
            
        except Exception as e:
            logging.error(f"Error analyzing file {file_path}: {e}")
            return AIAnalysisResult(
                file_path=file_path,
                completion_score=0.0,
                quality_score=0.0,
                issues=[],
                metrics=CodeMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0),
                suggestions=[f"Error analyzing file: {e}"],
                auto_fixes=[],
                estimated_fix_time=0
            )
    
    def _calculate_completion_score(self, content: str, issues: List[CodeIssue]) -> float:
        """Calculate completion score based on content and issues"""
        base_score = 50.0  # Starting point
        
        # Add points for functional indicators
        functional_patterns = ['function', 'const', 'useState', 'useEffect', 'export', 'import']
        for pattern in functional_patterns:
            base_score += len(re.findall(rf'\b{pattern}\b', content)) * 2
        
        # Subtract points for placeholder indicators
        placeholder_patterns = ['TODO', 'FIXME', 'placeholder', 'coming soon']
        for pattern in placeholder_patterns:
            base_score -= len(re.findall(pattern, content, re.IGNORECASE)) * 5
        
        # Subtract points for critical issues
        critical_issues = [issue for issue in issues if issue.severity == "critical"]
        base_score -= len(critical_issues) * 10
        
        return max(0, min(100, base_score))
    
    def _calculate_quality_score(self, metrics: CodeMetrics, issues: List[CodeIssue]) -> float:
        """Calculate overall quality score"""
        # Weight different factors
        maintainability_weight = 0.3
        security_weight = 0.3
        medical_weight = 0.2
        complexity_weight = 0.2
        
        # Normalize complexity (lower is better)
        complexity_score = max(0, 100 - (metrics.cyclomatic_complexity * 2))
        
        quality_score = (
            metrics.maintainability_index * maintainability_weight +
            metrics.security_score * security_weight +
            metrics.medical_compliance_score * medical_weight +
            complexity_score * complexity_weight
        )
        
        # Penalize for critical issues
        critical_issues = [issue for issue in issues if issue.severity == "critical"]
        quality_score -= len(critical_issues) * 15
        
        return max(0, min(100, quality_score))
    
    def _generate_ai_suggestions(self, content: str, issues: List[CodeIssue], metrics: CodeMetrics) -> List[str]:
        """Generate AI-powered improvement suggestions"""
        suggestions = []
        
        # Complexity suggestions
        if metrics.cyclomatic_complexity > 10:
            suggestions.append("Consider breaking down complex functions into smaller, more focused functions")
        
        # Technical debt suggestions
        if metrics.technical_debt_ratio > 20:
            suggestions.append("High technical debt detected. Consider refactoring and removing TODO/FIXME comments")
        
        # Issue-based suggestions
        critical_issues = [issue for issue in issues if issue.severity == "critical"]
        if critical_issues:
            suggestions.append(f"Address {len(critical_issues)} critical issues before production deployment")
        
        medical_issues = [issue for issue in issues if issue.medical_impact]
        if medical_issues:
            suggestions.append("Medical compliance issues found. Ensure proper validation and error handling")
        
        # Content-based suggestions
        if 'test' not in content.lower() and 'spec' not in content.lower():
            suggestions.append("Consider adding unit tests for better code coverage")
        
        if len(content.split('\n')) > 200:
            suggestions.append("Large file detected. Consider splitting into smaller modules")
        
        return suggestions
    
    def _generate_auto_fixes(self, content: str, issues: List[CodeIssue]) -> List[Dict[str, Any]]:
        """Generate automatic fixes for auto-fixable issues"""
        auto_fixes = []
        
        for issue in issues:
            if issue.auto_fixable:
                if issue.category == "security" and "console.log" in content:
                    auto_fixes.append({
                        "type": "remove_console_logs",
                        "description": "Remove console.log statements",
                        "line": issue.line,
                        "fix_type": "deletion"
                    })
                elif issue.category == "performance" and "inefficient_loops" in issue.message:
                    auto_fixes.append({
                        "type": "optimize_loop",
                        "description": "Cache array length in loop",
                        "line": issue.line,
                        "fix_type": "replacement"
                    })
        
        return auto_fixes
    
    def _estimate_fix_time(self, issues: List[CodeIssue]) -> int:
        """Estimate time to fix all issues (in minutes)"""
        time_estimates = {
            "critical": 30,
            "major": 15,
            "minor": 5,
            "info": 2
        }
        
        total_time = 0
        for issue in issues:
            if issue.auto_fixable:
                total_time += 2  # Auto-fixes are quick
            else:
                total_time += time_estimates.get(issue.severity, 5)
        
        return total_time
    
    async def analyze_project(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze entire project or specific file patterns"""
        start_time = time.time()
        
        # Default to TypeScript/JavaScript files
        if not file_patterns:
            file_patterns = ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"]
        
        # Find all matching files
        all_files = []
        frontend_src = Path(self.project_root) / "HARDCARDSUITE/vetsorcery_extracted/frontend/src"
        
        if frontend_src.exists():
            for pattern in file_patterns:
                if pattern.startswith("**"):
                    # Recursive search
                    extension = pattern.split("*.")[-1]
                    for file_path in frontend_src.rglob(f"*.{extension}"):
                        if file_path.is_file() and "node_modules" not in str(file_path):
                            all_files.append(str(file_path))
        
        # Analyze files in parallel
        max_concurrent = min(10, len(all_files))
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(file_path):
            async with semaphore:
                return await self.analyze_file(file_path)
        
        # Run analysis
        logging.info(f"Starting analysis of {len(all_files)} files")
        tasks = [analyze_with_semaphore(file_path) for file_path in all_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = [r for r in results if isinstance(r, AIAnalysisResult)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        # Calculate aggregate statistics
        total_issues = sum(len(result.issues) for result in successful_results)
        critical_issues = sum(len([i for i in result.issues if i.severity == "critical"]) 
                            for result in successful_results)
        medical_issues = sum(len([i for i in result.issues if i.medical_impact]) 
                           for result in successful_results)
        
        avg_completion = sum(result.completion_score for result in successful_results) / max(1, len(successful_results))
        avg_quality = sum(result.quality_score for result in successful_results) / max(1, len(successful_results))
        
        # Generate project-level suggestions
        project_suggestions = self._generate_project_suggestions(successful_results)
        
        analysis_time = time.time() - start_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_duration": analysis_time,
            "files_analyzed": len(successful_results),
            "files_failed": len(failed_results),
            "summary": {
                "average_completion_score": round(avg_completion, 1),
                "average_quality_score": round(avg_quality, 1),
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "medical_issues": medical_issues,
                "estimated_total_fix_time": sum(result.estimated_fix_time for result in successful_results)
            },
            "project_suggestions": project_suggestions,
            "detailed_results": [asdict(result) for result in successful_results[:20]],  # Limit for size
            "performance_metrics": {
                "files_per_second": len(successful_results) / analysis_time,
                "average_file_analysis_time": analysis_time / max(1, len(successful_results))
            }
        }
    
    def _generate_project_suggestions(self, results: List[AIAnalysisResult]) -> List[str]:
        """Generate project-level improvement suggestions"""
        suggestions = []
        
        # Files needing immediate attention
        critical_files = [r for r in results if any(i.severity == "critical" for i in r.issues)]
        if critical_files:
            suggestions.append(f"{len(critical_files)} files have critical issues requiring immediate attention")
        
        # Medical compliance
        medical_files = [r for r in results if any(i.medical_impact for i in r.issues)]
        if medical_files:
            suggestions.append(f"{len(medical_files)} files have medical compliance issues")
        
        # Low completion scores
        incomplete_files = [r for r in results if r.completion_score < 50]
        if incomplete_files:
            suggestions.append(f"{len(incomplete_files)} files are less than 50% complete")
        
        # High complexity
        complex_files = [r for r in results if r.metrics.cyclomatic_complexity > 15]
        if complex_files:
            suggestions.append(f"{len(complex_files)} files have high complexity and should be refactored")
        
        # Security issues
        security_issues = sum(len([i for i in r.issues if i.category == "security"]) for r in results)
        if security_issues > 0:
            suggestions.append(f"{security_issues} security issues found across the project")
        
        return suggestions

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='AI-Powered Code Analyzer')
    parser.add_argument('--file', help='Analyze specific file')
    parser.add_argument('--project', action='store_true', help='Analyze entire project')
    parser.add_argument('--patterns', nargs='*', help='File patterns to analyze')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--format', choices=['json', 'summary'], default='summary', help='Output format')
    
    args = parser.parse_args()
    
    analyzer = AICodeAnalyzer()
    
    async def run_analysis():
        if args.file:
            result = await analyzer.analyze_file(args.file)
            output = asdict(result)
        elif args.project:
            result = await analyzer.analyze_project(args.patterns)
            output = result
        else:
            print("Please specify --file or --project")
            return
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output, f, indent=2)
        
        if args.format == 'json':
            print(json.dumps(output, indent=2))
        else:
            # Summary format
            if args.file:
                print(f"🔍 AI Analysis for {output['file_path']}")
                print(f"Completion Score: {output['completion_score']:.1f}%")
                print(f"Quality Score: {output['quality_score']:.1f}%")
                print(f"Issues Found: {len(output['issues'])}")
                print(f"Estimated Fix Time: {output['estimated_fix_time']} minutes")
                
                if output['issues']:
                    print("\n🚨 Issues:")
                    for issue in output['issues'][:5]:  # Show first 5
                        print(f"  {issue['severity'].upper()}: {issue['message']} (Line {issue['line']})")
                
                if output['suggestions']:
                    print("\n💡 Suggestions:")
                    for suggestion in output['suggestions']:
                        print(f"  • {suggestion}")
            else:
                print(f"🔍 AI Project Analysis Complete")
                print(f"Files Analyzed: {output['files_analyzed']}")
                print(f"Average Completion: {output['summary']['average_completion_score']}%")
                print(f"Average Quality: {output['summary']['average_quality_score']}%")
                print(f"Total Issues: {output['summary']['total_issues']}")
                print(f"Critical Issues: {output['summary']['critical_issues']}")
                print(f"Medical Issues: {output['summary']['medical_issues']}")
                
                if output['project_suggestions']:
                    print("\n💡 Project Suggestions:")
                    for suggestion in output['project_suggestions']:
                        print(f"  • {suggestion}")
    
    asyncio.run(run_analysis())

if __name__ == "__main__":
    main()