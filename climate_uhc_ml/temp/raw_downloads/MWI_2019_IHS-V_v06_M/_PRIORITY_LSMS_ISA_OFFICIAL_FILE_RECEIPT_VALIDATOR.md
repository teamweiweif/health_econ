# Priority LSMS-ISA Official File Receipt Validator

IDNO: `MWI_2019_IHS-V_v06_M`

Country-wave: Malawi 2019-2020

Target folder: `temp/raw_downloads/MWI_2019_IHS-V_v06_M/`

Status: `blocked_no_original_package`

## Counts

| Metric | Value |
|---|---:|
| Official expected file rows | 108 |
| Official expected matched rows | 0 |
| Official expected missing rows | 108 |
| Official core file rows | 35 |
| Official core matched rows | 0 |
| Official core missing rows | 35 |
| Local original file/archive-member rows | 0 |

## Missing Core Files

| requirement | file_rank | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|
| climate_geography | 1 | householdgeovariables_ihs5.dta | ea_id;ea_lat_mod;ea_lon_mod | missing_expected_core_file |
| climate_geography | 2 | ihs5_consumption_aggregate.dta | area;ea_id | missing_expected_core_file |
| climate_geography | 3 | ag_mod_j.dta | ag_j06e;ag_j06e_oth | missing_expected_core_file |
| climate_geography | 4 | ag_mod_o2.dta | ag_o05e;ag_o05e_oth | missing_expected_core_file |
| climate_geography | 5 | hh_mod_a_filt.dta | ea_id | missing_expected_core_file |
| climate_geography | 6 | ag_mod_c.dta | ag_c05e_oth | missing_expected_core_file |
| climate_geography | 7 | HH_MOD_F1.dta | hh_f102e | missing_expected_core_file |
| consumption_or_income | 1 | HH_MOD_I1.dta | case_id;hh_i01;hh_i02;hh_i03;HHID | missing_expected_core_file |
| consumption_or_income | 2 | HH_MOD_G1.dta | hh_g00_2;hh_g00_1 | missing_expected_core_file |
| consumption_or_income | 3 | HH_MOD_I2.dta | case_id;hh_i04 | missing_expected_core_file |
| consumption_or_income | 4 | HH_MOD_K1.dta | hh_k03 | missing_expected_core_file |
| consumption_or_income | 5 | HH_MOD_K2.dta | hh_k03 | missing_expected_core_file |
| consumption_or_income | 6 | HH_MOD_T.dta | hh_t01 | missing_expected_core_file |
| health_need_and_access | 1 | HH_MOD_D.dta | hh_d34a;hh_d34b;hh_d04;hh_d05_oth;hh_d11;hh_d13;hh_d14;hh_d05a | missing_expected_core_file |
| health_need_and_access | 2 | com_cd.dta | com_cd60a;com_cd53;com_cd54;com_cd51a | missing_expected_core_file |
| household_person_keys | 1 | HH_MOD_B.dta | case_id | missing_expected_core_file |
| household_person_keys | 2 | ag_mod_c.dta | case_id | missing_expected_core_file |
| household_person_keys | 3 | ag_mod_j.dta | case_id | missing_expected_core_file |
| household_person_keys | 4 | ag_mod_o2.dta | case_id | missing_expected_core_file |
| household_person_keys | 5 | HH_MOD_F1.dta | case_id | missing_expected_core_file |
| household_person_keys | 6 | HH_MOD_N2.dta | HHID | missing_expected_core_file |
| household_person_keys | 7 | HH_MOD_X.dta | HHID | missing_expected_core_file |
| household_person_keys | 8 | HH_MOD_D.dta | PID | missing_expected_core_file |
| oop_health_expenditure | 1 | HH_MOD_D.dta | hh_d11;hh_d12;hh_d12_1;hh_d15;hh_d16;hh_d10;hh_d13;hh_d14;hh_d19;hh_d20;hh_d21;hh_d31 | missing_expected_core_file |
| survey_timing | 1 | HH_MOD_META.dta | module_f_1_start_date;moduleB_start_date;moduleF_start_date;moduleJ_start_date;moduleK_start_date;moduleL_start_date;... | missing_expected_core_file |
| survey_timing | 2 | hh_mod_a_filt.dta | interviewDate | missing_expected_core_file |
| survey_timing | 3 | com_ca.dta | InterviewDate | missing_expected_core_file |
| weights_and_design | 1 | hh_mod_a_filt.dta | ea_id;hh_wgt | missing_expected_core_file |
| weights_and_design | 2 | householdgeovariables_ihs5.dta | ea_id | missing_expected_core_file |
| weights_and_design | 3 | ihs5_consumption_aggregate.dta | ea_id | missing_expected_core_file |
| weights_and_design | 4 | com_cc.dta | ea_id | missing_expected_core_file |
| weights_and_design | 5 | com_meta.dta | ea_id | missing_expected_core_file |
| weights_and_design | 6 | com_ca.dta | ea_id | missing_expected_core_file |
| weights_and_design | 7 | com_cb.dta | ea_id | missing_expected_core_file |
| weights_and_design | 8 | com_cd.dta | ea_id | missing_expected_core_file |

