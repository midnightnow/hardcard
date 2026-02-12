const playwright = require('playwright');

(async () => {
  const browser = await playwright.chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  const consoleMessages = [];
  page.on('console', msg => consoleMessages.push(`${msg.type()}: ${msg.text()}`));
  
  try {
    console.log('Loading http://localhost:3002...');
    await page.goto('http://localhost:3002', { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(5000);
    
    console.log('\nCONSOLE MESSAGES:');
    consoleMessages.forEach(msg => console.log(msg));
    
    const hasElements = await page.evaluate(() => {
      return {
        main: !!document.querySelector('main'),
        nav: !!document.querySelector('nav'), 
        header: !!document.querySelector('header'),
        rootContent: document.querySelector('#root').innerHTML.length,
        title: document.title,
        readyState: document.readyState
      };
    });
    
    console.log('\nELEMENT CHECK:', hasElements);
    
    const html = await page.content();
    console.log('\nHTML STRUCTURE (first 500 chars):');
    console.log(html.substring(0, 500));
    
  } catch (error) {
    console.log('ERROR:', error.message);
  }
  
  await browser.close();
})();