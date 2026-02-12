#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// React performance optimization patterns
const OPTIMIZATION_PATTERNS = {
  // Add React.memo for components that don't need frequent re-renders
  addReactMemo: {
    pattern: /^(export\s+)?const\s+(\w+):\s*React\.FC/,
    replacement: (match, exportKeyword, componentName) => {
      return `${exportKeyword || ''}const ${componentName}: React.FC`;
    },
    memoWrapper: (componentName, content) => {
      return content.replace(
        new RegExp(`export default ${componentName};?$`, 'm'),
        `export default React.memo(${componentName});`
      ).replace(
        /^import React/m,
        'import React, { memo }'
      );
    }
  },

  // Add useMemo for expensive calculations
  addUseMemo: {
    patterns: [
      // Large array operations
      /(\w+)\.map\([^)]+\)\.filter\([^)]+\)/g,
      // Complex object transformations
      /Object\.entries\([^)]+\)\.reduce\([^)]+\)/g,
      // Math calculations
      /Math\.\w+\([^)]+\)/g
    ]
  },

  // Add useCallback for event handlers
  addUseCallback: {
    patterns: [
      /const\s+(\w*[Hh]andle\w*)\s*=\s*\([^)]*\)\s*=>\s*{/g,
      /const\s+(\w*[Oo]n\w*)\s*=\s*\([^)]*\)\s*=>\s*{/g
    ]
  },

  // Fix useEffect cleanup
  fixUseEffectCleanup: {
    patterns: [
      // Event listeners without cleanup
      /useEffect\(\(\)\s*=>\s*{[\s\S]*?addEventListener[\s\S]*?}\s*,\s*\[[^\]]*\]\s*\);/g,
      // Intervals without cleanup
      /useEffect\(\(\)\s*=>\s*{[\s\S]*?setInterval[\s\S]*?}\s*,\s*\[[^\]]*\]\s*\);/g,
      // Timeouts without cleanup
      /useEffect\(\(\)\s*=>\s*{[\s\S]*?setTimeout[\s\S]*?}\s*,\s*\[[^\]]*\]\s*\);/g
    ]
  }
};

// Components that should be memoized (heavy or frequently re-rendered)
const COMPONENTS_TO_MEMOIZE = [
  'Dashboard', 'AdminPage', 'BidForm', 'ProfileForm',
  'StarfieldBackground', 'SpiralVisualization', 'HyperspaceViewer',
  'SystemHealth', 'LoadingScreen', 'ErrorBoundary'
];

// Fix memory leaks in useEffect
function fixUseEffectCleanup(content) {
  let fixed = content;
  
  // Fix addEventListener without cleanup
  fixed = fixed.replace(
    /useEffect\(\(\)\s*=>\s*{\s*([\s\S]*?)addEventListener\(['"]([\w]+)['"],\s*(\w+)\);?([\s\S]*?)}\s*,\s*(\[[^\]]*\])\s*\);/g,
    (match, before, eventType, handler, after, deps) => {
      if (!match.includes('removeEventListener')) {
        return `useEffect(() => {
${before}addEventListener('${eventType}', ${handler});${after}
    return () => removeEventListener('${eventType}', ${handler});
  }, ${deps});`;
      }
      return match;
    }
  );

  // Fix setInterval without cleanup
  fixed = fixed.replace(
    /useEffect\(\(\)\s*=>\s*{\s*([\s\S]*?)const\s+(\w+)\s*=\s*setInterval\([^)]+\);?([\s\S]*?)}\s*,\s*(\[[^\]]*\])\s*\);/g,
    (match, before, intervalVar, after, deps) => {
      if (!match.includes('clearInterval')) {
        return `useEffect(() => {
${before}const ${intervalVar} = setInterval([previous interval args]);${after}
    return () => clearInterval(${intervalVar});
  }, ${deps});`;
      }
      return match;
    }
  );

  // Fix setTimeout patterns that might need cleanup
  fixed = fixed.replace(
    /useEffect\(\(\)\s*=>\s*{\s*([\s\S]*?)const\s+(\w+)\s*=\s*setTimeout\([^)]+\);?([\s\S]*?)}\s*,\s*(\[[^\]]*\])\s*\);/g,
    (match, before, timeoutVar, after, deps) => {
      if (!match.includes('clearTimeout')) {
        return `useEffect(() => {
${before}const ${timeoutVar} = setTimeout([previous timeout args]);${after}
    return () => clearTimeout(${timeoutVar});
  }, ${deps});`;
      }
      return match;
    }
  );

  return fixed;
}

