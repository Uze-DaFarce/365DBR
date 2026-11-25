import sys; sys.stdout.reconfigure(encoding="utf-8")
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

DBR = Path(__file__).resolve().parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
NPX = shutil.which("npx")
if not NPX:
    raise RuntimeError("npx not found on PATH")


def bundle(entry: str, outfile: str) -> int:
    cmd = [
        NPX, "esbuild", str(DBR / entry),
        "--bundle", "--minify", "--format=iife",
        "--jsx=automatic",
        f"--outfile={DBR / outfile}",
    ]
    res = subprocess.run(cmd, cwd=DBR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0:
        raise RuntimeError(f"esbuild failed for {entry}:\n{res.stderr or res.stdout}")
    return (DBR / outfile).stat().st_size


def update_html(html_name: str, bundle_name: str):
    p = DBR / html_name
    txt = p.read_text(encoding="utf-8")
    # Remove importmap and esm.sh/run
    txt = re.sub(r'\s*<script\s+type="importmap">.*?</script>', "", txt, flags=re.S)
    txt = re.sub(r'\s*<script\s+src="https://esm\.sh/run"[^>]*></script>', "", txt)
    # Replace inline TSX or existing bundle tag
    tag = f'<script src="{bundle_name}?v={STAMP}" defer></script>'
    if re.search(r'<script\s+type="text/tsx">.*?</script>', txt, re.S):
        txt = re.sub(r'<script\s+type="text/tsx">.*?</script>', tag, txt, count=1, flags=re.S)
    elif re.search(rf'<script\s+src="{re.escape(bundle_name)}(\?v=[^"]+)?"[^>]*></script>', txt):
        txt = re.sub(rf'<script\s+src="{re.escape(bundle_name)}(\?v=[^"]+)?"[^>]*></script>', tag, txt, count=1)
    p.write_text(txt, encoding="utf-8")


def update_sw():
    sw_p = DBR / "sw.js"
    if not sw_p.exists():
        return "sw.js not found"
    sw = sw_p.read_text(encoding="utf-8")
    sw = re.sub(r'CACHE_NAME\s*=\s*"dbr-v-[^"]+"', f'CACHE_NAME = "dbr-v-{STAMP}"', sw)
    for asset in ("/365DBR/index.bundle.js", "/365DBR/bible.bundle.js"):
        if asset not in sw and '"/365DBR/bible.html",' in sw:
            sw = sw.replace('"/365DBR/bible.html",', f'"/365DBR/bible.html",\n  "{asset}",', 1)
    sw_p.write_text(sw, encoding="utf-8")
    return f"dbr-v-{STAMP}"


def main():
    sz_idx = bundle("src/index.tsx", "index.bundle.js")
    sz_bib = bundle("src/bible.tsx", "bible.bundle.js")
    update_html("index.html", "index.bundle.js")
    update_html("bible.html", "bible.bundle.js")
    sw_ver = update_sw()
    print(f"Built index.bundle.js ({sz_idx:,} B), bible.bundle.js ({sz_bib:,} B), SW={sw_ver}")


if __name__ == "__main__":
    main()
