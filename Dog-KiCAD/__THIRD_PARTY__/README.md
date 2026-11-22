# Third-Party Libraries

This folder stores the project's third-party KiCad files: the symbols, footprints and 3D models that don't come with KiCad.

- Use one folder per part, for example `Teensy-4_1/`.
- Keep each library's license with its files.
- For Adafruit boards, keep Adafruit's original EagleCAD files in `<Part>/__EagleCAD-ORIGINAL__/`, and put the KiCad import next to that folder.

These files aren't used until they're linked to the KiCad project. To link them in KiCad 10, or to import an Adafruit EagleCAD design, follow [`../__Linker-Files__/README.md`](../__Linker-Files__/README.md).

## Contents

| Folder | What's in it | Source |
|---|---|---|
| `Teensy-4_1/teensy_library` | Teensy symbols | [XenGi/teensy_library](https://github.com/XenGi/teensy_library) |
| `Teensy-4_1/teensy.pretty` | Teensy footprints and 3D models | [XenGi/teensy.pretty](https://github.com/XenGi/teensy.pretty) |
| `Adafruit-Modules/` | One-part symbols and footprints for the Adafruit breakouts (BNO085, INA228). This is what the project links. | Made from the Adafruit PCB files below |
| `Adafruit-BNO08x/` | BNO085 9-DOF IMU breakout: KiCad import and the original EagleCAD files. Reference only, not linked. | [adafruit/Adafruit-BNO08x-PCB](https://github.com/adafruit/Adafruit-BNO08x-PCB) |
| `Adafruit-INA228/` | INA228 I2C power monitor breakout: KiCad import and the original EagleCAD files. Reference only, not linked. | [adafruit/Adafruit-INA228-PCB](https://github.com/adafruit/Adafruit-INA228-PCB) |