// Add React.memo to component
function addReactMemo(content, componentName) {
  if (content.includes(`React.memo(${componentName})`)) {
    return content; // Already memoized
  }

  // Add React import if not present
  if (!content.includes('import React')) {
    content = `import React from 'react';\n${content}`;
  }

  // Add memo to React import
  content = content.replace(
    /import React(,\s*{\s*([^}]+)\s*})?\s+from\s+['"]react['"];?/,
    (match, hasNamedImports, namedImports) => {
      if (hasNamedImports) {
        if (!namedImports.includes('memo')) {
          return `import React, { ${namedImports}, memo } from 'react';`;
        }
        return match;
      } else {
        return `import React, { memo } from 'react';`;
      }
    }
  );

  // Wrap export with memo
  content = content.replace(
    new RegExp(`export default ${componentName};?`, 'g'),
    `export default memo(${componentName});`
  );

  return content;
}

// Add useMemo for expensive operations
function addUseMemo(content) {
  // Add useMemo import if needed
  if (content.includes('.map(') && content.includes('.filter(') && !content.includes('useMemo')) {
    content = content.replace(
      /import React(,\s*{\s*([^}]+)\s*})?\s+from\s+['"]react['"];?/,
      (match, hasNamedImports, namedImports) => {
        if (hasNamedImports) {
          if (!namedImports.includes('useMemo')) {
            return `import React, { ${namedImports}, useMemo } from 'react';`;
          }
          return match;
        } else {
          return `import React, { useMemo } from 'react';`;
        }
      }
    );
  }

  // Wrap expensive array operations in useMemo
  content = content.replace(
    /const\s+(\w+)\s*=\s*([^;]+\.map\([^)]+\)\.filter\([^)]+\));/g,
    'const $1 = useMemo(() => $2, [/* add dependencies */]);'
  );

  return content;
}

// Add useCallback for event handlers
function addUseCallback(content) {
  // Add useCallback import if needed
  if (content.includes('Handle') && !content.includes('useCallback')) {
    content = content.replace(
      /import React(,\s*{\s*([^}]+)\s*})?\s+from\s+['"]react['"];?/,
      (match, hasNamedImports, namedImports) => {
        if (hasNamedImports) {
          if (!namedImports.includes('useCallback')) {
            return `import React, { ${namedImports}, useCallback } from 'react';`;
          }
          return match;
        } else {
          return `import React, { useCallback } from 'react';`;
        }
      }
    );
  }

  // Wrap event handlers in useCallback
  content = content.replace(
    /const\s+(\w*[Hh]andle\w*)\s*=\s*\(([^)]*)\)\s*=>\s*{/g,
    'const $1 = useCallback(($2) => {',
  );

  return content;
}

