#!/usr/bin/env python3
"""
HardCard Improvement Agent Framework
====================================
Multi-agent system for automated code quality improvement and completion
"""

import os
import json
import ast
import re
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

@dataclass
class FileIssue:
    """Represents an issue found in a file"""
    type: str
    severity: str  # critical, high, medium, low
    message: str
    line: int = 0
    column: int = 0
    fix_suggestion: str = ""

@dataclass
class FileAnalysis:
    """Complete analysis of a single file"""
    path: str
    completion_score: float
    issues: List[FileIssue]
    improvements_made: List[str]
    status: str  # placeholder, incomplete, complete, production-ready

class CodeQualityAgent:
    """Agent responsible for analyzing code quality issues"""
    
    def __init__(self):
        self.critical_patterns = {
            'alert_statements': r'\balert\s*\(',
            'console_log': r'\bconsole\.(log|error|warn|info)\s*\(',
            'dangerouslySetInnerHTML': r'dangerouslySetInnerHTML',
            'eval_usage': r'\beval\s*\(',
            'innerHTML': r'\.innerHTML\s*=',
            'document_write': r'document\.write',
            'hardcoded_secrets': r'(api[_-]?key|password|secret|token)\s*[:=]\s*["\'][^"\']+["\']',
            'todo_comments': r'(TODO|FIXME|XXX|HACK|BUG)\s*:',
            'deprecated_apis': r'(componentWillMount|componentWillReceiveProps|componentWillUpdate)',
            'any_type': r':\s*any\b',
            'ts_ignore': r'@ts-ignore',
            'eslint_disable': r'eslint-disable',
        }
        
        self.security_patterns = {
            'sql_injection': r'(SELECT|INSERT|UPDATE|DELETE).*\+.*["\']',
            'xss_risk': r'(innerHTML|outerHTML|document\.write)',
            'path_traversal': r'\.\.[/\\]',
            'command_injection': r'(exec|spawn|system)\s*\(',
        }
    
    def analyze_file(self, file_path: str) -> List[FileIssue]:
        """Analyze a single file for quality issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Check for critical patterns
            for pattern_name, pattern in self.critical_patterns.items():
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    severity = 'critical' if pattern_name in ['eval_usage', 'hardcoded_secrets', 'innerHTML'] else 'high'
                    
                    issues.append(FileIssue(
                        type=pattern_name,
                        severity=severity,
                        message=f"{pattern_name.replace('_', ' ').title()} detected",
                        line=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        fix_suggestion=self._get_fix_suggestion(pattern_name)
                    ))
            
            # Check for security patterns
            for pattern_name, pattern in self.security_patterns.items():
                matches = list(re.finditer(pattern, content))
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append(FileIssue(
                        type=f"security_{pattern_name}",
                        severity='critical',
                        message=f"Potential {pattern_name.replace('_', ' ')} vulnerability",
                        line=line_num,
                        column=match.start() - content.rfind('\n', 0, match.start()),
                        fix_suggestion=self._get_security_fix(pattern_name)
                    ))
            
            # TypeScript specific checks
            if file_path.endswith('.ts') or file_path.endswith('.tsx'):
                issues.extend(self._analyze_typescript(content, lines))
            
            # Python specific checks
            if file_path.endswith('.py'):
                issues.extend(self._analyze_python(content, lines))
                
        except Exception as e:
            issues.append(FileIssue(
                type='read_error',
                severity='medium',
                message=f"Could not analyze file: {str(e)}",
                fix_suggestion="Check file permissions and encoding"
            ))
        
        return issues
    
    def _analyze_typescript(self, content: str, lines: List[str]) -> List[FileIssue]:
        """TypeScript specific analysis"""
        issues = []
        
        # Check for missing type annotations
        function_pattern = r'(function|const|let|var)\s+(\w+)\s*=?\s*\([^)]*\)\s*(?!:)'
        for match in re.finditer(function_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            issues.append(FileIssue(
                type='missing_type_annotation',
                severity='medium',
                message='Function missing return type annotation',
                line=line_num,
                fix_suggestion='Add explicit return type annotation'
            ))
        
        # Check for unused imports
        import_pattern = r'import\s+(?:{[^}]+}|[\w\s,]+)\s+from\s+["\'][^"\']+["\']'
        imports = re.findall(r'import\s+{?([^}]+)}?\s+from', content)
        
        return issues
    
    def _analyze_python(self, content: str, lines: List[str]) -> List[FileIssue]:
        """Python specific analysis"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Check for missing docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    if not ast.get_docstring(node):
                        issues.append(FileIssue(
                            type='missing_docstring',
                            severity='low',
                            message=f'{node.__class__.__name__} missing docstring',
                            line=node.lineno if hasattr(node, 'lineno') else 0,
                            fix_suggestion='Add descriptive docstring'
                        ))
        except SyntaxError:
            pass
        
        return issues
    
    def _get_fix_suggestion(self, issue_type: str) -> str:
        """Get fix suggestion for common issues"""
        suggestions = {
            'alert_statements': 'Replace with proper UI notification system',
            'console_log': 'Remove or use proper logging system',
            'innerHTML': 'Use textContent or React dangerouslySetInnerHTML with sanitization',
            'eval_usage': 'Parse JSON or use Function constructor with validation',
            'hardcoded_secrets': 'Move to environment variables',
            'any_type': 'Use specific type annotation',
            'todo_comments': 'Complete the TODO or create a tracking issue',
        }
        return suggestions.get(issue_type, 'Review and fix this issue')
    
    def _get_security_fix(self, issue_type: str) -> str:
        """Get security fix suggestions"""
        fixes = {
            'sql_injection': 'Use parameterized queries or ORM',
            'xss_risk': 'Sanitize user input and use safe DOM methods',
            'path_traversal': 'Validate and sanitize file paths',
            'command_injection': 'Use subprocess with shell=False and validate input',
        }
        return fixes.get(issue_type, 'Apply security best practices')

