const fs = require('fs');
const path = require('path');

// Function to find and fix useCallback hooks missing dependency arrays
function fixUseCallbackInFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  // Pattern to match useCallback functions without dependency arrays
  const useCallbackPattern = /const\s+\w+\s*=\s*useCallback\([^)]*\)\s*=>\s*\{[^}]*\}\s*\);(?!\s*,\s*\[)/g;
  
  // Simple pattern to match useCallback ending with }; but not followed by dependency array
  const simplePattern = /(\s+const\s+\w+\s*=\s*useCallback\([^)]*\)\s*=>\s*\{[\s\S]*?\}\s*)\s*;(\s*$|\s*(?:const|function|return|\/\/))/gm;
  
  let modified = false;
  let newContent = content;
  
  // Replace }; with }, []); for useCallback functions
  newContent = newContent.replace(simplePattern, (match, callbackPart, after) => {
    // Check if there's already a dependency array
    if (callbackPart.includes('], [') || callbackPart.includes('}, [')) {
      return match; // Already has dependency array
    }
    modified = true;
    console.log(`Fixed useCallback in ${filePath}`);
    return callbackPart + ', []);' + after;
  });
  
  if (modified) {
    fs.writeFileSync(filePath, newContent);
    return true;
  }
  return false;
}

// Function to recursively find all .tsx files in pages directory
function findTsxFiles(dir) {
  const files = [];
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      files.push(...findTsxFiles(fullPath));
    } else if (item.endsWith('.tsx')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// Main function
function fixAllFiles() {
  const pagesDir = '/Users/studio/hardcard/hardcard-suite/apps/hardcard/src/pages';
  const componentsDir = '/Users/studio/hardcard/hardcard-suite/apps/hardcard/src/components';
  
  const pageFiles = findTsxFiles(pagesDir);
  const componentFiles = findTsxFiles(componentsDir);
  const allFiles = [...pageFiles, ...componentFiles];
  
  console.log(`Found ${pageFiles.length} page files and ${componentFiles.length} component files (${allFiles.length} total)`);
  
  let fixedCount = 0;
  for (const file of allFiles) {
    if (fixUseCallbackInFile(file)) {
      fixedCount++;
    }
  }
  
  console.log(`Fixed ${fixedCount} files with missing useCallback dependency arrays`);
}

if (require.main === module) {
  fixAllFiles();
}

module.exports = { fixAllFiles };