# aquarium tamagotchi: design notes (rev B)

schematic: `aquarium-tamagotchi/aquarium-tamagotchi.kicad_sch` (single A4 sheet, PDF in `docs/schematic.pdf`).
ERC: 0 violations (kicad-mcp-pro `run_erc` and `kicad-cli sch erc --severity-all`). The exported netlist was diffed pin by pin against `tools/build_netlist.py`, with no split or merged nets.

Rev B trims rev A down to screen + microcontroller + buttons + buzzer, powered from USB-C only. The battery/charger, the LIS3DH accelerometer and the reset button were removed. Rev A is in git history if any of them come back.

## pin map (ESP32-S3-MINI-1-N4R2)

| GPIO | module pin | net | goes to |
| --- | --- | --- | --- |
| IO0 | 4 | BOOT | SW1 boot button to GND (strapping pin, internal pull-up) |
| IO13 | 17 | BTN_FEED | SW2 to GND, use internal pull-up |
| IO14 | 18 | BTN_LIGHT | SW3 to GND, use internal pull-up |
| IO17 | 21 | BUZZER | R4 1k to Q1 base (piezo driver), PWM |
| IO19 | 23 | USB_DN | USB-C D- (fixed by the chip) |
| IO20 | 24 | USB_DP | USB-C D+ (fixed by the chip) |
| IO21 | 25 | BTN_MENU | SW4 to GND, use internal pull-up |
| IO35 | 31 | TFT_BL | screen backlight, PWM |
| IO36 | 32 | TFT_CS | screen chip select |
| IO37 | 33 | TFT_DC | screen data/command |
| IO38 | 34 | TFT_RST | screen reset |
| IO39 | 35 | TFT_MOSI | screen SDA (data in) |
| IO40 | 36 | TFT_SCK | screen SCL (clock) |
| EN | 45 | EN | 10k pull-up + 1uF RC delay (no reset button, unplug USB to reset) |

The screen is on IO35–IO40 because those pads sit on the module edge facing the screen header, so the six traces fan straight up without crossing. They go through the GPIO matrix, so set the SPI clock to 40 MHz or less (the ST7735 tops out around 27 MHz anyway). IO35–37 are free on the N4R2. Only octal-PSRAM variants use them.

All other GPIOs are unused and carry no-connect flags. Avoid 3, 45 and 46 (strapping pins) and 26 (wired to the in-package PSRAM). 1, 2, 4–12, 15, 16, 18, 33, 34, 41 and 42 are free if a feature comes back.

The module is the -N4R2 variant because the MINI-1 is only sold as -N8 (no PSRAM) or -N4R2 (4 MB flash, 2 MB PSRAM). The PSRAM holds the screen framebuffer.

## screen header J2 (1x8 socket, 2.54 mm)

| pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| signal | GND | VCC (3V3) | SCL | SDA | RES | DC | CS | BLK |

This matches the 1.8" 128x160 ST7735 module's pin order (GND, VCC, SCL, SDA, RST, DC, CS, BLK). Most of these modules run fine on 3.3V. Some red ones have a 5V regulator and a solder jumper (often labelled J1) that has to be bridged for 3.3V operation, so check yours.

Firmware: ST7735 driver ("green tab" or "black tab" variant, depending on the module), 128x160, SPI around 27 MHz. A full 16-bit framebuffer is only 40 KB, so it fits in internal RAM. PSRAM is spare.

## parts list (23)

| ref | value | footprint | notes |
| --- | --- | --- | --- |
| U1 | ESP32-S3-MINI-1-N4R2 | RF_Module:ESP32-S2-MINI-1 | same land pattern as the S3-MINI-1. KiCad has no separate footprint, and this is the library default for the symbol |
| U2 | AP2112K-3.3 | SOT-23-5 | 600 mA LDO, 5V USB → 3.3V |
| Q1 | MMBT3904 | SOT-23 | NPN buzzer driver |
| D1 | 1N4148WS | SOD-323 | flyback across the buzzer |
| J1 | USB-C 16P | HRO TYPE-C-31-M-12 | power + programming (common JLCPCB part) |
| J2 | 1x8 socket | PinSocket 1x08 2.54 mm | 1.8" ST7735 module plugs in here |
| SW1 | BOOT | TL3342 SMD | hold while plugging in to force download mode |
| SW2–SW4 | FEED, LIGHT, MENU | 6 mm THT tactile | user buttons |
| BZ1 | piezo | 12 x 9.5 mm, 7.6 mm pitch | passive piezo or magnetic buzzer |
| R1, R2 | 5.1k | 0603 | CC1/CC2 pulldowns (USB-C sink) |
| R3 | 10k | 0603 | EN pull-up |
| R4 | 1k | 0603 | Q1 base |
| R5 | 10k | 0603 | Q1 base pulldown (buzzer silent during boot) |
| C1, C2 | 10uF | 0805 | LDO in / out |
| C3, C4 | 10uF, 100nF | 0805, 0603 | ESP32 3V3 (Espressif reference) |
| C5 | 1uF | 0603 | EN delay |

## board (rev B)

`aquarium-tamagotchi/aquarium-tamagotchi.kicad_pcb`: 50 x 75 mm, 2 layers, 3 mm corner radius, GND pour on both layers. Renders in `docs/board-front.png` and `docs/board-back.png`.

