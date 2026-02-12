#!/usr/bin/env node

/**
 * Page Audit Tool - Identifies missing imports and non-existent files
 */

const fs = require('fs');
const path = require('path');

function auditPages() {
    console.log('🔍 Auditing HardCard Suite Pages');
    console.log('==================================');
    
    const pagesDir = '/Users/studio/hardcard/hardcard-suite/apps/hardcard/src/pages';
    const mainTsxPath = '/Users/studio/hardcard/hardcard-suite/apps/hardcard/src/main.tsx';
    
    // Get all actual page files
    const actualFiles = fs.readdirSync(pagesDir)
        .filter(file => file.endsWith('.tsx'))
        .map(file => file.replace('.tsx', ''))
        .sort();
    
    console.log(`📁 Found ${actualFiles.length} actual page files`);
    
    // Parse main.tsx for imports
    const mainContent = fs.readFileSync(mainTsxPath, 'utf8');
    const importMatches = mainContent.match(/const (\w+) = lazy\(\(\) => import\("\.\/pages\/(.+?)\.tsx"\)\);/g) || [];
    
    const importedPages = importMatches.map(match => {
        const componentMatch = match.match(/const (\w+) = lazy/);
        const fileMatch = match.match(/import\("\.\/pages\/(.+?)\.tsx"\)/);
        return {
            component: componentMatch[1],
            file: fileMatch[1]
        };
    });
    
    console.log(`📥 Found ${importedPages.length} imported components`);
    
    // Find mismatches
    const importedFileNames = importedPages.map(p => p.file).sort();
    const missingImports = actualFiles.filter(file => !importedFileNames.includes(file));
    const missingFiles = importedFileNames.filter(file => !actualFiles.includes(file));
    
    console.log('\n❌ MISSING IMPORTS (files exist but not imported):');
    missingImports.forEach(file => console.log(`  - ${file}.tsx`));
    
    console.log('\n🚫 MISSING FILES (imported but file doesn\'t exist):');
    missingFiles.forEach(file => console.log(`  - ${file}.tsx`));
    
    console.log('\n📊 SUMMARY:');
    console.log(`Total actual files: ${actualFiles.length}`);
    console.log(`Total imports: ${importedPages.length}`);
    console.log(`Missing imports: ${missingImports.length}`);
    console.log(`Missing files: ${missingFiles.length}`);
    
    if (missingFiles.length > 0) {
        console.log('\n🔧 RECOMMENDED ACTIONS:');
        console.log('1. Create missing page files or remove their imports');
        console.log('2. Add imports for existing pages');
        console.log('3. Add error boundaries to handle missing components gracefully');
    }
    
    return {
        actualFiles,
        importedPages,
        missingImports,
        missingFiles
    };
}

auditPages();