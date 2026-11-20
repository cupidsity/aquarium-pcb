# aquarium tamagotchi: design notes (rev C)

Rev C builds the board around a **Seeed Studio XIAO ESP32S3** dev board. It already has the USB-C port, the 3.3V regulator and the BOOT/RESET buttons, so the PCB only carries the screen, three buttons and the buzzer. Every part is through-hole, so the whole board can be hand-soldered. Rev B (ESP32-S3 module with its own USB-C and regulator) and rev A (plus battery charging and an accelerometer) are in git history.

- **Schematic:** `aquarium-tamagotchi/aquarium-tamagotchi.kicad_sch` (A4, PDF in `docs/schematic.pdf`). ERC 0 violations. The exported netlist was diffed pin by pin against `tools/build_netlist.py`.
- **Board:** `aquarium-tamagotchi/aquarium-tamagotchi.kicad_pcb`. 50 x 75 mm, 2 layers, routed, GND pour on both sides. DRC: 0 errors, 0 unconnected, 0 schematic-parity differences.
- **Project library:** `aquarium-tamagotchi/libs/`. Holds the XIAO symbol and footprint, because KiCad's built-in libraries don't include it. The footprint uses Seeed's official pad layout (two rows of 7, 15.24 mm apart, 2.54 mm pitch) with 1.0 mm holes for standard header pins.

## pin map (XIAO ESP32S3)

| XIAO pin | GPIO | net | goes to |
| --- | --- | --- | --- |
| D0 | 1 | BTN_FEED | FEED button to GND (use the internal pull-up) |
| D1 | 2 | BTN_LIGHT | LIGHT button to GND (internal pull-up) |
| D2 | 3 | TFT_RST | screen RST |
| D3 | 4 | BTN_MENU | MENU button to GND (internal pull-up) |
| D4 | 5 | BUZZER | 1k to the 2N3904 base, PWM for tones |
| D5 | 6 | (spare) | free for a future feature |
| D6 | 43 | TFT_BL | screen backlight, PWM. Flickers briefly at boot because this is the UART TX pin |
| D7 | 44 | TFT_DC | screen DC |
| D8 | 7 | TFT_SCK | screen SCL (XIAO default SPI SCK) |
| D9 | 8 | TFT_CS | screen CS |
| D10 | 9 | TFT_MOSI | screen SDA (XIAO default SPI MOSI) |
| 3V3 | | +3V3 | screen VCC and buzzer |
| GND | | GND | |
| 5V | | (unused) | |

In firmware, use the D-names (for example `D8`) or the GPIO numbers above. Check them against Seeed's pinout page for your board revision. Set up the ST7735 driver for 128x160 with SPI around 27 MHz. Pick "green tab" or "black tab" to match your module.

## board layout

- **Front:**
  - The 8-pin screen socket runs along the top edge. The 1.8" ST7735 module (assumed at most 34.5 x 56.5 mm, drawn on the F.Fab layer) plugs in and covers the upper part of the board.
  - The buzzer driver (R1, R2, D1, Q1) sits under the screen. Seat the 2N3904 low, because the screen hovers about 8.5 mm above the board on its socket.
  - FEED / LIGHT / MENU run along the bottom, below the screen.
- **Back:**
  - The XIAO plugs into two 7-pin sockets. Its USB-C sticks out about 1.4 mm past the right board edge, and its own BOOT/RESET buttons face outward.
  - The buzzer also sits on the back.
- **Routing:** Freerouting 2.0.1 via a Specctra DSN/SES round trip. 0.25 mm signals, 0.4 mm for +3V3 (rule in `aquarium-tamagotchi.kicad_dru`).
- **DRC warning (expected):** the XIAO outline touches the board edge because its USB end sits there on purpose.

## parts list

| qty | part | ref | notes |
| --- | --- | --- | --- |
| 1 | Seeed Studio XIAO ESP32S3 | U1 | the plain one, not the "Sense" camera version. Comes with pin headers |
| 2 | 1x7 female pin header, 2.54 mm | (for U1) | lets the XIAO unplug. Or solder the XIAO's male headers straight into the board |
| 1 | 1.8" ST7735 128x160 SPI module, 8-pin (GND VCC SCL SDA RST DC CS BLK) | (plugs into J1) | some red modules need a solder jumper bridged to run on 3.3V |
| 1 | 1x8 female pin header, 2.54 mm | J1 | screen socket |
| 3 | 6 x 6 mm through-hole tactile switch, 4 pins | SW1–SW3 | pick the actuator height for your case |
| 1 | passive magnetic buzzer, 12 mm, 7.6 mm pin spacing, 3–5V | BZ1 | must be passive (an active buzzer only plays one tone) |
| 1 | 2N3904 NPN transistor, TO-92 | Q1 | |
| 1 | 1N4148 diode, DO-35 | D1 | the band (cathode) goes to the square pad marked K |
| 1 | 1 kΩ resistor, 1/4 W axial | R1 | |
| 1 | 10 kΩ resistor, 1/4 W axial | R2 | |
| 1 | USB-C cable | | power and flashing, plugged into the XIAO |

## ordering the board

`aquarium-tamagotchi/fab/jlcpcb/gerbers.zip` holds the nine fab layers (copper, mask, paste and silkscreen on both sides, plus the outline) and the Excellon drill file in mm. Upload it on JLCPCB's PCB page with the defaults (2 layers, 1.6 mm, HASL). No assembly order is needed, since every part is through-hole and hand-soldered.

## things to confirm before ordering

- **Measure the screen module.** The layout assumes the 8-pin header runs along its short top edge, roughly centred, and the module is no bigger than 34.5 x 56.5 mm.
- **Check the screen's supply jumper.** The screen runs from the XIAO's 3.3V. If yours has a 5V regulator with a jumper, bridge it for 3.3V.
- **Check the backlight current.** BLK goes straight to D6. That's fine for modules with an on-board backlight transistor or resistor. If BLK draws more than ~20 mA, add a transistor.