class CompletionAgent:
    """Agent responsible for improving file completion"""
    
    def __init__(self):
        self.placeholder_indicators = [
            'TODO', 'PLACEHOLDER', 'IMPLEMENT', 'FIXME',
            'not implemented', 'coming soon', 'under construction'
        ]
        
        self.required_sections = {
            'react_component': ['imports', 'types/interfaces', 'component', 'exports'],
            'python_module': ['imports', 'constants', 'classes/functions', 'main'],
            'test_file': ['imports', 'setup', 'test_cases', 'teardown'],
        }
    
    def analyze_completion(self, file_path: str) -> Tuple[float, List[str]]:
        """Analyze file completion and return score with missing elements"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Calculate base completion score
            total_lines = len(lines)
            empty_lines = sum(1 for line in lines if not line.strip())
            placeholder_lines = sum(1 for line in lines if any(ind in line for ind in self.placeholder_indicators))
            
            if total_lines == 0:
                return 0.0, ['File is empty']
            
            # Base score calculation
            content_lines = total_lines - empty_lines
            implemented_lines = content_lines - placeholder_lines
            base_score = (implemented_lines / content_lines * 100) if content_lines > 0 else 0
            
            # Identify missing elements
            missing_elements = []
            
            # Check file type and required sections
            if file_path.endswith('.tsx') or file_path.endswith('.jsx'):
                missing_elements.extend(self._check_react_component(content))
            elif file_path.endswith('.py'):
                missing_elements.extend(self._check_python_module(content))
            elif 'test' in file_path.lower():
                missing_elements.extend(self._check_test_file(content))
            
            # Adjust score based on missing critical elements
            if missing_elements:
                base_score *= (1 - len(missing_elements) * 0.1)
            
            return max(0, min(100, base_score)), missing_elements
            
        except Exception as e:
            return 0.0, [f'Error analyzing file: {str(e)}']
    
    def _check_react_component(self, content: str) -> List[str]:
        """Check React component completeness"""
        missing = []
        
        if 'import React' not in content and 'from \'react\'' not in content:
            missing.append('React import')
        
        if not re.search(r'(interface|type)\s+\w+Props', content):
            missing.append('Props interface/type definition')
        
        if not re.search(r'export\s+(default\s+)?', content):
            missing.append('Component export')
        
        if 'return' not in content:
            missing.append('Component return statement')
        
        return missing
    
    def _check_python_module(self, content: str) -> List[str]:
        """Check Python module completeness"""
        missing = []
        
        if not content.strip().startswith('"""') and not content.strip().startswith("'''"):
            missing.append('Module docstring')
        
        if '__name__' not in content and len(content) > 100:
            missing.append('Main guard (if __name__ == "__main__")')
        
        return missing
    
    def _check_test_file(self, content: str) -> List[str]:
        """Check test file completeness"""
        missing = []
        
        if 'test' not in content.lower() and 'describe' not in content:
            missing.append('Test cases')
        
        if 'assert' not in content and 'expect' not in content:
            missing.append('Assertions')
        
        return missing
    
    def generate_completion_template(self, file_path: str, file_type: str) -> str:
        """Generate a completion template for placeholder files"""
        templates = {
            '.tsx': self._react_component_template,
            '.ts': self._typescript_module_template,
            '.py': self._python_module_template,
        }
        
        ext = Path(file_path).suffix
        template_func = templates.get(ext, self._generic_template)
        return template_func(Path(file_path).stem)
    
    def _react_component_template(self, name: str) -> str:
        """Generate React component template"""
        return f'''import React from 'react';

interface {name}Props {{
  // Add props here
}}

export const {name}: React.FC<{name}Props> = (props) => {{
  return (
    <div>
      <h1>{name}</h1>
      {{/* Add component content here */}}
    </div>
  );
}};

export default {name};
'''
    
    def _typescript_module_template(self, name: str) -> str:
        """Generate TypeScript module template"""
        return f'''/**
 * {name} module
 */

export interface {name}Config {{
  // Add configuration interface
}}

export class {name} {{
  constructor(private config: {name}Config) {{}}
  
  // Add methods here
}}

export default {name};
'''
    
    def _python_module_template(self, name: str) -> str:
        """Generate Python module template"""
        return f'''"""
{name} module
"""

from typing import Dict, List, Optional


class {name}:
    """Main class for {name}"""
    
    def __init__(self):
        """Initialize {name}"""
        pass
    
    # Add methods here


def main():
    """Main entry point"""
    pass


if __name__ == "__main__":
    main()
'''
    
    def _generic_template(self, name: str) -> str:
        """Generic template for unknown file types"""
        return f"// {name} - Implementation required\n"

