const { chromium } = require('playwright');

const FILE_URL = 'file:///Users/clausmedvesek/Developer/projects/kimi/ai-agents-overview/output/site/index.en.html';

(async () => {
  const consoleMessages = [];
  const pageErrors = [];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  page.on('console', msg => consoleMessages.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', err => pageErrors.push(err.message));

  await page.goto(FILE_URL, { waitUntil: 'load', timeout: 30000 });
  try {
    await page.waitForFunction(() => { const b=document.getElementById('boot'); return !b||b.style.display==='none'||getComputedStyle(b).opacity==='0'; }, { timeout: 6000 });
  } catch(e) {
    await page.evaluate(() => { const b=document.getElementById('boot'); if(b) b.style.display='none'; });
  }
  await page.waitForTimeout(400);

  // Get the loop ScrollTrigger's exact start/end (in scroll pixels)
  const bounds = await page.evaluate(() => {
    const all = ScrollTrigger.getAll();
    const st = all.find(s => s.vars && s.vars.trigger === '.loop-box');
    const lb = document.querySelector('.loop-box');
    const ps = document.querySelector('.pin-spacer');
    return {
      found: !!st,
      start: st ? st.start : null,      // scroll Y where pin begins
      end: st ? st.end : null,          // scroll Y where pin ends
      endMinusStart: st ? (st.end - st.start) : null,
      pinSpacing: st ? st.vars.pinSpacing : null,
      scrub: st ? st.vars.scrub : null,
      varsStart: st ? st.vars.start : null,
      varsEnd: st ? st.vars.end : null,
      loopBoxOffsetTopDoc: lb ? lb.getBoundingClientRect().top + window.scrollY : null,
      pinSpacerHeight: ps ? ps.getBoundingClientRect().height : null,
      viewport68pct: Math.round(window.innerHeight * 0.68),
    };
  });
  console.log('=== Loop ScrollTrigger bounds ===');
  console.log(JSON.stringify(bounds, null, 2));

  if (!bounds.found) { console.log('NO loop ScrollTrigger found — abort.'); await browser.close(); return; }

  // Start 120px BEFORE pin start so we see the none(-1) state and the transition into Think
  const startScroll = bounds.start - 120;
  await page.evaluate((y) => window.scrollTo(0, y), startScroll);
  await page.waitForTimeout(700); // let scrub settle

  console.log('\n=== Full stepped scroll through pin (start-120 .. end+120), 30px steps ===');
  console.log('step | scrollY | lbTop | lbPos | stProgress | active | callout | loopdetailPText');
  const rows = [];
  const totalSteps = Math.ceil(((bounds.end + 120) - startScroll) / 30);
  for (let i = 1; i <= totalSteps; i++) {
    await page.evaluate(() => window.scrollBy(0, 30));
    await page.waitForTimeout(180);
    const s = await page.evaluate(() => {
      const lb = document.querySelector('.loop-box');
      const nodes = Array.from(document.querySelectorAll('.loop-svg .node'));
      const active = nodes.find(n => n.classList.contains('active'));
      const detP = document.querySelector('#loopdetail p');
      const callout = document.getElementById('callout');
      const lbStyle = lb ? getComputedStyle(lb) : null;
      const lbRect = lb ? lb.getBoundingClientRect() : null;
      const all = ScrollTrigger.getAll();
      const st = all.find(x => x.vars && x.vars.trigger === '.loop-box');
      return {
        scrollY: window.scrollY,
        lbTop: lbRect ? Math.round(lbRect.top) : null,
        lbPos: lbStyle ? lbStyle.position : null,
        progress: st ? st.progress : null,
        active: active ? active.getAttribute('data-i') : null,
        calloutOn: callout ? callout.classList.contains('on') : null,
        text: detP ? detP.textContent : null,
      };
    });
    rows.push(s);
    console.log(
      String(i).padStart(3) + ' | ' +
      String(s.scrollY).padStart(6) + ' | ' +
      String(s.lbTop).padStart(5) + ' | ' +
      String(s.lbPos).padEnd(8) + ' | ' +
      (s.progress !== null ? s.progress.toFixed(3) : 'NA').padStart(7) + ' | ' +
      String(s.active === null ? '-' : s.active).padStart(6) + ' | ' +
      String(s.calloutOn).padEnd(5) + ' | ' +
      (s.text ? (s.text.length > 50 ? s.text.slice(0,50)+'...' : s.text) : '(empty)')
    );
  }

  // Distinct text states seen, in order
  console.log('\n=== Distinct active-node / text states observed (in order) ===');
  let prev = null;
  rows.forEach((r, idx) => {
    const key = r.active + '|' + (r.text ? r.text.slice(0,30) : 'empty');
    if (key !== prev) {
      console.log(`  at step ${idx+1}: scrollY=${r.scrollY}, progress=${r.progress!==null?r.progress.toFixed(3):'-'}, activeNode=${r.active===null?'none':r.active}, calloutOn=${r.calloutOn}, text="${r.text?r.text.slice(0,70):''}"`);
      prev = key;
    }
  });

  const errs = consoleMessages.filter(m => m.type === 'error');
  console.log(`\n=== Console errors during full run: ${errs.length} | pageerrors: ${pageErrors.length} ===`);
  errs.forEach(m => console.log('  ERR:', m.text));
  pageErrors.forEach(m => console.log('  PAGEERR:', m));

  await browser.close();
  console.log('\n=== DONE ===');
})().catch(e => { console.error('SCRIPT FATAL:', e); process.exit(1); });
