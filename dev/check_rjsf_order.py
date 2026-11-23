"""Check rjsf.json against react-jsonschema-form's ui:order rules (what ecoscope-desktop enforces).

Usage: python dev/check_rjsf_order.py path/to/rjsf.json
"""
import json
import sys


def check(props: dict, ui: dict, path: str, errors: list) -> None:
    order = ui.get("ui:order")
    if order is not None:
        keys = list(props)
        if "*" not in order:
            errors += [f"{path}: ui:order does not contain property {k!r}" for k in keys if k not in order]
        errors += [f"{path}: ui:order contains extraneous property {k!r}" for k in order if k != "*" and k not in keys]
    for k, sub in props.items():
        if isinstance(sub, dict) and isinstance(sub.get("properties"), dict):
            check(sub["properties"], ui.get(k, {}) if isinstance(ui.get(k), dict) else {}, f"{path}/{k}", errors)


rjsf = json.load(open(sys.argv[1]))
errs: list = []
check(rjsf["properties"], rjsf.get("uiSchema", {}), "root", errs)
print("\n".join(errs) or "ui:order OK")
sys.exit(1 if errs else 0)
