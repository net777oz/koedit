const puppeteer = require('puppeteer');
(async () => {
  console.log('Attempting to launch browser...');
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    console.log('Launch Success!');
    await browser.close();
    process.exit(0);
  } catch (e) {
    console.error('Launch Failed!');
    console.error(e.message);
    process.exit(1);
  }
})();
