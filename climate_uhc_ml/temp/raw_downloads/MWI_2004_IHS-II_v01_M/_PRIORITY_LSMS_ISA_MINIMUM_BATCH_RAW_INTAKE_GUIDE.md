# Minimum Batch Raw Intake Guide

IDNO: `MWI_2004_IHS-II_v01_M`

Country-wave: Malawi 2004-2005

Threshold rank: 3

Role: minimum_10_wave_core

Official World Bank microdata URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Target folder: `temp/raw_downloads/MWI_2004_IHS-II_v01_M/`

## Current Receipt Status

- Expected full official files: 52
- Matched full official files: 52
- Missing full official files: 0
- Expected core files: 37
- Matched core files: 37
- Missing core files: 0
- Official receipt status: `official_file_receipt_complete_pending_schema_value_review`

## Core Files To Confirm

| requirement | file_rank | file_id | expected_file_name | top_variable_names | official_core_file_match_status |
|---|---|---|---|---|---|
| climate_geography | 1 | F1 | sec_a.NSDstat | type | matched_expected_core_file |
| climate_geography | 2 | F10 | sec_f.NSDstat | type | matched_expected_core_file |
| climate_geography | 3 | F11 | sec_g.NSDstat | type | matched_expected_core_file |
| climate_geography | 4 | F12 | sec_h.NSDstat | type | matched_expected_core_file |
| climate_geography | 5 | F13 | sec_i.NSDstat | type | matched_expected_core_file |
| climate_geography | 6 | F14 | sec_j1.NSDstat | type | matched_expected_core_file |
| climate_geography | 7 | F15 | sec_j2.NSDstat | type | matched_expected_core_file |
| climate_geography | 8 | F16 | sec_k.NSDstat | type | matched_expected_core_file |
| consumption_or_income | 1 | F14 | sec_j1.NSDstat | add;case_id;dist;ea;hhid;hhsize;hhwght;j01a;j02a;j03a | matched_expected_core_file |
| consumption_or_income | 2 | F13 | sec_i.NSDstat | i03both | matched_expected_core_file |
| consumption_or_income | 3 | F2 | sec_aa.NSDstat | aa01 | matched_expected_core_file |
| health_need_and_access | 1 | F8 | sec_d.NSDstat | d05a;d05aoth;d05b;d05both;d27a;d27b;d04 | matched_expected_core_file |
| health_need_and_access | 2 | F46 | mod_d.NSDstat | cd51b;cd_51a;cd47;cd57a;cd_50 | matched_expected_core_file |
| household_person_keys | 1 | F6 | sec_b.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 2 | F1 | sec_a.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 3 | F10 | sec_f.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 4 | F11 | sec_g.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 5 | F12 | sec_h.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 6 | F13 | sec_i.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 7 | F14 | sec_j1.NSDstat | hhid | matched_expected_core_file |
| household_person_keys | 8 | F15 | sec_j2.NSDstat | hhid | matched_expected_core_file |
| oop_health_expenditure | 1 | F8 | sec_d.NSDstat | d13;d12;d14;d16;d19;add;case_id;d02;d03;d04;d05a;d05aoth | matched_expected_core_file |
| survey_timing | 1 | F33 | sec_z1.NSDstat | z08a;z08b;z10a;z10b | matched_expected_core_file |
| survey_timing | 2 | F40 | ihs2_household.NSDstat | idate | matched_expected_core_file |
| survey_timing | 3 | F7 | sec_c.NSDstat | c14;c16 | matched_expected_core_file |
| survey_timing | 4 | F29 | sec_v.NSDstat | v09a;v09b | matched_expected_core_file |
| survey_timing | 5 | F41 | ihs2_individ.NSDstat | age_months | matched_expected_core_file |
| survey_timing | 6 | F1 | sec_a.NSDstat | a14b | matched_expected_core_file |
| survey_timing | 7 | F23 | sec_q1.NSDstat | q03 | matched_expected_core_file |
| weights_and_design | 1 | F1 | sec_a.NSDstat | psu | matched_expected_core_file |

## Intake Steps

1. Use the official World Bank link above after login, terms, or Data Access Agreement acceptance.
2. Download the complete official package and documentation. Keep original archive names where possible.
3. Place the unchanged package or extracted original files under the target folder.
4. Rerun the post-download commands below.
5. Review raw-value, outcome, timing, geography, and climate-linkage gates before any promotion.

```bash
python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/152_build_priority_lsms_isa_credentialed_raw_acquisition_workbench.py; python script/153_validate_priority_lsms_isa_official_file_receipt.py; python script/154_build_priority_lsms_isa_threshold_download_sequence.py; python script/155_build_priority_lsms_isa_minimum_batch_raw_intake_guide.py; python script/156_probe_priority_lsms_isa_minimum_batch_endpoint_refresh.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/151_refresh_refocused_promoted_country_wave_registry.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py
```

## Stop Rule

Do not write this country-wave into data/ or run ML until complete official file receipt, raw-value verification, outcome construction, survey timing/geography, and accepted CHIRPS or ERA5 climate linkage all pass.
