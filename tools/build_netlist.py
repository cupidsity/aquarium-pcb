# netlist that generated the first schematic (edits made in kicad afterwards are not reflected here). running it writes build_calls.json, a
# [tool, args] list for kicad-mcp-pro's sch_build_circuit (which overwrites the sheet).
# after a rebuild the no-connect flags on unused pins have to be placed again.
# nets connect by name (stub + label/power symbol per pin), so placement only affects readability.
import json

RES = "Resistor_SMD:R_0603_1608Metric"
CAP = "Capacitor_SMD:C_0603_1608Metric"
CAP_BULK = "Capacitor_SMD:C_0805_2012Metric"

def part(reference, library, symbol_name, value, footprint, x_mm, y_mm, rotation=0, **properties):
    entry = {"reference": reference, "library": library, "symbol_name": symbol_name, "value": value,
             "footprint": footprint, "x_mm": x_mm, "y_mm": y_mm, "rotation": rotation}
    if properties:
        entry["properties"] = properties
    return entry

symbols = [
    # usb-c input: 5.1k on each cc pin tells a c-to-c charger we are a sink so it turns on vbus
    part("J1", "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", 35, 70),
    part("R1", "Device", "R", "5.1k", RES, 75, 45),
    part("R2", "Device", "R", "5.1k", RES, 90, 45),
    # usb side of the power path; schottky keeps vsys from back-feeding vbus
    part("D1", "Device", "D_Schottky", "B5819W", "Diode_SMD:D_SOD-123", 80, 95),
    # charger: prog = 4.7k sets ~210 mA, safe for 250 mAh and larger cells
    part("U2", "Battery_Management", "MCP73831-2-OT", "MCP73831-2-OT", "Package_TO_SOT_SMD:SOT-23-5", 130, 60),
    part("C1", "Device", "C", "4.7uF", CAP_BULK, 105, 90),
    part("C2", "Device", "C", "4.7uF", CAP_BULK, 160, 90),
    part("R3", "Device", "R", "4.7k", RES, 120, 95),
    part("R4", "Device", "R", "1k", RES, 140, 30),
    part("D2", "Device", "LED", "CHG", "LED_SMD:LED_0603_1608Metric", 195, 30),
    part("J2", "Connector_Generic", "Conn_01x02", "LiPo JST-PH", "Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal", 185, 95),
    # load sharing: with usb present the gate is high and the battery is cut off from vsys
    part("Q1", "Transistor_FET", "DMG2301L", "DMG2301L", "Package_TO_SOT_SMD:SOT-23", 210, 60),
    part("R5", "Device", "R", "100k", RES, 210, 95),
    # 3.3v ldo
    part("U3", "Regulator_Linear", "AP2112K-3.3", "AP2112K-3.3", "Package_TO_SOT_SMD:SOT-23-5", 260, 60),
    part("C3", "Device", "C", "10uF", CAP_BULK, 245, 95),
    part("C4", "Device", "C", "10uF", CAP_BULK, 280, 95),
    # battery sense: 100k/100k halves vbat into adc range, 100nF steadies the high-impedance node
    part("R6", "Device", "R", "100k", RES, 320, 50),
    part("R7", "Device", "R", "100k", RES, 340, 85),
    part("C11", "Device", "C", "100nF", CAP, 360, 85),

    # mcu
    part("U1", "RF_Module", "ESP32-S3-MINI-1", "ESP32-S3-MINI-1-N4R2", "RF_Module:ESP32-S2-MINI-1", 130, 190),
    part("C5", "Device", "C", "10uF", CAP_BULK, 60, 145),
    part("C6", "Device", "C", "100nF", CAP, 75, 145),
    # en rc delay per the espressif reference design so the chip resets after 3v3 is stable
    part("R8", "Device", "R", "10k", RES, 45, 175),
    part("C7", "Device", "C", "1uF", CAP, 25, 175),
    part("SW1", "Switch", "SW_Push", "BOOT", "Button_Switch_SMD:SW_SPST_TL3342", 60, 245),
    part("SW2", "Switch", "SW_Push", "RESET", "Button_Switch_SMD:SW_SPST_TL3342", 60, 225),

    # screen header, pinout matches common 1.54in st7789 breakouts: gnd vcc scl sda res dc cs blk
    part("J3", "Connector_Generic", "Conn_01x08", "ST7789 240x240", "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", 230, 160),

    # accelerometer, sdo tied low for i2c address 0x18, cs high selects i2c mode
    part("U4", "Sensor_Motion", "LIS3DH", "LIS3DH", "Package_LGA:LGA-16_3x3mm_P0.5mm_LayoutBorder3x5y", 320, 175),
    part("C8", "Device", "C", "100nF", CAP, 355, 140),
    part("C9", "Device", "C", "10uF", CAP_BULK, 370, 140),
    part("C10", "Device", "C", "100nF", CAP, 385, 140),
    part("R9", "Device", "R", "4.7k", RES, 280, 135),
    part("R10", "Device", "R", "4.7k", RES, 295, 135),
    # sa0 strap: 0 ohm to gnd gives address 0x18, move it to 3v3 for 0x19
    part("R13", "Device", "R", "0", RES, 355, 200),

    # user buttons, active low with the esp32 internal pull-ups
    part("SW3", "Switch", "SW_Push", "FEED", "Button_Switch_THT:SW_PUSH_6mm", 285, 212),
    part("SW4", "Switch", "SW_Push", "LIGHT", "Button_Switch_THT:SW_PUSH_6mm", 285, 229),
    part("SW5", "Switch", "SW_Push", "MENU", "Button_Switch_THT:SW_PUSH_6mm", 285, 246),

    # buzzer driver; 10k base pulldown keeps it quiet while the gpio floats during boot
    part("BZ1", "Device", "Buzzer", "Piezo", "Buzzer_Beeper:Buzzer_12x9.5RM7.6", 200, 222),
    part("D3", "Diode", "1N4148WS", "1N4148WS", "Diode_SMD:D_SOD-323", 225, 205),
    part("Q2", "Transistor_BJT", "MMBT3904", "MMBT3904", "Package_TO_SOT_SMD:SOT-23", 230, 245),
    part("R11", "Device", "R", "1k", RES, 165, 245, 90),
    part("R12", "Device", "R", "10k", RES, 180, 265, 90),
]

