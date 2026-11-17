#!/usr/bin/env python3
"""Element-by-element box-size comparison of an old and a new preview with the same DOM
structure but different class notation (standard library only).

Usage:
  python -I boxdiff.py jobs --old <old-package> --new <new-package> --prefix <css-prefix> --out <jobs.json>
         --widths <w1,w2,...> [--height 900] [--glob "preview/**/*.html"]
         [--card-selector <css>] [--element-selector <css>]
  python -I boxdiff.py measure --browser <chromium-executable> --user-data-dir <scratch-dir>
         --jobs <jobs.json> --out-dir <raw-dir> [--port 9337]
  python -I boxdiff.py diff --jobs <jobs.json> --raw <raw-dir> [--tol 0.5]
  python -I boxdiff.py --selftest

jobs     --widths lists the viewport widths to compare, e.g. one phone width, the brand's
         breakpoint values and one width just below each (take them from tokens.json).
         One job per fragment file x width x side; each job loads the file:// URL and runs a
         measuring script: for every card (default `article.<prefix>-preview-card`) it records
         [tag, width, height] of each component element in DOM order (default: descendants of
         `.<prefix>-preview-cell__stage` and `.<prefix>-preview-frame`), skipping elements whose
         class contains `<prefix>-preview-` (the preview frame itself).
measure  drives a local headless Chromium-family browser through the DevTools protocol on
         127.0.0.1 only (minimal standard-library WebSocket client) and writes <name>.json per
         job. The browser path and a throw-away profile folder are arguments; nothing is
         downloaded and no external host is contacted (the local probe ignores proxy settings).
diff     checks the results against the jobs manifest first: every job has its result, both
         sides of each file and width exist, each side measured at least one element, the two
         sides hold the same cards, and no result file outside the manifest is in --raw. Any of
         these problems exits 1, and so does any card that is empty on either side or whose
         elements differ in number or tag order (the DOM is not the same). Then it lists every element whose width or height differs by
         more than --tol px, largest first; a card with a different element count is reported
         as 999. The listing is for review; control heights (H4) are judged separately.
jobs     also exits 1 when a fragment exists on one side only.
"""
import argparse
import base64
import json
import os
import re
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EVAL = r"""(()=>{const out={};document.querySelectorAll(%(card)s).forEach(a=>{const rows=[];
a.querySelectorAll(%(elements)s).forEach(e=>{const c=(e.getAttribute('class')||'');
if(new RegExp('(^|\\s)'+%(frame)s).test(c)) return; const b=e.getBoundingClientRect(); rows.push([e.tagName.toLowerCase(), Math.round(b.width*100)/100, Math.round(b.height*100)/100]);});
out[a.id]=rows;}); return out;})()"""


# The DevTools probe goes to 127.0.0.1 only; an empty ProxyHandler keeps HTTP(S)_PROXY from
# sending it to a proxy.
LOCAL = urllib.request.build_opener(urllib.request.ProxyHandler({}))


# ---------------------------------------------------------------- jobs

def fragment_sets(old, new, glob):
    """(only in old, only in new) relative fragment paths."""
    a = {f.relative_to(old).as_posix() for f in Path(old).glob(glob)}
    b = {f.relative_to(new).as_posix() for f in Path(new).glob(glob)}
    return sorted(a - b), sorted(b - a)


def make_jobs(old, new, prefix, widths, height=900, glob="preview/**/*.html", card=None, elements=None, wait=0.3):
    old, new = Path(old).resolve(), Path(new).resolve()
    card = card or "article.%s-preview-card" % prefix
    elements = elements or ".%s-preview-cell__stage *, .%s-preview-frame *" % (prefix, prefix)
    script = EVAL % {"card": json.dumps(card), "elements": json.dumps(elements), "frame": json.dumps(re.escape(prefix) + "-preview-")}
    js = []
    for f in sorted(old.glob(glob)):
        rel = f.relative_to(old).as_posix()
        name = rel.replace("/", "_").replace(".html", "")
        for w in widths:
            for tag, root in (("old", old), ("new", new)):
                js.append({"name": "%s__%s__%d" % (tag, name, w), "url": (root / rel).as_uri(), "width": w,
                           "height": height, "eval": script, "wait": wait})
    return js


