# schematic notes (rev A)

schematic: `aquarium-tamagotchi/aquarium-tamagotchi.kicad_sch` (single A3 sheet, PDF in `docs/schematic.pdf`).
ERC: 0 violations (kicad-mcp-pro `run_erc` and `kicad-cli sch erc --severity-all`). The exported netlist was diffed pin by pin against `tools/build_netlist.py`, with no split or merged nets.

## pin map (ESP32-S3-MINI-1-N4R2)

| GPIO | module pin | net | goes to |
| --- | --- | --- | --- |
| IO0 | 4 | BOOT | SW1 boot button to GND (strapping pin, internal pull-up) |
| IO2 | 6 | VBAT_SENSE | VBAT / 2 divider (R6/R7 100k, C11 100nF). ADC1_CH1, works with wifi on |
| IO4 | 8 | I2C_SDA | LIS3DH SDA, 4.7k pull-up R9 |
| IO5 | 9 | I2C_SCL | LIS3DH SCL, 4.7k pull-up R10 |
| IO6 | 10 | ACCEL_INT1 | LIS3DH INT1 (tap / tilt interrupt) |
| IO7 | 11 | TFT_BL | screen backlight, PWM |
| IO8 | 12 | TFT_RST | screen reset |
| IO9 | 13 | TFT_DC | screen data/command |
| IO10 | 14 | TFT_CS | screen chip select |
| IO11 | 15 | TFT_MOSI | screen SDA (data in) |
| IO12 | 16 | TFT_SCK | screen SCL (clock) |
| IO13 | 17 | BTN_FEED | SW3 to GND, use internal pull-up |
| IO14 | 18 | BTN_LIGHT | SW4 to GND, use internal pull-up |
| IO17 | 21 | BUZZER | R11 1k to Q2 base (piezo driver), PWM |
| IO19 | 23 | USB_DN | USB-C D- (fixed by the chip) |
| IO20 | 24 | USB_DP | USB-C D+ (fixed by the chip) |
| IO21 | 25 | BTN_MENU | SW5 to GND, use internal pull-up |
| EN | 45 | EN | 10k pull-up + 1uF RC delay, SW2 reset to GND |

IO7–IO12 are the S3's FSPI-capable pins, routed through the GPIO matrix. That's fine for an ST7789 at 40–80 MHz.

All other GPIOs are unused and carry no-connect flags: 1, 3, 15, 16, 18, 26, 33–42, 45–48, plus TXD0/RXD0. The firmware should avoid 3, 45 and 46 (strapping pins) and leave 26 alone (on the N4R2 it is wired to the in-package PSRAM). 1, 15, 16, 18 and 33–42 are free for later features.

## screen header J3 (1x8 socket, 2.54 mm)

| pin | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| signal | GND | VCC (3V3) | SCL | SDA | RES | DC | CS | BLK |

This matches the common 1.54" 240x240 ST7789 breakouts that have a CS pin. Check the order printed on the module you buy before ordering the board, because some sellers swap pins.

## power path

USB VBUS → D1 (B5819W Schottky) → VSYS → U3 AP2112K-3.3 → +3V3.
VBAT → Q1 (DMG2301L P-FET) → VSYS. Q1's gate sits on VBUS with a 100k pulldown (R5): with USB plugged in, the battery is cut off from the load so the MCP73831 sees only the battery and terminates correctly; unplugged, the gate drops low and the battery feeds VSYS.
The charger U2 (MCP73831-2, 4.2 V) charges at ~210 mA with PROG = 4.7k (R3). Use a 2.2k resistor for ~450 mA if the cell is 500 mAh or larger. D2 lights while charging (STAT pulls low).

## parts list

