# Leg bench wiring

Wiring for testing one leg on the bench: a Teensy 4.1, three hobby servos (tilt, hip and knee), and three Adafruit INA228 current-sensor boards (product 5832), one per servo. The schematic is [`leg.kicad_sch`](leg.kicad_sch).

The servo pins come from the legs firmware's `app.overlay`, the I²C pins from Zephyr's Teensy 4.1 board files, and the board details from Adafruit's guide and PCB files.

> [!WARNING]
> **Power the INA228 boards from the Teensy's 3.3V pin, not 5 V.** The boards have no regulator or level shifter. Their 10 kΩ SDA and SCL pull-ups go straight to VIN, so at 5 V the I²C lines would sit at 5 V, and the Teensy 4.1's pins can't take that.

> [!CAUTION]
> **The 5 V servo supply also powers the Teensy.** It feeds the Teensy's VIN, and VIN takes 3.6–5.5 V. Keep the supply at 5 V. If your servos need more, power the Teensy separately and disconnect its VIN from the servo supply. See [Teensy power](#teensy-power).

> [!IMPORTANT]
> **The firmware doesn't use VBUS or ALRT yet.** `app.overlay` drives the servos on pins 4, 5 and 6 and reads current from the three boards, but it measures shunt voltage only and has nothing on pins 7–9. To read the supply voltage and power, change the INA228s' `adc-mode` to "Bus and shunt voltage continuous".

## Schematic

![Schematic exported from leg.kicad_sch. Teensy 4.1 (U1) pins 4, 5 and 6 drive the tilt, hip and knee servos (M1 to M3). Pins 18 (SDA0) and 19 (SCL0) run to three Adafruit INA228 boards: U2 at 0x40, U3 at 0x41 and U4 at 0x44, powered from the Teensy's 3.3V pin (Vout). The 5 V supply BT1 (PowerSupply1+) feeds each board's VIN+ and VBUS and the Teensy's VIN, with C1 (100 µF) to GND. Each board's VIN− feeds its servo's + wire. Each board's ALRT pin goes to Teensy pin 7, 8 or 9 (ALRT0 to ALRT2), with 10 kΩ pull-ups R1 to R3 to 3.3 V.](images/leg-bench-schematic.svg)

| In the drawing | Meaning |
| --- | --- |
| Green line | Wire |
| Dot | Wires joined |
| Lines crossing without a dot | Not joined. Each board's VIN− wire crosses the +5 V line this way. |
| Flag label (`SDA0`, `ALRT0`, …) | Joined to every other label with the same name |
| `GND`, `+5V` and `+3.3V` symbols | Joined to every other symbol with the same name. `+5V` is the `PowerSupply1+` net, and `+3.3V` is the `Vout` net. |
| Text inside a board | Its I²C address, and the jumpers that set it |

| Part | What it is |
| --- | --- |
| U1 | Teensy 4.1 |
| U2, U3, U4 | INA228 boards for the tilt, hip and knee servos |
| M1, M2, M3 | Tilt, hip and knee servos |
| BT1 | 5 V servo supply (bench PSU or battery) |
| C1 | 100 µF across the 5 V supply, at the Teensy |
| R1, R2, R3 | 10 kΩ pull-ups on the ALRT lines |

Not in the schematic: the joint position sensors on pins 14–16, the micro-USB console, and Ethernet to the master.

To update the image after changing the schematic, run this from this folder (see [`__Scripts__`](../../__Scripts__/README.md)):

```
python ../../__Scripts__/export_schematic_svg.py leg.kicad_sch images/leg-bench-schematic.svg
```

## How each servo gets power

![One servo's power loop. Servo supply + goes to the board's VIN+ terminal, through the 15 mΩ shunt to VIN−, then to the servo's red V+ wire. The servo's ground wire returns to supply −, which also joins the Teensy GND and the boards' GND. The board's VIN pad takes 3.3 V from the Teensy and carries no servo current.](images/servo-power-loop.svg)

1. **Supply + to VIN+.** The servo supply's + goes to the board's VIN+ screw terminal. One supply feeds the VIN+ terminal on all three boards.
2. **Through the shunt.** On the board, the current flows through the 15 mΩ shunt to the VIN− terminal. The shunt is already on the board, so there's nothing to wire. The INA228 reads the small voltage across it, and that's the current measurement.
3. **VIN− to the servo.** Each board's VIN− goes to the red V+ wire of the servo it measures.
4. **Servo ground back to supply −.** The servo's brown or black wire returns to the supply's −. The Teensy GND and every board's GND join that same ground. That's what the ground symbols on the schematic mean.

