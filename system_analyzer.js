#!/usr/bin/env node

/**
 * System Analyzer - Identifies improvement opportunities across the entire HardCard Suite
 */

const fs = require('fs');
const path = require('path');

class SystemAnalyzer {
    constructor() {
        this.baseDir = '/Users/studio/hardcard/hardcard-suite/apps/hardcard/src';
        this.analysis = {
            components_analysis: {},
            dependency_issues: [],
            performance_opportunities: [],
            missing_implementations: [],
            code_quality_issues: [],
            enhancement_opportunities: []
        };
    }

    async analyzeSystem() {
        console.log('🔍 COMPREHENSIVE SYSTEM ANALYSIS');
        console.log('=================================');

        // Analyze all page components
        await this.analyzePageComponents();
        
        // Check for missing dependencies
        await this.checkDependencies();
        
        // Identify performance opportunities
        await this.identifyPerformanceOpportunities();
        
        // Find missing implementations
        await this.findMissingImplementations();
        
        // Generate improvement recommendations
        await this.generateRecommendations();
        
        return this.analysis;
    }

    async analyzePageComponents() {
        console.log('\n📄 Analyzing Page Components...');
        
        const pagesDir = path.join(this.baseDir, 'pages');
        const pages = fs.readdirSync(pagesDir).filter(file => file.endsWith('.tsx'));
        
        let complexPages = 0;
        let simplePages = 0;
        let brokenPages = 0;
        
        for (const pageFile of pages) {
            const pagePath = path.join(pagesDir, pageFile);
            const content = fs.readFileSync(pagePath, 'utf8');
            
            const analysis = this.analyzePageContent(content, pageFile);
            this.analysis.components_analysis[pageFile] = analysis;
            
            if (analysis.complexity === 'complex') complexPages++;
            else if (analysis.complexity === 'simple') simplePages++;
            else if (analysis.complexity === 'broken') brokenPages++;
        }
        
        console.log(`  📊 Pages analyzed: ${pages.length}`);
        console.log(`  🟢 Simple pages: ${simplePages}`);
        console.log(`  🟡 Complex pages: ${complexPages}`);
        console.log(`  🔴 Broken pages: ${brokenPages}`);
    }

    analyzePageContent(content, filename) {
        const analysis = {
            complexity: 'simple',
            imports: [],
            missing_dependencies: [],
            potential_issues: [],
            lines_of_code: content.split('\n').length,
            has_state: false,
            has_effects: false,
            has_complex_logic: false
        };
        
        // Extract imports
        const importMatches = content.match(/import .+ from .+;/g) || [];
        analysis.imports = importMatches;
        
        // Check for missing dependencies
        const problematicImports = [
            'brain',
            'components/Layout',
            '@/components/ui/',
            'lucide-react',
            'recharts',
            'date-fns'
        ];
        
        for (const imp of importMatches) {
            for (const problematic of problematicImports) {
                if (imp.includes(problematic)) {
                    analysis.missing_dependencies.push(problematic);
                    analysis.complexity = 'broken';
                }
            }
        }
        
        // Check complexity indicators
        if (content.includes('useState')) analysis.has_state = true;
        if (content.includes('useEffect')) analysis.has_effects = true;
        if (content.includes('brain') || content.includes('complex')) analysis.has_complex_logic = true;
        
        if (analysis.lines_of_code > 200 || analysis.imports.length > 15) {
            analysis.complexity = 'complex';
        }
        
        return analysis;
    }

    async checkDependencies() {
        console.log('\n📦 Checking Dependencies...');
        
        const packageJsonPath = '/Users/studio/hardcard/hardcard-suite/package.json';
        let packageJson = {};
        
        try {
            packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        } catch (error) {
            console.log('  ❌ Could not read package.json');
            return;
        }
        
        const allDeps = {
            ...packageJson.dependencies || {},
            ...packageJson.devDependencies || {}
        };
        
        // Check for missing common dependencies
        const commonlyNeeded = [
            'lucide-react',
            'recharts', 
            'date-fns',
            '@radix-ui/react-tabs',
            '@radix-ui/react-card',
            'clsx',
            'tailwind-merge'
        ];
        
        for (const dep of commonlyNeeded) {
            if (!allDeps[dep]) {
                this.analysis.dependency_issues.push({
                    type: 'missing_package',
                    package: dep,
                    reason: 'Commonly used in complex components'
                });
            }
        }
        
        console.log(`  📊 Dependencies checked: ${Object.keys(allDeps).length}`);
        console.log(`  ❌ Missing dependencies: ${this.analysis.dependency_issues.length}`);
    }

    async identifyPerformanceOpportunities() {
        console.log('\n⚡ Identifying Performance Opportunities...');
        
        // Check for large components that could be optimized
        for (const [filename, analysis] of Object.entries(this.analysis.components_analysis)) {
            if (analysis.lines_of_code > 300) {
                this.analysis.performance_opportunities.push({
                    type: 'large_component',
                    file: filename,
                    lines: analysis.lines_of_code,
                    suggestion: 'Consider breaking into smaller components'
                });
            }
            
            if (analysis.imports.length > 20) {
                this.analysis.performance_opportunities.push({
                    type: 'heavy_imports',
                    file: filename,
                    imports: analysis.imports.length,
                    suggestion: 'Consider lazy loading or reducing imports'
                });
            }
        }
        
        console.log(`  📊 Performance opportunities found: ${this.analysis.performance_opportunities.length}`);
    }

