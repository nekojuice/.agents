#!/usr/bin/env python3
"""Compare same-named variables of a brand utility theme and the framework's default theme
(standard library only).

Usage:
  python -I theme_name_diff.py --theme <brand theme.css> --framework-theme <framework theme.css>
         --tokens-css <tokens.css> [--rem-px 16]
  python -I theme_name_diff.py --selftest

Brand values are first resolved through tokens.css (var() chains); rem converts to px with
--rem-px; `calc(a / b)` becomes a number. Prints the names whose values differ and the names
whose values are equal. Variables set to `initial` and wildcard resets are ignored.
"""
import argparse
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def defs(text):
    return {k: v.strip() for k, v in re.findall(r"(--[\w.-]+)\s*:\s*([^;]+);", text) if v.strip() != "initial" and "*" not in k}


def norm(v, rem_px=16.0):
    v = v.strip().lower().replace(" ", "")
    m = re.fullmatch(r"([\d.]+)rem", v)
    if m:
        return "%gpx" % (float(m.group(1)) * rem_px)
    m = re.fullmatch(r"calc\(([\d.]+)/([\d.]+)\)", v)
    if m:
        return "%g" % (float(m.group(1)) / float(m.group(2)))
    return v


def compare(brand_text, fw_text, tok_text, rem_px=16.0):
    brand, tw, tok = defs(brand_text), defs(fw_text), defs(tok_text)

    def resolve(v, depth=0):
        m = re.fullmatch(r"var\((--[\w-]+)\)", v.strip())
        if m and depth < 20 and m.group(1) in tok:
            return resolve(tok[m.group(1)], depth + 1)
        return v

    same, diff = [], []
    for k in sorted(brand):
        if k in tw and "--" not in k[2:]:
            b, d = norm(resolve(brand[k]), rem_px), norm(tw[k], rem_px)
            (same if b == d else diff).append((k, resolve(brand[k]), tw[k]))
    return same, diff


def selftest():
    brand = "@theme inline { --color-*: initial; --radius-sm: var(--x-radius-sm); --leading-tight: var(--x-lh); }"
    fw = "@theme { --radius-sm: 0.25rem; --leading-tight: calc(5 / 4); }"
    tok = ":root { --x-radius-sm: 6px; --x-lh: 1.25; }"
    same, diff = compare(brand, fw, tok)
    ok = [k for k, _b, _d in same] == ["--leading-tight"] and [k for k, _b, _d in diff] == ["--radius-sm"]
    print("theme_name_diff selftest: %s" % ("1/1 passed" if ok else "0/1 passed  same=%r diff=%r" % (same, diff)))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--theme", help="brand utility theme CSS")
    ap.add_argument("--framework-theme", help="the framework package's default theme CSS")
    ap.add_argument("--tokens-css", help="tokens.css used to resolve var() values")
    ap.add_argument("--rem-px", type=float, default=16.0, help="px per rem (default 16)")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixture test and exit")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    missing = [n for n in ("theme", "framework_theme", "tokens_css") if not getattr(a, n)]
    if missing:
        ap.error("missing: " + ", ".join("--" + m.replace("_", "-") for m in missing))
    read = lambda p: open(p, encoding="utf-8").read()  # noqa: E731
    same, diff = compare(read(a.theme), read(a.framework_theme), read(a.tokens_css), a.rem_px)
    print("same name, different value:")
    for k, b, d in diff:
        print("  %s  brand %s / default %s" % (k, b, d))
    print("same name, same value:", ", ".join(k for k, _b, _d in same))
    return 0


if __name__ == "__main__":
    sys.exit(main())
