# Final Time-Versioned Codebook

## Executive Summary

This metadata audit rebuilds the nursing-home staffing project around time-versioned variables before any new causal modeling. The corrected reading is straightforward: PBJ daily nurse staffing raw data existed before 2022, with quarterly public-use files beginning in 2017Q1. January 2022 is not the first existence of PBJ daily staffing data; it is the transparency and employee-level release moment. July 27, 2022 is the formal staffing-domain rating algorithm event, when the six-measure point score entered Five-Star staffing ratings.

The public Provider Data Catalog does not expose a direct facility-level official 0-380 staffing score in the audited snapshots. July 2022 also does not expose an explicit `Adjusted Weekend Total Nurse Staffing Hours per Resident per Day` field. The project can reconstruct that adjusted weekend component from official July fields using the all-day case-mix adjustment ratio and can reconstruct a 0-380 official-like staffing score; V3 validation matched July 2022 official staffing stars at 0.963. That supports rerunning threshold designs, but it does not by itself establish strong causal identification.

## Corrected Conceptual Understanding

This is not a simple DiD plus RD project. The credible design language is RD-DID / threshold design around July 2022 staffing-score cutoffs, formula-induced label shock from the overall-star rule change, and metric-salience DDD comparing targeted weekend staffing metrics with less-targeted staffing dimensions.

January-July 2022 is a transition/public-reporting/anticipation period, not a clean untreated pre-period. The cleanest pre-period for staffing behavior is 2017Q1-2021Q4, with special handling for documented 2021Q4 PBJ incompleteness. July 2022 is the formal algorithmic rating event. Ratings and deficiencies should stay secondary; staffing reliability outcomes are the primary behavior outcomes. Do not call staffing/rating changes resident clinical quality improvement.

## Timeline

| period_id | period_dates | public_reporting_status | five_star_rating_status | provider_catalog_field_status | interpretation_for_research_design |
| --- | --- | --- | --- | --- | --- |
| 2017Q1_to_2021Q4 | 2017-01-01 to 2021-12-31 | Standard staffing measures were public; weekend staffing and turnover were not yet newly posted as Care Compare measures. | Staffing rating used pre-July method based on adjusted total nurse and adjusted RN staffing, with RN staffing rating reported separately. | ProviderInfo contains adjusted total nurse HPRD, adjusted RN HPRD, staffing stars, and RN staffing rating; not the six-measure July 2022 point score. | Use for baseline trends and pre-period outcomes; do not call January 2022 the first existence of PBJ daily staffing data. |
| 2022_01_07_to_2022_01_25 | 2022-01-07 to 2022-01-25 | Announcement and anticipation; weekend/turnover public posting imminent. | Pre-July rating method still in force. | January Provider Data Catalog refresh begins to expose weekend and turnover facility-level measures. | Treat as announcement/anticipation window, not as untreated baseline. |
| 2022_01_26_to_2022_07_26 | 2022-01-26 to 2022-07-26 | Weekend staffing and turnover are public on Care Compare; employee-level PBJ detail is public. | New six-measure staffing score not yet formally applied to the staffing-domain star rating. | ProviderInfo contains reported weekend staffing and turnover fields, but not adjusted weekend total nurse HPRD or official 0-380 staffing score. | Useful for anticipation and transparency analyses; fragile as a pre-period for July RD-DID unless explicitly modeled. |
| 2022_07_27_to_2022_09_30 | 2022-07-27 to 2022-09-30 | Weekend and turnover measures remain public; July release changes rating consequences. | Six measures enter staffing rating; total score is mapped to 1-5 stars using 155/205/255/320 cutoffs. | July ProviderInfo exposes reported weekend total nurse HPRD plus total adjustment components, turnover, and stars, but not the official 0-380 score or explicit adjusted weekend total nurse HPRD. | Potential RD/RD-DID threshold event, but running variable is reconstructed and identification remains diagnostic-sensitive. |
| 2022Q4_onward | 2022-10-01 onward | Weekend and turnover public reporting continues. | Six-measure staffing rating method continues in technical guides and Provider Data Catalog. | October 2022 and January 2023 ProviderInfo expose explicit adjusted weekend total nurse HPRD in addition to other components. | Best post period for formula/label and metric-salience analyses; compare against true pre-period and isolate transition. |
| 2022_10_27_snapshot | 2022-10-27 Provider Data Catalog snapshot | Public ProviderInfo file includes the new facility-level measures. | Six-measure method in force. | Explicit `Adjusted Weekend Total Nurse Staffing Hours per Resident per Day` field is present; official 0-380 staffing score is still not found. | Validation snapshot for the adjusted-weekend reconstruction identity and star emulator. |
| 2023_01_02_snapshot | 2023-01-02 Provider Data Catalog snapshot | Public ProviderInfo file includes the new facility-level measures. | Six-measure method in force. | Explicit adjusted weekend total nurse HPRD remains present; official 0-380 staffing score is still not found. | Second validation snapshot for reconstruction and star emulator. |

