#!/usr/bin/env python3
"""
VetSorcery Code Review Analysis Script
Uses local static analysis to perform comprehensive code review
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class CodeReviewAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "HARDCARDSUITE/vetsorcery_extracted/backend"
        self.frontend_dir = self.project_root / "HARDCARDSUITE/vetsorcery_extracted/frontend"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "backend_analysis": {},
            "frontend_analysis": {},
            "security_analysis": {},
            "deployment_analysis": {},
            "recommendations": []
        }

    def analyze_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a Python file for code quality metrics"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            analysis = {
                "file": str(file_path.relative_to(self.project_root)),
                "lines_of_code": len(content.splitlines()),
                "functions": [],
                "classes": [],
                "imports": [],
                "issues": [],
                "complexity_score": 0
            }
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append({
                        "name": node.name,
                        "args_count": len(node.args.args),
                        "line": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)]),
                        "has_docstring": ast.get_docstring(node) is not None
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)
            
            # Check for potential issues
            if not content.strip():
                analysis["issues"].append("Empty file")
            
            if len(analysis["functions"]) == 0 and len(analysis["classes"]) == 0:
                analysis["issues"].append("No functions or classes defined")
            
            # Check for missing docstrings
            missing_docs = [f for f in analysis["functions"] if not f["has_docstring"]]
            if missing_docs:
                analysis["issues"].append(f"{len(missing_docs)} functions missing docstrings")
            
            # Simple complexity score
            analysis["complexity_score"] = len(analysis["functions"]) + len(analysis["classes"]) * 2
            
            return analysis
            
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": str(e),
                "issues": ["Failed to parse file"]
            }

    def analyze_javascript_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a JavaScript/TypeScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file": str(file_path.relative_to(self.project_root)),
                "lines_of_code": len(content.splitlines()),
                "functions": len(re.findall(r'\bfunction\b|\b=>\b|\bconst\s+\w+\s*=\s*\(', content)),
                "components": len(re.findall(r'export\s+default\s+\w+|export\s+const\s+\w+', content)),
                "imports": len(re.findall(r'^import\s+', content, re.MULTILINE)),
                "issues": []
            }
            
            # Check for common issues
            if 'console.log' in content:
                analysis["issues"].append("Contains console.log statements")
            
            if 'TODO' in content or 'FIXME' in content:
                analysis["issues"].append("Contains TODO/FIXME comments")
            
            if not content.strip():
                analysis["issues"].append("Empty file")
            
            return analysis
            
        except Exception as e:
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "error": str(e),
                "issues": ["Failed to parse file"]
            }

    def analyze_backend(self):
        """Analyze backend Python code"""
        print("🔍 Analyzing Backend Code...")
        
        backend_files = []
        if self.backend_dir.exists():
            backend_files = list(self.backend_dir.glob("**/*.py"))
        
        analysis = {
            "total_files": len(backend_files),
            "api_modules": [],
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "issues_summary": {},
            "file_analyses": []
        }
        
        for py_file in backend_files:
            file_analysis = self.analyze_python_file(py_file)
            analysis["file_analyses"].append(file_analysis)
            
            # Aggregate stats
            if "lines_of_code" in file_analysis:
                analysis["total_lines"] += file_analysis["lines_of_code"]
                analysis["total_functions"] += len(file_analysis.get("functions", []))
                analysis["total_classes"] += len(file_analysis.get("classes", []))
            
            # Track API modules
            if "/apis/" in str(py_file):
                module_name = py_file.parent.name
                if module_name not in analysis["api_modules"]:
                    analysis["api_modules"].append(module_name)
        
        # Summarize issues
        all_issues = []
        for fa in analysis["file_analyses"]:
            all_issues.extend(fa.get("issues", []))
        
        for issue in all_issues:
            analysis["issues_summary"][issue] = analysis["issues_summary"].get(issue, 0) + 1
        
        self.results["backend_analysis"] = analysis
        print(f"✅ Analyzed {len(backend_files)} Python files")

    def analyze_frontend(self):
        """Analyze frontend TypeScript/JavaScript code"""
        print("🔍 Analyzing Frontend Code...")
        
        frontend_files = []
        if self.frontend_dir.exists():
            frontend_files = list(self.frontend_dir.glob("**/*.tsx")) + \
                           list(self.frontend_dir.glob("**/*.ts")) + \
                           list(self.frontend_dir.glob("**/*.jsx")) + \
                           list(self.frontend_dir.glob("**/*.js"))
            
            # Exclude node_modules
            frontend_files = [f for f in frontend_files if "node_modules" not in str(f)]
        
        analysis = {
            "total_files": len(frontend_files),
            "total_lines": 0,
            "components": 0,
            "issues_summary": {},
            "file_analyses": []
        }
        
        for js_file in frontend_files:
            file_analysis = self.analyze_javascript_file(js_file)
            analysis["file_analyses"].append(file_analysis)
            
            if "lines_of_code" in file_analysis:
                analysis["total_lines"] += file_analysis["lines_of_code"]
                analysis["components"] += file_analysis.get("components", 0)
        
        # Summarize issues
        all_issues = []
        for fa in analysis["file_analyses"]:
            all_issues.extend(fa.get("issues", []))
        
        for issue in all_issues:
            analysis["issues_summary"][issue] = analysis["issues_summary"].get(issue, 0) + 1
        
        self.results["frontend_analysis"] = analysis
        print(f"✅ Analyzed {len(frontend_files)} frontend files")

    def analyze_security(self):
        """Analyze security aspects"""
        print("🔒 Analyzing Security...")
        
        security_issues = []
        security_strengths = []
        
        # Check environment files
        env_files = list(self.backend_dir.glob("**/.env*"))
        if env_files:
            security_issues.append(f"Found {len(env_files)} .env files - ensure they're not committed")
        
        # Check for hardcoded secrets
        for py_file in self.backend_dir.glob("**/*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                        security_issues.append(f"Potential hardcoded password in {py_file.name}")
                    if re.search(r'api_key\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
                        security_issues.append(f"Potential hardcoded API key in {py_file.name}")
            except:
                continue
        
        # Check for authentication in routers
        try:
            with open(self.backend_dir / "routers.json", 'r') as f:
                routers_config = json.load(f)
                auth_disabled = [name for name, config in routers_config["routers"].items() 
                               if config.get("disableAuth", False)]
                if auth_disabled:
                    security_issues.append(f"Authentication disabled for: {', '.join(auth_disabled)}")
                else:
                    security_strengths.append("Authentication enabled for all routers")
        except:
            security_issues.append("Could not read routers.json configuration")
        
        # Check for CORS configuration
        main_py = self.backend_dir / "main.py"
        if main_py.exists():
            try:
                with open(main_py, 'r') as f:
                    content = f.read()
                    if "CORSMiddleware" in content:
                        security_strengths.append("CORS middleware configured")
                    else:
                        security_issues.append("No CORS middleware found")
            except:
                pass
        
        self.results["security_analysis"] = {
            "issues": security_issues,
            "strengths": security_strengths,
            "risk_level": "medium" if len(security_issues) > 3 else "low"
        }
        print(f"✅ Security analysis complete: {len(security_issues)} issues, {len(security_strengths)} strengths")

    def analyze_deployment(self):
        """Analyze deployment configuration"""
        print("🚀 Analyzing Deployment Configuration...")
        
        deployment_files = []
        config_quality = []
        issues = []
        
        # Check for deployment scripts
        scripts = [
            "launch-vetsorcery-live.sh",
            "stop-vetsorcery.sh", 
            "monitor-vetsorcery.sh"
        ]
        
        for script in scripts:
            script_path = self.project_root / script
            if script_path.exists():
                deployment_files.append(script)
                config_quality.append(f"Found deployment script: {script}")
            else:
                issues.append(f"Missing deployment script: {script}")
        
        # Check for configuration files
        config_files = [
            "package.json",
            "requirements.txt",
            ".env.example",
            "routers.json"
        ]
        
        for config_file in config_files:
            if (self.backend_dir / config_file).exists() or (self.frontend_dir / config_file).exists():
                config_quality.append(f"Found config file: {config_file}")
        
        # Check for documentation
        docs = list(self.project_root.glob("**/*.md"))
        if docs:
            config_quality.append(f"Found {len(docs)} documentation files")
        
        self.results["deployment_analysis"] = {
            "deployment_files": deployment_files,
            "configuration_quality": config_quality,
            "issues": issues,
            "documentation_files": len(docs)
        }
        print(f"✅ Deployment analysis complete")

    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("💡 Generating Recommendations...")
        
        recommendations = []
        
        # Backend recommendations
        backend = self.results["backend_analysis"]
        if backend.get("total_functions", 0) > 0:
            functions_without_docs = sum(1 for fa in backend.get("file_analyses", []) 
                                       for f in fa.get("functions", []) if not f.get("has_docstring", False))
            if functions_without_docs > 0:
                recommendations.append({
                    "category": "Documentation",
                    "priority": "medium",
                    "description": f"Add docstrings to {functions_without_docs} functions for better maintainability"
                })
        
        # Security recommendations
        security = self.results["security_analysis"]
        if len(security.get("issues", [])) > 0:
            recommendations.append({
                "category": "Security",
                "priority": "high",
                "description": "Address security issues found in codebase",
                "details": security["issues"]
            })
        
        # API module recommendations
        api_modules = backend.get("api_modules", [])
        if len(api_modules) >= 6:
            recommendations.append({
                "category": "Architecture",
                "priority": "low",
                "description": f"Consider API versioning strategy with {len(api_modules)} modules"
            })
        
        # Frontend recommendations
        frontend = self.results["frontend_analysis"]
        console_logs = frontend.get("issues_summary", {}).get("Contains console.log statements", 0)
        if console_logs > 0:
            recommendations.append({
                "category": "Code Quality",
                "priority": "low",
                "description": f"Remove {console_logs} console.log statements before production"
            })
        
        # Deployment recommendations
        deployment = self.results["deployment_analysis"]
        if len(deployment.get("issues", [])) > 0:
            recommendations.append({
                "category": "DevOps",
                "priority": "medium",
                "description": "Improve deployment configuration",
                "details": deployment["issues"]
            })
        
        self.results["recommendations"] = recommendations
        print(f"✅ Generated {len(recommendations)} recommendations")

    def run_analysis(self):
        """Run complete code review analysis"""
        print("🔍 Starting Comprehensive Code Review Analysis")
        print("=" * 60)
        
        self.analyze_backend()
        self.analyze_frontend()
        self.analyze_security()
        self.analyze_deployment()
        self.generate_recommendations()
        
        return self.results

    def save_report(self, output_file: str = "code_review_report.json"):
        """Save analysis results to file"""
        output_path = self.project_root / output_file
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Report saved to: {output_path}")

def main():
    project_root = "/Users/studio/hardcard"
    analyzer = CodeReviewAnalyzer(project_root)
    
    # Run analysis
    results = analyzer.run_analysis()
    
    # Save detailed report
    analyzer.save_report()
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CODE REVIEW SUMMARY")
    print("=" * 60)
    
    backend = results["backend_analysis"]
    frontend = results["frontend_analysis"]
    security = results["security_analysis"]
    
    print(f"📁 Backend: {backend['total_files']} files, {backend['total_lines']} lines")
    print(f"   └─ {backend['total_functions']} functions, {backend['total_classes']} classes")
    print(f"   └─ {len(backend['api_modules'])} API modules: {', '.join(backend['api_modules'])}")
    
    print(f"📁 Frontend: {frontend['total_files']} files, {frontend['total_lines']} lines")
    print(f"   └─ {frontend['components']} components")
    
    print(f"🔒 Security: {len(security['issues'])} issues, {len(security['strengths'])} strengths")
    print(f"   └─ Risk level: {security['risk_level']}")
    
    print(f"💡 Recommendations: {len(results['recommendations'])}")
    for rec in results["recommendations"]:
        print(f"   └─ [{rec['priority'].upper()}] {rec['category']}: {rec['description']}")
    
    print("\n✅ Code review analysis complete!")

if __name__ == "__main__":
    main()