# JTL — Level-3 (Kategorie Ebene 3) categories to create

Pulled verbatim from the emitted Main CSV `Kategorie Ebene 3` column (the import source of truth), 2026-06-30.
**Parent path for every entry below:** `Netzwerk & Infrastruktur` › `Switches`  (create these two first, then the E3 leaves under "Switches").

Names are EXACT — copy them as-is (note: "Modules" line-card categories sit under Switches too, by design).

═══════════════════════════════════════════════════════════════════
CISCO — 58 categories
═══════════════════════════════════════════════════════════════════

# Small Business (3)
Cisco Small Business 350 Switches
Cisco Small Business 350X Switches
Cisco Small Business 550X Switches

# Catalyst — fixed (19)
Cisco Catalyst 1000 Switches
Cisco Catalyst 1200 Switches
Cisco Catalyst 1300 Switches
Cisco Catalyst 2960 Switches
Cisco Catalyst 3560 Switches
Cisco Catalyst 3650 Switches
Cisco Catalyst 3750 Switches
Cisco Catalyst 3850 Switches
Cisco Catalyst 4500 Switches
Cisco Catalyst 4900 Switches
Cisco Catalyst 6500 Switches
Cisco Catalyst 6800 Switches
Cisco Catalyst 9200 Switches
Cisco Catalyst 9300 Switches
Cisco Catalyst 9350 Switches
Cisco Catalyst 9400 Switches
Cisco Catalyst 9500 Switches
Cisco Catalyst 9600 Switches
Cisco Catalyst Micro Switches

# Catalyst IE (6)
Cisco Catalyst IE3100 Switches
Cisco Catalyst IE3200 Switches
Cisco Catalyst IE3300 Switches
Cisco Catalyst IE3400 Switches
Cisco Catalyst IE3500 Switches
Cisco Catalyst IE9300 Switches

# Industrial Ethernet (5)
Cisco Industrial Ethernet 1000 Switches
Cisco Industrial Ethernet 2000 Switches
Cisco Industrial Ethernet 3000 Switches
Cisco Industrial Ethernet 4000 Switches
Cisco Industrial Ethernet 5000 Switches

# Meraki MS (13)
Cisco Meraki MS120 Switches
Cisco Meraki MS125 Switches
Cisco Meraki MS130 Switches
Cisco Meraki MS150 Switches
Cisco Meraki MS210 Switches
Cisco Meraki MS225 Switches
Cisco Meraki MS250 Switches
Cisco Meraki MS350 Switches
Cisco Meraki MS355 Switches
Cisco Meraki MS390 Switches
Cisco Meraki MS410 Switches
Cisco Meraki MS425 Switches
Cisco Meraki MS450 Switches

# Nexus (7)
Cisco Nexus 2000 Switches
Cisco Nexus 3000 Switches
Cisco Nexus 5000 Switches
Cisco Nexus 7000 Switches
Cisco Nexus 9200 Switches
Cisco Nexus 9300 Switches
Cisco Nexus 9500 Switches

# MDS storage (1)
Cisco MDS 9000 Switches

# Modules — line cards (4)
Cisco Catalyst 4500 Modules
Cisco Catalyst 6500 Modules
Cisco Catalyst 6800 Modules
Cisco Nexus 7000 Modules

═══════════════════════════════════════════════════════════════════
HPE ARUBA — 17 categories
═══════════════════════════════════════════════════════════════════

Aruba CX 4100i Switches
Aruba CX 6000 Switches
Aruba CX 6100 Switches
Aruba CX 6200F Switches
Aruba CX 6200M Switches
Aruba CX 6300F Switches
Aruba CX 6300L Switches
Aruba CX 6300M Switches
Aruba CX 8100 Switches
Aruba CX 8320 Switches
Aruba CX 8325 Switches
Aruba CX 8325H Switches
Aruba CX 8360 Switches
Aruba CX 9300 Switches
Aruba CX 9300S Switches
Aruba CX 10000 Switches
Aruba CX 10040 Switches

═══════════════════════════════════════════════════════════════════
⚠️ DO NOT CREATE — MikroTik switches not yet remapped (39 SKUs)
═══════════════════════════════════════════════════════════════════
The MikroTik switch bundle still carries raw class-tokens in its E3 column instead of brand-series
categories. These are NOT valid E3 names — do not create them:
  - Managed Switch (L3)   [20 SKUs]
  - Smart-Managed Switch  [7 SKUs]
  - Industrie-Switch      [6 SKUs]
  - Data-Center-Switch    [6 SKUs]
FIX NEEDED: remap MikroTik switches to brand-series E3 (e.g. "MikroTik CRS3xx Switches",
"MikroTik CSS Switches", "MikroTik CCR Switches" …) — same treatment Cisco/Aruba got. Needs the
MikroTik series scheme decided first. Until then, hold the MikroTik switch import.

TOTAL ready to create now: 58 (Cisco) + 17 (Aruba) = 75 E3 categories.
