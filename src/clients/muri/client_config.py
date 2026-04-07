# fix sheet names
SHEETS_TO_PROCESS: list[str] = []

# sheet to process using regex
SHEETS_TO_PROCESS_REGEX: list[str] = []

# ignore columns with this regular expression
COLUMNS_TO_DROP_RE_EXPRESSION: list[str] = [r"^Unnamed:\s*\d+$", r"\s?YTD\s?"]

# columns to rename
COLUMN_RENAME_MAP: dict[str, str] = {"PRODUCT": "Description","Unit": "UOM"}


# Mapping between metric descriptions and PI tags.
TAG_MAPPING = {
    "Hydrate ( Rounded up)": "HIL-MUR-REF-DOR-P&B-TARGET-FOR-HYDRATE-MT",
    "    From CFBC": "HIL-MUR-REF-DOR-P&B-TARGET-FOR-STD-CALN-MT",
    "Total microfined": "HIL-MUR-REF-DOR-MICROFINER-TARGET",
    "Vanadium Production- 100 % Purity basis": "HIL-MUR-REF-DOR-VANADIUM-TARGET-PLAN",
    "Bauxite (as is)": "HIL-MUR-REF-DOR-CF-BAUXITE-T/T-TARGET",
    "Chemical soda loss ": "HIL-MUR-REF-DOR-CF-CHEM-CAUSTIC-KG/T-TARGET",
    "Liquor soda loss ": "HIL-MUR-REF-DOR-CF-LIQ-CAUSTIC-KG/T-TARGET",
    "Coal Consumption ": "HIL-MUR-REF-DOR-CF-COAL-AS-IS-3500-T/T-TARGET",
    "Furnace oil  ": "HIL-MUR-REF-DOR-CF-FO-FOR-CFBC-LTR/T-TARGET",
    "Lime  ": "HIL-MUR-REF-DOR-CF-LIME-KG/T-REFINERY-TARGET",
    "Moisture": "HIL-MUR-REF-DOR-BXT-QUALITY-MOISTURE-TARGET",
    "Sweetener Bxt Quality: Silica": "HIL-MUR-REF-DOR-BXT-QUALITY-SILICA-TARGET",
    "Chemical Extraction (CE)": "HIL-MUR-REF-KPI-CHEMICAL-EXTRACTION-P&B",
    "Post Digestion Recovery (PDR)": "HIL-MUR-REF-KPI-POST-DIGESTION-RECOVERY-P&B",
    "Digester Productivity LT ": "HIL-MUR-REF-DOR-DIG-EFFICIENCY-PROD-LT-GPL-TARGET",
    "Digester Productivity HTD": "HIL-MUR-REF-DOR-DIG-EFFICIENCY-PROD-HT-GPL-TARGET",
    "Net Digestor productivity": "HIL-MUR-REF-DOR-OVERALL-DIG-PRODUCTIVITY-GPL-TARGET",
    "Schedule Mnt. Refinery availability ": "HIL-MUR-REF-DOR-PLANT-AVAILABILITY-%-TARGET",
    "TTL flow LTD ": "HIL-MUR-REF-DOR-MIX-LIQ-FLOW-TO-LT-M3/HR-TARGET",
    "TTL flow HTD": "HIL-MUR-REF-DOR-MIX-LIQ-FLOW-TO-HT-M3/HR-TARGET",
    "Slurry charge": "HIL-MUR-REF-DOR-PDS-SLURRY-M3/HR-TARGET",
    "Mix liquor concentration": "HIL-MUR-REF-DOR-RA-MIX-LIQ-CONC-&-RATIO-GPL-&-A/C-TARGET",
    "Blow off ratio LTD": "HIL-MUR-REF-DOR-RA-LTBO-CONC-&-RATIO-GPL-&-A/C-TARGET",
    "Blow off ratio HTD": "HIL-MUR-REF-DOR-RA-HTBO-CONC-GPL-&-A/C-TARGET",
    "Last wash soda": "HIL-MUR-REF-DOR-RA-LW-SODA-GPL-TARGET",
    "Specific Steam for process": "HIL-MUR-REF-DOR-CF-PROCESS-STEAM-T/T-TARGET",
    "Coal (3500)": "HIL-MUR-REF-DOR-CGPP-COAL-CONSUMPTION-@-3500-MT-TARGET",
    "Steam for Hydrate": "HIL-MUR-REF-DOR-CGPP-TOTAL-STEAM-CONSUMPTION-T/T-TARGET",
    "Power for Hydrate": "HIL-MUR-REF-DOR-CF-ELEC-ENERGY-FOR-HYDRATE-KWH/T-TARGET",
    "Filling flow": "HIL-MUR-REF-DOR-PGL-FLOW-M3/HR-TARGET",
    "Filling concentration": "HIL-MUR-REF-DOR-RA-FILLING-CONC-&-RATIO-GPL-&-A/C-TARGET",
    "Spent liquor ratio": "HIL-MUR-REF-DOR-RA-SPENT-LIQ-CONC-&-RATIO-GPL-&-A/C-TARGET",
    "Wash water drawn": "HIL-MUR-REF-DOR-WASH-WATER-DRAWN-T/T-MUD-TARGET",
    "gland water": "HIL-MUR-REF-DOR-CF-GLAND-WATER-HT-M3/HR-TARGET",
    "Evap rate": "HIL-MUR-REF-DOR-EVAPORATION-RATE-TPH-TARGET",
}
