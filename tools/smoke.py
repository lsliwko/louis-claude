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
                pg.evaluate('afterFx=function(){};fireworks=function(){};say=function(){}'); missed = []
                for ch in pg.evaluate('Q.map(q=>q.c)'):
                    pg.evaluate(f'order[n]=Q.find(q=>q.c==={ch!r});res=[];show()')
                    info = pg.evaluate("(()=>{const b=pad.getBoundingClientRect(),rows=[];for(let y=0;y<G;y+=4){let s=null;for(let x=0;x<=G;x++){const on=x<G&&mask[x+y*G];if(on&&s===null)s=x;if(!on&&s!==null){rows.push([s,x-1,y]);s=null}}}return {l:b.left,t:b.top,k:S/G,rows}})()")
                    k = info['k']
                    for x0, x1, y in info['rows']:
                        j = lambda: random.uniform(-3, 3) * k
                        pg.mouse.move(info['l'] + (x0 + .5) * k + j(), info['t'] + (y + .5) * k + j()); pg.mouse.down()
                        pg.mouse.move(info['l'] + (x1 + .5) * k + j(), info['t'] + (y + .5) * k + j(), steps=4); pg.mouse.up()
                        if pg.evaluate('busy||tries>0'): break
                    if pg.evaluate("res[0]!=='ok'"): missed.append(ch)
                report('scribble wobbly tracing earns a star', not missed, ('failed: ' + ' '.join(missed)) if missed else 'all shapes')
            pg.close()
    b.close()
sys.exit(1 if fails else 0)
