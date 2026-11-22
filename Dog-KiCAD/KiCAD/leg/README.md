# Leg bench wiring

Wiring for testing one leg on the bench: a Teensy 4.1, three hobby servos (tilt, hip and knee), and three Adafruit INA228 current-sensor boards (product 5832), one per servo.

The servo pins come from the legs firmware's `app.overlay`, the I²C pins from Zephyr's Teensy 4.1 board files, and the board details from Adafruit's guide and PCB files.

> [!WARNING]
> **Power the INA228 boards from the Teensy's 3.3V pin, not 5 V.** The boards have no regulator or level shifter. Their 10 kΩ SDA and SCL pull-ups go straight to VIN, so at 5 V the I²C lines would sit at 5 V, and the Teensy 4.1's pins can't take that.

> [!IMPORTANT]
> **The firmware doesn't match this wiring yet.** The servo pins (4, 5, 6) already match. But `app.overlay` still expects analog current sensors on pins 17–19, and its sensor and servo pins are switched off (`LEG_PINS_WIRED 0`). The firmware needs I²C and INA228 support, with a 15 mΩ shunt, before it can read these boards.

## Schematic

![Schematic. Teensy 4.1 pins 4, 5 and 6 drive the tilt, hip and knee servo signals. Pins 18 (SDA) and 19 (SCL) run to three Adafruit INA228 boards at 0x40, 0x41 and 0x44, powered from the Teensy's 3.3V pin. Each board sits in one servo's power lead: servo supply + to VIN+, through the board's shunt to VIN−, and VIN− to the servo's V+.](images/leg-bench-schematic.svg)

| In the drawing | Meaning |
| --- | --- |
| Blue line | I²C (SDA, SCL) |
| Orange line | 3.3 V |
| Red line | Servo power |
| Purple line | Servo signal (PWM) |
| Black line | Ground. Every ground symbol is the same net. |
| Thin red line inside a board | Already on the Adafruit board. Don't wire it. |
| Red arrow | Which way the servo current flows |
| Dot | Wires joined |
| Hop (half circle) | Wires cross but aren't joined |

## How each servo gets power

![One servo's power loop. Servo supply + goes to the board's VIN+ terminal, through the 15 mΩ shunt to VIN−, then to the servo's red V+ wire. The servo's ground wire returns to supply −, which also joins the Teensy GND and the boards' GND. The board's VIN pad takes 3.3 V from the Teensy and carries no servo current.](images/servo-power-loop.svg)

1. **Supply + to VIN+.** The servo supply's + goes to the board's VIN+ screw terminal. One supply feeds the VIN+ terminal on all three boards.
2. **Through the shunt.** On the board, the current flows through the 15 mΩ shunt to the VIN− terminal. The shunt is already on the board, so there's nothing to wire. The INA228 reads the small voltage across it, and that's the current measurement.
3. **VIN− to the servo.** Each board's VIN− goes to the red V+ wire of the servo it measures.
4. **Servo ground back to supply −.** The servo's brown or black wire returns to the supply's −. The Teensy GND and every board's GND join that same ground. That's what the ground symbols on the schematic mean.

The signal wire isn't in this figure. It goes to pin 4, 5 or 6, as on the schematic.

**VIN and VIN+ are different pads.** VIN, next to SCL and SDA, takes 3.3 V from the Teensy and only runs the sensor chip. VIN+ and VIN− on the screw terminal carry the servo current.

## Wire list

| Net | From | To |
| --- | --- | --- |
| `PWM_TILT` | Teensy pin 4 | Tilt servo signal wire |
| `PWM_HIP` | Teensy pin 5 | Hip servo signal wire |
| `PWM_KNEE` | Teensy pin 6 | Knee servo signal wire |
| `SDA` | Teensy pin 18 | SDA on all three boards |
| `SCL` | Teensy pin 19 | SCL on all three boards |
| `+3V3` | Teensy 3.3V | VIN on all three boards |
| `GND` | Teensy GND | GND on all three boards, every servo ground wire, and servo supply − |
| `V_SERVO` | Servo supply + | VIN+ terminal on all three boards |
| Servo V+ ×3 | VIN− terminal on each board | The V+ wire of the servo that board measures |
| `VBUS` | Each board's VBUS | Its own VIN+ terminal (not the 3.3 V VIN pad), through the VBUS jumper on the back. No wire needed once the jumper is closed. |
| `ALRT` | Each board's ALRT | Not connected |

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

