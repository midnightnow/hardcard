#!/usr/bin/env python3
"""
VetSorcery Page Completion Tracker
Analyzes all pages and components to track completion levels and prevent shipping placeholders
"""

import os
import json
import re
import ast
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path

class PageCompletionTracker:
    def __init__(self, project_root: str = "/Users/studio/hardcard"):
        self.project_root = project_root
        self.frontend_path = os.path.join(project_root, "HARDCARDSUITE/vetsorcery_extracted/frontend/src")
        
        # Completion criteria weights
        self.criteria_weights = {
            'has_real_content': 30,      # Not just placeholders
            'has_functionality': 25,     # Interactive elements work
            'has_error_handling': 15,    # Proper error boundaries
            'has_loading_states': 10,    # Loading indicators
            'has_accessibility': 10,     # ARIA labels, etc.
            'has_styling': 5,           # Not default/broken styles
            'has_tests': 5              # Unit/integration tests
        }
        
        # Placeholder/incomplete indicators
        self.placeholder_indicators = [
            'TODO', 'FIXME', 'PLACEHOLDER', 'Coming Soon',
            'Under Construction', 'Not Implemented', 'Work in Progress',
            'Lorem ipsum', 'placeholder', 'mock data', 'dummy data',
            'console.log', 'alert(', 'debugger;'
        ]
        
        # Real content indicators
        self.real_content_indicators = [
            'useState', 'useEffect', 'API', 'fetch', 'axios',
            'onSubmit', 'onClick', 'onChange', 'validation',
            'form', 'input', 'button', 'Table', 'Chart'
        ]

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for completion indicators"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e), 'completion': 0}
        
        analysis = {
            'file_path': file_path,
            'relative_path': os.path.relpath(file_path, self.project_root),
            'lines_of_code': len([l for l in content.split('\n') if l.strip()]),
            'file_size': len(content),
            'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            'criteria': {},
            'issues': [],
            'completion_score': 0
        }
        
        # Check each completion criteria
        analysis['criteria']['has_real_content'] = self._check_real_content(content)
        analysis['criteria']['has_functionality'] = self._check_functionality(content)
        analysis['criteria']['has_error_handling'] = self._check_error_handling(content)
        analysis['criteria']['has_loading_states'] = self._check_loading_states(content)
        analysis['criteria']['has_accessibility'] = self._check_accessibility(content)
        analysis['criteria']['has_styling'] = self._check_styling(content)
        analysis['criteria']['has_tests'] = self._check_tests(file_path, content)
        
        # Find specific issues
        analysis['issues'] = self._find_issues(content)
        
        # Calculate weighted completion score
        total_score = 0
        for criteria, passed in analysis['criteria'].items():
            if passed:
                total_score += self.criteria_weights[criteria]
        
        analysis['completion_score'] = min(total_score, 100)
        analysis['completion_level'] = self._get_completion_level(analysis['completion_score'])
        
        return analysis

    def _check_real_content(self, content: str) -> bool:
        """Check if file has real content vs placeholders"""
        placeholder_count = sum(1 for indicator in self.placeholder_indicators 
                              if indicator.lower() in content.lower())
        real_content_count = sum(1 for indicator in self.real_content_indicators 
                               if indicator in content)
        
        # Fail if too many placeholders or no real content
        if placeholder_count > 3:
            return False
        if real_content_count == 0 and len(content) > 100:
            return False
        
        # Check for common placeholder patterns
        placeholder_patterns = [
            r'<div>.*?placeholder.*?</div>',
            r'// TODO:.*',
            r'Coming Soon',
            r'Under Construction',
            r'Not implemented yet'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False
        
        return True

    def _check_functionality(self, content: str) -> bool:
        """Check if component has interactive functionality"""
        functionality_indicators = [
            'useState', 'useEffect', 'useCallback', 'useMemo',
            'onClick', 'onSubmit', 'onChange', 'onFocus', 'onBlur',
            'handleSubmit', 'handleClick', 'handleChange',
            'fetch(', 'axios.', 'api.', 'query', 'mutation'
        ]
        
        return any(indicator in content for indicator in functionality_indicators)

    def _check_error_handling(self, content: str) -> bool:
        """Check for proper error handling"""
        error_handling_indicators = [
            'try {', 'catch', 'ErrorBoundary', 'error',
            'isError', 'hasError', 'onError', 'throw',
            'Error(', '.catch(', 'finally'
        ]
        
        return any(indicator in content for indicator in error_handling_indicators)

    def _check_loading_states(self, content: str) -> bool:
        """Check for loading state management"""
        loading_indicators = [
            'loading', 'isLoading', 'Loading', 'Spinner',
            'pending', 'isPending', 'fetching', 'isFetching',
            'Skeleton', 'Suspense'
        ]
        
        return any(indicator in content for indicator in loading_indicators)

    def _check_accessibility(self, content: str) -> bool:
        """Check for accessibility features"""
        a11y_indicators = [
            'aria-', 'role=', 'alt=', 'title=',
            'tabIndex', 'accessKey', 'label',
            'sr-only', 'screen reader'
        ]
        
        return any(indicator in content for indicator in a11y_indicators)

    def _check_styling(self, content: str) -> bool:
        """Check for proper styling (not just default)"""
        styling_indicators = [
            'className=', 'style=', 'css`', 'styled.',
            'bg-', 'text-', 'p-', 'm-', 'w-', 'h-',  # Tailwind classes
            'flex', 'grid', 'border', 'rounded'
        ]
        
        # Should have styling but not be overly basic
        has_styling = any(indicator in content for indicator in styling_indicators)
        
        # Check for basic/placeholder styling
        basic_styling_patterns = [
            r'className=""',
            r'style={{}}',
            r'<div>\s*</div>',
        ]
        
        has_basic_only = any(re.search(pattern, content) for pattern in basic_styling_patterns)
        
        return has_styling and not has_basic_only

    def _check_tests(self, file_path: str, content: str) -> bool:
        """Check if component has associated tests"""
        # Look for test files
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        test_patterns = [
            f"{base_name}.test.tsx",
            f"{base_name}.test.ts",
            f"{base_name}.spec.tsx",
            f"{base_name}.spec.ts"
        ]
        
        directory = os.path.dirname(file_path)
        test_directory = os.path.join(directory, '__tests__')
        
        # Check in same directory or __tests__ directory
        for pattern in test_patterns:
            if os.path.exists(os.path.join(directory, pattern)):
                return True
            if os.path.exists(os.path.join(test_directory, pattern)):
                return True
        
        # Check for inline tests or test utilities
        test_indicators = [
            'describe(', 'it(', 'test(', 'expect(',
            'jest', 'vitest', 'render(', 'screen.',
            'fireEvent', 'userEvent'
        ]
        
        return any(indicator in content for indicator in test_indicators)

    def _find_issues(self, content: str) -> List[str]:
        """Find specific issues in the code"""
        issues = []
        
        # Check for console.log statements (should be removed in production)
        if 'console.log' in content:
            console_count = content.count('console.log')
            issues.append(f"Found {console_count} console.log statements")
        
        # Check for TODO/FIXME comments
        for indicator in ['TODO', 'FIXME', 'HACK', 'XXX']:
            if indicator in content:
                count = content.count(indicator)
                issues.append(f"Found {count} {indicator} comments")
        
        # Check for common anti-patterns
        anti_patterns = [
            ('any', "TypeScript 'any' type used"),
            ('debugger;', "Debugger statements found"),
            ('alert(', "Alert statements found"),
            ('innerHTML', "Potential XSS risk with innerHTML")
        ]
        
        for pattern, message in anti_patterns:
            if pattern in content:
                issues.append(message)
        
        return issues

    def _get_completion_level(self, score: int) -> str:
        """Convert numeric score to completion level"""
        if score >= 90:
            return "COMPLETE"
        elif score >= 75:
            return "MOSTLY_COMPLETE"
        elif score >= 50:
            return "PARTIALLY_COMPLETE"
        elif score >= 25:
            return "BASIC_STRUCTURE"
        else:
            return "PLACEHOLDER"

    def analyze_all_pages(self) -> Dict[str, Any]:
        """Analyze all pages and components"""
        results = {
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'project_root': self.project_root,
            'total_files': 0,
            'pages': {},
            'components': {},
            'summary': {
                'completion_levels': {
                    'COMPLETE': 0,
                    'MOSTLY_COMPLETE': 0,
                    'PARTIALLY_COMPLETE': 0,
                    'BASIC_STRUCTURE': 0,
                    'PLACEHOLDER': 0
                },
                'average_completion': 0,
                'total_issues': 0,
                'critical_issues': [],
                'ready_for_production': 0
            }
        }
        
        # Find all TypeScript/TSX files
        tsx_files = []
        for root, dirs, files in os.walk(self.frontend_path):
            # Skip node_modules, dist, build directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '.git']]
            
            for file in files:
                if file.endswith(('.tsx', '.ts')) and not file.endswith('.d.ts'):
                    tsx_files.append(os.path.join(root, file))
        
        results['total_files'] = len(tsx_files)
        completion_scores = []
        
        for file_path in tsx_files:
            analysis = self.analyze_file(file_path)
            
            # Categorize as page or component
            relative_path = analysis['relative_path']
            if '/pages/' in relative_path:
                results['pages'][relative_path] = analysis
            else:
                results['components'][relative_path] = analysis
            
            # Update summary statistics
            if 'completion_score' in analysis:
                completion_scores.append(analysis['completion_score'])
                level = analysis['completion_level']
                results['summary']['completion_levels'][level] += 1
                
                # Count issues
                if 'issues' in analysis:
                    results['summary']['total_issues'] += len(analysis['issues'])
                    
                    # Flag critical issues
                    for issue in analysis['issues']:
                        if any(critical in issue.lower() for critical in ['debugger', 'alert', 'security', 'xss']):
                            results['summary']['critical_issues'].append({
                                'file': relative_path,
                                'issue': issue
                            })
                
                # Count production-ready files (>= 75% complete)
                if analysis['completion_score'] >= 75:
                    results['summary']['ready_for_production'] += 1
        
        # Calculate average completion
        if completion_scores:
            results['summary']['average_completion'] = round(sum(completion_scores) / len(completion_scores), 1)
        
        return results

    def generate_report(self, output_file: str = None) -> str:
        """Generate a completion report"""
        results = self.analyze_all_pages()
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        
        return self._format_report(results)

    def _format_report(self, results: Dict[str, Any]) -> str:
        """Format results into a readable report"""
        summary = results['summary']
        total_files = results['total_files']
        
        report = f"""
🐾 VetSorcery Page Completion Report
Generated: {results['analysis_timestamp']}
Total Files Analyzed: {total_files}

📊 COMPLETION SUMMARY
Average Completion: {summary['average_completion']}%
Production Ready: {summary['ready_for_production']}/{total_files} ({round(summary['ready_for_production']/total_files*100, 1)}%)

📈 COMPLETION LEVELS
✅ Complete (90-100%): {summary['completion_levels']['COMPLETE']}
🟢 Mostly Complete (75-89%): {summary['completion_levels']['MOSTLY_COMPLETE']}
🟡 Partially Complete (50-74%): {summary['completion_levels']['PARTIALLY_COMPLETE']}
🟠 Basic Structure (25-49%): {summary['completion_levels']['BASIC_STRUCTURE']}
🔴 Placeholder (0-24%): {summary['completion_levels']['PLACEHOLDER']}

⚠️ ISSUES FOUND
Total Issues: {summary['total_issues']}
Critical Issues: {len(summary['critical_issues'])}
"""
        
        # Add critical issues details
        if summary['critical_issues']:
            report += "\n🚨 CRITICAL ISSUES:\n"
            for issue in summary['critical_issues'][:10]:  # Show first 10
                report += f"  • {issue['file']}: {issue['issue']}\n"
        
        # Add lowest completion pages
        pages_by_completion = []
        for category in ['pages', 'components']:
            for path, analysis in results[category].items():
                if 'completion_score' in analysis:
                    pages_by_completion.append((path, analysis['completion_score'], analysis['completion_level']))
        
        pages_by_completion.sort(key=lambda x: x[1])  # Sort by completion score
        
        report += "\n🔴 LOWEST COMPLETION PAGES (Need Attention):\n"
        for path, score, level in pages_by_completion[:15]:  # Show bottom 15
            report += f"  • {score:2d}% [{level:20s}] {path}\n"
        
        report += "\n✅ HIGHEST COMPLETION PAGES (Ready for Production):\n"
        for path, score, level in pages_by_completion[-10:]:  # Show top 10
            report += f"  • {score:2d}% [{level:20s}] {path}\n"
        
        return report

    def get_agent_assignments(self) -> Dict[str, List[str]]:
        """Generate task assignments for each AI agent based on completion analysis"""
        results = self.analyze_all_pages()
        
        assignments = {
            'frontend-ai': [],
            'backend-ai': [],
            'testing-ai': [],
            'docs-ai': [],
            'security-ai': []
        }
        
        # Categorize files by completion level and assign to appropriate agents
        for category in ['pages', 'components']:
            for path, analysis in results[category].items():
                if 'completion_score' not in analysis:
                    continue
                
                score = analysis['completion_score']
                level = analysis['completion_level']
                issues = analysis.get('issues', [])
                
                # Assign based on completion level and issues
                if level == 'PLACEHOLDER' or score < 25:
                    assignments['frontend-ai'].append(f"🔴 URGENT: Complete placeholder page {path} (Score: {score}%)")
                
                elif level == 'BASIC_STRUCTURE' or score < 50:
                    assignments['frontend-ai'].append(f"🟠 HIGH: Add functionality to {path} (Score: {score}%)")
                
                elif level == 'PARTIALLY_COMPLETE' or score < 75:
                    assignments['frontend-ai'].append(f"🟡 MEDIUM: Polish and complete {path} (Score: {score}%)")
                
                # Testing assignments for files without tests
                if not analysis['criteria'].get('has_tests', False) and score > 50:
                    assignments['testing-ai'].append(f"🧪 Add tests for {path} (Score: {score}%)")
                
                # Security assignments for critical issues
                for issue in issues:
                    if any(critical in issue.lower() for critical in ['security', 'xss', 'debugger', 'alert']):
                        assignments['security-ai'].append(f"🚨 Security issue in {path}: {issue}")
                
                # Documentation assignments for complex pages
                if score >= 75 and '/pages/' in path:
                    assignments['docs-ai'].append(f"📚 Document completed page {path}")
        
        return assignments

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze VetSorcery page completion levels')
    parser.add_argument('--output', help='Output JSON file for detailed results')
    parser.add_argument('--assignments', action='store_true', help='Generate agent task assignments')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    tracker = PageCompletionTracker()
    
    if args.assignments:
        assignments = tracker.get_agent_assignments()
        print("🤖 AI AGENT TASK ASSIGNMENTS")
        print("=" * 50)
        
        for agent, tasks in assignments.items():
            if tasks:
                print(f"\n{agent.upper()}:")
                for task in tasks[:10]:  # Show first 10 tasks
                    print(f"  • {task}")
                if len(tasks) > 10:
                    print(f"  ... and {len(tasks) - 10} more tasks")
    else:
        report = tracker.generate_report(args.output)
        print(report)

if __name__ == "__main__":
    main()