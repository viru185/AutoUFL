# fix sheet names
SHEETS_TO_PROCESS: list[str] = []

# sheet to process using regex
SHEETS_TO_PROCESS_REGEX: list[str] = []

# ignore columns with this regular expression
COLUMNS_TO_DROP_RE_EXPRESSION: list[str] = [r"^Sl\.No\.$", r"^P&B FY \d{2}$"]

# columns to rename
COLUMN_RENAME_MAP: dict[str, str] = {"KPI": "Description"}


# Mapping between metric descriptions and PI tags.
TAG_MAPPING = {
    "Hydrate Production": "HIL_AL_UTKL_REF_DPR_HYD_PROD_P&B",
    "Alumina Production (Total)": "HIL_AL_UTKL_REF_DPR_AL_PROD_P&B",
    "THA": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_THA_AL_P&B",
    "K-SiO2": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_KSIO2_AL_P&B",
    "Moisture": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_MOIST_P&B",
    "Overall Recovery": "HIL_AL_UTKL_REF_DPR_OPR_EFF_OVR_RECOV_P&B",
    "Chemical Extraction": "HIL_AL_UTKL_REF_DPR_OPR_EFF_CHMCAL_EXT_P&B",
    "Post Digestion Recovery": "HIL_AL_UTKL_REF_DPR_OPR_EFF_POST_DIG_RECOVRYP&B",
    "Operating Efficiency (Production Basis) - (Production/Design)": "HIL_AL_UTKL_REF_DPR_OPR_EFF_OPR_EFF_LIQ_BASIS_P&B",
    "Plant Availability": "HIL_AL_UTKL_REF_DPR_OPR_EFF_PLANT_AVAIL_P&B",
    "Soda in Liquor to RDA": "HIL_AL_UTKL_REF_DPR_OPR_EFF_SODA_LIQ_TO_RDAP&B",
    "Caustic Soda Consumption as NaOH": "HIL_AL_UTKL_REF_DPR_OPR_EFF_CASTC_SODA_CONSUMP_NAOH_P&B",
    "Chemical Soda Consumption": "HIL_AL_UTKL_REF_DPR_OPR_EFF_CHMCAL_P&B",
    "Caustic Soda Loss in Liquor with Residue": "HIL_AL_UTKL_REF_DPR_OPR_EFF_LIQ_WTH_RESIDUE_P&B",
    "Caustic Soda Loss with Alumina": "HIL_AL_UTKL_REF_DPR_OPR_EFF_AL_P&B",
    "Lime Consumption": "HIL_AL_UTKL_REF_DPR_OPR_EFF_LIME_CONSUMP_P&B",
    "Total Steam Consumption ": "HIL_AL_UTKL_REF_DPR_OPR_EFF_TOTL_STM_CONSUMP_P&B",
    "Process Steam Consumption": "HIL_AL_UTKL_REF_DPR_OPR_EFF_PROCS_STM_CONSUMP_P&B",
    "Power Consumption - Hydrate": "HIL_AL_UTKL_REF_DPR_OPR_EFF_PWR_CONSUMP_HYD_P&B",
    "Power Consumption - Calcination": "HIL_AL_UTKL_REF_DPR_OPR_EFF_PWR_CONSUMP_CAL_P&B",
    "Calcination Oil Consumption": "HIL_AL_UTKL_REF_DPR_OPR_EFF_CAL_OIL_P&B",
    "Energy Consumption - Hydrate": "HIL_AL_UTKL_REF_DPR_OPR_EFF_ENERGY_HYD_P&B",
    "Energy Consumption - Calcination": "HIL_AL_UTKL_REF_DPR_OPR_EFF_ENERGY_CAL_P&B",
    "Total Energy Consumption": "HIL_AL_UTKL_REF_DPR_OPR_EFF_TOTL_ENERGY_CONSUMP_P&B",
    "Specific water consumption for Hydrate": "HIL_AL_UTKL_REF_DPR_OPR_EFF_SP_WTR_CONSUMP_HYD_P&B",
    "Steam Generation": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_STM_GEN_P&B",
    "Steam Sent out to Process": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_STM_SENT_OUT_TO_PROCESS_P&B",
    "Power Generation": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_PWR_GEN_P&B",
    "Boiler Efficiency": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_BLR_EFF_P&B",
    "Aux. Power Cons.": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_AUX_CONSUMP_P&B",
    "Fired Coal GCV": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_COAL_GCV_P&B",
    "Sp. Coal Consumption w.r.to steam": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_SP_WTR_CONSUMP_WRT_STM_P&B",
    "Sp. Oil Consumption": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_SP_OIL_CONSUMP_P&B",
    "Ash Generated (Fly ash and bottom ash)": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_ASH_GEN_P&B",
    "Ash Utilization": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_ASH_UTILIZAIN_P&B",
    "Specific water consumption ": "HIL_AL_UTKL_CPP_DPR_MNUL_ENTRY_SP_WTR_CONSUMP_P&B",
    "Digestion Feed (Caustic) Flow": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_DIG_FD_CASTC_FLP&B",
    "Digestion Feed Caustic Concentration": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_DIG_FD_CASTC_CONCEN_P&B",
    "Digestion Feed A/C": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_DIG_FD_A_C_P&B",
    "Blow Off A/C": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_BLW_OFF_A_C_P&B",
    "PGL Flow": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_PGL_FL_P&B",
    "PGL Caustic Concentration": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_PGL_CASTC_CON_P&B",
    "PGL A/C": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_PGL_A_C_P&B",
    "Spent Liquor A/C": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_SPNT_LIQ_A_C_P&B",
    "Red Mud Utilization": "HIL_AL_UTKL_REF_DPR_PLANT_DATA_RED_MUD_UTILIZT_P&B",
}