## Raw PBJ Daily Variables By Period

Raw PBJ daily fields are facility-day official fields. They are separate from HPRD, weekend shares, low-tail reliability measures, and reconstructed score components.

| exact_raw_variable_name | exact_label_or_description | job_code_if_applicable | staff_type_if_applicable | unit | first_available_period_verified | appears_before_jan2022 | appears_after_jan2022 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PROVNUM | Medicare provider number |  |  |  | 2017Q1 | yes | yes |
| PROVNAME | Provider name |  |  |  | 2017Q1 | yes | yes |
| CITY | Provider city |  |  |  | 2017Q1 | yes | yes |
| STATE | Postal abbreviation for state |  |  |  | 2017Q1 | yes | yes |
| COUNTY_NAME | Name of provider county, unique within state |  |  |  | 2017Q1 | yes | yes |
| COUNTY_FIPS | FIPS code for provider county, unique within state |  |  |  | 2017Q1 | yes | yes |
| CY_Qtr | Calendar quarter |  |  |  | 2017Q1 | yes | yes |
| WorkDate | Day for reported hours |  |  | YYYYMMDD | 2017Q1 | yes | yes |
| MDScensus | Resident census from MDS |  |  | resident count | 2017Q1 | yes | yes |
| Hrs_RNDON | Total hours for RN Director of Nursing | 5 | RN director of nursing | hours | 2017Q1 | yes | yes |
| Hrs_RNDON_emp | Employee hours for RN Director of Nursing | 5 | RN director of nursing | hours | 2017Q1 | yes | yes |
| Hrs_RNDON_ctr | Contract hours for RN Director of Nursing | 5 | RN director of nursing | hours | 2017Q1 | yes | yes |
| Hrs_RNadmin | Total hours for RN with administrative duties | 6 | RN administrative | hours | 2017Q1 | yes | yes |
| Hrs_RNadmin_emp | Employee hours for RN with administrative duties | 6 | RN administrative | hours | 2017Q1 | yes | yes |
| Hrs_RNadmin_ctr | Contract hours for RN with administrative duties | 6 | RN administrative | hours | 2017Q1 | yes | yes |
| Hrs_RN | Total hours for registered nurse | 7 | registered nurse | hours | 2017Q1 | yes | yes |
| Hrs_RN_emp | Employee hours for registered nurse | 7 | registered nurse | hours | 2017Q1 | yes | yes |
| Hrs_RN_ctr | Contract hours for registered nurse | 7 | registered nurse | hours | 2017Q1 | yes | yes |
| Hrs_LPNadmin | Total hours for LPN with administrative duties | 8 | LPN administrative | hours | 2017Q1 | yes | yes |
| Hrs_LPNadmin_emp | Employee hours for LPN with administrative duties | 8 | LPN administrative | hours | 2017Q1 | yes | yes |
| Hrs_LPNadmin_ctr | Contract hours for LPN with administrative duties | 8 | LPN administrative | hours | 2017Q1 | yes | yes |
| Hrs_LPN | Total hours for licensed practical/vocational nurse | 9 | licensed practical/vocational nurse | hours | 2017Q1 | yes | yes |
| Hrs_LPN_emp | Employee hours for licensed practical/vocational nurse | 9 | licensed practical/vocational nurse | hours | 2017Q1 | yes | yes |
| Hrs_LPN_ctr | Contract hours for licensed practical/vocational nurse | 9 | licensed practical/vocational nurse | hours | 2017Q1 | yes | yes |
| Hrs_CNA | Total hours for certified nurse aide | 10 | certified nurse aide | hours | 2017Q1 | yes | yes |
| Hrs_CNA_emp | Employee hours for certified nurse aide | 10 | certified nurse aide | hours | 2017Q1 | yes | yes |
| Hrs_CNA_ctr | Contract hours for certified nurse aide | 10 | certified nurse aide | hours | 2017Q1 | yes | yes |
| Hrs_NAtrn | Total hours for nurse aide in training | 11 | nurse aide trainee | hours | 2017Q1 | yes | yes |
| Hrs_NAtrn_emp | Employee hours for nurse aide in training | 11 | nurse aide trainee | hours | 2017Q1 | yes | yes |
| Hrs_NAtrn_ctr | Contract hours for nurse aide in training | 11 | nurse aide trainee | hours | 2017Q1 | yes | yes |
| Hrs_MedAide | Total hours for medication aide/technician | 12 | medication aide/technician | hours | 2017Q1 | yes | yes |
| Hrs_MedAide_emp | Employee hours for medication aide/technician | 12 | medication aide/technician | hours | 2017Q1 | yes | yes |
| Hrs_MedAide_ctr | Contract hours for medication aide/technician | 12 | medication aide/technician | hours | 2017Q1 | yes | yes |
| Incomplete | Provider has incomplete staffing data for the 2021Q4 ransomware-affected subset |  |  | 0/1 flag | 2021Q4 | yes | no |