## Missing Official Files

| file_id | expected_file_name | file_description | priority_core_target | official_file_match_status |
|---|---|---|---|---|
| F1 | HH_MOD_META.dta | Household questionnaire metadata | 1 | missing_expected_official_file |
| F2 | hh_mod_a_filt.dta | Data collected through Household Questionnaire, Module A: Household Identification (household level data) - This modu... | 1 | missing_expected_official_file |
| F3 | HH_MOD_B.dta | Data collected through Household Questionnaire, Module B: Household Roster ( individual level data) - This module con... | 1 | missing_expected_official_file |
| F4 | HH_MOD_C.dta | Data collected through Household Questionnaire, Module C: Education (individual level data) - The education module is... | 0 | missing_expected_official_file |
| F5 | HH_MOD_D.dta | Data collected through Household Questionnaire, Module D: Health (individual level data) - The health module is admin... | 1 | missing_expected_official_file |
| F6 | HH_MOD_E.dta | Data collected through Household Questionnaire, Module E: Time Use and Labour – individual level data - The module is... | 0 | missing_expected_official_file |
| F7 | HH_MOD_F.dta | Data collected through Household Questionnaire, Module F: Housing - household level data - This module on housing is ... | 0 | missing_expected_official_file |
| F8 | HH_MOD_F1.dta | Data collected through Household Questionnaire, Module F1: Land Roster - This is a new module and it collects informa... | 1 | missing_expected_official_file |
| F9 | HH_MOD_G1.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – consumption item leve... | 1 | missing_expected_official_file |
| F10 | HH_MOD_G2.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – food group (aggregate) | 0 | missing_expected_official_file |
| F11 | HH_MOD_G3.dta | Data collected through Household Questionnaire, Module G: Food Consumption Over Past One Week – age group (aggregate) | 0 | missing_expected_official_file |
| F12 | HH_MOD_H.dta | Data collected through Household Questionnaire, Module H: Food security – household level - This module collects info... | 0 | missing_expected_official_file |
| F13 | HH_MOD_I1.dta | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 1 | missing_expected_official_file |
| F14 | HH_MOD_I2.dta | Data collected through Household Questionnaire, Module I: Non-food Expenditures Over Past One Week and One Month – co... | 1 | missing_expected_official_file |
| F15 | HH_MOD_J.dta | Data collected through Household Questionnaire, Module J: Non-food Expenditures Over Past Three Months – consumption ... | 0 | missing_expected_official_file |
| F16 | HH_MOD_K1.dta | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months – consumption ite... | 1 | missing_expected_official_file |
| F17 | HH_MOD_K2.dta | Data collected through Household Questionnaire, Module K: Non-food Expenditures Over Past 12 Months - consumption ite... | 1 | missing_expected_official_file |
| F18 | HH_MOD_L.dta | Data collected through Household Questionnaire, Module L: Durable Goods - durable item level - This module collects i... | 0 | missing_expected_official_file |
| F19 | HH_MOD_M.dta | Data collected through Household Questionnaire, Module M: Farm Implements, Machinery, and Structures - This module co... | 0 | missing_expected_official_file |
| F20 | HH_MOD_N1.dta | Data collected through Household Questionnaire, Module N: Household Enterprises – household level data (questions 1 t... | 0 | missing_expected_official_file |
| F21 | HH_MOD_N2.dta | Data collected through Household Questionnaire, Module N: Household Enterprises (questions 9 to 41) - This module col... | 1 | missing_expected_official_file |
| F22 | HH_MOD_O.dta | Data collected through Household Questionnaire, Module O: Children Living Elsewhere - This module collects informatio... | 0 | missing_expected_official_file |
| F23 | HH_MOD_P.dta | Data collected through Household Questionnaire, Module P: Other income – income type - This module collects informati... | 0 | missing_expected_official_file |
| F24 | HH_MOD_Q.dta | Data collected through Household Questionnaire, Module Q: Gifts Given Out – gift type - This module collects informat... | 0 | missing_expected_official_file |
| F25 | HH_MOD_R.dta | Data collected through Household Questionnaire, Module R: Social Safety Nets - program level data - This module colle... | 0 | missing_expected_official_file |
| F26 | HH_MOD_S1.dta | Data collected through Household Questionnaire, Module S: Credit - source of loan - This module collects information ... | 0 | missing_expected_official_file |
| F27 | HH_MOD_S2.dta | Data collected through Household Questionnaire, Module S: Credit - household level (questions 12 to 19) - Information... | 0 | missing_expected_official_file |
| F28 | HH_MOD_T.dta | Data collected through Household Questionnaire, Module T: Subjective Assessment of Well-being - household level - Thi... | 1 | missing_expected_official_file |
| F29 | HH_MOD_U.dta | Data collected through Household Questionnaire, Module U: Shocks and Coping Strategies - This module collects informa... | 0 | missing_expected_official_file |
| F30 | HH_MOD_V.dta | Data collected through Household Questionnaire, Module V: Child Anthropometry – individual level - This module collec... | 0 | missing_expected_official_file |
| F31 | HH_MOD_W.dta | Data collected through Household Questionnaire, Module W: Deaths in the Household – individual level - This module re... | 0 | missing_expected_official_file |
| F32 | HH_MOD_X.dta | Data collected through Household Questionnaire, Module X: Filter Questions for Agriculture and Fishery Questionnaires... | 1 | missing_expected_official_file |
| F33 | ag_mod_meta.dta | Agriculture questionnaire metadata (Contains time stamps and respondent IDs for each module) | 0 | missing_expected_official_file |
| F34 | ag_mod_a.dta | Data collected through Agriculture Questionnaire, Module A: Ownership of land - household level data | 0 | missing_expected_official_file |
| F35 | ag_mod_b2.dta | Data collected through Agriculture Questionnaire, Module B: Garden Details (rainy season) - garden level - This modul... | 0 | missing_expected_official_file |
| F36 | ag_mod_c.dta | Data collected through Agriculture Questionnaire, Module C: Plot Roster (rainy season) - plot level - This module con... | 1 | missing_expected_official_file |
| F37 | ag_mod_d.dta | Data collected through Agriculture Questionnaire, Module D: Plot Details (rainy season) - plot level - This module co... | 0 | missing_expected_official_file |
| F38 | ag_mod_e1.dta | Data collected through Agriculture Questionnaire, Module E: Coupon Use (rainy season) - individual coupon type | 0 | missing_expected_official_file |
| F39 | ag_mod_e2.dta | Data collected through Agriculture Questionnaire, Module E: Coupon Use (rainy season) - individual coupon type | 0 | missing_expected_official_file |
| F40 | ag_mod_e3.dta | Data collected through Agriculture Questionnaire, Module E: Coupon Use (rainy season) - household level | 0 | missing_expected_official_file |
| F41 | ag_mod_e4.dta | Data collected through Agriculture Questionnaire, Module E: Coupon Use (rainy season) - coupon type | 0 | missing_expected_official_file |
| F42 | ag_mod_f.dta | Data collected through Agriculture Questionnaire, Module F: Other Inputs (rainy season) - input type - This module co... | 0 | missing_expected_official_file |
| F43 | ag_mod_g.dta | Data collected through Agriculture Questionnaire, Module G: Crops (rainy season) - plot-crop level - This module coll... | 0 | missing_expected_official_file |
| F44 | ag_mod_h.dta | Data collected through Agriculture Questionnaire, Module H: Seeds (rainy season) - seed type level - This module coll... | 0 | missing_expected_official_file |
| F45 | ag_mod_i.dta | Data collected through Agriculture Questionnaire, Module I: Sales/ Storage (rainy season) - crop level - This module ... | 0 | missing_expected_official_file |
| F46 | ag_mod_i_1.dta | Data collected through Agriculture Questionnaire, Module I: Post Harvest Labour (Rainy Season) - This is a new module... | 0 | missing_expected_official_file |
| F47 | ag_mod_i2.dta | Data collected through Agriculture Questionnaire, Module I: Garden Details (dry season) - garden level - This module ... | 0 | missing_expected_official_file |
| F48 | ag_mod_j.dta | Data collected through Agriculture Questionnaire, Module J: Plot Roster (Dry Season) - plot level - This module conta... | 1 | missing_expected_official_file |
| F49 | ag_mod_k.dta | Data collected through Agriculture Questionnaire, Module K: Plot Details (Dry Season) - plot level - This module coll... | 0 | missing_expected_official_file |
| F50 | ag_mod_l.dta | Data collected through Agriculture Questionnaire, Module L: Other Inputs (dry/ dimba season) - input type - This modu... | 0 | missing_expected_official_file |
| F51 | ag_mod_m.dta | Data collected through Agriculture Questionnaire, Module M: Crops (dry/ dimba season) - plot-crop - This module colle... | 0 | missing_expected_official_file |
| F52 | ag_mod_n.dta | Data collected through Agriculture Questionnaire, Module N: Seed (dry/ dimba season) - seed type - This module collec... | 0 | missing_expected_official_file |
| F53 | ag_mod_nr.dta | Data collected through Agriculture Questionnaire, Module N and R | 0 | missing_expected_official_file |
| F54 | ag_mod_o.dta | Data collected through Agriculture Questionnaire, Module O: Sales/ Storage (dry/ dimba season) - crop level - This mo... | 0 | missing_expected_official_file |
| F55 | ag_mod_o_1.dta | Data collected through Agriculture Questionnaire, Module O: Post Harvest Labour (Dry Season) - This is a new module w... | 0 | missing_expected_official_file |
| F56 | ag_mod_o2.dta | Data collected through Agriculture Questionnaire, Module O: Plot Roster Tree Crop Production - plot level - This modu... | 1 | missing_expected_official_file |
| F57 | ag_mod_p.dta | Data collected through Agriculture Questionnaire, Module P: Tree / Permanent Crop Production Last 12 Months - This mo... | 0 | missing_expected_official_file |
| F58 | ag_mod_q.dta | Data collected through Agriculture Questionnaire, Module Q: Tree/ Permanent Crop Sales/ Storage Last 12 Months - tree... | 0 | missing_expected_official_file |
| F59 | ag_mod_q_1.dta | Data collected through Agriculture Questionnaire, Module Q_I: Post Harvest Labour (Rainy Season) - This is a new modu... | 0 | missing_expected_official_file |
| F60 | ag_mod_r1.dta | Data collected through Agriculture Questionnaire, Module R: Livestock - This module collects information on number cu... | 0 | missing_expected_official_file |

## Required Next Action

Place the complete unchanged official raw package and documentation in the target folder.

After changing files in this folder, rerun:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

This validator only proves expected file-name receipt against official DDI
metadata. It does not prove variable values, labels, units, recall periods,
survey-design fields, merge keys, climate linkage, or analysis-ready status.