# ---------------------------------------------------------------- measure (DevTools protocol, localhost only)

class WS:
    def __init__(self, url):
        assert url.startswith("ws://")
        hostport, path = url[5:].split("/", 1)
        host, port = hostport.rsplit(":", 1)
        if host not in ("127.0.0.1", "localhost"):
            raise SystemExit("refusing non-local DevTools endpoint: %s" % host)
        self.s = socket.create_connection((host, int(port)), timeout=60)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET /{path} HTTP/1.1\r\nHost: {hostport}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.s.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.rest = buf.split(b"\r\n\r\n", 1)[1]
        self.id = 0

    def _recv_exact(self, n):
        while len(self.rest) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise EOFError
            self.rest += chunk
        out, self.rest = self.rest[:n], self.rest[n:]
        return out

    def send(self, obj):
        data = json.dumps(obj).encode()
        hdr = bytearray([0x81])
        n = len(data)
        if n < 126:
            hdr.append(0x80 | n)
        elif n < 65536:
            hdr.append(0x80 | 126)
            hdr += struct.pack(">H", n)
        else:
            hdr.append(0x80 | 127)
            hdr += struct.pack(">Q", n)
        mask = os.urandom(4)
        hdr += mask
        self.s.sendall(bytes(hdr) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def recv(self):
        msg = b""
        while True:
            b1, b2 = self._recv_exact(2)
            fin, op = b1 & 0x80, b1 & 0x0F
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._recv_exact(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._recv_exact(8))[0]
            payload = self._recv_exact(n)
            if op in (1, 0, 2):
                msg += payload
                if fin:
                    return json.loads(msg)

    def call(self, method, params=None):
        self.id += 1
        mid = self.id
        self.send({"id": mid, "method": method, "params": params or {}})
        while True:
            m = self.recv()
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})


