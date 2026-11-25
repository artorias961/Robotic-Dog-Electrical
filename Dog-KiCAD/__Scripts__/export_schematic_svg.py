#!/usr/bin/env python3
"""Export a KiCad schematic to an SVG for a README.

Runs kicad-cli to export the schematic without the sheet frame, crops the image to
the drawing, and makes the file smaller: coordinates are rounded to 0.01 mm, the
invisible search text is dropped, and the strokes of each piece of text are joined
into one path. The drawing itself is unchanged.

Needs KiCad 8 or newer (for kicad-cli) and Python 3.8 or newer. No other packages.

Example, run from KiCAD/leg:
    python ../../__Scripts__/export_schematic_svg.py leg.kicad_sch images/leg-bench-schematic.svg
"""
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
from xml.sax.saxutils import escape

NUM = r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'

# Text placed in the title block, like a date or revision, isn't part of the drawing.
# KiCad's default title block sits in this corner (mm from the page's right and bottom edges).
TITLE_BLOCK_W, TITLE_BLOCK_H = 130.0, 46.0


def find_kicad_cli(given):
    """Return the kicad-cli path: --kicad-cli, then PATH, then KiCad's default install folders."""
    if given:
        return given
    on_path = shutil.which('kicad-cli')
    if on_path:
        return on_path

    def version(path):  # ...\KiCad\10.0\bin\kicad-cli.exe -> (10, 0)
        folder = os.path.basename(os.path.dirname(os.path.dirname(path)))
        return tuple(int(n) for n in re.findall(r'\d+', folder))
    windows = glob.glob(os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'),
                                     'KiCad', '*', 'bin', 'kicad-cli.exe'))
    mac = ['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli']
    for c in sorted(windows, key=version, reverse=True) + mac:  # newest KiCad first
        if os.path.isfile(c):
            return c
    sys.exit("kicad-cli not found. Add it to PATH or pass --kicad-cli <path>.")


def export_pages(cli, sch, outdir):
    cmd = [cli, 'sch', 'export', 'svg', '--exclude-drawing-sheet', '-o', outdir, sch]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"kicad-cli failed ({r.returncode}):\n{r.stdout}{r.stderr}")
    pages = sorted(glob.glob(os.path.join(outdir, '*.svg')))
    if not pages:
        sys.exit("kicad-cli wrote no SVG files.")
    return pages


def drawing_bounds(t, keep_title_block):
    """Bounding box (mm) of everything drawn, from paths, circles and rects."""
    vb = [float(v) for v in re.search(r'viewBox="([^"]*)"', t).group(1).split()]
    page_w, page_h = vb[2], vb[3]
    pts = []
    for d in re.findall(r'\bd="([^"]*)"', t, re.S):
        for cmd, args in re.findall(r'([A-Za-z])([^A-Za-z]*)', d):
            v = [float(x) for x in re.findall(NUM, args)]
            if cmd in 'MLCQ':
                pts += [(v[i], v[i + 1]) for i in range(0, len(v) - 1, 2)]
            elif cmd == 'A':
                pts += [(v[i + 5], v[i + 6]) for i in range(0, len(v) - 6, 7)]
            elif cmd not in 'Zz':
                sys.exit(f"Unexpected SVG path command '{cmd}'. This script only knows kicad-cli's output.")
    for cx, cy, r in re.findall(r'<circle cx="(%s)" cy="(%s)"\s+r="(%s)"' % (NUM, NUM, NUM), t):
        cx, cy, r = float(cx), float(cy), float(r)
        pts += [(cx - r, cy - r), (cx + r, cy + r)]
    for x, y, w, h in re.findall(r'<rect x="(%s)" y="(%s)" width="(%s)" height="(%s)"' % (NUM, NUM, NUM, NUM), t):
        x, y, w, h = float(x), float(y), float(w), float(h)
        if w >= page_w * 0.95 and h >= page_h * 0.95:
            continue  # page background
        pts += [(x, y), (x + w, y + h)]
    if not keep_title_block:
        pts = [(x, y) for x, y in pts if not (x > page_w - TITLE_BLOCK_W and y > page_h - TITLE_BLOCK_H)]
    if not pts:
        sys.exit("The page is empty.")
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def shrink(t):
    """Make the file smaller without changing what it draws."""
    t = re.sub(r'-?\d+\.\d{3,}', lambda m: ('%.2f' % float(m.group(0))).rstrip('0').rstrip('.'), t)
    t = re.sub(r'\bd="([^"]*)"', lambda m: 'd="' + ' '.join(m.group(1).split()) + '"', t, flags=re.S)
    t = re.sub(r'<text\b[^>]*opacity="0"[^>]*>[^<]*</text>', '', t, flags=re.S)
    t = re.sub(r'\n\s*\n', '\n', t)

    # Sibling paths in a stroke-only group become one path.
    def merge(m):
        head, body = m.group(1), m.group(2)
        if 'fill:none' not in head.replace(' ', ''):
            return m.group(0)
        ds = re.findall(r'<path d="([^"]*)"\s*/>', body)
        if len(ds) < 2:
            return m.group(0)
        return head + '<path d="' + ' '.join(ds) + '"/>\n</g>'
    t = re.sub(r'(<g style="[^"]*">\s*)((?:<path d="[^"]*"\s*/>\s*)+)</g>', merge, t, flags=re.S)

    # Each stroke of KiCad's text is its own two-point path. Chain them into one path per text.
    for m in re.finditer(r'<g class="stroked-text">', t):
        parent = t.rfind('<g style="', 0, m.start())
        if 'fill:none' not in t[parent:t.index('>', parent)].replace(' ', ''):
            return t  # never seen in kicad-cli output; chaining here could fill shapes, so stop
    seg = re.compile(r'<path d="M(%s) (%s) L(%s) (%s)"\s*/>' % (NUM, NUM, NUM, NUM))

    def chain(m):
        head, body = m.group(1), m.group(2)
        if seg.sub('', body).strip():
            return m.group(0)
        out, last = [], None
        for x1, y1, x2, y2 in seg.findall(body):
            out.append(f'L{x2} {y2}' if (x1, y1) == last else f'M{x1} {y1}L{x2} {y2}')
            last = (x2, y2)
        return head + '<path d="' + ''.join(out) + '"/>\n</g>'
    return re.sub(r'(<g class="stroked-text"><desc>[^<]*</desc>\s*)((?:<path d="[^"]*"\s*/>\s*)+)</g>',
                  chain, t, flags=re.S)


