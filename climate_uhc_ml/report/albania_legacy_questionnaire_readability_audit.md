# Albania Legacy Questionnaire Readability Audit

Status: environment/readability audit only. This report inventories ALB_2002, ALB_2005, and ALB_2008 legacy `.xls` questionnaire files and tests whether the current reproducibility environment can inspect sheet contents. It does not extract questionnaire timing/geography content, does not write `data/`, and does not promote any climate-linkage evidence.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| albania_legacy_questionnaire_files | 5 | Legacy Albania questionnaire .xls files expected in local raw extractions. |
| albania_legacy_questionnaire_present_files | 5 | Legacy questionnaire files present locally. |
| albania_legacy_questionnaire_ole_signature_files | 5 | Files with OLE compound-file signature expected for legacy .xls. |
| albania_legacy_questionnaire_xlrd_installed | 1 | Whether xlrd is importable in the current Python environment. |
| albania_legacy_questionnaire_python_calamine_installed | 0 | Whether python_calamine is importable in the current Python environment. |
| albania_legacy_questionnaire_soffice_available | 0 | Whether soffice is available on PATH for reproducible conversion. |
| albania_legacy_questionnaire_read_ok_files | 5 | Legacy questionnaire files readable by pandas in the current environment. |
| albania_legacy_questionnaire_read_failed_files | 0 | Legacy questionnaire files not readable by pandas in the current environment. |
| albania_legacy_questionnaire_missing_reader_blocked_files | 0 | Files blocked from questionnaire content extraction because a legacy .xls reader/converter is unavailable. |
| albania_legacy_questionnaire_timing_content_audit_ready_rows | 5 | Legacy questionnaire files ready for separate timing/geography content extraction after this readability audit. |
| albania_legacy_questionnaire_climate_linkage_ready_rows | 0 | Rows ready for climate-linkage promotion after this audit. |
| albania_legacy_questionnaire_current_decision | legacy_questionnaires_readable_content_audit_required | Current fail-closed decision for legacy questionnaire readability. |

## File-Level Readability

| idno | wave | relative_path | file_exists | ole_compound_file_signature | schema_inventory_status | read_attempt_status | read_attempt_error |
|---|---|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | 2002 | temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Questionnaire 2002/LSMS02_Questionnaire.xls | 1 | 1 | failed | read_ok |  |
| ALB_2005_LSMS_v01_M | 2005 | temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_questionnaire_part1.xls | 1 | 1 | failed | read_ok |  |
| ALB_2005_LSMS_v01_M | 2005 | temp/raw_extracted/lsms2005en_1e7f1965c4a5/lsms2005en/Questionnaire 2005/LSMS05_Questionnaire_part2.xls | 1 | 1 | failed | read_ok |  |
| ALB_2008_LSMS_v01_M | 2008 | temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 1 ENGLISH.xls | 1 | 1 | failed | read_ok |  |
| ALB_2008_LSMS_v01_M | 2008 | temp/raw_extracted/lsms_2008_eng_a54110ab32b9/LSMS 2008_eng/Questionnaire/FINAL LSMS08 PART 2 ENGLISH1.xls | 1 | 1 | failed | read_ok |  |

## Interpretation

- Five legacy Albania questionnaire workbooks are present and are valid legacy `.xls`/OLE files.
- `xlrd` is available in the current Python environment, so the legacy workbooks can be opened and sheet names can be inspected.
- Readability is only a gate to content review. It does not verify household-level raw interview timing values, geography, skip patterns, units, recall periods, or outcome semantics.
- Therefore ALB_2002, ALB_2005, and ALB_2008 questionnaire timing, geography, skip-pattern, and outcome-semantics evidence still require a separate content audit before use.
- This does not promote any legacy wave to harmonization or climate linkage.

## Required Next Action

Run `script/67_audit_albania_legacy_questionnaire_timing_fields.py` before using any ALB_2002/2005/2008 questionnaire timing, geography, or skip-pattern content. Keep all questionnaire-derived evidence out of climate-linkage inputs unless it is connected to verified raw household timing/geography values.

## Machine-Readable Outputs

- `temp/albania_legacy_questionnaire_readability_audit.csv`
- `result/albania_legacy_questionnaire_readability_summary.csv`