## Employee-Level PBJ Variables And Why January 2022 Matters

Employee-level PBJ data were not publicly available before January 26, 2022. The public employee-detail file contains facility, state, quarter, work date, system employee identifier, job code, employee/contract type, and hours. Turnover measures require employee-level identifiers, job codes, dates, and hours because starts/stops/departures cannot be recovered from facility-day aggregate PBJ daily fields alone.

| exact_raw_variable_name | exact_label_or_description | unit | first_public_availability | needed_for_turnover | appears_before_jan2022_publicly | appears_after_jan2022_publicly |
| --- | --- | --- | --- | --- | --- | --- |
| PROVNUM | Federal Provider Number | facility identifier | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| STATE | Postal abbreviation for state | state code | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | supporting | no | yes |
| CY_Qtr | Calendar Quarter | yyyyQn | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | supporting | no | yes |
| WorkDate | Work Date | YYYYMMDD | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| SYS_EMPLEE_ID | System Employee ID | system-generated employee identifier | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| EMPLEE_JOB_CD_ID | Employee Job Code | PBJ mandatory reporting job code; includes nursing and non-nursing codes | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| EMP_CTR | Employee Type | 1 = Employee; 2 = Contract | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| WORK_HRS_NUM | Hours worked | hours, two decimals | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | yes | no | yes |
| WORK_HRS_FN | Hours footnote | file-specific flag/footnote field in current CMS API header | January 26, 2022 public release; quarterly files include data beginning with 2020Q2 content | supporting | no | yes |

## Provider Data Catalog Variables By Snapshot

The latest official nursing-homes archive snapshot observed from the CMS archive API during this audit is 2026-06-24. ProviderInfo field availability was checked variable-by-snapshot for January 2022, April 2022, July 2022, October 2022, January 2023, and that current/latest snapshot.

