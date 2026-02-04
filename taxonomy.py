TAXONOMY_VERSION = "2026-02-04"

TAXONOMY_ROWS = [
    ("Banking & Financial", "Banking Charges", "Not sure"),
    ("Banking & Financial", "Global Rating", "Not sure"),
    ("Banking & Financial", "Insurance", "Not sure"),
    ("Facilities", "Food Services", "Not sure"),
    ("Facilities", "Janitorial Services", "Not sure"),
    ("Facilities", "Security Services", "Not sure"),
    ("Facilities", "Uniform", "Not sure"),
    ("HR", "Employee Benefits", "Not sure"),
    ("HR", "Employee Recognition", "Not sure"),
    ("HR", "Recruitment Services", "Not sure"),
    ("HR", "Training", "Not sure"),
    ("IT", "Hardware", "Accessories"),
    ("IT", "Hardware", "Laptop"),
    ("IT", "Hardware", "Mobile"),
    ("IT", "Software", "Licenses Cost"),
    ("IT", "Software", "Subscription"),
    ("Professional Services", "Audit Services", "Not sure"),
    ("Professional Services", "Consulting Services", "Not sure"),
    ("Professional Services", "Legal Services", "Not sure"),
    ("Professional Services", "Risk Consulting Services", "Not sure"),
    ("T&E", "Air", "Not sure"),
    ("T&E", "Food", "Not sure"),
    ("T&E", "Ground Transportation", "Not sure"),
    ("T&E", "Hotel", "Not sure"),
    ("T&E", "Parking Fees", "Not sure"),
    ("Unaddressable", "Utilities", "Not sure"),
    ("Tax", "Utilities", "Not sure"),
    ("Utilities", "Power", "Not sure"),
    ("Utilities", "Water", "Not sure"),
]


def _validate_taxonomy(rows):
    seen = set()
    for row in rows:
        if len(row) != 3:
            raise ValueError("Each taxonomy row must have exactly 3 columns.")
        l1, l2, l3 = row
        if not l1 or not l2:
            raise ValueError("L1 and L2 values must be non-empty.")
        if row in seen:
            raise ValueError(f"Duplicate taxonomy row: {row}")
        seen.add(row)


_validate_taxonomy(TAXONOMY_ROWS)

TAXONOMY = (
    "L1 | L2 | L3\n"
    "---|---|---\n"
    + "\n".join(f"{l1} | {l2} | {l3}" for l1, l2, l3 in TAXONOMY_ROWS)
)
