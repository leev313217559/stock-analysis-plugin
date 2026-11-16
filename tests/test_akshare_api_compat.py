"""Guard: every akshare attribute referenced by tools/*.py must exist.

akshare renames public functions frequently (1.20.44 renamed a batch of
index/fund-flow APIs). Upstream code and tests hard-coded the old names; this
fork adapts them with compatibility helpers. This test fails if a merge brings
back a direct reference to an attribute the installed akshare no longer has,
or if a compatibility fallback list has no usable name at all.
"""

import re
from pathlib import Path

import akshare as ak

TOOLS = Path(__file__).resolve().parent.parent / "tools"
DIRECT = re.compile(r"(?<![\w.])ak\.([A-Za-z_]\w*)")
FALLBACK = re.compile(r"_ak_any\(([^)]*)\)")
STRING = re.compile(r"\"([A-Za-z_]\w*)\"")


def test_direct_akshare_attributes_exist():
    missing = {}
    for path in sorted(TOOLS.glob("*.py")):
        for name in sorted(set(DIRECT.findall(path.read_text(encoding="utf-8")))):
            if not hasattr(ak, name):
                missing.setdefault(path.name, []).append(name)
    assert not missing, f"tools reference missing akshare attributes: {missing}"


def test_akshare_fallback_lists_have_a_usable_name():
    broken = {}
    for path in sorted(TOOLS.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for call in FALLBACK.findall(text):
            names = STRING.findall(call)
            if names and not any(hasattr(ak, name) for name in names):
                broken.setdefault(path.name, []).append(names)
    assert not broken, f"_ak_any fallbacks resolve to nothing: {broken}"
