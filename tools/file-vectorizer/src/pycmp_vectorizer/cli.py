"""CLI: JSONL on stdout, diagnostics on stderr."""
import argparse
import json
from pathlib import Path
import sys

from .api import Vectorizer


def emit(value, handle):
    handle.write(json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n")
    handle.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pycmp-vectorizer")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "vectorize"):
        sub = commands.add_parser(name)
        sub.add_argument("--checkpoint", required=True)
        sub.add_argument("--runtime-manifest")
        sub.add_argument("--host-runtime", action="store_true", help="explicit development mode: only the current Python 3.14 runtime")
        if name == "vectorize":
            sub.add_argument("inputs", nargs="+")
            sub.add_argument("--recursive", action="store_true")
            sub.add_argument("--include-units", action="store_true")
            sub.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    handle, vectorizer = None, None
    try:
        if args.command == "vectorize" and args.output != "-":
            target = Path(args.output).absolute()
            # Output must not become an input during traversal.
            for value in args.inputs:
                source = Path(value).absolute()
                if target == source or (source.is_dir() and source in target.parents):
                    raise ValueError("output must be outside input directories")
            if target.exists() or target.is_symlink():
                raise ValueError("refusing to overwrite existing output")
        vectorizer = Vectorizer(args.checkpoint, runtime_manifest=args.runtime_manifest,
            host_runtime=args.host_runtime, include_units=getattr(args, "include_units", False))
        if args.command == "check":
            emit(vectorizer.check(), sys.stdout)
            return 0
        handle = sys.stdout if args.output == "-" else open(args.output, "x", encoding="utf-8")
        for result in vectorizer.vectorize_paths(args.inputs, args.recursive):
            emit(result, handle)
        summary = vectorizer.summary
        emit(summary, handle)
        emit(summary, sys.stderr)
        if not summary["counts"]["candidates"]:
            return 1
        return 2 if summary["counts"]["failed"] else 0
    except (Exception, KeyboardInterrupt) as exc:
        interrupted = isinstance(exc, KeyboardInterrupt)
        if handle and vectorizer and vectorizer.summary:
            summary = dict(vectorizer.summary, completion="partial", reason="interrupted" if interrupted else str(exc)[:1000])
            try:
                emit(summary, handle)
            except (OSError, ValueError):
                pass
        print("pycmp-vectorizer: " + ("interrupted" if interrupted else str(exc)[:1000]), file=sys.stderr)
        return 130 if interrupted else 1
    finally:
        if vectorizer:
            vectorizer.close()
        if handle and handle is not sys.stdout:
            handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
