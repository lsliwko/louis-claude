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
            if g == 'options/index.html' and w == 390:
                # choose a voice on the Voice page, then a game must use it (fake British voices, as on an iPhone)
                fake = '''(()=>{const vs=[['Daniel','com.apple.voice.super-compact.en-GB.Daniel'],['Daniel','com.apple.voice.compact.en-GB.Daniel'],['Daniel','com.apple.voice.compact.en-GB.Daniel'],['Martha','com.apple.voice.compact.en-GB.Martha']].map(([n,u])=>({name:n,voiceURI:u,lang:'en-GB',localService:true}));
                  vs.push({name:'Samantha',lang:'en-US',localService:true});speechSynthesis.getVoices=()=>vs;})()'''
                # grown-ups gate: a child's year is refused, an adult's year opens the options
                kid = str(__import__('datetime').date.today().year - 5)
                for d in kid: pg.locator('#keys button', has_text=d).first.click()
                pg.wait_for_timeout(400); shut = pg.evaluate("$('opts').hidden && !$('gate').hidden && !$('list').offsetParent")
                pg.evaluate(fake)
                for d in '1985': pg.locator('#keys button', has_text=d).first.click()
                opened = pg.evaluate("$('opts').hidden===false && $('gate').hidden && !!$('list').offsetParent")
                report('options gate refuses a child, opens for a grown-up', shut and opened, 'child year %s shut %s, 1985 opens %s' % (kid, shut, opened))
                pg.evaluate('draw()')
                rows = pg.locator('.row').count(); pg.locator('.row', has_text='super-compact').locator('.use').click()
                chosen = pg.evaluate("localStorage.getItem('voice')")
                on = pg.locator('.row.on').count()
                pg.add_init_script(fake.replace('(()=>{', '(()=>{try{').replace('})()', '}catch(e){}})()'))
                pg.goto((ROOT / 'scribble/index.html').as_uri()); pg.wait_for_timeout(300); pg.evaluate('pickVoice()')
                used = pg.evaluate('VOICE&&VOICE.voiceURI'); pg.evaluate("localStorage.setItem('voice','phone');pickVoice()"); phone = pg.evaluate('VOICE===null')
                pg.evaluate("localStorage.removeItem('voice');pickVoice()"); auto = pg.evaluate('VOICE&&VOICE.voiceURI')
                ios_default = pg.evaluate('''(()=>{Object.defineProperty(navigator,'userAgent',{configurable:true,get:()=>'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)'});
                  localStorage.removeItem('voice');VOICE=undefined;pickVoice();return VOICE===null})()''')
                report('voice page choice is used by the games', rows == 4 and on == 1 and chosen.startswith('com.apple.voice.super-compact') and used == chosen and phone and ios_default and auto == 'com.apple.voice.compact.en-GB.Daniel',
                       'rows %d (phone + 3: two Daniels, duplicate once), %d marked chosen, chosen %s, game uses %s, phone voice %s, iPhone default is the phone voice %s, without a choice elsewhere %s' % (rows, on, chosen, used, phone, ios_default, auto))
            if g == 'reading/index.html' and w == 390:
                # start button covers the card; its tap says the word inside the tap and uncovers it
                shown = pg.evaluate("!$('go').hidden")
                pg.evaluate('''(()=>{window.__said=[];const ss=speechSynthesis;window.__sp=ss.speak.bind(ss);ss.speak=function(u){window.__said.push(u.text)};
                  $('go').addEventListener('click',()=>{window.__inTap=window.__said.slice()},{once:true})})()''')
                locked = pg.evaluate("document.body.classList.contains('waiting') && $('hear').disabled && [...$('opts').children].every(b=>b.disabled)")
                pg.locator('.opt').first.click(force=True); still = pg.evaluate("tries===0 && res.length===0")
                pg.click('#go'); said = pg.evaluate('window.__inTap||[]'); word = pg.evaluate('order[n].w')
                freed = pg.evaluate("!document.body.classList.contains('waiting') && !$('hear').disabled && [...$('opts').children].every(b=>!b.disabled)")
                report('reading buttons wait for the start tap', locked and still and freed, 'before: locked %s, a tap on a word ignored %s; after: free %s' % (locked, still, freed))
                report('reading start button says the word', shown and pg.evaluate("$('go').hidden") and word in said, 'said in the tap: %s (word %s)' % (said, word))
                pg.evaluate("window.__ac=AC;window.__cheers=0;const c0=cheer;cheer=function(){window.__cheers++;c0()};0")
                pg.click(f".opt[data-w='{word}']"); pg.wait_for_timeout(400)
                report('reading right word gives a gold star', pg.evaluate("res[0]==='ok'"))
                # the word was spoken, so the answer tap must remake the sound engine (inside the tap) and the cheer must play
                fresh = pg.evaluate("AC!==window.__ac && !!AC"); cheers = pg.evaluate('window.__cheers')
                report('reading answer tap after speech remakes the sound and cheers', fresh and cheers == 1, 'new sound engine %s, cheers %d' % (fresh, cheers))
                pg.wait_for_timeout(5000); said2 = pg.evaluate('window.__said'); w2 = pg.evaluate('order[n].w')
                report('reading next word is said when it appears', pg.evaluate('n') == 1 and w2 in said2, 'n %d, said %s' % (pg.evaluate('n'), said2[-2:]))
                # letter case: one case for all four words per question, all three cases turn up, and no word spills out of its button
                cs = pg.evaluate('''(()=>{const seen={},bad=[];const W=['strawberry','screwdriver','watermelon','cat'];
                  for(let i=0;i<60;i++){order[n]=WORDS.find(w=>w.w===W[i%W.length]);show();const t=[...$('opts').children].map(b=>b.textContent);
                    const k=t.every(x=>x===x.toLowerCase())?'lower':t.every(x=>x===x.toUpperCase())?'upper':t.every(x=>x[0]===x[0].toUpperCase()&&x.slice(1)===x.slice(1).toLowerCase())?'title':'mixed';
                    seen[k]=1;[...$('opts').children].forEach(b=>{if(b.scrollWidth>b.clientWidth)bad.push(b.textContent)})}
                  return [Object.keys(seen).sort().join(' '),bad.slice(0,3)]})()''')
                report('reading letter case varies, same for all four words', cs[0] == 'lower title upper' and not cs[1], 'cases %s; spilling %s' % (cs[0], cs[1] or 'none'))
                # two wrong words: grey star, then the next word
                pg.reload(); pg.wait_for_timeout(400); errs.clear(); pg.click('#go'); n0 = pg.evaluate('n')
                for _ in range(2):
                    c = pg.evaluate('order[n].w'); pg.locator(f".opt:not([disabled]):not([data-w='{c}'])").first.click(); pg.wait_for_timeout(200)
                pg.wait_for_timeout(4200)
                moved = pg.evaluate('n') == n0 + 1 and pg.evaluate("res[%d]==='miss'" % n0)
                report('reading two wrong words move on', moved and not errs, '; '.join(errs)[:160] or ('n %d -> %d' % (n0, pg.evaluate('n'))))
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
                slocked = pg.evaluate("document.body.classList.contains('waiting') && $('hear').disabled && $('erase').disabled")
                pg.evaluate('''(()=>{window.__calls=0;const ss=speechSynthesis;window.__sp=ss.speak.bind(ss);
                  Object.defineProperty(ss,'pending',{configurable:true,get:()=>true});
                  ss.speak=function(u){window.__calls++};$('go').addEventListener('click',()=>{window.__inTap=window.__calls},{once:true})})()''')
                pg.click('#go')
                sync = pg.evaluate("(()=>{const ss=speechSynthesis;ss.speak=window.__sp;delete ss.pending;return window.__inTap||0})()")
                gone = pg.evaluate("$('go').hidden")
                sfreed = pg.evaluate("!document.body.classList.contains('waiting') && !$('hear').disabled && !$('erase').disabled")
                report('scribble buttons wait for the start tap', slocked and sfreed, 'locked before %s, free after %s' % (slocked, sfreed))
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
    # stars and prizes: a gold star in a game is banked; the menu shows it; Prizes asks before spending, refuses without
    # enough stars, shows a badge once bought; Options can mark it given (stars stay spent) or give the stars back
    ctx = b.new_context(viewport={'width': 393, 'height': 760}); pg = ctx.new_page(); errs2 = []
    pg.on('pageerror', lambda e: errs2.append(str(e)))
    pg.goto((ROOT / 'reading/index.html').as_uri()); pg.wait_for_timeout(300); pg.evaluate('say=function(){}'); pg.click('#go')
    w = pg.evaluate('order[n].w'); pg.click(f".opt[data-w='{w}']"); pg.wait_for_timeout(200)
    earned = pg.evaluate("JSON.parse(localStorage.getItem('star-bank')).earned")
    pg.goto((ROOT / 'index.html').as_uri()); pg.wait_for_timeout(200); menu = pg.evaluate("document.getElementById('bankn').textContent")
    report('stars from a game are banked and shown on the menu', earned == 1 and menu == '1', 'banked %s, menu shows %s' % (earned, menu))
    pg.goto((ROOT / 'prizes/index.html').as_uri()); pg.wait_for_timeout(200); pg.evaluate('say=function(){}')
    pg.locator('.prize').first.click(); poor = pg.evaluate("$('ask').hidden")
    pg.evaluate("localStorage.setItem('star-bank',JSON.stringify({earned:150,spent:0,owed:{}}));draw()")
    pg.locator('.prize').first.click(); asked = pg.evaluate("!$('ask').hidden"); pg.click('#askno')
    kept = pg.evaluate("JSON.parse(localStorage.getItem('star-bank')).spent") == 0
    pg.locator('.prize').first.click(); pg.click('#askyes'); pg.wait_for_timeout(200)
    bk = pg.evaluate("JSON.parse(localStorage.getItem('star-bank'))"); badge = pg.locator('.prize').first.locator('.owed').count()
    pg.evaluate("localStorage.setItem('star-bank',JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('star-bank')),{earned:400})));draw()")
    pg.locator('.prize').first.click(); again = pg.evaluate("$('ask').hidden")  # one sushi already waiting: can't buy another
    report('prizes ask first, spend stars, show a badge', poor and asked and kept and bk['spent'] == 100 and bk['owed'].get('sushi') == 1 and badge == 1 and again and not errs2,
           'too few: no ask %s; ask %s; cross keeps stars %s; tick: %s, badge %d; a second one refused %s %s' % (poor, asked, kept, bk, badge, again, errs2[:1]))
    pg.evaluate("localStorage.setItem('star-bank',JSON.stringify({earned:300,spent:200,owed:{sushi:1,milkshake:1}}))")
    pg.goto((ROOT / 'options/index.html').as_uri()); pg.wait_for_timeout(200)
    for d in '1985': pg.locator('#keys button', has_text=d).first.click()
    rows = pg.locator('#owed .row').count()
    pg.click('#plus50'); plus = pg.evaluate("JSON.parse(localStorage.getItem('star-bank')).earned")
    pg.click('#minus50'); pg.click('#minus50'); pg.click('#minus50'); pg.click('#minus50'); minus = pg.evaluate("JSON.parse(localStorage.getItem('star-bank')).earned")
    report('options +50 and -50 stars buttons', plus == 350 and minus == 200 and '0 to spend' in pg.evaluate("$('stars').textContent"), 'after +50 earned %s; after 4 x -50 earned %s (spent 200), %s' % (plus, minus, pg.evaluate("$('stars').textContent")))
    pg.click('#plus50'); pg.click('#plus50'); pg.click('#plus50')
    pg.locator('#owed .row', has_text='Sushi').get_by_role('button', name='Given').click()
    pg.locator('#owed .row', has_text='Strawberry').get_by_role('button', name='Give stars back').click()
    bk = pg.evaluate("JSON.parse(localStorage.getItem('star-bank'))")
    report('options: given keeps stars spent, give back returns them', rows == 2 and bk['owed'] == {} and bk['spent'] == 100 and bk['earned'] == 350 and pg.evaluate("!$('noowed').hidden"),
           'rows %d, after: %s' % (rows, bk))
    ctx.close()
    # phone held sideways: every page is covered by the turn-upright picture (nothing underneath can be tapped); upright it's hidden
    side = []
    for g in games:
        pg = b.new_page(viewport={'width': 740, 'height': 360}); pg.goto((ROOT / g).as_uri()); pg.wait_for_timeout(200)
        cov = pg.evaluate("(()=>{const t=document.querySelector('.turnme');const e=document.elementFromPoint(innerWidth/2,innerHeight/2);return !!t&&getComputedStyle(t).display!=='none'&&t.contains(e)})()")
        pg.set_viewport_size({'width': 390, 'height': 740}); pg.wait_for_timeout(100)
        up = pg.evaluate("getComputedStyle(document.querySelector('.turnme')).display==='none'")
        if not (cov and up): side.append(g)
        pg.close()
    report('sideways phone shows the turn-upright cover on every page', not side, ('failed: ' + ' '.join(side)) if side else '%d pages' % len(games))
    b.close()
sys.exit(1 if fails else 0)
