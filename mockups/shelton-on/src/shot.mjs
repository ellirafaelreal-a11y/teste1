// Rasterise HTML/SVG files with headless Chromium.
// usage: node shot.mjs <jobs.json>
//   jobs.json = [{ "in": "file.html|svg", "out": "file.png", "w": 1000, "h": 800,
//                  "scale": 2, "transparent": true }]
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';

const require = createRequire(import.meta.url);
let pw;
try { pw = require('playwright'); } catch {
  pw = require(path.join(execSync('npm root -g').toString().trim(), 'playwright'));
}
const { chromium } = pw;

const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const browser = await chromium.launch();
for (const j of jobs) {
  const page = await browser.newPage({
    viewport: { width: j.w, height: j.h },
    deviceScaleFactor: j.scale ?? 1,
  });
  let url = pathToFileURL(path.resolve(j.in)).href;
  if (j.in.endsWith('.svg')) {
    const svg = fs.readFileSync(j.in, 'utf8');
    const html = `<!doctype html><html><head><style>html,body{margin:0;background:${j.bg ?? 'transparent'}}svg{display:block;width:${j.w}px;height:${j.h}px}</style></head><body>${svg}</body></html>`;
    const tmp = j.in.replace(/\.svg$/, '.__wrap.html');
    fs.writeFileSync(tmp, html);
    url = pathToFileURL(path.resolve(tmp)).href;
  }
  await page.goto(url, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts && document.fonts.ready);
  await page.screenshot({ path: j.out, omitBackground: j.transparent ?? false, fullPage: false });
  await page.close();
  if (j.in.endsWith('.svg')) fs.unlinkSync(j.in.replace(/\.svg$/, '.__wrap.html'));
  console.log('wrote', j.out);
}
await browser.close();
