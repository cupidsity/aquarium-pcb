# schematic notes (rev B)

schematic: `aquarium-tamagotchi/aquarium-tamagotchi.kicad_sch` (single A4 sheet, PDF in `docs/schematic.pdf`).
ERC: 0 violations (kicad-mcp-pro `run_erc` and `kicad-cli sch erc --severity-all`). The exported netlist was diffed pin by pin against `tools/build_netlist.py`, with no split or merged nets.

Rev B trims rev A down to screen + microcontroller + buttons + buzzer, powered from USB-C only. The battery/charger, the LIS3DH accelerometer and the reset button were removed. Rev A is in git history if any of them come back.

## pin map (ESP32-S3-MINI-1-N4R2)

| GPIO | module pin | net | goes to |
| --- | --- | --- | --- |
| IO0 | 4 | BOOT | SW1 boot button to GND (strapping pin, internal pull-up) |
| IO7 | 11 | TFT_BL | screen backlight, PWM |
| IO8 | 12 | TFT_RST | screen reset |
| IO9 | 13 | TFT_DC | screen data/command |
| IO10 | 14 | TFT_CS | screen chip select |
| IO11 | 15 | TFT_MOSI | screen SDA (data in) |
| IO12 | 16 | TFT_SCK | screen SCL (clock) |
| IO13 | 17 | BTN_FEED | SW2 to GND, use internal pull-up |
| IO14 | 18 | BTN_LIGHT | SW3 to GND, use internal pull-up |
| IO17 | 21 | BUZZER | R4 1k to Q1 base (piezo driver), PWM |
| IO19 | 23 | USB_DN | USB-C D- (fixed by the chip) |
| IO20 | 24 | USB_DP | USB-C D+ (fixed by the chip) |
| IO21 | 25 | BTN_MENU | SW4 to GND, use internal pull-up |
| EN | 45 | EN | 10k pull-up + 1uF RC delay (no reset button, unplug USB to reset) |

All other GPIOs are unused and carry no-connect flags. Avoid 3, 45 and 46 (strapping pins) and 26 (wired to the in-package PSRAM). 1, 2, 4, 5, 6, 15, 16, 18 and 33–42 are free if a feature comes back.

The module is the -N4R2 variant because the MINI-1 is only sold as -N8 (no PSRAM) or -N4R2 (4 MB flash, 2 MB PSRAM). The PSRAM holds the screen framebuffer.

## screen header J2 (1x8 socket, 2.54 mm)

| pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| signal | GND | VCC (3V3) | SCL | SDA | RES | DC | CS | BLK |

This matches the common 1.54" 240x240 ST7789 breakouts that have a CS pin. Check the order printed on your module before ordering the board.

## parts list (23)

| ref | value | footprint | notes |
| --- | --- | --- | --- |
| U1 | ESP32-S3-MINI-1-N4R2 | RF_Module:ESP32-S2-MINI-1 | same land pattern as the S3-MINI-1. KiCad has no separate footprint, and this is the library default for the symbol |
| U2 | AP2112K-3.3 | SOT-23-5 | 600 mA LDO, 5V USB → 3.3V |
| Q1 | MMBT3904 | SOT-23 | NPN buzzer driver |
| D1 | 1N4148WS | SOD-323 | flyback across the buzzer |
| J1 | USB-C 16P | HRO TYPE-C-31-M-12 | power + programming (common JLCPCB part) |
| J2 | 1x8 socket | PinSocket 1x08 2.54 mm | ST7789 module |
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

## things to confirm

- **Backlight drive:** BLK goes straight to IO7. That's fine for modules with an on-board backlight transistor or resistor. If yours draws more than ~20 mA on BLK, add a transistor.
- **No USB ESD protection.** Fine for a hobby board.
