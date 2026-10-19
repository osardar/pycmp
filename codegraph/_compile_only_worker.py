"""Compile staged source without importing or executing it (Python 3.4 compatible)."""
from __future__ import print_function

import base64
import json
import os
import py_compile
import shutil
import sys
import tempfile


def main():
    optimization = int(sys.argv[1])
    source = sys.argv[2]
    if not source.startswith("/inputs/") or not source.endswith(".py") or ".." in source:
        raise ValueError("source must be a staged /inputs/*.py file")
    directory = tempfile.mkdtemp(prefix="pycmp-compile-")
    try:
        staged = os.path.join(directory, "source.py")
        shutil.copyfile(source, staged)
        os.utime(staged, (946684800, 946684800))
        legacy = sys.version_info[:2] < (3, 5)
        suffix = ".pyo" if legacy and optimization else ".pyc"
        if legacy:
            name = "source" + suffix
        else:
            marker = ".opt-%s" % optimization if optimization else ""
            name = "source." + sys.implementation.cache_tag + marker + suffix
        target = os.path.join(directory, name)
        py_compile.compile(staged, cfile=target, dfile="source.py", doraise=True,
                           optimize=optimization)
        with open(target, "rb") as handle:
            raw = handle.read()
        magic = raw[:4].hex() if hasattr(raw, "hex") else "".join(
            "%02x" % value for value in bytearray(raw[:4]))
        print(json.dumps({"ok": True, "version": sys.version, "file": name,
                          "magic": magic, "base64": base64.b64encode(raw).decode("ascii")}))
    except Exception as exc:
        print(json.dumps({"ok": False, "error_type": type(exc).__name__, "error": str(exc)}))
    finally:
        shutil.rmtree(directory, ignore_errors=True)


if __name__ == "__main__":
    main()
