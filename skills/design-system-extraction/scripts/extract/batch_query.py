#!/usr/bin/env python3
"""Batch queries against a CSS rule index: load the index once, run one `query` per line.

Usage:
  python -I batch_query.py --index <css-index.json> --queries <queries.txt> [--out <result.txt>]

Each line of queries.txt holds the arguments of one css_index.py `query` call (without
--index), for example:
  --class <class> --profile <profile-id>
  --id <id> --profile <profile-id> --property color
Blank lines and lines starting with # are skipped. Each result is preceded by `=== <args>`.
css_index.py must sit next to this file.
"""
import argparse
import contextlib
import importlib.util
import io
import shlex
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_indexer():
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("css_index", here / "css_index.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def query_parser(mod):
    qp = mod.argparse.ArgumentParser(add_help=False)
    qp.add_argument("--class", dest="cls", action="append")
    qp.add_argument("--id", action="append")
    qp.add_argument("--selector", action="append")
    qp.add_argument("--property", action="append")
    qp.add_argument("--profile")
    qp.add_argument("--page")
    qp.add_argument("--tag", action="append")
    qp.add_argument("--media")
    qp.add_argument("--include-inline", action="store_true")
    qp.add_argument("--limit", type=int)
    qp.add_argument("--json", action="store_true")
    return qp


def run(mod, doc, lines):
    qp = query_parser(mod)
    buf = io.StringIO()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        buf.write("=== %s\n" % line)
        try:
            qargs = qp.parse_args(shlex.split(line))
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                mod.run_query(doc, qargs)
        except SystemExit as e:
            buf.write("!! %s\n" % e)
    return buf.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--index", required=True, help="index JSON written by css_index.py")
    ap.add_argument("--queries", required=True, help="text file, one query per line")
    ap.add_argument("--out", help="write results here instead of stdout")
    a = ap.parse_args(argv)
    mod = load_indexer()
    doc = mod.load_index(Path(a.index))
    text = run(mod, doc, Path(a.queries).read_text(encoding="utf-8").splitlines())
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