- **Front:** screen socket J2 along the top edge. The screen module plugs in and covers the middle of the board (34.5 x 56.5 mm assumed, the largest common 1.8" ST7735 module, drawn on the F.Fab layer). All SMD parts sit underneath it, so JLCPCB only assembles one side. The FEED / LIGHT / MENU buttons run along the bottom, below the screen.
- **ESP32:** lies along the left edge with its antenna flush to the edge, outside the screen's footprint. The copper-free strip down the left edge is Espressif's antenna keep-out.
- **USB-C:** on the right edge.
- **BOOT (SW1):** under the screen. Unplug the screen to reach it, which only matters if firmware breaks USB flashing.
- **Back:** only the piezo buzzer (9.5 mm tall, too tall to fit under the screen).
- **Routing:** Freerouting 2.0.1 via a Specctra DSN/SES round trip. 0.25 mm signals, 0.4 mm for VBUS and +3V3. The 0.4 mm rule is in `aquarium-tamagotchi.kicad_dru`.
- **Schematic link:** every footprint is linked to its schematic symbol. `kicad-cli pcb drc --schematic-parity` reports 0 differences.
- **DRC:** 0 errors, 0 unconnected. 5 warnings remain: the ESP32 and USB-C silkscreen outlines touch the board edge because both parts sit flush with it on purpose. JLCPCB trims silkscreen at the edge.

## things to confirm

- **Backlight drive:** BLK goes straight to IO35. That's fine for modules with an on-board backlight transistor or resistor. If yours draws more than ~20 mA on BLK, add a transistor.
- **No USB ESD protection.** Fine for a hobby board.
- **Screen module outline:** the layout assumes the 8-pin header runs along the module's short top edge, roughly centred, and the module is at most 34.5 x 56.5 mm. Measure yours before ordering. A module taller than 56.5 mm will cover the button row, and an off-centre header shifts the screen sideways.
- **Button height:** the screen sits ~10 mm above the PCB on its socket. Pick a tactile switch tall enough for the enclosure you plan, e.g. 6 x 6 mm with 9.5 mm or 13 mm actuators.

## shopping list

The PCB itself: JLCPCB, 2 layers, 50 x 75 mm, 1.6 mm. The order files are in `aquarium-tamagotchi/fab/jlcpcb/` (see ordering below).

**Parts JLCPCB can assemble** (all on the front, one-sided SMT):

| qty | part | package | ref |
| --- | --- | --- | --- |
| 1 | Espressif ESP32-S3-MINI-1-N4R2 | module | U1 |
| 1 | Diodes Inc AP2112K-3.3TRG1 (3.3 V LDO) | SOT-23-5 | U2 |
| 1 | MMBT3904 NPN transistor | SOT-23 | Q1 |
| 1 | 1N4148WS diode | SOD-323 | D1 |
| 1 | HRO TYPE-C-31-M-12 USB-C receptacle | SMD | J1 |
| 1 | 4-pad SMD tactile switch, E-Switch TL3342 footprint | SMD | SW1 (BOOT) |
| 2 | 5.1 kΩ resistor 1% | 0603 | R1, R2 |
| 2 | 10 kΩ resistor 1% | 0603 | R3, R5 |
| 1 | 1 kΩ resistor 1% | 0603 | R4 |
| 3 | 10 µF ceramic, X5R, ≥10 V | 0805 | C1, C2, C3 |
| 1 | 100 nF ceramic, X7R | 0603 | C4 |
| 1 | 1 µF ceramic, X7R | 0603 | C5 |

**Parts to solder yourself** (through-hole):

| qty | part | notes |
| --- | --- | --- |
| 1 | 1.8" ST7735 128x160 SPI module, 8-pin (GND VCC SCL SDA RST DC CS BLK) | the one you picked |
| 1 | 1x8 female pin header, 2.54 mm, vertical | the screen plugs into this. A straight male header works too if you'd rather solder the screen down |
| 3 | 6 x 6 mm through-hole tactile switch, 4 pins | FEED / LIGHT / MENU. Pick the actuator height to suit your case (5, 7, 9.5 or 13 mm) |
| 1 | passive magnetic buzzer, 12 mm diameter, 9.5 mm tall, 7.6 mm pin pitch, 3–5 V | must be **passive**. An active buzzer only plays one fixed tone |

Plus a USB-C cable for power and flashing.

## ordering from JLCPCB

Files are in `aquarium-tamagotchi/fab/jlcpcb/`:

- `gerbers.zip`: the nine fab layers (copper, mask, paste and silkscreen on both sides, plus the board outline) and separate plated/unplated Excellon drill files in mm. Upload this on the PCB order page. The defaults are fine: 2 layers, 1.6 mm, HASL lead-free.
- `bom.csv` and `cpl.csv`: for PCB Assembly, top side only. They cover the 15 SMD parts (11 BOM lines) with LCSC codes checked against the JLCPCB catalog on 2026-11-20. The ESP32 (C3013941), the AP2112K (C51118) and the USB-C (C165948) are "extended" parts, so each adds a small setup fee. Everything else is a basic part.
- **Left out of assembly, solder these yourself:** the screen socket J2, the FEED/LIGHT/MENU buttons, the buzzer and the BOOT switch SW1. No LCSC switch was confirmed to match the TL3342 pad layout. You can pick one in JLCPCB's BOM screen if you'd rather they fit it.
- **Check the 3D preview before paying.** In JLCPCB's placement preview, part rotations sometimes come out 90° or 180° off for modules and SOT parts. Fix any that look wrong right there: the ESP32 antenna must point at the left board edge, and the USB-C opening must face the right edge.

To regenerate after board changes: export gerbers, drill and positions with `kicad-cli` (layer list in this section), then `python3 tools/make_jlc_files.py positions.csv aquarium-tamagotchi/fab/jlcpcb`.
