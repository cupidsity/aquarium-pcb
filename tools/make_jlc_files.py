# turns kicad's position export into jlcpcb's bom.csv and cpl.csv for the parts jlcpcb assembles.
# through-hole parts and the boot switch are left out and soldered by hand (see docs/design-notes.md).
import csv, sys
from collections import OrderedDict

positions_path, output_dir = sys.argv[1], sys.argv[2]

# lcsc codes checked against the jlcpcb catalog on 2026-11-20
LCSC_BY_PART = {
    ("5.1k", "R_0603_1608Metric"): ("C23186", "0603WAF5101T5E"),
    ("10k", "R_0603_1608Metric"): ("C25804", "0603WAF1002T5E"),
    ("1k", "R_0603_1608Metric"): ("C21190", "0603WAF1001T5E"),
    ("10uF", "C_0805_2012Metric"): ("C15850", "CL21A106KAYNNNE"),
    ("100nF", "C_0603_1608Metric"): ("C14663", "CC0603KRX7R9BB104"),
    ("1uF", "C_0603_1608Metric"): ("C15849", "CL10A105KB8NNNC"),
    ("1N4148WS", "D_SOD-323"): ("C2128", "1N4148WS"),
    ("MMBT3904", "SOT-23"): ("C20526", "MMBT3904"),
    ("AP2112K-3.3", "SOT-23-5"): ("C51118", "AP2112K-3.3TRG1"),
    ("USB-C", "USB_C_Receptacle_HRO_TYPE-C-31-M-12"): ("C165948", "TYPE-C-31-M-12"),
    ("ESP32-S3-MINI-1-N4R2", "ESP32-S2-MINI-1"): ("C3013941", "ESP32-S3-MINI-1-N4R2"),
}
HAND_SOLDERED = {"BZ1", "J2", "SW1", "SW2", "SW3", "SW4"}

rows = list(csv.DictReader(open(positions_path)))
bom_groups = OrderedDict()
with open(f"{output_dir}/cpl.csv", "w", newline="") as cpl_file:
    cpl = csv.writer(cpl_file)
    cpl.writerow(["Designator", "Mid X", "Mid Y", "Layer", "Rotation"])
    for row in rows:
        reference = row["Ref"]
        if reference in HAND_SOLDERED:
            continue
        key = (row["Val"], row["Package"])
        if key not in LCSC_BY_PART:
            sys.exit(f"no lcsc code for {reference} {key}")
        cpl.writerow([reference, f'{float(row["PosX"]):.3f}mm', f'{float(row["PosY"]):.3f}mm',
                      "Top" if row["Side"] == "top" else "Bottom", f'{float(row["Rot"]):.0f}'])
        bom_groups.setdefault(key, []).append(reference)

with open(f"{output_dir}/bom.csv", "w", newline="") as bom_file:
    bom = csv.writer(bom_file)
    bom.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "Manufacturer Part"])
    for (value, package), references in bom_groups.items():
        lcsc_code, manufacturer_part = LCSC_BY_PART[(value, package)]
        bom.writerow([value, ",".join(sorted(references, key=lambda ref: (ref[0], int(ref[1:])))), package, lcsc_code, manufacturer_part])
print(f"{sum(len(refs) for refs in bom_groups.values())} placements, {len(bom_groups)} bom lines")
