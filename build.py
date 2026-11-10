#!/usr/bin/env python3
"""Regenerate the map's generated blocks from world.json and validate every page.

Usage:  python3 build.py          # build + validate
        python3 build.py --check  # validate only, don't touch index.html
"""
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORLD = ROOT / "world.json"
INDEX = ROOT / "index.html"
FOLDERS = {"places": "places", "people": "people", "lore": "lore", "events": "events"}
INK, BLOOD, PARCH, BONE = "#2b2219", "#8e2a20", "#e2d3ae", "#f6f1e3"

errors, warnings = [], []
esc = lambda s: html.escape(str(s), quote=True)


def load():
    return json.loads(WORLD.read_text(encoding="utf-8"))


def viewbox(w):
    """Map canvas as [x, y, width, height]. Grow it in world.json meta.map_viewbox when the map gets cramped."""
    return w["meta"].get("map_viewbox", [0, 0, 1000, 700])


def all_entries(w):
    for kind in FOLDERS:
        for e in w.get(kind, []):
            yield kind, e


# ---------------------------------------------------------------- validation

def validate(w):
    known = {e["id"] for _, e in all_entries(w)}
    ids = {}
    for kind, e in all_entries(w):
        if e["id"] in ids:
            errors.append(f"duplicate id '{e['id']}' ({ids[e['id']]} and {kind})")
        ids[e["id"]] = kind
        page = e.get("page")
        if page:
            expected = f"{FOLDERS[kind]}/{e['id']}.html"
            if page != expected:
                errors.append(f"{e['id']}: page should be '{expected}', is '{page}'")
            if not (ROOT / page).exists():
                errors.append(f"{e['id']}: page '{page}' does not exist")
        for ref in e.get("links", []) + e.get("places", []) + e.get("people", []):
            if ref not in known:
                errors.append(f"{e['id']}: links to unknown id '{ref}'")
        if kind == "events" and not isinstance(e.get("year"), int):
            errors.append(f"{e['id']}: event needs an integer 'year' (AS)")
        if kind == "places":
            vx, vy, vw, vh = viewbox(w)
            x, y = e.get("x"), e.get("y")
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))
                    and vx <= x <= vx + vw and vy <= y <= vy + vh):
                errors.append(f"{e['id']}: coordinates outside the map "
                              f"(x {vx}..{vx + vw}, y {vy}..{vy + vh})")

    place_ids = {p["id"] for p in w.get("places", [])}
    for r in w.get("roads", []) + w.get("routes", []):
        for end in (r["from"], r["to"]):
            if end not in place_ids:
                errors.append(f"road/route endpoint '{end}' is not a place")

    pages = {(ROOT / e["page"]).resolve(): e["id"] for _, e in all_entries(w) if e.get("page")}
    for path, eid in pages.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        linked = set()
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
            if re.match(r"^[a-z]+:", href):
                continue
            target = (path.parent / href).resolve()
            if not target.exists():
                errors.append(f"{eid}: broken link '{href}'")
            elif target in pages and pages[target] != eid:
                linked.add(pages[target])
        if len(linked) < 2:
            errors.append(f"{eid}: links to {len(linked)} other page(s); needs at least 2")
        if "Loose threads" not in text:
            errors.append(f"{eid}: missing a 'Loose threads' section")

    for folder in set(FOLDERS.values()):
        for f in (ROOT / folder).glob("*.html"):
            if f.resolve() not in pages:
                warnings.append(f"{folder}/{f.name} is not listed in world.json")


# ---------------------------------------------------------------- generation

GLYPHS = {
    "capital": f'<circle r="9.5" fill="{PARCH}" stroke="{INK}" stroke-width="1.2"/>'
               f'<circle r="5" fill="{BLOOD}" stroke="{INK}" stroke-width="1"/>',
    "fortress": f'<path d="M-6.5 6.5 V-4 H-4.5 V-7.5 H-1.8 V-4 H1.8 V-7.5 H4.5 V-4 H6.5 V6.5 Z" '
                f'fill="{BONE}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>'
                f'<path d="M-1.6 6.5 V2.5 A1.6 1.6 0 0 1 1.6 2.5 V6.5" fill="{INK}"/>',
    "town": f'<circle r="5.2" fill="{INK}"/><circle r="2.1" fill="{PARCH}"/>',
    "crossing": f'<path d="M-10 3 Q0 -7 10 3" fill="none" stroke="{INK}" stroke-width="2.4"/>'
                f'<path d="M-5 0 V5 M0 -2 V5 M5 0 V5" stroke="{INK}" stroke-width="1.3"/>',
    "ruin": f'<path d="M-6 6 V-5 L-2 -3 L1 -6 L6 -2 V6 Z" fill="none" stroke="{INK}" stroke-width="1.3" stroke-dasharray="3 1.5"/>',
    "site": f'<path d="M0 -7 L6 6 H-6 Z" fill="{PARCH}" stroke="{INK}" stroke-width="1.2"/>',
}

LABEL_POS = {
    "right": (12, 4, "start"),
    "left": (-12, 4, "end"),
    "above": (0, -13, "middle"),
    "below": (0, 21, "middle"),
}


def gen_roads(w):
    pts = {p["id"]: (p["x"], p["y"]) for p in w["places"]}
    out = []
    for r in w.get("roads", []):
        (x1, y1), (x2, y2) = pts[r["from"]], pts[r["to"]]
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        b = r.get("bend", 0.0) * length
        cx, cy = (x1 + x2) / 2 - dy / length * b, (y1 + y2) / 2 + dx / length * b
        out.append(f'        <path d="M{x1} {y1} Q{cx:.0f} {cy:.0f} {x2} {y2}">'
                   f'<title>Road: {esc(r["from"])} – {esc(r["to"])}</title></path>')
    return "\n".join(out)


