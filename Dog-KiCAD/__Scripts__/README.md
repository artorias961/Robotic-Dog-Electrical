# Scripts

Helper scripts for the KiCad projects. They aren't needed to open or edit the projects.

| Script | What it does |
| --- | --- |
| `export_schematic_svg.py` | Exports a schematic to an SVG for a README. The image has no sheet frame, is cropped to the drawing, and is a smaller file than KiCad's own export. |

## export_schematic_svg.py

Needs KiCad 8 or newer and Python 3.8 or newer. It finds `kicad-cli` on your PATH or in KiCad's default install folder.

Run it from the project folder. For example, from `KiCAD/leg`:

```
python ../../__Scripts__/export_schematic_svg.py leg.kicad_sch images/leg-bench-schematic.svg
```

Run it again whenever you change the schematic, so the README image stays current.

Options:

| Option | What it does |
| --- | --- |
| `--title`, `--desc` | Title and description stored in the SVG, for screen readers |
| `--margin` | Space around the drawing, in mm (default 5) |
| `--scale` | Pixels per mm for the image size (default 4) |
| `--keep-title-block` | Keep text placed in the title-block corner, such as a date or revision. It's cropped off by default, because the frame isn't exported. |
| `--kicad-cli` | Path to `kicad-cli`, if it isn't found automatically |

Notes:

- The drawing is KiCad's own export. Only the crop and the file size change.
- If the schematic has sub-sheets, each one gets its own file, named `<output>-<sheet>.svg`.
- KiCad doesn't need to be closed. The script only reads the schematic.
