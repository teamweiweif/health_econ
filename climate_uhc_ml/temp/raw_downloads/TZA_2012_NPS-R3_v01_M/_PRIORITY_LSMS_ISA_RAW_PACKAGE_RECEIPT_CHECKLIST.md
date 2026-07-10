# Priority LSMS-ISA Raw Package Receipt Checklist

Dataset: `TZA_2012_NPS-R3_v01_M` - Tanzania 2012-2013

Official get-microdata URL: https://microdata.worldbank.org/catalog/2252/get-microdata

Target folder: `temp/raw_downloads/TZA_2012_NPS-R3_v01_M/`

Current receipt status: `blocked_no_original_package`

Required package scope: Complete unchanged World Bank official package for this IDNO, including raw microdata modules, documentation, questionnaires, codebooks, DDI/XML, and any geography or timing supplements that the get-microdata package provides.

Official public documentation status: `complete_core_public_documentation_receipt`

Official public documentation snapshots: 7

## Receipt Fields To Fill

- Download account/source:
- Received package file names:
- Received documentation file names:
- Download date:
- Terms/DAA confirmed:
- SHA256 manifest completed:
- Complete package received:
- Ready for raw value review:

## Requirement Receipt Gate

| requirement | requirement_role | candidate_variable_rows | candidate_file_rows | current_receipt_status | current_verification_status |
|---|---|---|---|---|---|
| household_person_keys | merge_key_gate | 12 | 11 | blocked_no_original_package | blocked_no_original_package |
| weights_and_design | survey_design_gate | 12 | 6 | blocked_no_original_package | blocked_no_original_package |
| consumption_or_income | financial_denominator_gate | 12 | 2 | blocked_no_original_package | blocked_no_original_package |
| oop_health_expenditure | financial_outcome_gate | 12 | 1 | blocked_no_original_package | blocked_no_original_package |
| health_need_and_access | access_outcome_gate | 12 | 6 | blocked_no_original_package | blocked_no_original_package |
| survey_timing | climate_timing_gate | 12 | 5 | blocked_no_original_package | blocked_no_original_package |
| climate_geography | climate_geography_gate | 12 | 5 | blocked_no_original_package | blocked_no_original_package |
| missing_codes_units_recall_skip_patterns | documentation_semantics_gate | 0 | 0 | blocked_no_original_package | blocked_no_original_package |

## After Receipt

Run:

`python script/17_audit_raw_downloads.py; python script/144_build_priority_lsms_isa_raw_package_intake_packet.py; python script/145_build_priority_lsms_isa_archive_member_preflight.py; python script/149_build_priority_lsms_isa_raw_value_verification_workbook.py; python script/150_build_priority_lsms_isa_raw_package_receipt_checklist.py; python script/132_build_priority_analysis_dataset_synthesis_blueprint.py; python script/148_build_priority_lsms_isa_country_wave_promotion_packets.py; python script/127_enforce_promoted_data_gate.py; python script/36_build_direct_read_audit_bundle.py; python script/14_validate_workspace.py`

## Stop Rule

Do not mark this wave as complete, value-verified, climate-linkage-ready, or
analysis-ready until the receipt fields and the raw-value workbook are filled
from original raw files and accepted.
