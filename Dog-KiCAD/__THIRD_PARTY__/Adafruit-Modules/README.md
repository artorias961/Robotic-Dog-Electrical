# Adafruit Modules

Adafruit breakout boards as single parts, one symbol and one footprint per breakout, so a whole breakout can be placed on our PCB like the Teensy. The footprint has the header holes, the mounting holes and the board outline. It does not include the parts on the breakout itself.

| Part | Pins (header order) | Board | Mounting holes |
|---|---|---|---|
| `Adafruit_BNO085_Breakout` ([4754](https://www.adafruit.com/product/4754)) | 1–6: VIN, 3Vo, GND, SCL, SDA, INT. 7–12: BT, P0, P1, RST, DI, CS | 25.4 × 22.86 mm | 4 |
| `Adafruit_INA228_Breakout` ([5832](https://www.adafruit.com/product/5832)) | 1–8: VIN, GND, SCL, SDA, VBUS, VIN-, VIN+, ALRT | 25.4 × 20.32 mm | 2 |

- Pin positions, hole positions and outlines were taken from Adafruit's PCB files in `../Adafruit-BNO08x/` and `../Adafruit-INA228/`. Pin names match the labels printed on the boards.
- Header pins: 1.0 mm drill, 1.7 mm pads, 2.54 mm pitch. Pin 1 is the square pad, and the footprint origin is on pin 1.
- Mounting holes: 2.7 mm, non-plated, for M2.5 screws or standoffs.
- The INA228's 3-pin screw terminal isn't in the footprint. It sits on the breakout, and its signals (VIN-, VBUS, VIN+) are also on the 8-pin header.
- There are no 3D models.

Linked in the project as `Adafruit_Modules` (see [`../../__Linker-Files__/README.md`](../../__Linker-Files__/README.md)).

## Add another Adafruit breakout

1. Import its EagleCAD files (see the Linker README).
2. Open the imported `.kicad_pcb` and note the position of every header pin and mounting hole, plus the board size.
3. In KiCad's Symbol Editor and Footprint Editor, add a new symbol and footprint to `Adafruit_Modules`, named `Adafruit_<Part>_Breakout`. Use the pin labels printed on the board as pin names.
4. Set the symbol's Footprint field to `Adafruit_Modules:Adafruit_<Part>_Breakout`.

## License

Derived from Adafruit's open-source PCB designs, by Limor Fried/Ladyada for Adafruit Industries, licensed CC BY-SA. See `license.txt` in each `__EagleCAD-ORIGINAL__/` folder.
