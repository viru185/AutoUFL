# fix sheet names
SHEETS_TO_PROCESS: list[str] = []

# sheet to process using regex
SHEETS_TO_PROCESS_REGEX: list[str] = []

# ignore columns with this regular expression
COLUMNS_TO_DRIP_RE_EXPRESSION: list[str] = [r"\s?Area Name\s?"]

# columns to rename
COLUMN_RENAME_MAP: dict[str, str] = {}


# Mapping between metric descriptions and PI tags.
TAG_MAPPING = {
    "Total absolute power consumption of ABF": "HIL_ALU_MAH_SMLTR_CARB_ABF_ABS_PWR_CONSUM_P_AND_B_VAL",
    "Gross baked anode production (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_MTD_P_AND_B_VAL",
    "Number of gross baked anodes produced (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_NO_MTD_P_AND_B_VAL",
    "Total count of gross baked anodes": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_NO_P_AND_B_VAL",
    "Number of gross baked anodes (YTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_NO_YTD_P_AND_B_VAL",
    "Total gross baked anode production": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_P_AND_B_VAL",
    "Gross baked anode production (YTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_CALC_GROSS_BAKE_ANOD_PROD_YTD_P_AND_B_VAL",
    "Rejected baked anodes (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_REJ_BAKED_ANOD_MTD_P_AND_B_VAL",
    "Total rejected baked anodes": "HIL_ALU_MAH_SMLTR_CARB_ABF_REJ_BAKED_ANOD_P_AND_B_VAL",
    "Rejected green anodes (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ABF_REJ_GRN_ANOD_MTD_P_AND_B_VAL",
    "Total rejected green anodes": "HIL_ALU_MAH_SMLTR_CARB_ABF_REJ_GRN_ANOD_P_AND_B_VAL",
    "Total power consumption in ARS": "HIL_ALU_MAH_SMLTR_CARB_ARS_ABS_PWR_CONSM_P_AND_B_VAL",
    "Compressed air consumption in ARS": "HIL_ALU_MAH_SMLTR_CARB_ARS_AIR_CONSM_P_AND_B_VAL",
    "Furnace power consumption in ARS": "HIL_ALU_MAH_SMLTR_CARB_ARS_FURN_PWR_CONSM_P_AND_B_VAL",
    "ARS production (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ARS_PROD_MTD_P_AND_B_VAL",
    "Total ARS production": "HIL_ALU_MAH_SMLTR_CARB_ARS_PROD_P_AND_B_VAL",
    "ARS rejected units (MTD)": "HIL_ALU_MAH_SMLTR_CARB_ARS_REJCT_MTD_P_AND_B_VAL",
    "Total ARS rejected units": "HIL_ALU_MAH_SMLTR_CARB_ARS_REJCT_P_AND_B_VAL",
    "Dispatched rod-anode assemblies": "HIL_ALU_MAH_SMLTR_CARB_ARS_ROD_ANODE_ASMB_DISPCH_P_AND_B_VAL",
    "Shift-end inventory of rod anodes": "HIL_ALU_MAH_SMLTR_CARB_ARS_ROD_ANODE_INVT_SHFT_END_P_AND_B_VAL",
    "Rejected rod anodes": "HIL_ALU_MAH_SMLTR_CARB_ARS_ROD_ANODE_REJ_P_AND_B_VAL",
    "Current production at rodding bench": "HIL_ALU_MAH_SMLTR_CARB_ARS_ROD_BNCH_CUR_PROD_P_AND_B_VAL",
    "Specific power consumption in ARS": "HIL_ALU_MAH_SMLTR_CARB_ARS_SPCFC_PWR_CONSM_P_AND_B_VAL",
    "Net anode production (MTD)": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_CALC_NET_ANOD_PROD_MTD_P_AND_B_VAL",
    "Total net anode production": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_CALC_NET_ANOD_PROD_P_AND_B_VAL",
    "Total anode production (MTD)": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_TOT_ANOD_PROD_MTD_P_AND_B_VAL",
    "Total anode production": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_TOT_ANOD_PROD_P_AND_B_VAL",
    "Total anode production (YTD)": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_TOT_ANOD_PROD_YTD_P_AND_B_VAL",
    "Total rejected anodes (MTD)": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_TOT_ANOD_RJCT_MTD_P_AND_B_VAL",
    "Total rejected anodes": "HIL_ALU_MAH_SMLTR_CARB_GAP_GRP_K_TOT_ANOD_RJCT_P_AND_B_VAL",
    "Specific power consumption in GAP": "HIL_ALU_MAH_SMLTR_CARB_GAP_SPEC_PWR_CONS_P_AND_B_VAL",
    "Total butt (recycled anode) consumption": "HIL_ALU_MAH_SMLTR_CARB_TOT_BUTT_P_AND_B_VAL",
    "Total coke consumption": "HIL_ALU_MAH_SMLTR_CARB_TOT_COKE_P_AND_B_VAL",
    "Total green paste consumption": "HIL_ALU_MAH_SMLTR_CARB_TOT_GRN_PASTE_P_AND_B_VAL",
    "Total furnace oil (HFO) consumption": "HIL_ALU_MAH_SMLTR_CARB_TOT_HFO_P_AND_B_VAL",
    "Total pitch consumption": "HIL_ALU_MAH_SMLTR_CARB_TOT_PTCH_P_AND_B_VAL",
    "Billet casting production (MTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_BILT_CAST_CALC_BILT_PROD_MTD_P_AND_B",
    "Billet casting production (YTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_BILT_CAST_CALC_BILT_PROD_YTD_P_AND_B",
    "ICM production (MTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_ICM_ICM_PROD_MTD_P_AND_B",
    "ICM production (YTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_ICM_ICM_PROD_YTD_P_AND_B",
    "Total sow weight transferred (Monthly)": "HIL_ALU_MAH_SMLTR_CAST_HSE_SCM_SOW_TFR_CONVER_CALC_TOT_SOW_WGT_MONTH_P_AND_B",
    "Total sow weight transferred (Yearly)": "HIL_ALU_MAH_SMLTR_CAST_HSE_SCM_SOW_TFR_CONVER_CALC_TOT_SOW_WGT_YEARLY_P_AND_B",
    "Total coil weight (MTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_WRM_COILR_SCTN_CALC_TOT_COIL_WGT_MTD_P_AND_B",
    "Total coil weight (YTD)": "HIL_ALU_MAH_SMLTR_CAST_HSE_WRM_COILR_SCTN_CALC_TOT_COIL_WGT_YTD_P_AND_B",
}