def gen_labels(w):
    out = []
    for r in w.get("realms", []):
        x, y = r["label"]
        size, spacing, op = (26, 14, 0.75) if r["kind"] == "kingdom" else (22, 10, 0.55)
        out.append(f'        <text x="{x}" y="{y}" font-size="{size}" letter-spacing="{spacing}" '
                   f'text-anchor="middle" opacity="{op}">{esc(r["name"].upper())}</text>')
    for r in w.get("regions", []):
        x, y = r["label"]
        out.append(f'        <text x="{x}" y="{y}" font-size="12" letter-spacing="3" '
                   f'text-anchor="middle" opacity="0.6" font-style="italic">{esc(r["name"].upper())}</text>')
    for p in w["places"]:
        dx, dy, anchor = LABEL_POS[p.get("label_pos", "right")]
        size = 16 if p["type"] == "capital" else 14
        out.append(f'        <text x="{p["x"] + dx}" y="{p["y"] + dy}" font-size="{size}" text-anchor="{anchor}" '
                   f'stroke="{PARCH}" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round">'
                   f'{esc(p["name"])}</text>')
    return "\n".join(out)


def gen_markers(w):
    out = []
    for p in w["places"]:
        glyph = GLYPHS.get(p["type"], GLYPHS["site"])
        inner = (f'<title>{esc(p["name"])}</title>'
                 f'<circle r="15" fill="transparent"/><g class="glyph">{glyph}</g>')
        if p.get("page"):
            body = f'<a href="{esc(p["page"])}" class="marker" aria-label="{esc(p["name"])}">{inner}</a>'
        else:
            body = f'<g class="marker">{inner}</g>'
        out.append(f'        <g transform="translate({p["x"]} {p["y"]})">{body}</g>')
    return "\n".join(out)


def gen_codex(w):
    def section(title, items, show_year=False):
        lis = []
        for e in items:
            yr = ""
            if show_year:
                yr = f'<span class="yr">{"c. " if e.get("approx") else ""}{e["year"]} AS</span>'
            name = (f'<a href="{esc(e["page"])}" title="{esc(e.get("summary", ""))}">{esc(e["name"])}</a>'
                    if e.get("page") else f'<span class="unconfirmed">{esc(e["name"])}</span>')
            lis.append(f"      <li>{yr}{name}</li>")
        return f"    <h2>{title}</h2>\n    <ul>\n" + "\n".join(lis) + "\n    </ul>"

    events = sorted(w.get("events", []), key=lambda e: e["year"])
    parts = [
        '    <p class="intro">Drag to pan, scroll to zoom. Hover a marker for its name; click to open it.</p>',
        section("Places", sorted(w["places"], key=lambda e: e["name"])),
        section("People", sorted(w.get("people", []), key=lambda e: e["name"])),
        section("Lore", sorted(w.get("lore", []), key=lambda e: e["name"])),
        section("Chronicle", events, show_year=True),
    ]
    return "\n".join(parts)


def replace_block(text, name, content):
    pat = re.compile(rf"(<!-- BEGIN:{name} -->\n).*?(<!-- END:{name} -->)", re.S)
    if not pat.search(text):
        errors.append(f"index.html is missing the BEGIN/END:{name} block")
        return text
    return pat.sub(lambda m: m.group(1) + (content + "\n" if content else "") + m.group(2), text)


def sync_canvas(text, w):
    """Keep the svg viewBox, the full-size rects and the zoom script's FULL box in step with map_viewbox."""
    x, y, vw, vh = viewbox(w)
    subs = [
        (r'(<svg id="map" viewBox=")[^"]*(")', rf'\g<1>{x} {y} {vw} {vh}\g<2>'),
        (r'const FULL = \{[^}]*\};', f'const FULL = {{ x: {x}, y: {y}, w: {vw}, h: {vh} }};'),
        (r'(<rect data-canvas="(?:paper|vignette)") x="[^"]*" y="[^"]*" width="[^"]*" height="[^"]*"',
         rf'\g<1> x="{x}" y="{y}" width="{vw}" height="{vh}"'),
        (r'(<rect data-canvas="ground") x="[^"]*" y="[^"]*" width="[^"]*" height="[^"]*"',
         rf'\g<1> x="{x - vw}" y="{y - vh}" width="{3 * vw}" height="{3 * vh}"'),
    ]
    for pat, rep in subs:
        text, n = re.subn(pat, rep, text)
        if not n:
            errors.append(f"index.html: canvas element not found for /{pat}/")
    return text


def build(w):
    text = INDEX.read_text(encoding="utf-8")
    text = sync_canvas(text, w)
    for name, fn in (("roads", gen_roads), ("labels", gen_labels),
                     ("markers", gen_markers), ("codex", gen_codex)):
        text = replace_block(text, name, fn(w))
    INDEX.write_text(text, encoding="utf-8")


def main():
    w = load()
    validate(w)
    if "--check" not in sys.argv and not errors:
        build(w)
    for m in warnings:
        print("warning:", m)
    for m in errors:
        print("ERROR:  ", m)
    counts = {k: len(w.get(k, [])) for k in FOLDERS}
    print(("FAILED" if errors else "ok") + " — " + ", ".join(f"{v} {k}" for k, v in counts.items()))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
