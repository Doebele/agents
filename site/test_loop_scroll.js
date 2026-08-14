const { chromium } = require('playwright');

const FILE_URL = 'file:///Users/clausmedvesek/Developer/projects/kimi/ai-agents-overview/output/site/index.en.html';

(async () => {
  const consoleMessages = [];
  const pageErrors = [];
  const failedRequests = [];

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  // Capture console
  page.on('console', msg => {
    consoleMessages.push({ type: msg.type(), text: msg.text() });
  });
  page.on('pageerror', err => {
    pageErrors.push(err.message + (err.stack ? '\n' + err.stack : ''));
  });
  page.on('requestfailed', req => {
    failedRequests.push({ url: req.url(), failure: req.failure() && req.failure().errorText });
  });

  console.log('=== STEP 1-2: Navigate (file://) @ 1440x900 ===');
  await page.goto(FILE_URL, { waitUntil: 'load', timeout: 30000 });
  console.log('Navigated OK.');

  // Wait for boot overlay to finish (it hides #boot). Also give GSAP time.
  try {
    await page.waitForFunction(() => {
      const b = document.getElementById('boot');
      return !b || b.style.display === 'none' || getComputedStyle(b).opacity === '0';
    }, { timeout: 6000 });
    console.log('Boot overlay hidden.');
  } catch (e) {
    console.log('Boot overlay did NOT hide within timeout; forcing it.');
    await page.evaluate(() => { const b = document.getElementById('boot'); if (b) { b.style.display='none'; } });
  }
  await page.waitForTimeout(400);

  // STEP 3: Console errors / script load status
  console.log('\n=== STEP 3: JS environment & console errors ===');
  const env = await page.evaluate(() => ({
    hasGsap: typeof gsap !== 'undefined',
    hasScrollTrigger: typeof ScrollTrigger !== 'undefined',
    gsapVersion: (typeof gsap !== 'undefined') ? gsap.version : null,
    scrollTriggerVersion: (typeof ScrollTrigger !== 'undefined') ? ScrollTrigger.version : null,
    scrollTriggerRegistered: (typeof ScrollTrigger !== 'undefined' && gsap && gsap.core) ? !!(gsap.core.globals && gsap.core.globals('ScrollTrigger')) : 'n/a',
    docReady: document.readyState,
    bodyScrollHeight: document.body.scrollHeight,
    innerHeight: window.innerHeight,
  }));
  console.log('ENV:', JSON.stringify(env, null, 2));

  const errs = consoleMessages.filter(m => m.type === 'error');
  const warns = consoleMessages.filter(m => m.type === 'warning');
  console.log(`\nConsole messages total: ${consoleMessages.length}`);
  console.log(`Console ERRORS: ${errs.length}`);
  errs.forEach((m, i) => console.log(`  [err ${i}] ${m.text}`));
  console.log(`Console WARNINGS: ${warns.length}`);
  warns.forEach((m, i) => console.log(`  [warn ${i}] ${m.text}`));
  console.log(`\npageerror count: ${pageErrors.length}`);
  pageErrors.forEach((m, i) => console.log(`  [pageerror ${i}] ${m}`));
  console.log(`\nfailed requests: ${failedRequests.length}`);
  failedRequests.forEach((r, i) => console.log(`  [fail ${i}] ${r.url} -> ${r.failure}`));

  // Helper to read loop state
  async function readState() {
    return page.evaluate(() => {
      const lb = document.querySelector('.loop-box');
      const nodes = Array.from(document.querySelectorAll('.loop-svg .node'));
      const activeNode = nodes.find(n => n.classList.contains('active'));
      const detP = document.querySelector('#loopdetail p');
      const callout = document.getElementById('callout');
      const ctail = document.getElementById('ctail');
      const lbStyle = lb ? getComputedStyle(lb) : null;
      const lbRect = lb ? lb.getBoundingClientRect() : null;
      // ScrollTrigger stores progress on the trigger; try to find it
      let stProgress = null, stActive = null, stPinActive = null;
      if (typeof ScrollTrigger !== 'undefined') {
        const all = ScrollTrigger.getAll ? ScrollTrigger.getAll() : [];
        const loopST = all.find(s => s.vars && (s.vars.trigger === '.loop-box' || (s.trigger && s.trigger.classList && s.trigger.classList.contains('loop-box'))));
        if (loopST) {
          stProgress = loopST.progress;
          stActive = loopST.isActive;
          stPinActive = loopST.pin ? true : false;
        }
        return {
          scrollY: window.scrollY,
          loopBoxRect: lbRect ? {x:Math.round(lbRect.x), y:Math.round(lbRect.y), w:Math.round(lbRect.width), h:Math.round(lbRect.height), top:Math.round(lbRect.top), bottom:Math.round(lbRect.bottom)} : null,
          loopBoxTransform: lbStyle ? lbStyle.transform : null,
          loopBoxPosition: lbStyle ? lbStyle.position : null,
          loopBoxWillChange: lbStyle ? lbStyle.willChange : null,
          loopdetailInnerHTML: document.getElementById('loopdetail') ? document.getElementById('loopdetail').innerHTML : null,
          loopdetailPText: detP ? detP.textContent : null,
          activeNodeIndex: activeNode ? activeNode.getAttribute('data-i') : null,
          activeNodeAria: activeNode ? activeNode.getAttribute('aria-label') : null,
          calloutHasOn: callout ? callout.classList.contains('on') : null,
          ctailD: ctail ? ctail.getAttribute('d') : null,
          stProgress, stActive, stPinActive,
          stTotal: all.length,
        };
      }
      return {
        scrollY: window.scrollY,
        loopBoxRect: lbRect ? {x:Math.round(lbRect.x), y:Math.round(lbRect.y), w:Math.round(lbRect.width), h:Math.round(lbRect.height), top:Math.round(lbRect.top), bottom:Math.round(lbRect.bottom)} : null,
        loopBoxTransform: lbStyle ? lbStyle.transform : null,
        loopBoxPosition: lbStyle ? lbStyle.position : null,
        loopdetailInnerHTML: document.getElementById('loopdetail') ? document.getElementById('loopdetail').innerHTML : null,
        loopdetailPText: detP ? detP.textContent : null,
        activeNodeIndex: activeNode ? activeNode.getAttribute('data-i') : null,
        activeNodeAria: activeNode ? activeNode.getAttribute('aria-label') : null,
        calloutHasOn: callout ? callout.classList.contains('on') : null,
        ctailD: ctail ? ctail.getAttribute('d') : null,
      };
    });
  }

  // STEP 4-9: Initial measurements + pin-spacer + scroll into view
  console.log('\n=== STEP 4-7: Initial element measurements (before scroll) ===');
  const initialDom = await page.evaluate(() => {
    const sec = document.getElementById('sec-loop');
    const lb = document.querySelector('.loop-box');
    const ps = document.querySelector('.pin-spacer');
    const secRect = sec ? sec.getBoundingClientRect() : null;
    const lbRect = lb ? lb.getBoundingClientRect() : null;
    // also check pin-spacer as parent of loop-box
    const lbParent = lb ? lb.parentElement : null;
    return {
      secLoopRect: secRect ? {x:Math.round(secRect.x), y:Math.round(secRect.y), w:Math.round(secRect.width), h:Math.round(secRect.height), top:Math.round(secRect.top), bottom:Math.round(secRect.bottom)} : null,
      secLoopOffsetTop: sec ? sec.offsetTop : null,
      loopBoxRect: lbRect ? {x:Math.round(lbRect.x), y:Math.round(lbRect.y), w:Math.round(lbRect.width), h:Math.round(lbRect.height), top:Math.round(lbRect.top), bottom:Math.round(lbRect.bottom)} : null,
      loopBoxOffsetTop: lb ? lb.getBoundingClientRect().top + window.scrollY : null,
      pinSpacerExists: !!ps,
      pinSpacerClass: lbParent && lbParent.classList.contains('pin-spacer') ? 'loop-box parent IS pin-spacer' : 'loop-box parent is NOT pin-spacer ('+ (lbParent ? lbParent.className : 'none') +')',
      pinSpacerRect: ps ? {w:Math.round(ps.getBoundingClientRect().width), h:Math.round(ps.getBoundingClientRect().height)} : null,
      loopdetailInitial: document.getElementById('loopdetail') ? document.getElementById('loopdetail').innerHTML : null,
    };
  });
  console.log(JSON.stringify(initialDom, null, 2));

  console.log('\n=== STEP 8: Active node before scroll ===');
  const beforeScroll = await readState();
  console.log(JSON.stringify(beforeScroll, null, 2));

  // STEP 9: Scroll loop-box into view (its top - 200px)
  console.log('\n=== STEP 9: Scroll to loop-box top - 200px ===');
  const scrollTarget = initialDom.loopBoxOffsetTop - 200;
  await page.evaluate((y) => { window.scrollTo(0, y); }, scrollTarget);
  console.log('Scrolled window to y =', scrollTarget);

  // STEP 10: wait 500ms
  await page.waitForTimeout(500);

  console.log('\n=== State right after scrolling into view (+500ms) ===');
  const afterScrollInView = await readState();
  console.log(JSON.stringify(afterScrollInView, null, 2));

  // STEP 11: Step-scroll 50px x 20, capturing each
  console.log('\n=== STEP 11: Stepped scroll (50px x 20, 200ms between) ===');
  console.log('step | scrollY | lbTop | lbTransform | stProgress | activeNode | loopdetailPText');
  const rows = [];
  for (let i = 1; i <= 20; i++) {
    await page.evaluate(() => { window.scrollBy(0, 50); });
    await page.waitForTimeout(200);
    const s = await readState();
    const lbTop = s.loopBoxRect ? s.top || s.loopBoxRect.top : null;
    rows.push({ step: i, ...s });
    console.log(
      String(i).padStart(3) + ' | ' +
      String(s.scrollY).padStart(6) + ' | ' +
      String(s.loopBoxRect ? s.loopBoxRect.top : 'NA').padStart(6) + ' | ' +
      String(s.loopBoxTransform || 'none').padEnd(40) + ' | ' +
      String(s.stProgress !== undefined ? s.stProgress.toFixed(3) : 'NA').padStart(9) + ' | ' +
      String(s.activeNodeIndex === null ? '-' : s.activeNodeIndex).padStart(2) + ' | ' +
      (s.loopdetailPText ? (s.loopdetailPText.length > 48 ? s.loopdetailPText.slice(0,48)+'...' : s.loopdetailPText) : '(empty)')
    );
  }

  // Summary of text changes
  console.log('\n=== SUMMARY: loopdetail text changes during scroll ===');
  let lastText = afterScrollInView.loopdetailPText;
  const transitions = [{ at: 'after-scroll-into-view', text: lastText, active: afterScrollInView.activeNodeIndex }];
  for (const r of rows) {
    if (r.loopdetailPText !== lastText) {
      transitions.push({ at: 'step '+r.step, scrollY: r.scrollY, stProgress: r.stProgress, text: r.loopdetailPText, active: r.activeNodeIndex });
      lastText = r.loopdetailPText;
    }
  }
  transitions.forEach(t => console.log('  CHANGE @ ' + t.at + ' (scrollY=' + (t.scrollY!==undefined?t.scrollY:'-') + ', progress=' + (t.stProgress!==undefined&&t.stProgress!==null?t.stProgress.toFixed(3):'-') + ', active=' + (t.active===null?'none':t.active) + '): ' + (t.text ? '"'+t.text.slice(0,70)+'"' : '(empty)')));

  await browser.close();
  console.log('\n=== DONE ===');
})().catch(e => { console.error('SCRIPT FATAL:', e); process.exit(1); });