def measure(browser, udd, jobs, out, port=9337):
    os.makedirs(out, exist_ok=True)
    proc = subprocess.Popen([browser, "--headless=new", f"--remote-debugging-port={port}", "--remote-debugging-address=127.0.0.1",
                             f"--user-data-dir={udd}", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                             "--no-default-browser-check", "--disable-background-networking", "--disable-sync",
                             "--disable-component-update", "--disable-extensions", "--allow-file-access-from-files", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tabs = None
        for _ in range(60):
            try:
                tabs = json.load(LOCAL.open(f"http://127.0.0.1:{port}/json"))
                break
            except Exception:  # noqa: BLE001
                time.sleep(0.5)
        if tabs is None:
            raise SystemExit("browser DevTools endpoint did not come up on 127.0.0.1:%d" % port)
        page = next(t for t in tabs if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.call("Page.enable")
        ws.call("Runtime.enable")
        for j in jobs:
            w = j["width"]
            ws.call("Emulation.setDeviceMetricsOverride", {"width": w, "height": j.get("height", 900), "deviceScaleFactor": 1, "mobile": w < 768})
            ws.call("Emulation.setEmulatedMedia", {"features": [{"name": "prefers-reduced-motion", "value": "no-preference"}]})
            ws.call("Page.navigate", {"url": j["url"]})
            for _ in range(100):
                r = ws.call("Runtime.evaluate", {"expression": "document.readyState", "returnByValue": True})
                if r["result"].get("value") == "complete":
                    break
                time.sleep(0.2)
            time.sleep(j.get("wait", 1.5))
            r = ws.call("Runtime.evaluate", {"expression": j["eval"], "returnByValue": True, "awaitPromise": True})
            with open(os.path.join(out, j["name"] + ".json"), "w", encoding="utf-8") as fh:
                json.dump(r["result"].get("value"), fh, ensure_ascii=False, indent=1)
            print("eval", j["name"])
        ws.call("Browser.close")
    finally:
        try:
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            proc.kill()


# ---------------------------------------------------------------- diff

def diff(raw, tol, jobs):
    """Return (pages, worst, problems); problems are manifest failures that make the comparison invalid."""
    raw = Path(raw)
    problems = []
    names = [j["name"] for j in jobs]
    if not names:
        problems.append("the jobs manifest is empty")
    present = {f.name[:-len(".json")] for f in raw.glob("*.json")}
    for n in sorted(set(names) - present):
        problems.append("missing result: %s" % n)
    for n in sorted(present - set(names)):
        problems.append("result not in this manifest: %s" % n)
    keys = sorted({n.split("__", 1)[1] for n in names if "__" in n})
    worst = []
    pages = 0
    total = 0
    for key in keys:
        fa, fb = raw / ("old__%s.json" % key), raw / ("new__%s.json" % key)
        if not (("old__" + key) in names and ("new__" + key) in names):
            problems.append("manifest lacks one side: %s" % key)
            continue
        if not (fa.exists() and fb.exists()):
            continue
        a = json.load(open(fa, encoding="utf-8")) or {}
        b = json.load(open(fb, encoding="utf-8")) or {}
        for side, doc in (("old", a), ("new", b)):
            if not any(doc.values()):
                problems.append("no element measured: %s__%s" % (side, key))
        if set(a) != set(b):
            problems.append("cards differ in %s: only old %s, only new %s" % (key, sorted(set(a) - set(b)), sorted(set(b) - set(a))))
        for card, rows in a.items():
            rb = b.get(card, [])
            total += len(rows)
            if card in b and (not rows or not rb):
                problems.append("no element measured in card %s of %s (%s side)" % (card, key, "old" if not rows else "new"))
            if len(rows) != len(rb):
                worst.append((999, key, card, "element count %d -> %d" % (len(rows), len(rb))))
                if card in b and rows and rb:
                    problems.append("card %s of %s: element count %d -> %d, not the same DOM" % (card, key, len(rows), len(rb)))
                continue
            tags = [i for i, (x, y) in enumerate(zip(rows, rb)) if x[0] != y[0]]
            if tags:
                i = tags[0]
                problems.append("card %s of %s: element #%d is %s -> %s, not the same DOM" % (card, key, i, rows[i][0], rb[i][0]))
            for i, (x, y) in enumerate(zip(rows, rb)):
                d = max(abs(x[1] - y[1]), abs(x[2] - y[2]))
                if d > tol:
                    worst.append((d, key, card, "#%d %s %sx%s -> %sx%s" % (i, x[0], x[1], x[2], y[1], y[2])))
        pages += 1
    if names and not total:
        problems.append("no element measured in any result")
    worst.sort(key=lambda r: -r[0])
    return pages, worst, problems


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        for side in ("o", "n"):
            (d / side / "preview" / "components").mkdir(parents=True)
            (d / side / "preview" / "components" / "a.html").write_text("<p>x</p>", encoding="utf-8")
        js = make_jobs(d / "o", d / "n", "x", [375, 800])
        ok &= len(js) == 4 and js[0]["name"] == "old__preview_components_a__375" and "x-preview-card" in js[0]["eval"]
        raw = d / "raw"
        raw.mkdir()
        manifest = [{"name": "old__p__375"}, {"name": "new__p__375"}]
        (raw / "old__p__375.json").write_text(json.dumps({"c1": [["div", 100, 40], ["span", 20, 10]], "c2": [["p", 1, 1]]}), encoding="utf-8")
        (raw / "new__p__375.json").write_text(json.dumps({"c1": [["div", 100, 42], ["span", 20.3, 10]], "c2": [["p", 1, 1]]}), encoding="utf-8")
        pages, worst, problems = diff(raw, 0.5, manifest)
        ok &= pages == 1 and [(w[0], w[2]) for w in worst] == [(2, "c1")] and not problems
        # one card empty on the new side while the other still measures fails (partial empty card)
        (raw / "new__p__375.json").write_text(json.dumps({"c1": [["div", 100, 40], ["span", 20, 10]], "c2": []}), encoding="utf-8")
        ok &= any("no element measured in card c2" in x for x in diff(raw, 0.5, manifest)[2])
        # a different element count or tag order is not the same DOM
        (raw / "new__p__375.json").write_text(json.dumps({"c1": [["div", 100, 40]], "c2": [["p", 1, 1]]}), encoding="utf-8")
        ok &= any("element count 2 -> 1" in x for x in diff(raw, 0.5, manifest)[2])
        (raw / "new__p__375.json").write_text(json.dumps({"c1": [["div", 100, 40], ["em", 20, 10]], "c2": [["p", 1, 1]]}), encoding="utf-8")
        ok &= any("element #1 is span -> em" in x for x in diff(raw, 0.5, manifest)[2])
        # missing side, empty side, stale result and an empty manifest all fail
        (raw / "new__p__375.json").unlink()
        ok &= any("missing result: new__p__375" in x for x in diff(raw, 0.5, manifest)[2])
        (raw / "new__p__375.json").write_text(json.dumps({"c1": [], "c2": []}), encoding="utf-8")
        ok &= any("no element measured: new__p" in x for x in diff(raw, 0.5, manifest)[2])
        (raw / "old__q__375.json").write_text("{}", encoding="utf-8")
        ok &= any("not in this manifest: old__q__375" in x for x in diff(raw, 0.5, manifest)[2])
        ok &= any("manifest is empty" in x for x in diff(d / "nothing", 0.5, [])[2])
        (d / "n" / "preview" / "components" / "b.html").write_text("<p>y</p>", encoding="utf-8")
        ok &= fragment_sets(d / "o", d / "n", "preview/**/*.html") == ([], ["preview/components/b.html"])
    ok &= all(not h.proxies for h in LOCAL.handlers if isinstance(h, urllib.request.ProxyHandler))
    print("boxdiff selftest: %s" % ("1/1 passed" if ok else "0/1 passed"))
    return 0 if ok else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    sub = ap.add_subparsers(dest="cmd")
    j = sub.add_parser("jobs", help="write the measuring jobs")
    j.add_argument("--old", required=True, help="old package root")
    j.add_argument("--new", required=True, help="new package root")
    j.add_argument("--prefix", required=True, help="CSS prefix of the preview frame classes")
    j.add_argument("--out", required=True, help="jobs JSON to write")
    j.add_argument("--widths", required=True, help="comma-separated viewport widths, e.g. 375,768,1024")
    j.add_argument("--height", type=int, default=900)
    j.add_argument("--glob", default="preview/**/*.html", help="fragment glob relative to --old")
    j.add_argument("--card-selector", help="CSS selector of a card (default article.<prefix>-preview-card)")
    j.add_argument("--element-selector", help="CSS selector of measured elements inside a card")
    m = sub.add_parser("measure", help="run the jobs in a local headless browser")
    m.add_argument("--browser", required=True, help="Chromium-family browser executable")
    m.add_argument("--user-data-dir", required=True, help="throw-away browser profile folder")
    m.add_argument("--jobs", required=True, help="jobs JSON")
    m.add_argument("--out-dir", required=True, help="folder for <name>.json results")
    m.add_argument("--port", type=int, default=9337, help="local DevTools port")
    d = sub.add_parser("diff", help="check the results against the jobs manifest, then compare old__* and new__*")
    d.add_argument("--jobs", required=True, help="jobs JSON the results were measured from")
    d.add_argument("--raw", required=True, help="folder with the measured JSON files")
    d.add_argument("--tol", type=float, default=0.5, help="tolerance in px")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "jobs":
        only_old, only_new = fragment_sets(a.old, a.new, a.glob)
        if only_old or only_new:
            print("fragments on one side only: old %s, new %s" % (only_old, only_new))
            return 1
        js = make_jobs(a.old, a.new, a.prefix, [int(x) for x in a.widths.split(",") if x.strip()], a.height, a.glob,
                       a.card_selector, a.element_selector)
        Path(a.out).write_text(json.dumps(js, ensure_ascii=False, indent=1), encoding="utf-8")
        print(len(js), "jobs")
        return 0
    if a.cmd == "measure":
        measure(a.browser, a.user_data_dir, json.load(open(a.jobs, encoding="utf-8")), a.out_dir, a.port)
        return 0
    if a.cmd == "diff":
        pages, worst, problems = diff(a.raw, a.tol, json.load(open(a.jobs, encoding="utf-8")))
        for x in problems:
            print("PROBLEM", x)
        for r in worst:
            print("%7.2f  %s  %s  %s" % r)
        print("pages", pages, "diffs", len(worst), "problems", len(problems))
        return 1 if problems else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
