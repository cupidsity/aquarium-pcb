# netlist that generated the schematic (edits made in kicad afterwards are not reflected here).
# running it writes build_calls.json, a [tool, args] list for kicad-mcp-pro's sch_build_circuit,
# which overwrites the whole sheet, so the no-connect flags on unused pins have to be placed again after.
# nets connect by name (stub + label/power symbol per pin), so placement only affects readability.
import json

RES = "Resistor_SMD:R_0603_1608Metric"
CAP = "Capacitor_SMD:C_0603_1608Metric"
CAP_BULK = "Capacitor_SMD:C_0805_2012Metric"

def part(reference, library, symbol_name, value, footprint, x_mm, y_mm, rotation=0):
    return {"reference": reference, "library": library, "symbol_name": symbol_name, "value": value,
            "footprint": footprint, "x_mm": x_mm, "y_mm": y_mm, "rotation": rotation}

symbols = [
    # usb-c input: 5.1k on each cc pin tells a c-to-c charger we are a sink so it turns on vbus
    part("J1", "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", 35, 55),
    part("R1", "Device", "R", "5.1k", RES, 70, 35),
    part("R2", "Device", "R", "5.1k", RES, 85, 35),
    # 3.3v ldo straight off usb 5v, en tied to vin so it is always on while plugged in
    part("U2", "Regulator_Linear", "AP2112K-3.3", "AP2112K-3.3", "Package_TO_SOT_SMD:SOT-23-5", 135, 40),
    part("C1", "Device", "C", "10uF", CAP_BULK, 115, 70),
    part("C2", "Device", "C", "10uF", CAP_BULK, 155, 70),

    # mcu. the s2-mini-1 footprint is the same land pattern as the s3-mini-1 (kicad has no separate one)
    part("U1", "RF_Module", "ESP32-S3-MINI-1", "ESP32-S3-MINI-1-N4R2", "RF_Module:ESP32-S2-MINI-1", 120, 140),
    part("C3", "Device", "C", "10uF", CAP_BULK, 50, 100),
    part("C4", "Device", "C", "100nF", CAP, 65, 100),
    # en rc delay per the espressif reference design so the chip resets after 3v3 is stable
    part("R3", "Device", "R", "10k", RES, 40, 135),
    part("C5", "Device", "C", "1uF", CAP, 20, 135),
    part("SW1", "Switch", "SW_Push", "BOOT", "Button_Switch_SMD:SW_SPST_TL3342", 45, 170),

    # screen header, pinout matches the 1.8in st7735 module: gnd vcc scl sda rst dc cs blk
    part("J2", "Connector_Generic", "Conn_01x08", "ST7735 1.8in 128x160", "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", 215, 105),

    # user buttons, active low with the esp32 internal pull-ups
    part("SW2", "Switch", "SW_Push", "FEED", "Button_Switch_THT:SW_PUSH_6mm", 225, 127),
    part("SW3", "Switch", "SW_Push", "LIGHT", "Button_Switch_THT:SW_PUSH_6mm", 225, 142),
    part("SW4", "Switch", "SW_Push", "MENU", "Button_Switch_THT:SW_PUSH_6mm", 225, 157),

    # buzzer driver; 10k base pulldown keeps it quiet while the gpio floats during boot
    part("BZ1", "Device", "Buzzer", "Piezo", "Buzzer_Beeper:Buzzer_12x9.5RM7.6", 205, 40),
    part("D1", "Diode", "1N4148WS", "1N4148WS", "Diode_SMD:D_SOD-323", 250, 30),
    part("Q1", "Transistor_BJT", "MMBT3904", "MMBT3904", "Package_TO_SOT_SMD:SOT-23", 250, 65),
    part("R4", "Device", "R", "1k", RES, 190, 65, 90),
    part("R5", "Device", "R", "10k", RES, 205, 82, 90),
]

nets = {
    "GND": ["J1.A1", "J1.A12", "J1.B1", "J1.B12", "J1.SH", "R1.2", "R2.2", "U2.2", "C1.2", "C2.2",
            "U1.1", "C3.2", "C4.2", "C5.2", "SW1.2", "J2.1", "SW2.2", "SW3.2", "SW4.2", "Q1.2", "R5.2"],
    "VBUS": ["J1.A4", "J1.A9", "J1.B4", "J1.B9", "U2.1", "U2.3", "C1.1"],
    "CC1": ["J1.A5", "R1.1"],
    "CC2": ["J1.B5", "R2.1"],
    "USB_DP": ["J1.A6", "J1.B6", "U1.24"],
    "USB_DN": ["J1.A7", "J1.B7", "U1.23"],
    "+3V3": ["U2.5", "C2.1", "U1.3", "C3.1", "C4.1", "R3.1", "J2.2", "BZ1.1", "D1.1"],
    "EN": ["U1.45", "R3.2", "C5.1"],
    "BOOT": ["U1.4", "SW1.1"],
    "TFT_SCK": ["U1.36", "J2.3"],
    "TFT_MOSI": ["U1.35", "J2.4"],
    "TFT_RST": ["U1.34", "J2.5"],
    "TFT_DC": ["U1.33", "J2.6"],
    "TFT_CS": ["U1.32", "J2.7"],
    "TFT_BL": ["U1.31", "J2.8"],
    "BTN_FEED": ["U1.17", "SW2.1"],
    "BTN_LIGHT": ["U1.18", "SW3.1"],
    "BTN_MENU": ["U1.25", "SW4.1"],
    "BUZZER": ["U1.21", "R4.1"],
    "BUZZ_BASE": ["R4.2", "Q1.1", "R5.1"],
    "BUZZ_DRV": ["BZ1.2", "D1.2", "Q1.3"],
}

# the screen uses io35-io40 because those pads face the header in the board layout, giving six uncrossed traces.
# esp32 module pins left unused: io1-io12 (minus io0), io15 io16 io18 io26 io33 io34 io41 io42 io45-48 txd0 rxd0
UNUSED_U1_PINS = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 22, 26, 27, 28, 29, 30, 37, 38, 39, 40, 41, 44]
UNUSED_J1_PINS = ["A8", "B8"]

if __name__ == "__main__":
    call = ["sch_build_circuit", {
        "symbols": symbols,
        "nets": [{"name": name, "pins": pins} for name, pins in nets.items()],
    }]
    json.dump([call], open("build_calls.json", "w"), indent=1)
    seen = {}
    for name, pins in nets.items():
        for pin in pins:
            assert pin not in seen, f"{pin} in {seen[pin]} and {name}"
            seen[pin] = name
    print(len(symbols), "symbols,", len(nets), "nets,", len(seen), "pin connections")
