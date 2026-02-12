const fs = require('fs');
const path = require('path');

// Function to fix ALL useCallback syntax errors more aggressively
function fixUseCallbackErrors(content) {
    let fixed = content;
    
    // Pattern 1: useCallback without dependency array (ending with }; on same or next line)
    fixed = fixed.replace(
        /(\buseCallback\s*\([^)]*\)\s*=>\s*{[^}]*})\s*;(?!\s*,\s*\[)/gm,
        '$1, []);'
    );
    
    // Pattern 2: useCallback that ends with just } (missing both ; and dependency array)
    fixed = fixed.replace(
        /(\buseCallback\s*\([^)]*\)\s*=>\s*{[^}]*})\s*(?=\n\s*(?:const|let|var|function|return|\/\/|\/\*|\}|export))/gm,
        (match, callback) => {
            if (!callback.includes('], [') && !callback.includes('}, [')) {
                return callback + ', []);';
            }
            return match;
        }
    );
    
    return fixed;
}

// Find all TypeScript/JavaScript files
function findFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory() && !file.includes('node_modules') && !file.startsWith('.')) {
            findFiles(filePath, fileList);
        } else if (file.endsWith('.tsx') || file.endsWith('.ts')) {
            fileList.push(filePath);
        }
    });
    
    return fileList;
}

// Main function
function fixAllCallbacks() {
    const vetsorceryPath = '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src';
    const files = findFiles(vetsorceryPath);
    
    let fixedCount = 0;
    const errors = [];
    
    files.forEach(file => {
        try {
            const content = fs.readFileSync(file, 'utf8');
            
            // Check if file contains useCallback
            if (!content.includes('useCallback')) {
                return;
            }
            
            const fixed = fixUseCallbackErrors(content);
            
            if (content !== fixed) {
                fs.writeFileSync(file, fixed, 'utf8');
                console.log(`Fixed: ${file}`);
                fixedCount++;
            }
        } catch (err) {
            errors.push({ file, error: err.message });
        }
    });
    
    console.log(`\nTotal files fixed: ${fixedCount}`);
    
    if (errors.length > 0) {
        console.log('\nErrors encountered:');
        errors.forEach(({ file, error }) => {
            console.log(`  ${file}: ${error}`);
        });
    }
}

// Run the fix
fixAllCallbacks();