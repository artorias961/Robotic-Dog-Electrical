# Linker Files (KiCad 10)

Master copies of the project's KiCad library tables. They point KiCad at the libraries in `../__THIRD_PARTY__/` using paths relative to the project, so the libraries work right after cloning. No global KiCad setup is needed.

| File | Links |
|---|---|
| `sym-lib-table` | Symbol libraries (`.kicad_sym`) |
| `fp-lib-table` | Footprint libraries (`.pretty` folders) |

## Use them in a KiCad project

1. Copy `sym-lib-table` and `fp-lib-table` into the project folder, next to the `.kicad_pro` file (for example `KiCAD/`).
2. In KiCad, open **File → Project Settings → Text Variables** and add:
   - Name: `KICAD_USER_DIR`
   - Value: `${KIPRJMOD}/../__THIRD_PARTY__/Teensy-4_1`

   The Teensy footprints use this variable to find their 3D models.
3. Open (or reopen) the project. The libraries show up under their nicknames in the symbol and footprint choosers (see **Current libraries**).

> `${KIPRJMOD}` is the folder that contains the `.kicad_pro`. The paths assume the project sits one folder below `Dog-KiCAD/` (like `Dog-KiCAD/KiCAD/`). For a project one level deeper, use `../../` instead of `../`, in the tables and in the text variable. Current projects: `KiCAD/` (`main`) uses `../`, and `KiCAD/leg/` uses `../../`.

## Add another library

1. Put the library in its own folder in `__THIRD_PARTY__/`, for example `__THIRD_PARTY__/<Part>/`.
2. Add a line to each table here, before the last `)`:

   `sym-lib-table`
   ```
   (lib (name "<nickname>") (type "KiCad") (uri "${KIPRJMOD}/../__THIRD_PARTY__/<Part>/<file>.kicad_sym") (options "") (descr "<what it is>"))
   ```

   `fp-lib-table`
   ```
   (lib (name "<nickname>") (type "KiCad") (uri "${KIPRJMOD}/../__THIRD_PARTY__/<Part>/<folder>.pretty") (options "") (descr "<what it is>"))
   ```
3. Copy the updated tables into every project folder, then reopen the project.
4. Check the 3D model path. Open one of the new `.kicad_mod` files and find its `(model ...)` line. If the path starts with a variable KiCad doesn't define, add that variable under Text Variables (like `KICAD_USER_DIR`).

If you'd rather use the GUI, go to **Preferences → Manage Symbol Libraries** (or **Manage Footprint Libraries**) and open the **Project Specific Libraries** tab. That edits the project's tables. Copy them back here afterwards so this folder stays the master copy.

## Import an Adafruit EagleCAD design

Adafruit shares its boards as EagleCAD files (`.sch` + `.brd`). KiCad 10 converts them into a KiCad project and creates a symbol library and a footprint library from them. Adafruit's own guide: [Viewing with KiCad](https://learn.adafruit.com/accessing-and-using-adafruit-pcb-design-files/viewing-with-kicad).

Folder layout, using the BNO08x as the example:

```
__THIRD_PARTY__/Adafruit-BNO08x/
├── __EagleCAD-ORIGINAL__/                  Adafruit's files (.sch, .brd, license.txt)
├── Adafruit_BNO08x.kicad_pro / _sch / _pcb Converted KiCad project
├── Adafruit_BNO08x-eagle-import.kicad_sym  Symbols
└── Adafruit_BNO08x-import-fps.pretty/      Footprints
```

1. Download the Adafruit PCB repo into `__THIRD_PARTY__/<Part>/__EagleCAD-ORIGINAL__/`.
2. In the KiCad project manager, go to **File → Import Non-KiCad Project → EAGLE Project...**
3. Select the `.brd` file.
4. For the **KiCad Project Destination**, pick `__THIRD_PARTY__/<Part>/`.
5. In the layer-mapping window, click **Auto-Match Layers**, then **OK**. Click **OK** on any warnings about layers that couldn't be matched.
6. Save both windows that open (schematic and PCB) with **Ctrl+S**. Nothing is written until you do.
7. To place the whole breakout as one part, add a symbol and footprint for it to `Adafruit-Modules`. The steps are in [its README](../__THIRD_PARTY__/Adafruit-Modules/README.md). The import stays in its folder as the reference for pin positions.

The import's own libraries (`<name>-eagle-import.kicad_sym` and `<name>-import-fps.pretty`) hold Adafruit's individual parts, such as the chip, capacitors and resistors, not one part for the breakout. They aren't linked in this project. Link them only if you want to put those parts directly on your own board. If you do, give the footprint library the nickname `<name>` (without `-import-fps`), because that's the name the imported symbols' Footprint fields use. The footprint folder only has the footprints used on Adafruit's board.

Notes:

- The import also creates a `.history/` folder and a `<name>.kicad_prl` file. Don't commit them: `.history/` is KiCad's local history and contains its own `.git` folder, and `.kicad_prl` holds your personal view settings.
- KiCad can only import Eagle XML files (Eagle 6 and newer). Adafruit's files are XML.
- Check the imported parts against the datasheet before using them. Imports can move silkscreen text, and they come without 3D models.
- Adafruit's files are licensed CC BY-SA, so keep `license.txt` and the credit with them.

## Tips

- Give each library its own nickname that doesn't match one of KiCad's built-in libraries.
- Link only `.kicad_sym` files and `.pretty` folders. Skip `.lib` and `.dcm` files; they're the old KiCad 5 format.
- Some symbols ship with an empty Footprint field, including the Teensy ones. After placing one, set the field yourself, for example `teensy:Teensy41`.
- KiCad only reads the tables next to the `.kicad_pro`, so keep them in sync with this folder.

## Current libraries

| Nickname (symbols and footprints) | Folder in `__THIRD_PARTY__/` | Parts |
|---|---|---|
| `teensy` | `Teensy-4_1/` | Teensy boards (use `Teensy4.1` with footprint `Teensy41`) |
| `Adafruit_Modules` | `Adafruit-Modules/` | `Adafruit_BNO085_Breakout`, `Adafruit_INA228_Breakout` |
