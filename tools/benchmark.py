"""Reproducible local Chromium benchmark. Baseline is the first optimization commit."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import subprocess
import threading
import re
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
baseline = subprocess.check_output(["git", "show", "48c45d0:index.html"], cwd=root)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/baseline.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(baseline)
        elif re.fullmatch(r"/assets/[a-f0-9]{24}\.webp", self.path) and not (root / self.path[1:]).is_file():
            data = subprocess.check_output(["git", "show", "48c45d0:" + self.path[1:]], cwd=root)
            self.send_response(200)
            self.send_header("Content-Type", "image/webp")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(root)))
threading.Thread(target=server.serve_forever, daemon=True).start()
results = {}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, path in [("baseline", "baseline.html"), ("optimized", "index.html")]:
            page = browser.new_page(viewport={"width": 1366, "height": 768})
            page.add_init_script("window.requestAnimationFrame = () => 0;")
            page.add_init_script("let seed=9821;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};")
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{server.server_port}/{path}", wait_until="networkidle", timeout=120000)
            lobby = page.evaluate("""() => ({requests:performance.getEntriesByType('resource').filter(r=>r.name.includes('/assets/')).length,
                encodedBytes:performance.getEntriesByType('resource').filter(r=>r.name.includes('/assets/')).reduce((n,r)=>n+r.encodedBodySize,0)})""")
            page.evaluate("""() => {
                state.inLobby=false;
                if (!GFX._initialized && GFX.ensureInitialized) GFX.ensureInitialized();
                resetGame(); state.inLobby=false; state.paused=false;
                state.player.hp=state.player.maxHp=1e9;
                state.enemies=[];
                let seed=12345; Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
                for(let i=0;i<240;i++) {
                    spawnEnemy('imp');const e=state.enemies[state.enemies.length-1];
                    e.x=state.player.x+(i%20-10)*65;e.y=state.player.y+(Math.floor(i/20)-6)*65;
                }
            }""")
            page.evaluate("drawGame()")
            page.wait_for_timeout(2000)
            if label == "optimized":
                page.wait_for_function("GameRuntime.frames('idle', state.player.dirPose || 'down_diag').length > 0", polling=100, timeout=60000)
            page.wait_for_load_state("networkidle")
            result = page.evaluate("""() => {
                const timings={};
                for(const name of ['drawComprehensiveTerrain','collectDynamicLights','applyShadowTransform','getImageShadowSilhouette','applyDynamicLightingToStructure']) {
                    const original=GFX[name]; if(!original)continue;
                    GFX[name]=function(...args){const t=performance.now();try{return original.apply(this,args)}finally{timings[name]=(timings[name]||0)+performance.now()-t}};
                }
                for(let i=0;i<3;i++)drawGame();
                for(const key of Object.keys(timings))timings[key]=0;
                const draws=[],updates=[];
                for(let i=0;i<30;i++) {
                    let t=performance.now();drawGame();draws.push(performance.now()-t);
                    t=performance.now();updateGame(1/60);updates.push(performance.now()-t);
                }
                const stats=a=>{a.sort((x,y)=>x-y);return {meanMs:a.reduce((n,v)=>n+v,0)/a.length,p50Ms:a[Math.floor(a.length*.5)],p95Ms:a[Math.floor(a.length*.95)]}};
                return {draw:stats(draws),update:stats(updates),gfxTotalMs:timings,
                    caches:GFX.cacheStats?GFX.cacheStats():{terrainBytes:(GFX._terrainQuads||[]).reduce((n,c)=>n+(c?c.width*c.height*4:0),0)}};
            }""")
            result["lobby"] = lobby
            result["errors"] = errors
            results[label] = result
            page.close()
        browser.close()
finally:
    server.shutdown()
(root / "artifacts").mkdir(exist_ok=True)
(root / "artifacts/benchmark.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
print(json.dumps(results, indent=2))
