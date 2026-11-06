#!/usr/bin/env python3
"""Open every game in a headless phone-sized browser and report problems in one line each.
   python3 tools/smoke.py            quick: loads, no errors, no sideways scroll, plays one Maths answer
   python3 tools/smoke.py --scribble also traces every Scribble shape (slower, about a minute)
   python3 tools/smoke.py --shots    also saves screenshots to /tmp/game-shots/"""
import pathlib, sys, random
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
SHOTS = pathlib.Path('/tmp/game-shots'); full = '--scribble' in sys.argv; shots = '--shots' in sys.argv
games = ['index.html'] + sorted(str(p.relative_to(ROOT)) for p in ROOT.glob('*/index.html'))
fails = 0
def report(name, good, info=''):
    global fails; print(('ok   ' if good else 'FAIL ') + name + (' - ' + info if info else '')); fails += 0 if good else 1
with sync_playwright() as p:
    b = p.chromium.launch()
    for g in games:
        for w in (320, 390):
            pg = b.new_page(viewport={'width': w, 'height': 760}, has_touch=True); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto((ROOT / g).as_uri()); pg.wait_for_timeout(1700 if 'scribble' in g else 400)
            side = pg.evaluate('document.documentElement.scrollWidth>innerWidth')
            report(f'{g} @{w}px', not errs and not side, '; '.join(errs)[:160] or ('sideways scroll' if side else ''))
            if shots and w == 390: SHOTS.mkdir(exist_ok=True); pg.screenshot(path=str(SHOTS / (g.replace('/', '_') + '.png')))
            if g == 'voices/index.html' and w == 390:
                # choose a voice on the Voice page, then a game must use it (fake British voices, as on an iPhone)
                fake = '''(()=>{const vs=['Daniel','Daniel','Daniel (Enhanced)','Serena (Premium)','Martha'].map(n=>({name:n,voiceURI:n,lang:'en-GB',localService:true}));
                  vs.push({name:'Samantha',lang:'en-US',localService:true});speechSynthesis.getVoices=()=>vs;})()'''
                pg.evaluate(fake); pg.evaluate('draw()')
                rows = pg.locator('.row').count(); pg.locator('.row', has_text='Martha').locator('.use').click()
                chosen = pg.evaluate("localStorage.getItem('voice')")
                pg.add_init_script(fake.replace('(()=>{', '(()=>{try{').replace('})()', '}catch(e){}})()'))
                pg.goto((ROOT / 'scribble/index.html').as_uri()); pg.wait_for_timeout(300); pg.evaluate('pickVoice()')
                used = pg.evaluate('VOICE&&VOICE.name'); pg.evaluate("localStorage.setItem('voice','phone');pickVoice()"); phone = pg.evaluate('VOICE===null')
                pg.evaluate("localStorage.removeItem('voice');pickVoice()"); auto = pg.evaluate('VOICE&&VOICE.name')
                report('voice page choice is used by the games', rows == 5 and chosen == 'Martha' and used == 'Martha' and phone and auto != 'Martha' and 'Enhanced' in auto + 'Premium',
                       'rows %d (phone + 4 British, duplicate shown once), chosen %s, game uses %s, phone voice %s, without a choice %s' % (rows, chosen, used, phone, auto))
            if g == 'maths/index.html' and w == 390:
                c = pg.evaluate('ans(order[n])'); pg.click(f".opt:text-is('{c}')"); pg.wait_for_timeout(200)
                report('maths right answer gives a gold star', pg.evaluate("res[0]==='ok'"))
                # two wrong answers: grey star, then the next question (after the answer is said)
                pg.reload(); pg.wait_for_timeout(400); errs.clear(); n0 = pg.evaluate('n')
                for _ in range(2):
                    c = pg.evaluate('ans(order[n])'); pg.locator('.opt:not([disabled])').filter(has_not_text=str(c)).first.click(); pg.wait_for_timeout(200)
                pg.wait_for_timeout(4200)
                moved = pg.evaluate('n') == n0 + 1 and pg.evaluate("res[%d]==='miss'" % n0)
                report('maths two wrong answers move on', moved and not errs, '; '.join(errs)[:160] or ('n %d -> %d' % (n0, pg.evaluate('n'))))
            if g == 'scribble/index.html' and w == 390:
                # opening: a start button covers the pad (on iPhone only a tap, not drawing, turns sound on); tapping it must
                # speak inside the tap even with the silent load-time prompt stuck in the queue, and uncover the pad
                shown = pg.evaluate("!$('go').hidden")
                pg.evaluate('''(()=>{window.__calls=0;const ss=speechSynthesis;window.__sp=ss.speak.bind(ss);
                  Object.defineProperty(ss,'pending',{configurable:true,get:()=>true});
                  ss.speak=function(u){window.__calls++};$('go').addEventListener('click',()=>{window.__inTap=window.__calls},{once:true})})()''')
                pg.click('#go')
                sync = pg.evaluate("(()=>{const ss=speechSynthesis;ss.speak=window.__sp;delete ss.pending;return window.__inTap||0})()")
                gone = pg.evaluate("$('go').hidden")
                report('scribble start button speaks inside the tap', shown and gone and sync > 0, 'shown %s, hidden after tap %s, speak during tap %d' % (shown, gone, sync))
            if g == 'scribble/index.html' and w == 390 and full:
                pg.evaluate('afterFx=function(){};fireworks=function(){};say=function(){}'); missed = []; worst = 0
                # busy phone: a whole stroke (down the l and back up to the middle) arrives as one pointermove with the points batched (coalesced); all of them must be drawn
                bat = pg.evaluate('''(()=>{order[n]=Q.find(q=>q.c==='l');res=[];show();const b=pad.getBoundingClientRect(),cx=b.left+b.width/2;
                  const pt=(y,id)=>({clientX:cx,clientY:b.top+y*b.height,pointerId:id,bubbles:true,cancelable:true,isPrimary:true,pointerType:'touch'});
                  pad.dispatchEvent(new PointerEvent('pointerdown',pt(0.08,7)));
                  const co=[];for(let i=1;i<=40;i++)co.push(new PointerEvent('pointermove',pt(0.08+i*0.02,99)));for(let i=1;i<=19;i++)co.push(new PointerEvent('pointermove',pt(0.88-i*0.02,99)));
                  pad.dispatchEvent(new PointerEvent('pointermove',Object.assign(pt(0.5,7),{coalescedEvents:co})));
                  const c=coverage();pad.dispatchEvent(new PointerEvent('pointerup',pt(0.5,7)));busy=false;done=false;res=[];return c})()''')
                report('scribble batched finger moves draw the whole stroke', bat > 0.9, 'covered %d%% of l from one batched move' % (bat * 100))
                for ch in pg.evaluate('Q.map(q=>q.c)'):
                    pg.evaluate(f'order[n]=Q.find(q=>q.c==={ch!r});res=[];show()')
                    info = pg.evaluate("(()=>{const b=pad.getBoundingClientRect(),rows=[];for(let y=0;y<G;y+=4){let s=null;for(let x=0;x<=G;x++){const on=x<G&&mask[x+y*G];if(on&&s===null)s=x;if(!on&&s!==null){rows.push([s,x-1,y]);s=null}}}return {l:b.left,t:b.top,k:S/G,ri:r,rows}})()")
                    k = info['k']
                    for x0, x1, y in info['rows']:
                        # keep the finger's centre inside the shape (a child follows the stroke, not swiping past its edges)
                        ri = info['ri']; x0, x1 = (x0 + ri, x1 - ri) if x1 - x0 > 2 * ri else ((x0 + x1) / 2,) * 2
                        j = lambda: random.uniform(-3, 3) * k
                        pg.mouse.move(info['l'] + (x0 + .5) * k + j(), info['t'] + (y + .5) * k + j()); pg.mouse.down()
                        pg.mouse.move(info['l'] + (x1 + .5) * k + j(), info['t'] + (y + .5) * k + j(), steps=4); pg.mouse.up()
                        if pg.evaluate('busy||tries>0'): break
                    if pg.evaluate("res[0]!=='ok'"): missed.append(ch)
                    worst = max(worst, pg.evaluate('outside()'))
                report('scribble wobbly tracing earns a star', not missed, ('failed: ' + ' '.join(missed)) if missed else 'all shapes, most ink outside %d%% (limit %d%%)' % (worst * 100, pg.evaluate('OUTSIDE') * 100))
                # following the middle of every stroke (its skeleton) must cover enough of the shape and keep the ink on it
                try:
                    import numpy as np
                    from skimage.morphology import skeletonize
                    from scipy.ndimage import binary_dilation
                    def disc(rad):
                        q = int(np.ceil(rad)); yy, xx = np.mgrid[-q:q + 1, -q:q + 1]; return xx * xx + yy * yy <= rad * rad
                    low = []
                    for ch in pg.evaluate('Q.map(q=>q.c)'):
                        d = pg.evaluate(f'(()=>{{order[n]=Q.find(q=>q.c==={ch!r});show();return {{m:Array.from(mask),d:Array.from(dil),R,r,G,C:COVER,O:OUTSIDE}}}})()')
                        G = d['G']; m = np.array(d['m'], bool).reshape(G, G); dl = np.array(d['d'], bool).reshape(G, G); sk = skeletonize(m)
                        cov = (binary_dilation(sk, disc(d['R'])) & m).sum() / m.sum(); ink = binary_dilation(sk, disc(d['r']))
                        out = (ink & ~dl).sum() / ink.sum(); low.append((cov, ch, out))
                    low.sort(); bad = [c for v, c, o in low if v < d['C'] or o > d['O']]
                    report('scribble centre-line tracing covers the shape', not bad, ('failed: ' + ' '.join(bad)) if bad else 'lowest %s %d%% (need %d%%)' % (low[0][1], low[0][0] * 100, d['C'] * 100))
                except ImportError:
                    print('skip scribble centre-line check (needs numpy, scikit-image, scipy)')
                # scribbling zigzags over the whole pad must not earn a star
                scrib = []
                for ch in ['o', 'l', 'A', '7']:
                    pg.evaluate(f'order[n]=Q.find(q=>q.c==={ch!r});res=[];show()')
                    bx = pg.evaluate('(()=>{const r=pad.getBoundingClientRect();return [r.left,r.top,r.width,r.height]})()')
                    pg.mouse.move(bx[0] + 4, bx[1] + 4); pg.mouse.down()
                    for i in range(1, 25):
                        pg.mouse.move(bx[0] + (bx[2] - 8 if i % 2 else 4), bx[1] + 4 + i * (bx[3] - 8) / 24, steps=6)
                    pg.mouse.up()
                    if pg.evaluate("res[0]==='ok'"): scrib.append(ch)
                report('scribble scribbling over the pad gets no star', not scrib, ('starred: ' + ' '.join(scrib)) if scrib else 'o l A 7')
            pg.close()
    b.close()
sys.exit(1 if fails else 0)
