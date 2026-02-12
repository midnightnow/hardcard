const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function visualTestVetSorcery() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1920, height: 1080 },
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Create screenshots directory
  const screenshotsDir = './vetsorcery_screenshots';
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir);
  }
  
  const issues = [];
  const timestamp = Date.now();
  
  // Helper function to take labeled screenshots
  async function takeScreenshot(label) {
    const filename = `${screenshotsDir}/${timestamp}_${label.replace(/\s+/g, '_')}.png`;
    await page.screenshot({ path: filename, fullPage: true });
    console.log(`📸 Screenshot saved: ${label}`);
    return filename;
  }
  
  // Helper function to analyze visual issues
  async function analyzeVisualIssues() {
    return await page.evaluate(() => {
      const issues = [];
      
      // Check for elements with no height
      const zeroHeightElements = Array.from(document.querySelectorAll('*')).filter(el => {
        const rect = el.getBoundingClientRect();
        return rect.height === 0 && el.children.length === 0 && el.textContent.trim();
      });
      
      if (zeroHeightElements.length > 0) {
        issues.push({
          type: 'layout',
          severity: 'high',
          description: `Found ${zeroHeightElements.length} elements with zero height but containing text`,
          elements: zeroHeightElements.slice(0, 5).map(el => ({
            tag: el.tagName,
            class: el.className,
            text: el.textContent.substring(0, 50)
          }))
        });
      }
      
      // Check for overlapping elements
      const allElements = Array.from(document.querySelectorAll('*:not(script):not(style):not(meta)'));
      const overlapping = [];
      
      for (let i = 0; i < Math.min(allElements.length, 100); i++) {
        const el1 = allElements[i];
        const rect1 = el1.getBoundingClientRect();
        if (rect1.width === 0 || rect1.height === 0) continue;
        
        for (let j = i + 1; j < Math.min(allElements.length, 100); j++) {
          const el2 = allElements[j];
          if (el1.contains(el2) || el2.contains(el1)) continue;
          
          const rect2 = el2.getBoundingClientRect();
          if (rect2.width === 0 || rect2.height === 0) continue;
          
          const overlap = !(rect1.right < rect2.left || 
                          rect2.right < rect1.left || 
                          rect1.bottom < rect2.top || 
                          rect2.bottom < rect1.top);
          
          if (overlap && el1.style.position === 'static' && el2.style.position === 'static') {
            overlapping.push({
              el1: { tag: el1.tagName, class: el1.className },
              el2: { tag: el2.tagName, class: el2.className }
            });
          }
        }
      }
      
      if (overlapping.length > 0) {
        issues.push({
          type: 'layout',
          severity: 'medium',
          description: `Found ${overlapping.length} potentially overlapping elements`,
          elements: overlapping.slice(0, 3)
        });
      }
      
      // Check text contrast
      const textElements = Array.from(document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6, a, button'));
      const lowContrast = [];
      
      textElements.forEach(el => {
        const style = window.getComputedStyle(el);
        const color = style.color;
        const bgColor = style.backgroundColor;
        
        if (color === bgColor && color !== 'rgba(0, 0, 0, 0)') {
          lowContrast.push({
            tag: el.tagName,
            class: el.className,
            color: color,
            text: el.textContent.substring(0, 30)
          });
        }
      });
      
      if (lowContrast.length > 0) {
        issues.push({
          type: 'accessibility',
          severity: 'high',
          description: `Found ${lowContrast.length} elements with potentially invisible text (same color as background)`,
          elements: lowContrast.slice(0, 5)
        });
      }
      
      // Check for broken images
      const images = Array.from(document.querySelectorAll('img'));
      const brokenImages = images.filter(img => !img.complete || img.naturalHeight === 0);
      
      if (brokenImages.length > 0) {
        issues.push({
          type: 'content',
          severity: 'medium',
          description: `Found ${brokenImages.length} broken images`,
          elements: brokenImages.map(img => ({
            src: img.src,
            alt: img.alt
          }))
        });
      }
      
      // Check form elements
      const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
      const unlabeledInputs = inputs.filter(input => {
        const id = input.id;
        const label = id ? document.querySelector(`label[for="${id}"]`) : null;
        return !label && input.type !== 'hidden' && input.type !== 'submit';
      });
      
      if (unlabeledInputs.length > 0) {
        issues.push({
          type: 'accessibility',
          severity: 'medium',
          description: `Found ${unlabeledInputs.length} form inputs without labels`,
          elements: unlabeledInputs.slice(0, 5).map(input => ({
            type: input.type,
            name: input.name,
            placeholder: input.placeholder
          }))
        });
      }
      
      // Check viewport usage
      const viewportWidth = window.innerWidth;
      const bodyWidth = document.body.scrollWidth;
      
      if (bodyWidth > viewportWidth) {
        issues.push({
          type: 'responsive',
          severity: 'high',
          description: 'Page has horizontal scroll',
          details: {
            viewportWidth,
            bodyWidth,
            overflow: bodyWidth - viewportWidth
          }
        });
      }
      
      return issues;
    });
  }
  
  try {
    console.log('🚀 Starting VetSorcery Visual Testing...\n');
    
    // Test 1: Initial page load
    console.log('1. Testing initial page load...');
    await page.goto('http://localhost:3005', { waitUntil: 'networkidle2' });
    await page.waitForTimeout(3000);
    
    await takeScreenshot('01_initial_load');
    
    // Analyze current page
    const currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);
    
    // Test 2: Check if we're on login page
    const isLoginPage = currentUrl.includes('/login');
    if (isLoginPage) {
      console.log('\n2. On login page - analyzing login UI...');
      
      const loginIssues = await analyzeVisualIssues();
      issues.push(...loginIssues);
      
      // Try to find and highlight form elements
      await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
          input.style.border = '2px solid red';
        });
      });
      
      await takeScreenshot('02_login_highlighted');
      
      // Reset borders
      await page.evaluate(() => {
        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
          input.style.border = '';
        });
      });
    }
    
    // Test 3: Check navigation menu
    console.log('\n3. Checking navigation menu...');
    const hasNavigation = await page.$('nav') || await page.$('[role="navigation"]');
    if (hasNavigation) {
      console.log('   ✓ Navigation found');
      
      // Highlight navigation
      await page.evaluate(() => {
        const nav = document.querySelector('nav') || document.querySelector('[role="navigation"]');
        if (nav) nav.style.border = '3px solid green';
      });
      
      await takeScreenshot('03_navigation_highlighted');
    } else {
      console.log('   ✗ No navigation found');
      issues.push({
        type: 'navigation',
        severity: 'high',
        description: 'No navigation menu found on page'
      });
    }
    
    // Test 4: Test different viewport sizes
    console.log('\n4. Testing responsive design...');
    const viewports = [
      { name: 'mobile', width: 375, height: 667 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];
    
    for (const viewport of viewports) {
      await page.setViewport(viewport);
      await page.waitForTimeout(1000);
      await takeScreenshot(`04_viewport_${viewport.name}`);
      
      const responsiveIssues = await analyzeVisualIssues();
      if (responsiveIssues.length > 0) {
        issues.push({
          type: 'responsive',
          severity: 'medium',
          description: `Issues found at ${viewport.name} viewport`,
          viewport: viewport,
          issues: responsiveIssues
        });
      }
    }
    
    // Test 5: Color contrast analysis
    console.log('\n5. Analyzing color contrast and visibility...');
    const contrastAnalysis = await page.evaluate(() => {
      const results = {
        totalTextElements: 0,
        invisibleText: [],
        lowContrastText: []
      };
      
      const textElements = document.querySelectorAll('*');
      textElements.forEach(el => {
        if (el.textContent && el.textContent.trim() && el.children.length === 0) {
          results.totalTextElements++;
          
          const style = window.getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          
          // Check if element is visible
          if (rect.width === 0 || rect.height === 0 || style.display === 'none' || style.visibility === 'hidden') {
            if (el.textContent.trim().length > 0) {
              results.invisibleText.push({
                text: el.textContent.substring(0, 50),
                reason: rect.width === 0 ? 'zero width' : rect.height === 0 ? 'zero height' : 'hidden'
              });
            }
          }
        }
      });
      
      return results;
    });
    
    if (contrastAnalysis.invisibleText.length > 0) {
      issues.push({
        type: 'visibility',
        severity: 'high',
        description: `Found ${contrastAnalysis.invisibleText.length} invisible text elements`,
        details: contrastAnalysis
      });
    }
    
    // Test 6: Check specific VetSorcery components
    console.log('\n6. Checking VetSorcery specific components...');
    
    // Try to click on navigation items if not on login page
    if (!isLoginPage) {
      const navLinks = await page.$$('a[href*="/"], button');
      console.log(`   Found ${navLinks.length} navigation links/buttons`);
      
      // Take screenshot with all interactive elements highlighted
      await page.evaluate(() => {
        document.querySelectorAll('a, button').forEach(el => {
          el.style.outline = '2px dashed blue';
        });
      });
      
      await takeScreenshot('05_interactive_elements');
    }
    
    // Generate report
    const report = {
      timestamp: new Date().toISOString(),
      url: 'http://localhost:3005',
      issues: issues,
      summary: {
        total: issues.length,
        high: issues.filter(i => i.severity === 'high').length,
        medium: issues.filter(i => i.severity === 'medium').length,
        low: issues.filter(i => i.severity === 'low').length
      }
    };
    
    fs.writeFileSync('vetsorcery_visual_report.json', JSON.stringify(report, null, 2));
    
    console.log('\n📊 Visual Testing Summary:');
    console.log('==========================');
    console.log(`Total issues found: ${report.summary.total}`);
    console.log(`High severity: ${report.summary.high}`);
    console.log(`Medium severity: ${report.summary.medium}`);
    console.log(`Low severity: ${report.summary.low}`);
    console.log('\nDetailed report saved to: vetsorcery_visual_report.json');
    console.log(`Screenshots saved in: ${screenshotsDir}/`);
    
  } catch (error) {
    console.error('❌ Error during visual testing:', error);
  } finally {
    await browser.close();
  }
}

// Run the visual tests
visualTestVetSorcery().catch(console.error);