"""Decode/parse only. No compile or execution mode is exposed."""
import json
import resource
import sys
import tokenize
import io
from pathlib import Path


def main():
    # macOS does not implement this Linux address-space limit reliably. The
    # coordinator enforces the RSS watchdog on both platforms; release Linux
    # containers additionally retain this hard address-space bound.
    if sys.platform == "linux":
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024**2,) * 2)
    # -I -S removes environment/site imports; add only this trusted package root.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        mode, path = sys.argv[1:]
        cap = 65536 if mode == "source" else 8 * 1024**2
        with open(path, "rb") as handle:
            raw = handle.read(cap + 1)
        if len(raw) > cap:
            raise ValueError("input_limit")
        if mode == "source":
            from pycmp_vectorizer.vendor.ast_normalize import ASTNormalizer
            encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
            graphs = ASTNormalizer().unit_graphs(raw.decode(encoding), origin="input.py")
            values = [g.to_dict() for g in graphs]
            limit = 10000
        elif mode == "bytecode":
            from pycmp_vectorizer.vendor.bytecode_reference import decode
            values = [decode(raw)]
            limit = 100000
        else:
            raise ValueError("unsupported worker mode")
        if sum(len(g["nodes"]) for g in values) > limit:
            raise ValueError("node_limit")
        result = {"graphs": values}
    except (SyntaxError, UnicodeError, LookupError) as exc:
        result = {"error": "invalid_source", "diagnostic": str(exc)[:1000]}
    except MemoryError:
        result = {"error": "memory_limit", "diagnostic": "parser memory limit"}
    except Exception as exc:
        reason = str(exc)
        result = {"error": reason if reason in ("input_limit", "node_limit", "edge_limit") else "invalid_input",
                  "diagnostic": reason[:1000]}
    print(json.dumps(result, allow_nan=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