class AutomatedFixAgent:
    """Agent responsible for automated fixes"""
    
    def __init__(self):
        self.fix_strategies = {
            'alert_statements': self._fix_alert_statements,
            'console_log': self._fix_console_logs,
            'missing_type_annotation': self._fix_missing_types,
            'innerHTML': self._fix_inner_html,
        }
    
    def can_auto_fix(self, issue: FileIssue) -> bool:
        """Check if an issue can be automatically fixed"""
        return issue.type in self.fix_strategies
    
    def fix_issue(self, file_path: str, issue: FileIssue) -> bool:
        """Attempt to fix an issue automatically"""
        if issue.type not in self.fix_strategies:
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            fixed_content = self.fix_strategies[issue.type](content, issue)
            
            if fixed_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return True
        except Exception as e:
            print(f"Error fixing {issue.type} in {file_path}: {e}")
        
        return False
    
    def _fix_alert_statements(self, content: str, issue: FileIssue) -> str:
        """Replace alert statements with console.warn (temporary fix)"""
        # This is a simple fix - in production, use proper notification system
        return re.sub(r'\balert\s*\(', 'console.warn(/* TODO: Replace with proper notification */ ', content)
    
    def _fix_console_logs(self, content: str, issue: FileIssue) -> str:
        """Comment out console.log statements"""
        return re.sub(r'(\s*)(console\.(log|error|warn|info)\s*\([^)]+\);?)', r'\1// \2', content)
    
    def _fix_missing_types(self, content: str, issue: FileIssue) -> str:
        """Add 'any' type annotation (needs manual review)"""
        # This is a temporary fix - developers should add proper types
        return re.sub(
            r'(function|const|let|var)\s+(\w+)\s*=?\s*\(([^)]*)\)\s*(?!:)',
            r'\1 \2 = (\3): any',
            content
        )
    
    def _fix_inner_html(self, content: str, issue: FileIssue) -> str:
        """Replace innerHTML with textContent where possible"""
        # Simple replacement - may need manual review
        return re.sub(r'\.innerHTML\s*=\s*(["\'][^"\']*["\'])', r'.textContent = \1', content)

