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
            if g == 'maths/index.html' and w == 390:
                c = pg.evaluate('ans(order[n])'); pg.click(f".opt:text-is('{c}')"); pg.wait_for_timeout(200)
                report('maths right answer gives a gold star', pg.evaluate("res[0]==='ok'"))
            if g == 'scribble/index.html' and w == 390 and full:
                # first touch after opening: the load-time prompt is stuck in the queue (as on iPhone); speech must start inside the touch, not after a delay
                sync = pg.evaluate('''(()=>{spoken=false;let calls=0;const ss=speechSynthesis,sp=ss.speak.bind(ss);
                  Object.defineProperty(ss,'pending',{configurable:true,get:()=>true});ss.speak=function(u){calls++};
                  pad.dispatchEvent(new TouchEvent('touchend',{bubbles:true,cancelable:true}));
                  const c=calls;ss.speak=sp;delete ss.pending;return c})()''')
                report('scribble first touch speaks inside the touch', sync > 0, 'speak called %d time(s) during the touch' % sync)
                pg.evaluate('afterFx=function(){};fireworks=function(){};say=function(){}'); missed = []; worst = 0
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
