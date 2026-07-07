# Official Score Field Hunt V3

Conclusion: **enough official components found to reconstruct without proxy substitution**.

## Search Scope

- CMS Provider Data Catalog nursing-home archive API.
- Provider Data Catalog archived ZIPs for January 2022, April 2022, July 2022, October 2022, and January 2023.
- All ZIP member names, CSV headers, ProviderInfo fields, and `NH_Primary_Data_Dictionary.xlsx` rows in those snapshots.
- Official July 2022 Technical Users' Guide text already snapshotted in V2.

## Findings

- Official facility-level 0-380 staffing score found: False.
- Explicit July 2022 adjusted weekend total nurse HPRD field found: False.
- July 2022 official components sufficient for reconstruction found: True.
- The reconstruction uses official July ProviderInfo reported weekend total nurse HPRD and the official all-day total nurse case-mix adjustment ratio `adjusted_total_nurse_hprd / reported_total_nurse_hprd`.
- The official July guide states that the all-days case-mix value is used to calculate case-mix adjusted total nurse staffing on weekends.
- October 2022 and January 2023 contain an explicit adjusted weekend total nurse HPRD field, which is used in Stage 2 to validate the reconstruction identity.

## Key July Candidate Fields

| source_name | file_name | field_name | possible_role | usable_for_july2022 | missingness | final_decision |
| --- | --- | --- | --- | --- | --- | --- |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Q1 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Footnote for Q1 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Q2 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Footnote for Q2 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Q3 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Footnote for Q3 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Q4 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Footnote for Q4 Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Four Quarter Average Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrMDS | Footnote for Four Quarter Average Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrClaims | Adjusted Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrClaims | Observed Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrClaims | Expected Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::QualityMsrClaims | Footnote for the Measure Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Reported Total Nurse Staffing Hours per Resident per Day | reported_total_nurse_hprd_component | yes_component |  | candidate_component |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Total number of nurse staff hours per resident per day on the weekend | reported_weekend_total_nurse_hprd_component | yes_component |  | candidate_component |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Adjusted Total Nurse Staffing Hours per Resident per Day | adjusted_total_nurse_hprd_component | yes_component |  | candidate_component |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 1 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 1 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 1 Total Health Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 2 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 2 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 2 Total Health Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 3 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 3 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Rating cycle 3 Total Health Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::ProviderInfo | Total Weighted Health Survey Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain |  | dictionary_context |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::StateUSAverages | Reported Total Nurse Staffing Hours per Resident per Day | reported_total_nurse_hprd_component | yes_component |  | candidate_component |
| Provider Data Catalog NH_Primary_Data_Dictionary.xlsx | nursing_homes_including_rehab_services_07_2022/NH_Primary_Data_Dictionary.xlsx::StateUSAverages | Total number of nurse staff hours per resident per day on the weekend | reported_weekend_total_nurse_hprd_component | yes_component |  | candidate_component |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Reported Total Nurse Staffing Hours per Resident per Day | reported_total_nurse_hprd_component | yes_component | 0.036961 | candidate_component |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Total number of nurse staff hours per resident per day on the weekend | reported_weekend_total_nurse_hprd_component | yes_component | 0.036961 | candidate_component |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Adjusted Total Nurse Staffing Hours per Resident per Day | adjusted_total_nurse_hprd_component | yes_component | 0.042430 | candidate_component |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 1 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 1 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 1 Total Health Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 2 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 2 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 2 Total Health Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 3 Health Deficiency Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |
| Provider Data Catalog archived ZIP CSV header | nursing_homes_including_rehab_services_07_2022/NH_ProviderInfo_Jul2022.csv | Rating Cycle 3 Health Revisit Score | possible_official_staffing_score | yes_if_facility_level_staffing_domain | 0.000000 | not_official_score |

Showing 40 of 65 rows.