class ImprovementOrchestrator:
    """Main orchestrator for all improvement agents"""
    
    def __init__(self, auto_fix: bool = False):
        self.quality_agent = CodeQualityAgent()
        self.completion_agent = CompletionAgent()
        self.fix_agent = AutomatedFixAgent()
        self.auto_fix = auto_fix
        self.results = []
    
    def analyze_codebase(self, root_dir: str = '.', patterns: List[str] = None) -> Dict[str, Any]:
        """Analyze entire codebase"""
        if patterns is None:
            patterns = ['*.py', '*.ts', '*.tsx', '*.js', '*.jsx']
        
        files_to_analyze = []
        for pattern in patterns:
            files_to_analyze.extend(Path(root_dir).rglob(pattern))
        
        # Filter out node_modules, venv, etc.
        excluded_dirs = {'node_modules', 'venv', '.git', '__pycache__', 'dist', 'build'}
        files_to_analyze = [
            f for f in files_to_analyze 
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
        
        print(f"🔍 Analyzing {len(files_to_analyze)} files...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_file = {
                executor.submit(self._analyze_file, str(file_path)): file_path
                for file_path in files_to_analyze
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
        
        return self._generate_report()
    
    def _analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyze a single file with all agents"""
        # Quality analysis
        quality_issues = self.quality_agent.analyze_file(file_path)
        
        # Completion analysis
        completion_score, missing_elements = self.completion_agent.analyze_completion(file_path)
        
        # Convert missing elements to issues
        for element in missing_elements:
            quality_issues.append(FileIssue(
                type='missing_element',
                severity='medium',
                message=f'Missing: {element}',
                fix_suggestion=f'Add {element} to complete the file'
            ))
        
        improvements_made = []
        
        # Auto-fix if enabled
        if self.auto_fix:
            for issue in quality_issues[:]:  # Copy list to avoid modification during iteration
                if self.fix_agent.can_auto_fix(issue):
                    if self.fix_agent.fix_issue(file_path, issue):
                        improvements_made.append(f"Fixed: {issue.type}")
                        quality_issues.remove(issue)
        
        # Determine status
        status = self._determine_status(completion_score, quality_issues)
        
        return FileAnalysis(
            path=file_path,
            completion_score=completion_score,
            issues=quality_issues,
            improvements_made=improvements_made,
            status=status
        )
    
    def _determine_status(self, completion_score: float, issues: List[FileIssue]) -> str:
        """Determine file status based on completion and issues"""
        critical_issues = [i for i in issues if i.severity == 'critical']
        
        if completion_score < 25:
            return 'placeholder'
        elif completion_score < 75 or critical_issues:
            return 'incomplete'
        elif completion_score >= 90 and not critical_issues:
            return 'production-ready'
        else:
            return 'complete'
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive improvement report"""
        total_files = len(self.results)
        
        # Calculate statistics
        stats = {
            'total_files': total_files,
            'average_completion': sum(r.completion_score for r in self.results) / total_files if total_files > 0 else 0,
            'status_distribution': {},
            'issue_summary': {},
            'improvements_made': sum(len(r.improvements_made) for r in self.results),
            'critical_issues': sum(1 for r in self.results for i in r.issues if i.severity == 'critical'),
        }
        
        # Count status distribution
        for result in self.results:
            stats['status_distribution'][result.status] = stats['status_distribution'].get(result.status, 0) + 1
        
        # Count issue types
        for result in self.results:
            for issue in result.issues:
                stats['issue_summary'][issue.type] = stats['issue_summary'].get(issue.type, 0) + 1
        
        # Find worst files
        worst_files = sorted(self.results, key=lambda x: (x.completion_score, -len(x.issues)))[:10]
        
        # Find files with critical issues
        critical_files = [r for r in self.results if any(i.severity == 'critical' for i in r.issues)]
        
        report = {
            'timestamp': datetime.now(UTC).isoformat(),
            'statistics': stats,
            'worst_files': [asdict(f) for f in worst_files],
            'critical_files': [asdict(f) for f in critical_files],
            'all_results': [asdict(r) for r in self.results],
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_path: str = 'improvement_report.json'):
        """Save report to file"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Also generate markdown summary
        self._generate_markdown_summary(report, output_path.replace('.json', '.md'))
    
    def _generate_markdown_summary(self, report: Dict[str, Any], output_path: str):
        """Generate markdown summary of the report"""
        stats = report['statistics']
        
        markdown = f"""# Code Improvement Report
Generated: {report['timestamp']}

## Summary Statistics
- **Total Files Analyzed**: {stats['total_files']}
- **Average Completion**: {stats['average_completion']:.1f}%
- **Critical Issues**: {stats['critical_issues']}
- **Improvements Made**: {stats['improvements_made']}

## Status Distribution
"""
        
        for status, count in stats['status_distribution'].items():
            percentage = (count / stats['total_files'] * 100) if stats['total_files'] > 0 else 0
            markdown += f"- **{status.title()}**: {count} files ({percentage:.1f}%)\n"
        
        markdown += "\n## Top Issues Found\n"
        for issue_type, count in sorted(stats['issue_summary'].items(), key=lambda x: x[1], reverse=True)[:10]:
            markdown += f"- {issue_type.replace('_', ' ').title()}: {count} occurrences\n"
        
        markdown += "\n## Critical Files Requiring Immediate Attention\n"
        for file_data in report['critical_files'][:10]:
            markdown += f"\n### {file_data['path']}\n"
            markdown += f"- Completion: {file_data['completion_score']:.1f}%\n"
            markdown += f"- Critical Issues:\n"
            for issue in file_data['issues']:
                if issue['severity'] == 'critical':
                    markdown += f"  - {issue['message']} (line {issue['line']})\n"
        
        markdown += "\n## Files Needing Most Work\n"
        for file_data in report['worst_files'][:10]:
            markdown += f"- {file_data['path']}: {file_data['completion_score']:.1f}% complete, {len(file_data['issues'])} issues\n"
        
        with open(output_path, 'w') as f:
            f.write(markdown)

def main():
    parser = argparse.ArgumentParser(description='HardCard Code Improvement Agent System')
    parser.add_argument('--root', default='.', help='Root directory to analyze')
    parser.add_argument('--auto-fix', action='store_true', help='Enable automatic fixes')
    parser.add_argument('--patterns', nargs='+', help='File patterns to analyze')
    parser.add_argument('--output', default='improvement_report.json', help='Output report file')
    
    args = parser.parse_args()
    
    orchestrator = ImprovementOrchestrator(auto_fix=args.auto_fix)
    
    print("🤖 Starting HardCard Improvement Agent System...")
    report = orchestrator.analyze_codebase(args.root, args.patterns)
    
    orchestrator.save_report(report, args.output)
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 Report saved to: {args.output}")
    print(f"📝 Markdown summary: {args.output.replace('.json', '.md')}")
    
    # Print quick summary
    stats = report['statistics']
    print(f"\n📈 Quick Summary:")
    print(f"   - Files analyzed: {stats['total_files']}")
    print(f"   - Average completion: {stats['average_completion']:.1f}%")
    print(f"   - Critical issues: {stats['critical_issues']}")
    print(f"   - Auto-fixes applied: {stats['improvements_made']}")

if __name__ == '__main__':
    main()