| ref | value | footprint | notes |
| --- | --- | --- | --- |
| U1 | ESP32-S3-MINI-1-N4R2 | RF_Module:ESP32-S2-MINI-1 | KiCad has no separate S3-MINI-1 footprint. The S2 one is the same 15.4 x 20.5 mm land pattern and is the library's default for this symbol |
| U2 | MCP73831-2-OT | SOT-23-5 | LiPo charger |
| U3 | AP2112K-3.3 | SOT-23-5 | 600 mA LDO |
| U4 | LIS3DH | LGA-16 3x3 mm | accelerometer, I2C address 0x18 |
| Q1 | DMG2301L | SOT-23 | P-FET, battery/USB load sharing |
| Q2 | MMBT3904 | SOT-23 | NPN buzzer driver |
| D1 | B5819W | SOD-123 | Schottky, VBUS → VSYS |
| D2 | LED (CHG) | 0603 | charge indicator |
| D3 | 1N4148WS | SOD-323 | flyback across the buzzer |
| J1 | USB-C 16P | HRO TYPE-C-31-M-12 | USB 2.0 receptacle (common JLCPCB part) |
| J2 | JST-PH 2-pin | S2B-PH-K horizontal | LiPo. pin 1 = +, pin 2 = GND |
| J3 | 1x8 socket | PinSocket 1x08 2.54 mm | ST7789 module |
| SW1, SW2 | BOOT, RESET | TL3342 SMD | programming buttons |
| SW3–SW5 | FEED, LIGHT, MENU | 6 mm THT tactile | user buttons |
| BZ1 | piezo | 12 x 9.5 mm, 7.6 mm pitch | passive piezo / magnetic buzzer |
| R1, R2 | 5.1k | 0603 | CC1/CC2 pulldowns (USB-C sink) |
| R3 | 4.7k | 0603 | charge current |
| R4 | 1k | 0603 | charge LED |
| R5 | 100k | 0603 | Q1 gate pulldown |
| R6, R7 | 100k | 0603 | battery sense divider |
| R8 | 10k | 0603 | EN pull-up |
| R9, R10 | 4.7k | 0603 | I2C pull-ups |
| R11 | 1k | 0603 | Q2 base |
| R12 | 10k | 0603 | Q2 base pulldown (buzzer silent during boot) |
| R13 | 0 | 0603 | LIS3DH SA0 strap to GND. Move it to 3V3 for address 0x19 |
| C1, C2 | 4.7uF | 0805 | charger VDD / VBAT (per MCP73831 datasheet) |
| C3, C4 | 10uF | 0805 | LDO in / out (datasheet asks for ≥1uF) |
| C5, C6 | 10uF, 100nF | 0805, 0603 | ESP32 3V3 (Espressif reference) |
| C7 | 1uF | 0603 | EN delay |
| C8, C9 | 100nF, 10uF | 0603, 0805 | LIS3DH VDD (per datasheet) |
| C10 | 100nF | 0603 | LIS3DH VDD_IO |
| C11 | 100nF | 0603 | battery sense filter |

## things to decide during review

- **Module variant:** the plan asked for N8R2, but the MINI-1 is only sold as -N8 (8 MB flash, no PSRAM) and -N4R2 (4 MB flash, 2 MB PSRAM). The schematic uses N4R2 to keep the PSRAM framebuffer. Use the S3-WROOM-1 if you need 8 MB flash and PSRAM together (bigger module, different footprint).

- **Battery polarity:** JST-PH LiPo leads are not standardized between sellers. Check the cell's red wire lands on J2 pin 1 before plugging in.
- **Backlight drive:** BLK goes straight to IO7. That's fine for modules with an on-board backlight transistor or resistor (most 1.54" breakouts). If yours draws more than ~20 mA on BLK, add a transistor.
- **Not included:** USB ESD protection (e.g. USBLC6-2SC6) and a power switch. Every part on the board is powered whenever a battery is connected, so the firmware should use deep sleep.
- **Footprint choices to confirm:** J1 (HRO TYPE-C-31-M-12), the 6 mm THT tactile buttons, and the 12 mm buzzer were picked as common JLCPCB parts. LCSC part numbers aren't assigned yet.
