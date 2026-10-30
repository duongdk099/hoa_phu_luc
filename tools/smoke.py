"""Browser smoke check; install playwright and its chromium browser first."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import threading

from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(root)))
threading.Thread(target=server.serve_forever, daemon=True).start()
errors, failures = [], []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1366, "height": 768})
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: failures.append({"status": response.status, "url": response.url}) if response.status >= 400 else None)
        page.goto(f"http://127.0.0.1:{server.server_port}/", wait_until="networkidle", timeout=120000)
        page.wait_for_timeout(3000)
        print("INITIAL", json.dumps(page.evaluate("({title:document.title, lobby:state.inLobby, canvas:[canvas.width,canvas.height], assets:Object.keys(window.CANVAS_ASSETS).length})"), ensure_ascii=False))
        print("BUTTONS", json.dumps(page.locator("button:visible").evaluate_all("els=>els.map(e=>({id:e.id,text:e.textContent.trim().slice(0,60)}))"), ensure_ascii=False))
        page.locator("#btnLobbyFreeMode").click()
        page.get_by_text("Tiếp Tục Chiến Trường", exact=False).first.click()
        page.wait_for_timeout(3000)
        assert page.evaluate("!state.inLobby && !state.paused && state.time > 0")
        print("RUN", json.dumps(page.evaluate("({time:state.time, wave:state.wave, enemies:state.enemies.length})")))
        (root / "artifacts").mkdir(exist_ok=True)
        page.screenshot(path=str(root / "artifacts/smoke.png"))
        print("ERRORS", json.dumps(errors))
        print("HTTP_FAILURES", json.dumps(failures))
        browser.close()
        assert not errors, errors
        assert not [failure for failure in failures if "127.0.0.1" in failure["url"] and not failure["url"].endswith("favicon.ico")], failures
finally:
    server.shutdown()