| snapshot_date | exact_raw_variable_name | role | missingness | direct_official_field | notes |
| --- | --- | --- | --- | --- | --- |
| 2022-01-27 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.032616 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-01-27 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | field_absent | no | Expected/role-relevant field absent from this snapshot header. |
| 2022-01-27 | Total nursing staff turnover | total nurse turnover | 0.164982 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-01-27 | Staffing Rating | staffing star rating | 0.018441 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-01-27 | RN Staffing Rating | RN staffing rating | 0.018441 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-04-27 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.042952 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-04-27 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | field_absent | no | Expected/role-relevant field absent from this snapshot header. |
| 2022-04-27 | Total nursing staff turnover | total nurse turnover | 0.168388 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-04-27 | Staffing Rating | staffing star rating | 0.032230 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-04-27 | RN Staffing Rating | RN staffing rating | 0.032230 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-07-27 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.036961 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-07-27 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | field_absent | no | Critical absence: July 2022 has reported weekend total nurse HPRD and all-day adjustment components, but not this explicit adjusted weekend field. |
| 2022-07-27 | Total nursing staff turnover | total nurse turnover | 0.176901 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-07-27 | Staffing Rating | staffing star rating | 0.020885 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-07-27 | RN Staffing Rating | RN staffing rating | field_absent | no | Separate RN staffing star field disappears after the July six-measure staffing-score reform in the audited snapshots. |
| 2022-10-27 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.040800 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-10-27 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | 0.045686 | yes | Direct official field present; used to validate the July reconstruction identity. |
| 2022-10-27 | Total nursing staff turnover | total nurse turnover | 0.172047 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-10-27 | Staffing Rating | staffing star rating | 0.018221 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2022-10-27 | RN Staffing Rating | RN staffing rating | field_absent | no | Separate RN staffing star field disappears after the July six-measure staffing-score reform in the audited snapshots. |
| 2023-01-02 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.033097 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2023-01-02 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | 0.037731 | yes | Direct official field present; used to validate the July reconstruction identity. |
| 2023-01-02 | Total nursing staff turnover | total nurse turnover | 0.165619 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2023-01-02 | Staffing Rating | staffing star rating | 0.019991 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2023-01-02 | RN Staffing Rating | RN staffing rating | field_absent | no | Separate RN staffing star field disappears after the July six-measure staffing-score reform in the audited snapshots. |
| 2026-06-24 | Total number of nurse staff hours per resident per day on the weekend | reported weekend total nurse HPRD | 0.039333 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2026-06-24 | Adjusted Weekend Total Nurse Staffing Hours per Resident per Day | adjusted weekend total nurse HPRD | 0.040422 | yes | Direct official field present; used to validate the July reconstruction identity. |
| 2026-06-24 | Total nursing staff turnover | total nurse turnover | 0.089826 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2026-06-24 | Staffing Rating | staffing star rating | 0.013678 | yes | Direct official Provider Data Catalog field in this snapshot. |
| 2026-06-24 | RN Staffing Rating | RN staffing rating | field_absent | no | Separate RN staffing star field disappears after the July six-measure staffing-score reform in the audited snapshots. |

## The Six Official Staffing-Rating Measures

| official_six_measure_number | official_measure_name_from_technical_guide | max_points | point_rule | exact_available_field_jul2022 | direct_or_reconstructed | project_variable_name | evidence_strength | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Case-mix adjusted total nurse HPRD | 100 | National deciles; lowest decile 10 points, highest decile 100 points. | Adjusted Total Nurse Staffing Hours per Resident per Day | direct official measure | adjusted_total_nurse_hprd | high_direct | Directly safe as a component, subject to CMS exclusions/missingness. |
| 2 | Case-mix adjusted RN HPRD | 100 | National deciles; lowest decile 10 points, highest decile 100 points. | Adjusted RN Staffing Hours per Resident per Day | direct official measure | adjusted_rn_hprd | high_direct | Directly safe as a component, subject to CMS exclusions/missingness. |
| 3 | Case-mix adjusted weekend total nurse HPRD | 50 | National deciles; lowest decile 5 points, highest decile 50 points. | absent; reported field available: Total number of nurse staff hours per resident per day on the weekend | reconstructed for July 2022; direct official field in October 2022 and January 2023 | adjusted_weekend_total_nurse_hprd_reconstructed | strong_reconstruction_validated | Safe enough to rerun the RD running variable as reconstructed official-like evidence, not a directly observed July score. |
| 4 | Total nurse turnover | 50 | National deciles; highest turnover decile 5 points, lowest turnover decile 50 points. | Total nursing staff turnover | direct official measure | total_nursing_staff_turnover | high_direct | Requires employee-level identifiers to calculate from raw data; direct facility-level measure is in ProviderInfo after January 2022. |
| 5 | RN turnover | 50 | National deciles; highest turnover decile 5 points, lowest turnover decile 50 points. | Registered Nurse turnover | direct official measure | rn_turnover | high_direct | Requires employee-level identifiers to calculate from raw data; direct facility-level measure is in ProviderInfo after January 2022. |
| 6 | Administrator turnover / administrator departures | 30 | 0 departures = 30 points; 1 departure = 25 points; 2 or more departures = 10 points. | Number of administrators who have left the nursing home | direct official measure | administrator_departures | high_direct | Direct facility-level measure is in ProviderInfo after January 2022; raw reconstruction requires employee-level job code and employee identifier. |

