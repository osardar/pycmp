"""Owned-fixture compiler/oracle runner; deliberately compatible with Python 3.4."""
import base64
import importlib.util
import json
import os
import py_compile
import shutil
import sys


def main():
    mode, optimization = sys.argv[1], int(sys.argv[2])
    # Only this staged project is visible. Compilation writes into container tmpfs.
    shutil.copytree("/input", "/tmp/project")
    os.chdir("/tmp/project")
    sys.path.insert(0, os.getcwd())
    modules = sorted(name for name in os.listdir(".") if name.endswith(".py"))
    if mode == "compile":
        artifacts = []
        for name in modules:
            os.utime(name, (946684800, 946684800))
            suffix = ".pyo" if sys.version_info[:2] < (3, 5) and optimization else ".pyc"
            if sys.version_info[:2] < (3, 5):
                target = name[:-3] + suffix
            else:
                marker = ".opt-%s" % optimization if optimization else ""
                target = name[:-3] + "." + sys.implementation.cache_tag + marker + suffix
            py_compile.compile(name, cfile=target, dfile=name,
                               doraise=True, optimize=optimization)
            with open(target, "rb") as handle:
                raw = handle.read()
            artifacts.append({"module": name, "file": target,
                              "base64": base64.b64encode(raw).decode("ascii"),
                              "magic": raw[:4].hex() if hasattr(raw, "hex") else
                              "".join("%02x" % value for value in bytearray(raw[:4]))})
        print(json.dumps({"version": sys.version, "artifacts": artifacts}))
        return
    with open("oracle.json") as handle:
        cases = json.load(handle)
    if mode == "bytecode":
        # Tagged modern artifacts need legacy-location aliases for sourceless
        # imports of sibling modules; preserve the original tagged artifact.
        for name in os.listdir("."):
            if ".cpython-" in name and name.endswith(".pyc"):
                shutil.copyfile(name, name.split(".")[0] + ".pyc")
        target = "main.pyo" if os.path.exists("main.pyo") else "main.pyc"
        # Sourceless loader does not recognize .pyo on modern hosts; this runs
        # in the actual originating interpreter.
        from importlib.machinery import SourcelessFileLoader
        module = SourcelessFileLoader("main", target).load_module()
    else:
        import main as module
    results = []
    for case in cases:
        try:
            actual = module.run(case["input"])
            expected_error = case.get("error")
            results.append({"passed": not expected_error and actual == case.get("expected"),
                            "actual": actual})
        except Exception as error:
            results.append({"passed": type(error).__name__ == case.get("error"),
                            "error": type(error).__name__})
    print(json.dumps({"version": sys.version, "passed": all(row["passed"] for row in results),
                      "results": results}, sort_keys=True))


if __name__ == "__main__":
    main()