## Jumpers on the back

| Board | Measures | A0 | A1 | Address | VBUS |
| --- | --- | --- | --- | --- | --- |
| U1 | Tilt servo | Open | Open | `0x40` | Closed |
| U2 | Hip servo | Closed | Open | `0x41` | Closed |
| U3 | Knee servo | Open | Closed | `0x44` | Closed |

An open A0 or A1 jumper leaves that pin pulled to GND through 10 kΩ, and closing it ties the pin to VIN. Addresses are from TI's Table 7-2. Label each board with its address once you've soldered the jumpers.

## VBUS

The INA228 measures two things:

- **Current**, from the voltage across the shunt (VIN+ minus VIN−).
- **Voltage**, from the VBUS pin. This is the supply voltage, measured against GND.

From those two, the chip also works out power (voltage × current) and keeps running totals of energy and charge. Here, VBUS reads the servo supply voltage, which can show the supply sagging when a servo stalls, or a battery running low.

Nothing from the Teensy or the servos connects to VBUS. It gets the supply voltage from VIN+ through the VBUS jumper on the back.

**Check the VBUS jumper with a meter.** Adafruit's guide says it ships open, but the README in its PCB files implies it ships closed. Measure continuity between the VBUS and VIN+ terminals:

- **If it beeps,** the jumper is closed and VBUS needs no wire.
- **If it doesn't,** solder the jumper closed, or join VBUS to VIN+ with a short wire.

Without it, current still reads correctly, but voltage and power don't.

> [!CAUTION]
> The link goes to **VIN+**, never to VIN. With the jumper closed, a wire from VBUS to VIN would short the servo supply onto the Teensy's 3.3 V rail.

## Before you power it

- **Don't add pull-ups.** Each board has 10 kΩ on SDA and SCL, so three boards give about 3.3 kΩ in parallel, which is fine for a short 3.3 V bus.
- **The shunt is fixed at 15 mΩ, rated 10 A.** That gives ±163.84 mV ÷ 15 mΩ ≈ ±10.9 A full scale, or about ±2.7 A in the chip's high-resolution range (±40.96 mV). If your servo's stall current is under about 2.7 A, that range reads in finer steps.
- **Power the servos from their own supply**, never from the Teensy, and connect that supply's ground to the Teensy's GND. Hobby servo wires are usually orange, yellow or white for signal, red for V+, and brown or black for ground.
- **Leave ALRT unconnected.** The firmware doesn't use it, and the board has no pull-up on it.

## What this was checked against

- **Servo pins 4, 5, 6:** `submodule/Legs/app.overlay` routes them to FlexPWM2 submodules 0, 1 and 2, output A (pads GPIO_EMC_06, GPIO_EMC_08 and GPIO_B0_10), at 50 Hz.
- **I²C pins 18 (SDA) and 19 (SCL):** Zephyr 4.4's `boards/pjrc/teensy4/teensy4-pinctrl.dtsi` puts LPI2C1 SDA on GPIO_AD_B1_01 (pin 18) and SCL on GPIO_AD_B1_00 (pin 19). Zephyr's INA228 driver (`ti,ina228`) needs `rshunt-micro-ohms = <15000>` for this board's shunt.
- **Adafruit INA228 board:** Adafruit's PCB files (`Adafruit-INA228-PCB`, Eagle schematic) show no regulator or level shifter. They show the 10 kΩ SDA and SCL pull-ups to VIN, A0 and A1 jumpers to VIN with 10 kΩ pull-downs, the VBUS jumper between VBUS and VIN+, a 15 mΩ shunt between VIN+ and VIN−, 0.1 µF and 10 µF on VIN, and two STEMMA QT ports carrying GND, V+, SDA and SCL. The product page and learn guide give the 10 A rating, default address 0x40, and high-side wiring (VIN+ to the supply, VIN− to the load).
- **INA228 chip:** TI datasheet SLYS021A (Rev. A, May 2022): addresses in Table 7-2, shunt input range in Electrical Characteristics (6.5), and pin functions in Table 5-1.
- **The drawings:** a script built the schematic from a declared list of wires, then worked out every connection from the drawing's geometry and compared it with the wire list above. It found 11 nets and 3 unused ALRT pads, all matching. Every junction has a dot, every crossing has a hop, and no label overlaps a wire or another label. The power-loop figure was checked for overlapping labels, loose wire ends, and arrows that aren't on a wire.
