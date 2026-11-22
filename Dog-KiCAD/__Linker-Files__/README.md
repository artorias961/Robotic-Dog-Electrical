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

> `${KIPRJMOD}` is the folder that contains the `.kicad_pro`. The paths assume the project sits one folder below `Dog-KiCAD/` (like `Dog-KiCAD/KiCAD/`). For a project one level deeper (like `KiCAD/main-leg/`), use `../../` instead of `../`, in the tables and in the text variable.

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
7. Link the two new libraries with the steps in **Add another library**, using these nicknames:
   - Symbols, `<name>-eagle-import.kicad_sym`: nickname `<name>-eagle-import`
   - Footprints, `<name>-import-fps.pretty`: nickname `<name>`, without `-import-fps`. The imported symbols' Footprint fields use this name (for example `Adafruit_BNO08x:BNO080`), so the footprints link automatically.

Notes:

- The `.pretty` folder only has the footprints used on Adafruit's board. Symbols for other package variants point to footprints that aren't there.
- The import also creates a `.history/` folder and a `<name>.kicad_prl` file. Don't commit them: `.history/` is KiCad's local history and contains its own `.git` folder, and `.kicad_prl` holds your personal view settings.
- KiCad can only import Eagle XML files (Eagle 6 and newer). Adafruit's files are XML.
- Check the imported parts against the datasheet before using them. Imports can move silkscreen text, and they come without 3D models.
- This gives you the parts used on the Adafruit board, such as the BNO085 chip. To place the whole breakout on your PCB the way the Teensy is placed, you need a module footprint (header pins and mounting holes), which these files don't include.
- Adafruit's files are licensed CC BY-SA, so keep `license.txt` and the credit with them.

## Tips

- Give each library its own nickname that doesn't match one of KiCad's built-in libraries.
- Link only `.kicad_sym` files and `.pretty` folders. Skip `.lib` and `.dcm` files; they're the old KiCad 5 format.
- Some symbols ship with an empty Footprint field, including the Teensy ones. After placing one, set the field yourself, for example `teensy:Teensy41`.
- KiCad only reads the tables next to the `.kicad_pro`, so keep them in sync with this folder.

## Current libraries

| Symbol nickname | Footprint nickname | Folder in `__THIRD_PARTY__/` |
|---|---|---|
| `teensy` | `teensy` | `Teensy-4_1/` |
| `Adafruit_BNO08x-eagle-import` | `Adafruit_BNO08x` | `Adafruit-BNO08x/` |
| `Adafruit INA228 I2C Power Monitor-eagle-import` | `Adafruit INA228 I2C Power Monitor` | `Adafruit-INA228/` |
