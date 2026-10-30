"""Exercise lazy animation, bounded caches, terrain edges, lighting and bosses."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(root)))
threading.Thread(target=server.serve_forever, daemon=True).start()
errors, missing = [], []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.add_init_script("window.requestAnimationFrame=()=>0")
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: missing.append(response.url) if response.status >= 400 and '/assets/' in response.url else None)
        page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="networkidle")
        assert page.evaluate("""() => {
            const urls=new Set(Object.entries(CANVAS_ASSETS).filter(([key])=>key.startsWith('player_')).map(([,path])=>new URL(path,location.href).href));
            return performance.getEntriesByType('resource').every(r=>!urls.has(r.name));
        }""")
        # A cold group stays unpublished until every frame has decoded.
        assert page.evaluate("GameRuntime.frames('run','up').length") == 0
        for action in ['idle', 'run', 'cast', 'run_cast']:
            for pose in ['down', 'down_diag', 'side', 'up_diag', 'up']:
                page.wait_for_function("([a,p])=>GameRuntime.frames(a,p).length>0", arg=[action, pose], polling=100, timeout=60000)
                assert page.evaluate("([a,p])=>GameRuntime.frames(a,p).every(i=>i.complete && i.naturalWidth===256)", [action, pose])
                assert page.evaluate("Object.values(GFX.cacheStats()).every(c=>c.bytes<=c.limit)")
        page.evaluate("state.inLobby=false;resetGame();state.inLobby=false;state.paused=false;drawGame()")
        page.wait_for_function("GFX.cacheStats().images.bytes>0", polling=100)
        page.wait_for_timeout(500)
        # Visit opposite edges and zoom levels, then load every procedural boss sprite.
        stats = page.evaluate("""() => {
            for(const zoom of [.45,.9,1.4]) for(const x of [300,2200,4100]) {
                state.camera.x=x;state.camera.y=x;state.camera.zoom=zoom;drawGame();
                for(const cache of Object.values(GFX.cacheStats())) if(cache.bytes>cache.limit)throw Error('Cache budget exceeded');
            }
            for(const type of ['boss_monkey','boss_fire_demon','boss_serpent','boss_zombie_king','boss_final']) {
                const sprite=GFX.enemySprites[type]; if(!sprite.width)throw Error('Empty boss sprite');
                GFX.getImageShadowSilhouette(sprite);
            }
            return GFX.cacheStats();
        }""")
        # Compare a large bake with adjacent tiles to detect coordinate shifts/seams.
        difference = page.evaluate("""() => {
            const whole=document.createElement('canvas'),split=document.createElement('canvas');
            whole.width=split.width=1100;whole.height=split.height=1100;
            GFX.bakeLushMeadowQuadrant(whole.getContext('2d'),1100,1100,1100,1100);
            for(let y=0;y<2;y++)for(let x=0;x<2;x++){
                const tile=document.createElement('canvas');tile.width=tile.height=550;
                GFX.bakeLushMeadowQuadrant(tile.getContext('2d'),1100+x*550,1100+y*550,550,550);
                split.getContext('2d').drawImage(tile,x*550,y*550);
            }
            const a=whole.getContext('2d').getImageData(0,0,1100,1100).data;
            const b=split.getContext('2d').getImageData(0,0,1100,1100).data;
            let delta=0;for(let i=0;i<a.length;i++)delta+=Math.abs(a[i]-b[i]);
            return delta/a.length;
        }""")
        assert difference < 0.5, difference
        assert not errors, errors
        assert not missing, missing
        print(json.dumps({"animation_groups_checked": 20, "terrain_mean_channel_difference": difference, "caches": stats, "errors": errors, "missing": missing}, indent=2))
        browser.close()
finally:
    server.shutdown()