// Optimize React component
function optimizeReactComponent(filePath) {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalContent = content;
    
    // Extract component name
    const componentMatch = content.match(/(?:export\s+)?const\s+(\w+):\s*React\.FC/);
    if (!componentMatch) {
      return { optimized: false, reason: 'No React FC component found' };
    }
    
    const componentName = componentMatch[1];
    let optimizations = [];

    // 1. Fix useEffect cleanup issues
    const fixedContent = fixUseEffectCleanup(content);
    if (fixedContent !== content) {
      content = fixedContent;
      optimizations.push('Fixed useEffect cleanup');
    }

    // 2. Add React.memo for heavy components
    if (COMPONENTS_TO_MEMOIZE.includes(componentName)) {
      const memoContent = addReactMemo(content, componentName);
      if (memoContent !== content) {
        content = memoContent;
        optimizations.push('Added React.memo');
      }
    }

    // 3. Add useMemo for expensive operations
    if (content.includes('.map(') && content.includes('.filter(')) {
      const memoContent = addUseMemo(content);
      if (memoContent !== content) {
        content = memoContent;
        optimizations.push('Added useMemo for expensive operations');
      }
    }

    // 4. Add useCallback for event handlers
    if (/const\s+\w*[Hh]andle\w*\s*=/.test(content)) {
      const callbackContent = addUseCallback(content);
      if (callbackContent !== content) {
        content = callbackContent;
        optimizations.push('Added useCallback for event handlers');
      }
    }

    // Write optimized content if changes were made
    if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return { 
        optimized: true, 
        optimizations,
        component: componentName
      };
    }

    return { optimized: false, reason: 'No optimizations needed' };
  } catch (error) {
    return { optimized: false, reason: `Error: ${error.message}` };
  }
}

// Find all React component files
function findReactComponents(dir) {
  const componentFiles = [];
  
  function traverse(currentDir) {
    try {
      const items = fs.readdirSync(currentDir);
      
      for (const item of items) {
        const fullPath = path.join(currentDir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && item !== 'node_modules' && item !== '.git' && item !== 'dist') {
          traverse(fullPath);
        } else if (item.endsWith('.tsx') || item.endsWith('.jsx')) {
          // Check if file contains React components
          try {
            const content = fs.readFileSync(fullPath, 'utf8');
            if (content.includes('React.FC') || content.includes('function') && content.includes('return')) {
              componentFiles.push(fullPath);
            }
          } catch (error) {
            // Skip files we can't read
          }
        }
      }
    } catch (error) {
      // Skip directories we can't read
    }
  }
  
  traverse(dir);
  return componentFiles;
}

// Main execution
function main() {
  console.log('🚀 Starting React Performance Optimization');
  console.log('==========================================\n');
  
  const startTime = Date.now();
  const componentFiles = findReactComponents('./hardcard-suite/apps');
  
  console.log(`Found ${componentFiles.length} React component files:\n`);
  
  let totalOptimized = 0;
  let optimizationStats = {};
  
  componentFiles.forEach(filePath => {
    const result = optimizeReactComponent(filePath);
    
    if (result.optimized) {
      totalOptimized++;
      console.log(`✅ Optimized ${result.component} (${path.relative('.', filePath)}):`);
      result.optimizations.forEach(opt => {
        console.log(`   - ${opt}`);
        optimizationStats[opt] = (optimizationStats[opt] || 0) + 1;
      });
      console.log('');
    } else {
      console.log(`ℹ️  Skipped ${path.relative('.', filePath)}: ${result.reason}`);
    }
  });
  
  const endTime = Date.now();
  const duration = ((endTime - startTime) / 1000).toFixed(2);
  
  console.log('\n📊 React Performance Optimization Summary');
  console.log('=========================================');
  console.log(`✅ Processed: ${componentFiles.length} component files`);
  console.log(`🚀 Optimized: ${totalOptimized} components`);
  console.log(`⏱️  Duration: ${duration} seconds`);
  
  console.log('\n🔧 Optimization Types Applied:');
  Object.entries(optimizationStats).forEach(([type, count]) => {
    console.log(`   ${type}: ${count} files`);
  });
  
  if (totalOptimized > 0) {
    console.log('\n🔧 Next Steps:');
    console.log('1. Review the optimized components for correctness');
    console.log('2. Add proper dependency arrays to useMemo and useCallback');
    console.log('3. Test components to ensure functionality is preserved');
    console.log('4. Run performance tests to measure improvements');
  }
  
  console.log('\n✨ React performance optimization complete!');
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = { optimizeReactComponent, findReactComponents };