    async findMissingImplementations() {
        console.log('\n🔍 Finding Missing Implementations...');
        
        // Check for components that need full implementation
        const criticalPages = [
            'Dashboard.tsx',
            'BitcoinWallet.tsx', 
            'Vault.tsx',
            'Alexandria.tsx',
            'HardcardCreator.tsx'
        ];
        
        for (const page of criticalPages) {
            const analysis = this.analysis.components_analysis[page];
            if (analysis) {
                if (analysis.complexity === 'broken') {
                    this.analysis.missing_implementations.push({
                        type: 'broken_component',
                        file: page,
                        issues: analysis.missing_dependencies,
                        priority: 'critical'
                    });
                } else if (analysis.lines_of_code < 50) {
                    this.analysis.missing_implementations.push({
                        type: 'stub_component', 
                        file: page,
                        lines: analysis.lines_of_code,
                        priority: 'high'
                    });
                }
            }
        }
        
        console.log(`  📊 Missing implementations: ${this.analysis.missing_implementations.length}`);
    }

    async generateRecommendations() {
        console.log('\n💡 Generating Improvement Recommendations...');
        
        // High Priority Fixes
        const criticalIssues = this.analysis.missing_implementations.filter(i => i.priority === 'critical');
        const highIssues = this.analysis.missing_implementations.filter(i => i.priority === 'high');
        
        this.analysis.enhancement_opportunities = [
            {
                category: 'Critical Fixes',
                priority: 'critical',
                items: criticalIssues.length,
                description: 'Components with broken dependencies that prevent functionality'
            },
            {
                category: 'Component Development',
                priority: 'high', 
                items: highIssues.length,
                description: 'Stub components that need full implementation'
            },
            {
                category: 'Performance Optimization',
                priority: 'medium',
                items: this.analysis.performance_opportunities.length,
                description: 'Code splitting and optimization opportunities'
            },
            {
                category: 'Dependency Management',
                priority: 'medium',
                items: this.analysis.dependency_issues.length,
                description: 'Missing packages and dependency resolution'
            }
        ];
        
        console.log('  📋 Recommendations generated');
    }

    async generateDetailedReport() {
        const reportPath = '/Users/studio/hardcard/SYSTEM_ANALYSIS_REPORT.md';
        
        let report = `# 🔍 COMPREHENSIVE SYSTEM ANALYSIS REPORT\n\n`;
        report += `**Analysis Date:** ${new Date().toISOString()}\n`;
        report += `**Total Components Analyzed:** ${Object.keys(this.analysis.components_analysis).length}\n\n`;
        
        report += `## 📊 SYSTEM OVERVIEW\n\n`;
        
        const complexCount = Object.values(this.analysis.components_analysis).filter(a => a.complexity === 'complex').length;
        const simpleCount = Object.values(this.analysis.components_analysis).filter(a => a.complexity === 'simple').length;
        const brokenCount = Object.values(this.analysis.components_analysis).filter(a => a.complexity === 'broken').length;
        
        report += `- 🟢 **Simple Components:** ${simpleCount}\n`;
        report += `- 🟡 **Complex Components:** ${complexCount}\n`;
        report += `- 🔴 **Broken Components:** ${brokenCount}\n\n`;
        
        report += `## 🚨 CRITICAL ISSUES\n\n`;
        
        const criticalIssues = this.analysis.missing_implementations.filter(i => i.priority === 'critical');
        if (criticalIssues.length > 0) {
            report += `### Broken Components (${criticalIssues.length})\n`;
            criticalIssues.forEach(issue => {
                report += `- **${issue.file}:** ${issue.issues.join(', ')}\n`;
            });
            report += `\n`;
        }
        
        report += `## 🎯 IMPROVEMENT OPPORTUNITIES\n\n`;
        
        this.analysis.enhancement_opportunities.forEach(opp => {
            const icon = opp.priority === 'critical' ? '🔴' : opp.priority === 'high' ? '🟡' : '🟢';
            report += `### ${icon} ${opp.category} (${opp.items} items)\n`;
            report += `${opp.description}\n\n`;
        });
        
        report += `## 📋 DEPENDENCY ISSUES\n\n`;
        this.analysis.dependency_issues.forEach(dep => {
            report += `- **Missing:** \`${dep.package}\` - ${dep.reason}\n`;
        });
        
        report += `\n## 🚀 NEXT STEPS\n\n`;
        report += `1. **Fix Critical Issues:** Resolve broken component dependencies\n`;
        report += `2. **Implement Stub Components:** Build out minimal components into full functionality\n`;
        report += `3. **Add Missing Dependencies:** Install required packages\n`;
        report += `4. **Optimize Performance:** Implement code splitting and lazy loading\n`;
        
        fs.writeFileSync(reportPath, report);
        console.log(`\n📋 Detailed report saved to: ${reportPath}`);
        
        return reportPath;
    }
}

// Execute analysis
async function main() {
    const analyzer = new SystemAnalyzer();
    await analyzer.analyzeSystem();
    await analyzer.generateDetailedReport();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { SystemAnalyzer };