## What Exists Directly, What Must Be Reconstructed, And What Is Unavailable

Raw variables: PBJ daily fields such as `Hrs_RN`, `Hrs_LPN`, `Hrs_CNA`, `MDScensus`, `WorkDate`, and employee/contract splits are official raw fields. Official published measures: ProviderInfo fields such as adjusted total nurse HPRD, adjusted RN HPRD, reported weekend total nurse HPRD, turnover measures, and star ratings are direct official measures when present. Reconstructed official-like variables: July adjusted weekend total nurse HPRD and the 0-380 staffing score are reconstructed from official components. Research-created outcomes: RN<8h days, zero-RN days, lower-tail weekend HPRD, contract share, and reallocation metrics are project-created outcomes.

| constructed_variable_name | constructed_from_raw_or_official_component | first_period_constructible | valid_pre_period | valid_post_period | used_as_outcome | used_as_running_variable_component |
| --- | --- | --- | --- | --- | --- | --- |
| rn_hprd | constructed from raw PBJ daily fields | 2017Q1 | yes | yes | yes | yes_as_component_or_outcome |
| total_nurse_hprd | constructed from raw PBJ daily fields | 2017Q1 | yes | yes | yes | yes_as_component_or_outcome |
| weekend_total_nurse_hprd | constructed from raw PBJ daily fields; also has reported official ProviderInfo measure after Jan 2022 | 2017Q1 | yes | yes | yes | yes_component_input |
| weekend_rn_hprd | constructed from raw PBJ daily fields; also has reported official ProviderInfo measure after Jan 2022 | 2017Q1 | yes | yes | yes | no_not_in_six_component_score |
| rn_lt8h_day_indicator_share | purely research-created outcome | 2017Q1 | yes | yes | yes | no |
| zero_rn_day_indicator_share | purely research-created outcome | 2017Q1 | yes | yes | yes | no |
| weekend_p10_hprd | purely research-created outcome | 2017Q1 | yes | yes | yes | no |
| weekend_p25_hprd | purely research-created outcome | 2017Q1 | yes | yes | yes | no |
| worst_weekend_hprd | purely research-created outcome | 2017Q1 | yes | yes | yes | no |
| contract_share | purely research-created staffing mix variable | 2017Q1 | yes | yes | yes | no |
| weekend_share_of_total_hours | purely research-created staffing allocation variable | 2017Q1 | yes | yes | yes | no |
| reconstructed_adjusted_weekend_total_nurse_hprd | reconstructed official-like measure | 2022-07-27 | no_for_true_pre_jan_public_fields; yes_from_raw PBJ if independently constructed | yes | no | yes_component |
| reconstructed_staffing_score_0_380 | reconstructed official-like score | 2022-07-27 | no_old_method_pre_july | yes | no | yes_running_variable |
| staffing_star_threshold_indicators | project-created threshold exposure from reconstructed official-like score | 2022-07-27 | no | yes | no | yes_running_variable |
| formula_induced_overall_star_loss | project-created formula-shock exposure | 2022-07-27 | no | yes | no | no |
| high_shadow_price_rating_incentive | project-created incentive variable | 2022-07-27 | no | yes | no | yes_context |

## Running Variable Explanation

