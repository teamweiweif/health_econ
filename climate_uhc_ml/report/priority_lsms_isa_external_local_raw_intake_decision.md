# Priority LSMS/ISA External Local Raw Intake Decision

Status: intake decision layer for external local raw-folder candidates. It turns the filename discovery audit into a concrete review queue, but still does not accept provenance, copy raw files, write `data/`, or open modeling.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| external_local_raw_intake_review_rows | 10 | External local candidate folders with expected-file matches promoted from discovery into intake review. |
| external_local_raw_intake_selected_review_rows | 7 | Currently selected refocused-plan rows with external local candidate matches. |
| external_local_raw_intake_copy_review_ready_rows | 4 | Selected rows ready for human official-provenance review before copying into temp/raw_downloads. |
| external_local_raw_intake_selected_partial_review_rows | 3 | Selected rows with partial external local matches needing missing-file or provenance triage. |
| external_local_raw_intake_backup_review_rows | 3 | Backup rows with external local matches held behind the selected batch. |
| external_local_raw_intake_document_manifest_rows | 17 | Documentation files found in external local candidate folders. |
| external_local_raw_intake_questionnaire_document_rows | 14 | Documentation files whose filename suggests questionnaire or interview evidence. |
| external_local_raw_intake_provenance_accepted_rows | 0 | External local folders accepted as official raw receipt; remains zero until official-source and unchanged-package rev... |
| external_local_raw_intake_immediate_copy_rows | 0 | Rows copied automatically by this script; must remain zero. |
| data_write_gate_status | blocked_no_data_write | This intake decision writes no promoted data and copies no raw files. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Intake Queue

| intake_rank | country | wave | idno | locked_download_target | documentation_file_rows | external_expected_file_match_rows | expected_file_rows | external_core_file_match_rows | core_file_rows | intake_decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 1 | 1 | 52 | 52 | 37 | 37 | copy_review_ready_pending_official_provenance |
| 10 | Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 1 | 2 | 104 | 104 | 26 | 26 | copy_review_ready_pending_official_provenance |
| 10 | Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1 | 1 | 94 | 95 | 38 | 38 | copy_review_ready_pending_official_provenance |
| 10 | Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 1 | 2 | 80 | 80 | 33 | 33 | copy_review_ready_pending_official_provenance |
| 30 | Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1 | 2 | 100 | 103 | 20 | 26 | selected_partial_intake_review_required |
| 30 | Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1 | 4 | 97 | 99 | 21 | 27 | selected_partial_intake_review_required |
| 30 | Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 1 | 1 | 2 | 61 | 4 | 35 | selected_partial_intake_review_required |
| 60 | Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 0 | 1 | 99 | 99 | 35 | 35 | backup_intake_review_after_selected_batch |
| 60 | Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 0 | 1 | 85 | 85 | 36 | 36 | backup_intake_review_after_selected_batch |
| 60 | Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 0 | 2 | 101 | 103 | 30 | 32 | backup_intake_review_after_selected_batch |

## Documentation Evidence

| country | wave | idno | document_file_name | document_evidence_role | document_bytes |
| --- | --- | --- | --- | --- | --- |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | IHS-2 HH questionnaire final draft.pdf | questionnaire_or_household_interview_document | 470617 |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | PH_W3_Household_Quest.pdf | questionnaire_or_household_interview_document | 1850071 |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | PP_W3_Household_Quest.pdf | questionnaire_or_household_interview_document | 1594221 |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | NPS_Household_Qx_English_Year_2.pdf | questionnaire_or_household_interview_document | 1121873 |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | NPS_Household_Qx_Y3_Final_English.pdf | questionnaire_or_household_interview_document | 2163777 |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | NPS_Wave_3 _Final _Report.pdf | other_documentation | 1893792 |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | GHS_PANEL_HOUSEHOLD_POST_HARVEST_FINAL.pdf | questionnaire_or_household_interview_document | 577427 |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | Panel_Household_Questionnaire_FINAL.pdf | questionnaire_or_household_interview_document | 440831 |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | PostHarvesQuestionnaire.pdf | questionnaire_or_household_interview_document | 625255 |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | PostPLantingQuestionnaire.pdf | questionnaire_or_household_interview_document | 440831 |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | AGHS_Panel_PP_Household.pdf | questionnaire_or_household_interview_document | 1847212 |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | AW2_PH_HH_Questionnaire.pdf | questionnaire_or_household_interview_document | 2486843 |
| Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | TZNPS_Geovariables_Y1.pdf | other_documentation | 452209 |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | IHS3.Household.Qx.FINAL.pdf | questionnaire_or_household_interview_document | 1138439 |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | fourth_integrated_household_survey_2016_2017_household_questionnaire.pdf | questionnaire_or_household_interview_document | 1517936 |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | Note_Consumption_Aggregate.txt | other_documentation | 376 |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | Uganda2011-12HouseholdQuestionnaire.pdf | questionnaire_or_household_interview_document | 1497477 |

## Operational Rule

Rows marked `copy_review_ready_pending_official_provenance` are the next practical acquisition targets. A human/source review still has to confirm that the external local folder is an unchanged official package before copying it into `temp/raw_downloads/` and running the existing post-download validation command.

The current accepted-provenance count is intentionally zero. This prevents accidental promotion from local filename matches alone.
