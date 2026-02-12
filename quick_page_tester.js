#!/usr/bin/env node

/**
 * Quick Page Tester - Focused testing for specific issues
 */

const playwright = require('playwright');

async function quickTest() {
    console.log('🔍 Quick Page Testing for Issue Diagnosis');
    
    const browser = await playwright.chromium.launch({ headless: false });
    const page = await browser.newPage();
    
    // Monitor console messages
    const messages = [];
    page.on('console', msg => {
        messages.push(`${msg.type()}: ${msg.text()}`);
    });
    
    // Test HardCard Suite Dashboard
    try {
        console.log('\n📄 Testing HardCard Suite Dashboard...');
        await page.goto('http://localhost:3002/dashboard', { waitUntil: 'networkidle', timeout: 15000 });
        
        const content = await page.evaluate(() => {
            return {
                title: document.title,
                hasContent: document.body.textContent.trim().length > 100,
                contentLength: document.body.textContent.trim().length,
                hasMain: !!document.querySelector('main'),
                hasNav: !!document.querySelector('nav'),
                hasHeader: !!document.querySelector('header'),
                rootContent: document.querySelector('#root')?.innerHTML?.substring(0, 200) || 'NO ROOT CONTENT'
            };
        });
        
        console.log('📊 Content Analysis:', content);
        console.log('🗣️ Console Messages:');
        messages.forEach(msg => console.log(`  ${msg}`));
        
    } catch (error) {
        console.log('❌ Error:', error.message);
    }
    
    await browser.close();
}

quickTest().catch(console.error);