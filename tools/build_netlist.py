# netlist that generated the schematic (edits made in kicad afterwards are not reflected here).
# running it writes build_calls.json, a [tool, args] list for kicad-mcp-pro's sch_build_circuit,
# which overwrites the whole sheet, so the no-connect flags on unused pins have to be placed again after.
# nets connect by name (stub + label/power symbol per pin), so placement only affects readability.
import json

def part(reference, library, symbol_name, value, footprint, x_mm, y_mm, rotation=0):
    return {"reference": reference, "library": library, "symbol_name": symbol_name, "value": value,
            "footprint": footprint, "x_mm": x_mm, "y_mm": y_mm, "rotation": rotation}

symbols = [
    # the xiao brings its own usb-c, 3.3v regulator and boot/reset buttons; its 3v3 pin powers the rest of the board
    part("U1", "aquarium", "XIAO_ESP32S3", "Seeed XIAO ESP32S3", "aquarium:XIAO_ESP32S3_THT", 110, 100),

    # screen header, pinout matches the 1.8in st7735 module: gnd vcc scl sda rst dc cs blk
    part("J1", "Connector_Generic", "Conn_01x08", "ST7735 1.8in 128x160", "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", 205, 95),

    # user buttons, active low with the esp32 internal pull-ups
    part("SW1", "Switch", "SW_Push", "FEED", "Button_Switch_THT:SW_PUSH_6mm", 225, 125),
    part("SW2", "Switch", "SW_Push", "LIGHT", "Button_Switch_THT:SW_PUSH_6mm", 225, 140),
    part("SW3", "Switch", "SW_Push", "MENU", "Button_Switch_THT:SW_PUSH_6mm", 225, 155),

    # passive piezo buzzer driven straight from a gpio: a piezo is a small capacitor, so it draws far less
    # than a pin can supply and needs no transistor (a magnetic buzzer would)
    part("BZ1", "Device", "Buzzer", "Passive piezo", "Buzzer_Beeper:Buzzer_12x9.5RM7.6", 205, 40),
]

nets = {
    "GND": ["U1.13", "J1.1", "SW1.2", "SW2.2", "SW3.2", "BZ1.2"],
    "+3V3": ["U1.12", "J1.2"],
    # d8 / d10 are the xiao's default spi sck / mosi pins
    "TFT_SCK": ["U1.9", "J1.3"],
    "TFT_MOSI": ["U1.11", "J1.4"],
    "TFT_RST": ["U1.3", "J1.5"],
    "TFT_DC": ["U1.8", "J1.6"],
    "TFT_CS": ["U1.10", "J1.7"],
    "TFT_BL": ["U1.7", "J1.8"],
    "BTN_FEED": ["U1.1", "SW1.1"],
    "BTN_LIGHT": ["U1.2", "SW2.1"],
    "BTN_MENU": ["U1.4", "SW3.1"],
    "BUZZER": ["U1.5", "BZ1.1"],
}

# d5 is spare; the xiao's 5v pin is not needed because everything runs from its 3v3 output
UNUSED_PINS = {"U1": ["6", "14"]}

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