def process(src, dst, args, name):
    t = open(src, encoding='utf-8').read()
    x0, y0, x1, y1 = drawing_bounds(t, args.keep_title_block)
    x0, y0 = x0 - args.margin, y0 - args.margin
    w, h = x1 - x0 + args.margin, y1 - y0 + args.margin
    t = shrink(t)
    t, n = re.subn(r'width="[^"]*mm" height="[^"]*mm"\s*viewBox="[^"]*"',
                   f'width="{round(w * args.scale)}" height="{round(h * args.scale)}" '
                   f'viewBox="{x0:.2f} {y0:.2f} {w:.2f} {h:.2f}" role="img"', t, count=1, flags=re.S)
    if n != 1:
        sys.exit("Couldn't find the page size in kicad-cli's SVG.")
    title = args.title or f"Schematic: {name}"
    desc = args.desc or f"Exported from {name} with kicad-cli."
    t = re.sub(r'<title>[^<]*</title>\s*<desc>[^<]*</desc>',
               lambda m: f'<title>{escape(title)}</title>\n<desc>{escape(desc)}</desc>', t, count=1)
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    with open(dst, 'w', encoding='utf-8', newline='\n') as f:
        f.write(t)
    print(f"{dst}: {round(w * args.scale)} x {round(h * args.scale)} px, {len(t.encode()) // 1024} KB")


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    p.add_argument('schematic', help='the .kicad_sch file')
    p.add_argument('output', help='the .svg file to write (sub-sheets get -<sheet> added to the name)')
    p.add_argument('--title', help='title stored in the SVG (default: "Schematic: <file>")')
    p.add_argument('--desc', help='description stored in the SVG, for screen readers')
    p.add_argument('--margin', type=float, default=5.0, help='space around the drawing, in mm (default 5)')
    p.add_argument('--scale', type=float, default=4.0, help='pixels per mm for the image size (default 4)')
    p.add_argument('--keep-title-block', action='store_true',
                   help="keep text placed in the title-block corner (it's cropped off by default)")
    p.add_argument('--kicad-cli', help='path to kicad-cli, if it is not found automatically')
    args = p.parse_args()

    sch = os.path.abspath(args.schematic)
    if not os.path.isfile(sch):
        sys.exit(f"No such file: {args.schematic}")
    stem = os.path.splitext(os.path.basename(sch))[0]
    out_base, out_ext = os.path.splitext(args.output)
    with tempfile.TemporaryDirectory() as tmp:
        for page in export_pages(find_kicad_cli(args.kicad_cli), sch, tmp):
            sheet = os.path.splitext(os.path.basename(page))[0]
            suffix = sheet[len(stem):] if sheet.startswith(stem) else '-' + sheet
            process(page, out_base + suffix + (out_ext or '.svg'), args, os.path.basename(sch))


if __name__ == '__main__':
    main()
