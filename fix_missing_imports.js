const fs = require('fs');
const path = require('path');

// Files that need useCallback import
const filesToFix = [
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/components/ConsultNoteForm.tsx',
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/components/SlotTypeFormDialog.tsx',
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/components/StaffFormDialog.tsx',
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/pages/StaffManagementPage.tsx',
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/pages/SlotTypeManagementPage.tsx',
  '/Users/studio/hardcard/hardcard-suite/apps/vetsorcery/src/pages/PricingPage.tsx'
];

function addUseCallbackImport(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Check if useCallback is already imported
    if (content.includes('import') && content.includes('useCallback')) {
      console.log(`useCallback already imported in: ${filePath}`);
      return;
    }
    
    // Find the first React import
    const reactImportMatch = content.match(/import\s+(?:React|\{[^}]*\})\s+from\s+['"]react['"]/);
    
    if (reactImportMatch) {
      const importLine = reactImportMatch[0];
      
      if (importLine.includes('{')) {
        // It's a named import, add useCallback to it
        const newImport = importLine.replace(/\{([^}]*)\}/, (match, imports) => {
          const importList = imports.split(',').map(i => i.trim()).filter(i => i);
          if (!importList.includes('useCallback')) {
            importList.push('useCallback');
          }
          return `{ ${importList.join(', ')} }`;
        });
        content = content.replace(importLine, newImport);
      } else {
        // It's a default import, add a separate line
        const insertPosition = content.indexOf(importLine) + importLine.length;
        content = content.slice(0, insertPosition) + 
                 `\nimport { useCallback } from 'react';` + 
                 content.slice(insertPosition);
      }
      
      fs.writeFileSync(filePath, content, 'utf8');
      console.log(`Fixed import in: ${filePath}`);
    } else {
      console.log(`No React import found in: ${filePath}`);
    }
  } catch (err) {
    console.error(`Error processing ${filePath}:`, err.message);
  }
}

// Fix all files
filesToFix.forEach(addUseCallbackImport);

console.log('\nDone!');