| running_variable_name | official_or_reconstructed | source_components | official_cutoffs | validation_match_rate | validity_status | design_implication |
| --- | --- | --- | --- | --- | --- | --- |
| official_facility_level_staffing_score_0_380 | official field searched, not found | No direct field found in ProviderInfo headers, data dictionaries, or score-field scan. | 155, 205, 255, 320 | not applicable because direct official score field is absent | not_directly_observed | RD can only use a reconstructed official-like score, not a direct official running variable. |
| reconstructed_staffing_score_0_380 | reconstructed official-like score | Adjusted total nurse HPRD; adjusted RN HPRD; reconstructed adjusted weekend total nurse HPRD; total nurse turnover; RN turnover; administrator departures. | 155, 205, 255, 320 | July 2022=0.963; Oct 2022=0.967; Jan 2023=0.966 | candidate_validated_reconstruction | Use as a transparent reconstructed running variable; report density, balance, pre-outcome, and placebo diagnostics before causal claims. |

The official facility-level 0-380 staffing score is not directly found. The RD running variable is a reconstructed official-like 0-380 score based on the six official components and Table A2 point rules. The July adjusted weekend component is reconstructed as `reported_weekend_total_nurse_hprd * adjusted_total_nurse_hprd / reported_total_nurse_hprd`, supported by the technical-guide case-mix adjustment logic and checked against later snapshots where the adjusted weekend field is explicit.

## Outcome Explanation

| outcome_family | outcome_variable_name | raw_or_constructed | period_available | interpretation | policy_proximity | should_be_primary | limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Staffing behavior / staffing reliability | zero_rn_day_share | constructed | 2017Q1 onward | Share of resident days/weekend days with no RN hours. | close staffing reliability | yes | Sensitive to reporting artifacts and 2021Q4 truncation; not resident clinical quality. |
| Staffing behavior / staffing reliability | rn_lt8h_day_share | constructed | 2017Q1 onward | Share of days with RN hours below eight. | close staffing reliability | yes | Threshold is research-defined and should be justified. |
| Staffing behavior / staffing reliability | weekend_p10_total_hprd | constructed | 2017Q1 onward | Lower-tail weekend staffing intensity. | directly targeted by July weekend measure | yes | Extreme values need cleaning rules. |
| Staffing behavior / staffing reliability | worst_weekend_total_hprd | constructed | 2017Q1 onward | Minimum weekend staffing intensity. | directly targeted by July weekend measure | yes | Can be noisy; pair with percentile outcomes. |
| Staffing mix / contract labor / reallocation | contract_share | constructed | 2017Q1 onward | Reliance on contract labor among nursing hours. | staffing mix not direct rating score | no | Useful mechanism, not primary quality outcome. |
| Staffing mix / contract labor / reallocation | weekend_share_of_total_hours | constructed | 2017Q1 onward | Allocation of nurse hours toward weekends. | metric-salience/reallocation | secondary | Interpret with total hours to distinguish reallocation from expansion. |
| Demand / operation | avg_daily_census | raw/constructed from MDScensus | 2017Q1 onward | Resident census / demand scale. | not direct staffing policy outcome | no | Can be affected by occupancy/demand shocks. |
| Ratings | staffing_rating | direct official ProviderInfo field | Provider snapshots | Public staffing star label. | direct policy label | secondary | Rating outcome is partly mechanical under the July formula. |
| Ratings | overall_rating | direct official ProviderInfo field | Provider snapshots | Overall public star label. | formula-mediated public label | secondary | Formula-induced changes are labels, not clinical quality. |
| Ratings | rn_staffing_rating | direct official ProviderInfo field where present | pre-July Provider snapshots; absent in audited July onward snapshots | Separate RN staffing star under old method. | old-method rating context | secondary | Not the July six-measure score. |
| Deficiencies / downstream quality | health_deficiency_score | direct official ProviderInfo field | Provider snapshots | Inspection/survey deficiency score. | downstream/secondary | no_primary | Not immediate staffing behavior; timing and survey cycles complicate causal attribution. |
| Deficiencies / downstream quality | quality_measure_rating | direct official ProviderInfo field | Provider snapshots | Quality measure star domain. | secondary public quality domain | no_primary | Do not describe as resident clinical quality improvement without separate clinical outcome evidence. |

## Implications For Causal Design

