#!/usr/bin/env node

/**
 * Master Page Testing Orchestrator
 * Coordinates expanded testing to maximize working page count
 * Combines targeted testing with comprehensive coverage
 */

const fs = require('fs');
const path = require('path');
const { ExpandedPageTester } = require('./expanded_page_tester.js');
const { ComprehensiveRouteTester } = require('./comprehensive_route_tester.js');

class MasterPageTestingOrchestrator {
    constructor() {
        this.config = {
            baseline_working_pages: 12, // Current known working pages
            target_improvement: 20, // Goal: +20 working pages minimum
            testing_phases: [
                {
                    name: 'expanded_targeted_testing',
                    description: 'Test 70+ carefully selected high-probability routes',
                    tester: 'ExpandedPageTester'
                },
                {
                    name: 'comprehensive_bulk_testing', 
                    description: 'Test ALL 165+ available routes for maximum coverage',
                    tester: 'ComprehensiveRouteTester'
                }
            ],
            output: {
                master_results_dir: '/Users/studio/hardcard/master_testing_results',
                master_reports_dir: '/Users/studio/hardcard/master_testing_reports'
            }
        };

        // Create master output directories
        Object.values(this.config.output).forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });

        this.masterResults = {
            session_id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            baseline: {
                working_pages: this.config.baseline_working_pages,
                target_improvement: this.config.target_improvement
            },
            phases: {},
            final_summary: {
                total_routes_tested: 0,
                total_working_pages: 0,
                total_functional_pages: 0, // working + auth_required
                net_improvement: 0,
                success_rate: 0,
                achievement_rate: 0 // how close we got to target
            },
            recommendations: []
        };
    }

    async orchestrateCompleteTesting() {
        console.log('🎭 MASTER PAGE TESTING ORCHESTRATOR');
        console.log('===================================');
        console.log(`🎯 Goal: Find +${this.config.target_improvement} working pages (baseline: ${this.config.baseline_working_pages})`);
        console.log(`📊 Strategy: Multi-phase testing for maximum coverage\n`);

        try {
            // Phase 1: Expanded Targeted Testing
            console.log('🎯 PHASE 1: EXPANDED TARGETED TESTING');
            console.log('=====================================');
            console.log('Testing 70+ high-probability routes with detailed analysis\n');
            
            const expandedTester = new ExpandedPageTester();
            const expandedResults = await expandedTester.runExpandedTesting();
            
            this.masterResults.phases.expanded_testing = {
                phase: 1,
                name: 'expanded_targeted_testing',
                timestamp: new Date().toISOString(),
                results: expandedResults,
                status: 'completed'
            };

            console.log(`\n✅ Phase 1 Complete:`);
            console.log(`   Working Pages: ${expandedResults.working_count}`);
            console.log(`   Functional Pages: ${expandedResults.functional_count}`);
            console.log(`   Success Rate: ${expandedResults.success_rate}%\n`);

            // Phase 2: Comprehensive Bulk Testing
            console.log('🌟 PHASE 2: COMPREHENSIVE BULK TESTING');
            console.log('======================================');
            console.log('Testing ALL 165+ routes for absolute maximum coverage\n');
            
            const comprehensiveTester = new ComprehensiveRouteTester();
            const comprehensiveResults = await comprehensiveTester.runComprehensiveTesting();
            
            this.masterResults.phases.comprehensive_testing = {
                phase: 2,
                name: 'comprehensive_bulk_testing',
                timestamp: new Date().toISOString(),
                results: comprehensiveResults,
                status: 'completed'
            };

            console.log(`\n✅ Phase 2 Complete:`);
            console.log(`   Working Pages: ${comprehensiveResults.working_count}`);
            console.log(`   Functional Pages: ${comprehensiveResults.functional_count}`);
            console.log(`   Success Rate: ${comprehensiveResults.success_rate}%\n`);

        } catch (error) {
            console.log(`❌ Testing orchestration error: ${error.message}`);
        }

        // Generate master analysis and recommendations
        await this.generateMasterAnalysis();
        
        return this.masterResults;
    }

    async generateMasterAnalysis() {
        console.log('📊 GENERATING MASTER ANALYSIS...\n');

        // Extract best results from both phases
        const expandedResults = this.masterResults.phases.expanded_testing?.results;
        const comprehensiveResults = this.masterResults.phases.comprehensive_testing?.results;

        // Use comprehensive results as primary (should have better coverage)
        const primaryResults = comprehensiveResults || expandedResults;
        const secondaryResults = comprehensiveResults ? expandedResults : null;

        if (primaryResults) {
            this.masterResults.final_summary = {
                total_routes_tested: primaryResults.total_routes || primaryResults.routes_tested || 0,
                total_working_pages: primaryResults.working_count || 0,
                total_functional_pages: primaryResults.functional_count || 0,
                net_improvement: (primaryResults.functional_count || 0) - this.config.baseline_working_pages,
                success_rate: parseFloat(primaryResults.success_rate || '0'),
                achievement_rate: Math.min(100, ((primaryResults.functional_count || 0) - this.config.baseline_working_pages) / this.config.target_improvement * 100)
            };
        }

        // Generate intelligent recommendations
        this.generateRecommendations(primaryResults, secondaryResults);

        // Save master report
        const masterReportPath = path.join(this.config.output.master_reports_dir, 
            `MASTER_TESTING_REPORT_${this.masterResults.session_id}.json`);
        fs.writeFileSync(masterReportPath, JSON.stringify(this.masterResults, null, 2));

        // Generate executive summary
        await this.generateExecutiveSummary();

        // Display final results
        this.displayFinalResults();

        return this.masterResults;
    }

    generateRecommendations(primaryResults, secondaryResults) {
        const recommendations = [];
        const workingCount = primaryResults?.working_count || 0;
        const functionalCount = primaryResults?.functional_count || 0;
        const authRequiredCount = (primaryResults?.auth_required_count || 0);
        const brokenCount = primaryResults?.broken_count || 0;

        // Immediate impact recommendations
        if (workingCount > this.config.baseline_working_pages) {
            recommendations.push({
                priority: 'HIGH',
                type: 'immediate_win',
                title: 'Deploy Working Pages Immediately',
                description: `${workingCount} pages are fully functional and ready for production`,
                impact: `+${workingCount - this.config.baseline_working_pages} working pages`,
                effort: 'LOW'
            });
        }

        // Authentication setup recommendations
        if (authRequiredCount > 0) {
            recommendations.push({
                priority: 'MEDIUM',
                type: 'auth_setup',
                title: 'Enable Authentication for Protected Pages',
                description: `${authRequiredCount} pages load but require authentication`,
                impact: `Potential +${authRequiredCount} functional pages`,
                effort: 'MEDIUM',
                actions: ['Configure user authentication', 'Set up login flow', 'Test protected routes']
            });
        }

        // Bug fixing recommendations
        if (brokenCount > 0) {
            const fixableEstimate = Math.ceil(brokenCount * 0.6); // Assume 60% are fixable
            recommendations.push({
                priority: 'MEDIUM',
                type: 'bug_fixes',
                title: 'Fix Broken Pages',
                description: `${brokenCount} pages have errors, estimated ${fixableEstimate} are fixable`,
                impact: `Potential +${fixableEstimate} working pages`,
                effort: 'HIGH',
                actions: ['Analyze error logs', 'Fix component issues', 'Update dependencies']
            });
        }

        // Goal achievement assessment
        const improvement = functionalCount - this.config.baseline_working_pages;
        if (improvement >= this.config.target_improvement) {
            recommendations.push({
                priority: 'HIGH',
                type: 'goal_achieved',
                title: 'Target Exceeded - Plan Next Phase',
                description: `Goal of +${this.config.target_improvement} pages exceeded with +${improvement} pages`,
                impact: 'Strategic planning needed',
                effort: 'LOW',
                actions: ['Document successful pages', 'Plan feature expansion', 'Set new targets']
            });
        } else {
            const shortfall = this.config.target_improvement - improvement;
            recommendations.push({
                priority: 'HIGH',
                type: 'gap_analysis',
                title: 'Close Remaining Gap',
                description: `${shortfall} more pages needed to reach target of +${this.config.target_improvement}`,
                impact: `Gap: ${shortfall} pages`,
                effort: 'VARIABLE',
                actions: ['Prioritize auth pages', 'Fix easiest broken pages', 'Create new content']
            });
        }

        this.masterResults.recommendations = recommendations;
    }

    async generateExecutiveSummary() {
        const summaryPath = path.join(this.config.output.master_reports_dir, 'EXECUTIVE_SUMMARY.md');
        
        let summary = `# 🎯 EXECUTIVE SUMMARY - EXPANDED PAGE TESTING\n\n`;
        summary += `**Date:** ${new Date().toLocaleString()}\n`;
        summary += `**Objective:** Increase working page count by +${this.config.target_improvement} pages\n`;
        summary += `**Baseline:** ${this.config.baseline_working_pages} working pages\n\n`;

        // Key Results
        summary += `## 🏆 KEY RESULTS\n\n`;
        summary += `| Metric | Value | Target | Status |\n`;
        summary += `|--------|-------|--------|---------|\n`;
        summary += `| Working Pages | ${this.masterResults.final_summary.total_working_pages} | ${this.config.baseline_working_pages + this.config.target_improvement} | ${this.masterResults.final_summary.total_working_pages >= this.config.baseline_working_pages + this.config.target_improvement ? '✅' : '⚠️'} |\n`;
        summary += `| Functional Pages | ${this.masterResults.final_summary.total_functional_pages} | - | - |\n`;
        summary += `| Net Improvement | +${this.masterResults.final_summary.net_improvement} | +${this.config.target_improvement} | ${this.masterResults.final_summary.net_improvement >= this.config.target_improvement ? '✅' : '⚠️'} |\n`;
        summary += `| Success Rate | ${this.masterResults.final_summary.success_rate}% | - | - |\n`;
        summary += `| Achievement Rate | ${this.masterResults.final_summary.achievement_rate.toFixed(1)}% | 100% | ${this.masterResults.final_summary.achievement_rate >= 100 ? '✅' : '⚠️'} |\n\n`;

        // Phase Results
        summary += `## 📊 PHASE RESULTS\n\n`;
        Object.entries(this.masterResults.phases).forEach(([phaseName, phaseData]) => {
            const results = phaseData.results;
            summary += `### ${phaseName.replace(/_/g, ' ').toUpperCase()}\n`;
            if (results) {
                summary += `- **Working Pages:** ${results.working_count || 0}\n`;
                summary += `- **Functional Pages:** ${results.functional_count || 0}\n`;
                summary += `- **Success Rate:** ${results.success_rate || 0}%\n`;
            }
            summary += `- **Status:** ${phaseData.status}\n\n`;
        });

        // Recommendations
        summary += `## 🎯 PRIORITY RECOMMENDATIONS\n\n`;
        this.masterResults.recommendations.forEach((rec, index) => {
            const priorityIcon = rec.priority === 'HIGH' ? '🔥' : rec.priority === 'MEDIUM' ? '⚡' : '💡';
            summary += `### ${priorityIcon} ${rec.title}\n`;
            summary += `**Priority:** ${rec.priority} | **Effort:** ${rec.effort} | **Impact:** ${rec.impact}\n\n`;
            summary += `${rec.description}\n\n`;
            if (rec.actions) {
                summary += `**Actions:**\n`;
                rec.actions.forEach(action => summary += `- ${action}\n`);
                summary += `\n`;
            }
        });

        // Strategic Outlook
        summary += `## 🚀 STRATEGIC OUTLOOK\n\n`;
        const totalPotential = this.masterResults.final_summary.total_working_pages + 
                             Math.ceil((this.masterResults.phases.comprehensive_testing?.results?.auth_required_count || 0) * 0.7);
        
        summary += `**Current State:** ${this.masterResults.final_summary.total_working_pages} working pages\n`;
        summary += `**Near-term Potential:** ~${totalPotential} pages with auth setup\n`;
        summary += `**Strategic Value:** ${this.masterResults.final_summary.net_improvement > 0 ? 'POSITIVE' : 'NEEDS_WORK'}\n\n`;
        
        if (this.masterResults.final_summary.achievement_rate >= 100) {
            summary += `🎉 **SUCCESS:** Target exceeded! Consider expanding goals.\n`;
        } else if (this.masterResults.final_summary.achievement_rate >= 75) {
            summary += `⚡ **GOOD PROGRESS:** Close to target, focus on quick wins.\n`;
        } else {
            summary += `🔧 **NEEDS WORK:** Significant effort required to reach target.\n`;
        }

        fs.writeFileSync(summaryPath, summary);
        console.log(`📄 Executive summary saved: ${summaryPath}`);
    }

    displayFinalResults() {
        console.log('🎉 MASTER TESTING ORCHESTRATION COMPLETE!');
        console.log('=========================================');
        console.log('\n📊 FINAL SCORECARD:');
        console.log(`   Baseline Working Pages: ${this.config.baseline_working_pages}`);
        console.log(`   Final Working Pages: ${this.masterResults.final_summary.total_working_pages}`);
        console.log(`   Net Improvement: +${this.masterResults.final_summary.net_improvement}`);
        console.log(`   Target Achievement: ${this.masterResults.final_summary.achievement_rate.toFixed(1)}%`);
        
        console.log('\n🎯 SUCCESS METRICS:');
        console.log(`   Total Routes Tested: ${this.masterResults.final_summary.total_routes_tested}`);
        console.log(`   Functional Pages: ${this.masterResults.final_summary.total_functional_pages}`);
        console.log(`   Success Rate: ${this.masterResults.final_summary.success_rate}%`);
        
        console.log('\n🔥 TOP RECOMMENDATIONS:');
        this.masterResults.recommendations.slice(0, 3).forEach((rec, index) => {
            console.log(`   ${index + 1}. ${rec.title} (${rec.priority} priority)`);
        });
        
        const status = this.masterResults.final_summary.achievement_rate >= 100 ? 
                       '🎉 TARGET EXCEEDED!' : 
                       this.masterResults.final_summary.achievement_rate >= 75 ?
                       '⚡ STRONG PROGRESS!' : 
                       '🔧 MORE WORK NEEDED';
        
        console.log(`\n${status}`);
        console.log(`Net improvement of +${this.masterResults.final_summary.net_improvement} pages over baseline\n`);
    }
}

// Main execution
async function main() {
    console.log('🎭 Initializing Master Page Testing Orchestration...\n');
    
    const orchestrator = new MasterPageTestingOrchestrator();
    const results = await orchestrator.orchestrateCompleteTesting();
    
    return results;
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = { MasterPageTestingOrchestrator };