`V_SERVO` in this figure is the `PowerSupply1+` net in the schematic. The figure leaves out the signal wire (pin 4, 5 or 6), the [VBUS](#vbus) link and the [Teensy's VIN](#teensy-power), which also connect to the supply +.

**VIN and VIN+ are different pads.** VIN, next to SCL and SDA, takes 3.3 V from the Teensy and only runs the sensor chip. VIN+ and VIN− on the screw terminal carry the servo current.

## Wire list

| Net | From | To |
| --- | --- | --- |
| `PWM0` | Teensy pin 4 | M1 (tilt servo) signal wire |
| `PWM1` | Teensy pin 5 | M2 (hip servo) signal wire |
| `PWM2` | Teensy pin 6 | M3 (knee servo) signal wire |
| `SDA0` | Teensy pin 18 | SDA on U2, U3 and U4 |
| `SCL0` | Teensy pin 19 | SCL on U2, U3 and U4 |
| `Vout` (`+3.3V`) | Teensy 3.3V | VIN on U2, U3 and U4, and R1, R2 and R3 |
| `GND` | Teensy GND | GND on U2, U3 and U4, every servo ground wire, BT1 −, and C1 |
| `PowerSupply1+` (`+5V`) | BT1 + | VIN+ and VBUS on U2, U3 and U4, the Teensy's VIN, and C1 |
| Servo + ×3 | VIN− on U2, U3 and U4 | The + (red) wire of M1, M2 and M3 |
| `ALRT0` | U2 ALRT | Teensy pin 7, and R1 |
| `ALRT1` | U3 ALRT | Teensy pin 8, and R2 |
| `ALRT2` | U4 ALRT | Teensy pin 9, and R3 |

The 15 mΩ shunt sits on each board between VIN+ and VIN−, so the servo current flows in at VIN+ and out at VIN−. Use the labels printed on the board's terminal block.

## STEMMA QT cabling

The Teensy has no STEMMA QT port. Use a STEMMA QT to male-header cable from the Teensy to the first board, then ordinary STEMMA QT cables from board to board. Both QT ports on each board carry the same four signals, so the order doesn't matter.

| Cable wire | Teensy 4.1 | Board |
| --- | --- | --- |
| Red | 3.3V | VIN |
| Black | GND | GND |
| Blue | Pin 18 | SDA |
| Yellow | Pin 19 | SCL |

Colors are from Adafruit's STEMMA QT cables (products 4209 and 4397), which follow the Qwiic convention. Jumper wires to the board's header pins work the same way.

The QT cables don't carry VBUS or ALRT. Wire those to the board's header pins.

## Jumpers on the back

| Board | Measures | A0 | A1 | Address | VBUS jumper |
| --- | --- | --- | --- | --- | --- |
| U2 | Tilt servo (M1) | Open | Open | `0x40` | Either |
| U3 | Hip servo (M2) | Closed | Open | `0x41` | Either |
| U4 | Knee servo (M3) | Open | Closed | `0x44` | Either |

An open A0 or A1 jumper leaves that pin pulled to GND through 10 kΩ, and closing it ties the pin to VIN. Addresses are from TI's Table 7-2. Label each board with its address once you've soldered the jumpers.

The jumpers can only tie A0 and A1 to VIN, so the board offers just four addresses: `0x40`, `0x41`, `0x44` and `0x45`. `0x42` would need A0 wired to SDA, and the board's 10 kΩ pull-down on A0 would then drag SDA low.

The VBUS jumper can be open or closed, because VBUS is wired to the supply anyway (see [VBUS](#vbus)).

## VBUS

The INA228 measures two things:

- **Current**, from the voltage across the shunt (VIN+ minus VIN−).
- **Voltage**, from the VBUS pin. This is the supply voltage, measured against GND.

From those two, the chip also works out power (voltage × current) and keeps running totals of energy and charge. Here, VBUS reads the servo supply voltage, which can show the supply sagging when a servo stalls, or a battery running low.

Each board's VBUS pin is wired to the 5 V supply (`PowerSupply1+`), the same net as VIN+. On the bench, run a wire from VBUS to the supply +, or close the VBUS jumper on the back, which joins VBUS to VIN+ on the board. Either gives the same reading, and doing both is harmless.

Without it, VBUS floats: current still reads correctly, but voltage and power don't.

> [!CAUTION]
> VBUS goes to the 5 V supply, never to VIN. VIN is the Teensy's 3.3 V rail, so with the jumper closed, a wire from VBUS to VIN would short the servo supply onto it.

## ALRT

Each board's ALRT pin has its own Teensy pin: U2 goes to pin 7, U3 to pin 8 and U4 to pin 9 (`ALRT0` to `ALRT2`). The INA228 pulls ALRT low within about 75 µs when a reading crosses a limit the firmware sets, such as:

- too much current, for a stalled servo
- the supply sagging
- too much power
- the chip getting too hot

The firmware can then stop that servo without polling I²C. Reading the chip's `DIAG_ALRT` register shows which limit tripped.

- **ALRT is open-drain, and the board has no pull-up on it,** so R1, R2 and R3 (10 kΩ) pull each line up to 3.3 V.
- **Pull ALRT up to 3.3 V, never 5 V.** The pin can't go above the board's VIN + 0.3 V.
- **Pins 7 and 8 are also Serial2.** The firmware's console runs over USB, so they're free. Any free pin works if that changes.

## Teensy power

The Teensy's VIN connects straight to the 5 V supply (`PowerSupply1+`). C1 (100 µF) sits across the supply at the Teensy, from +5 V to GND.

- **VIN takes 3.6–5.5 V,** so the supply must stay at or below 5.5 V.
- **Cut the VIN–VUSB pad if USB and the supply can be connected at the same time.** The Teensy 4.1 joins VIN and VUSB through a pad on its underside. With the pad intact, the 5 V supply would feed back into the computer's USB port. Once it's cut, the Teensy runs only from VIN, and USB still carries data.

## Before you power it

- **Don't add pull-ups on SDA or SCL.** Each board has 10 kΩ on SDA and SCL, so three boards give about 3.3 kΩ in parallel, which is fine for a short 3.3 V bus.
- **The shunt is fixed at 15 mΩ, rated 10 A.** That gives ±163.84 mV ÷ 15 mΩ ≈ ±10.9 A full scale, or about ±2.7 A in the chip's high-resolution range (±40.96 mV). If your servo's stall current is under about 2.7 A, that range reads in finer steps.
- **Power the servos from the 5 V supply, never from the Teensy's pins,** and connect that supply's ground to the Teensy's GND. Hobby servo wires are usually orange, yellow or white for signal, red for V+, and brown or black for ground.
- **Cut the VIN–VUSB pad first** if USB will be plugged in while the supply is on (see [Teensy power](#teensy-power)).

## What this was checked against

- **Servo pins 4, 5, 6:** `submodule/Legs/app.overlay` routes them to FlexPWM2 submodules 0, 1 and 2, output A (pads GPIO_EMC_06, GPIO_EMC_08 and GPIO_B0_10), at 50 Hz.
- **I²C pins 18 (SDA) and 19 (SCL):** Zephyr 4.4's `boards/pjrc/teensy4/teensy4-pinctrl.dtsi` puts LPI2C1 SDA on GPIO_AD_B1_01 (pin 18) and SCL on GPIO_AD_B1_00 (pin 19). Zephyr's INA228 driver (`ti,ina228`) needs `rshunt-micro-ohms = <15000>` for this board's shunt.
- **Firmware:** `app.overlay` turns on the three INA228s at `0x40`, `0x41` and `0x44` with `adc-mode = "Shunt voltage continuous"`, sends the console over USB (`cdc_acm_uart0`), and uses none of pins 7–9.
- **Adafruit INA228 board:** Adafruit's PCB files (`Adafruit-INA228-PCB`, Eagle schematic) show no regulator or level shifter. They show the 10 kΩ SDA and SCL pull-ups to VIN, A0 and A1 jumpers to VIN with 10 kΩ pull-downs, the VBUS jumper between VBUS and VIN+, a 15 mΩ shunt between VIN+ and VIN−, 0.1 µF and 10 µF on VIN, and two STEMMA QT ports carrying GND, V+, SDA and SCL. ALRT runs only from the chip to header pin 8, with no pull-up. The product page and learn guide give the 10 A rating, default address 0x40, and high-side wiring (VIN+ to the supply, VIN− to the load).
- **INA228 chip:** TI datasheet SLYS021A (Rev. A, May 2022):
  - Addresses: Table 7-2
  - Shunt input range: Electrical Characteristics (6.5)
  - Pin functions: Table 5-1
  - ALRT maximum of VS + 0.3 V: Absolute Maximum Ratings (6.1)
  - ALRT open-drain, and the alert sources: 7.3.7
  - 75 µs alert response: Features
  - VBUS to "the voltage powering the load": Figure 10-1
- **The schematic:** `leg.kicad_sch`, checked with kicad-cli 10.0.8. Its netlist has 14 nets, all matching the wire list. ERC reports no errors on the INA228 boards, servos, resistors, battery or C1. Its remaining errors are the Teensy's unused pins and the power symbols without a power flag, plus 3 warnings that some nets have two names (`+5V` and `PowerSupply1+`, `+3.3V` and `Vout`, `GND` and `PowerSupply1-`).
- **The schematic image:** made from `leg.kicad_sch` by `__Scripts__/export_schematic_svg.py`. It runs `kicad-cli sch export svg --exclude-drawing-sheet`, then crops the result to the drawing and shrinks the file without changing the drawing.
- **The power-loop figure:** checked for overlapping labels, loose wire ends, and arrows that aren't on a wire.