- True pre-period: use 2017Q1-2021Q4 PBJ daily staffing behavior, with 2021Q4 data-quality sensitivity checks.
- Transition period: treat January 7/26 through July 26, 2022 as public-reporting, employee-level release, and anticipation rather than clean untreated baseline.
- July 2022 RD/RD-DID: possible with the reconstructed running variable, but fragile. It still needs density, covariate balance, pre-outcome, bandwidth, and placebo-cutoff diagnostics.
- Old high/low exposure DiD: remains weak because broad exposure definitions do not solve pretrend and timing concerns.
- Formula-induced label shock: useful as conditional mechanism evidence because it isolates rating-label consequences of the July overall-star rule, but exclusion remains fragile.
- Metric-salience DDD: useful for asking whether facilities changed targeted weekend staffing metrics more than less-targeted staffing dimensions.

## Final Clean Table For Human Readers

| period_id | period_dates | public_reporting_status | five_star_rating_status | provider_catalog_field_status | interpretation_for_research_design |
| --- | --- | --- | --- | --- | --- |
| 2017Q1_to_2021Q4 | 2017-01-01 to 2021-12-31 | Standard staffing measures were public; weekend staffing and turnover were not yet newly posted as Care Compare measures. | Staffing rating used pre-July method based on adjusted total nurse and adjusted RN staffing, with RN staffing rating reported separately. | ProviderInfo contains adjusted total nurse HPRD, adjusted RN HPRD, staffing stars, and RN staffing rating; not the six-measure July 2022 point score. | Use for baseline trends and pre-period outcomes; do not call January 2022 the first existence of PBJ daily staffing data. |
| 2022_01_07_to_2022_01_25 | 2022-01-07 to 2022-01-25 | Announcement and anticipation; weekend/turnover public posting imminent. | Pre-July rating method still in force. | January Provider Data Catalog refresh begins to expose weekend and turnover facility-level measures. | Treat as announcement/anticipation window, not as untreated baseline. |
| 2022_01_26_to_2022_07_26 | 2022-01-26 to 2022-07-26 | Weekend staffing and turnover are public on Care Compare; employee-level PBJ detail is public. | New six-measure staffing score not yet formally applied to the staffing-domain star rating. | ProviderInfo contains reported weekend staffing and turnover fields, but not adjusted weekend total nurse HPRD or official 0-380 staffing score. | Useful for anticipation and transparency analyses; fragile as a pre-period for July RD-DID unless explicitly modeled. |
| 2022_07_27_to_2022_09_30 | 2022-07-27 to 2022-09-30 | Weekend and turnover measures remain public; July release changes rating consequences. | Six measures enter staffing rating; total score is mapped to 1-5 stars using 155/205/255/320 cutoffs. | July ProviderInfo exposes reported weekend total nurse HPRD plus total adjustment components, turnover, and stars, but not the official 0-380 score or explicit adjusted weekend total nurse HPRD. | Potential RD/RD-DID threshold event, but running variable is reconstructed and identification remains diagnostic-sensitive. |
| 2022Q4_onward | 2022-10-01 onward | Weekend and turnover public reporting continues. | Six-measure staffing rating method continues in technical guides and Provider Data Catalog. | October 2022 and January 2023 ProviderInfo expose explicit adjusted weekend total nurse HPRD in addition to other components. | Best post period for formula/label and metric-salience analyses; compare against true pre-period and isolate transition. |
| 2022_10_27_snapshot | 2022-10-27 Provider Data Catalog snapshot | Public ProviderInfo file includes the new facility-level measures. | Six-measure method in force. | Explicit `Adjusted Weekend Total Nurse Staffing Hours per Resident per Day` field is present; official 0-380 staffing score is still not found. | Validation snapshot for the adjusted-weekend reconstruction identity and star emulator. |
| 2023_01_02_snapshot | 2023-01-02 Provider Data Catalog snapshot | Public ProviderInfo file includes the new facility-level measures. | Six-measure method in force. | Explicit adjusted weekend total nurse HPRD remains present; official 0-380 staffing score is still not found. | Second validation snapshot for reconstruction and star emulator. |

## Source-Grounded Audit Files

Machine-readable outputs are in `result/tables/`. The build script is `script/build_metadata_audit.py`; the formal self-check is `script/self_check_metadata_audit.py`.