nets = {
    "GND": ["J1.A1", "J1.SH", "R1.2", "R2.2", "U2.2", "C1.2", "C2.2", "R3.2", "J2.2", "R5.2",
            "U3.2", "C3.2", "C4.2", "R7.2", "C11.2", "U1.1", "C5.2", "C6.2", "C7.2", "SW1.2", "SW2.2",
            "J3.1", "U4.5", "U4.10", "U4.12", "R13.2", "C8.2", "C9.2", "C10.2",
            "SW3.2", "SW4.2", "SW5.2", "Q2.2", "R12.2"],
    "VBUS": ["J1.A4", "D1.2", "U2.4", "C1.1", "R4.1", "Q1.1", "R5.1"],
    "CC1": ["J1.A5", "R1.1"],
    "CC2": ["J1.B5", "R2.1"],
    "USB_DP": ["J1.A6", "J1.B6", "U1.24"],
    "USB_DN": ["J1.A7", "J1.B7", "U1.23"],
    "CHG_LED": ["R4.2", "D2.2"],
    "CHG_STAT": ["D2.1", "U2.1"],
    "PROG": ["U2.5", "R3.1"],
    "VBAT": ["U2.3", "C2.1", "J2.1", "Q1.3", "R6.1"],
    "VSYS": ["D1.1", "Q1.2", "U3.1", "U3.3", "C3.1"],
    "+3V3": ["U3.5", "C4.1", "U1.3", "C5.1", "C6.1", "R8.1", "J3.2", "U4.1", "U4.14", "U4.8",
             "C8.1", "C9.1", "C10.1", "R9.1", "R10.1", "BZ1.1", "D3.1"],
    "VBAT_SENSE": ["R6.2", "R7.1", "C11.1", "U1.6"],
    "EN": ["U1.45", "R8.2", "C7.1", "SW2.1"],
    "BOOT": ["U1.4", "SW1.1"],
    "TFT_SCK": ["U1.16", "J3.3"],
    "TFT_MOSI": ["U1.15", "J3.4"],
    "TFT_RST": ["U1.12", "J3.5"],
    "TFT_DC": ["U1.13", "J3.6"],
    "TFT_CS": ["U1.14", "J3.7"],
    "TFT_BL": ["U1.11", "J3.8"],
    "I2C_SDA": ["U1.8", "U4.6", "R9.2"],
    "I2C_SCL": ["U1.9", "U4.4", "R10.2"],
    "ACCEL_INT1": ["U1.10", "U4.11"],
    "BTN_FEED": ["U1.17", "SW3.1"],
    "BTN_LIGHT": ["U1.18", "SW4.1"],
    "BTN_MENU": ["U1.25", "SW5.1"],
    "BUZZER": ["U1.21", "R11.1"],
    "ACCEL_SA0": ["U4.7", "R13.1"],
    "BUZZ_BASE": ["R11.2", "Q2.1", "R12.1"],
    "BUZZ_DRV": ["BZ1.2", "D3.2", "Q2.3"],
}
# the second usb vbus pins and the second gnd pins on the connector
nets["VBUS"] += ["J1.A9", "J1.B4", "J1.B9"]
nets["GND"] += ["J1.A12", "J1.B1", "J1.B12"]

call = ["sch_build_circuit", {
    "symbols": symbols,
    "nets": [{"name": name, "pins": pins} for name, pins in nets.items()],
    "max_paper": "A3",
}]
json.dump([call], open("build_calls.json", "w"), indent=1)

# sanity check: no pin used twice
seen = {}
for name, pins in nets.items():
    for pin in pins:
        assert pin not in seen, f"{pin} in {seen[pin]} and {name}"
        seen[pin] = name
print(len(symbols), "symbols,", len(nets), "nets,", len(seen), "pin connections")
