"""Extract embedded PNGs and choose smaller lossless encodings. Usage: python tools/optimize.py source.html"""
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import sys

from PIL import Image

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]).read_text(encoding="utf-8")
assets = root / "assets"
assets.mkdir(exist_ok=True)
seen = {}
occurrences = 0


def extract(match):
    global occurrences
    occurrences += 1
    raw = base64.b64decode(match[1])
    key = hashlib.sha256(raw).hexdigest()
    if key not in seen:
        image = Image.open(io.BytesIO(raw))
        cached = assets / f"{key[:24]}.webp"
        output = io.BytesIO()
        if cached.exists():
            encoded = cached.read_bytes()
        else:
            image.save(output, format="WEBP", lossless=True, exact=True, method=6)
            encoded = output.getvalue()
        extension = "webp"
        if len(encoded) >= len(raw):
            encoded, extension = raw, "png"
        # Verify decoded pixels, dimensions and transparency before writing.
        check = Image.open(io.BytesIO(encoded)).convert("RGBA")
        assert check.size == image.size
        assert check.tobytes() == image.convert("RGBA").tobytes()
        name = f"assets/{key[:24]}.{extension}"
        (root / name).write_bytes(encoded)
        seen[key] = {"path": name, "original_bytes": len(raw), "bytes": len(encoded)}
    return seen[key]["path"]


result = re.sub(r"data:image/png;base64,([A-Za-z0-9+/=]+)", extract, source)
# HTML/CSS references are requested before later JS assigns CANVAS_ASSETS.
# Rewrite their old names as well, avoiding missing-file requests on startup.
names = dict(re.findall(r'window\.CANVAS_ASSETS\["([^"\n]+)"\]\s*=\s*"(assets/[^"\n]+)"', result))
if "LệnhLogo" in names:
    names.setdefault("LenhLogo", names["LệnhLogo"])
def rewrite_reference(match):
    return names.get(Path(match[0]).stem, match[0])
result = re.sub(r"assets/(?:[A-Za-z0-9_-]+/)*[^\s\"'()<>/]+\.png", rewrite_reference, result)
(root / "index.html").write_text(result, encoding="utf-8")
report = {
    "source_bytes": len(source.encode("utf-8")),
    "html_bytes": len(result.encode("utf-8")),
    "image_occurrences": occurrences,
    "unique_images": len(seen),
    "asset_bytes": sum(asset["bytes"] for asset in seen.values()),
    "assets": list(seen.values()),
}
(root / "optimization-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps({key: value for key, value in report.items() if key != "assets"}, indent=2))
