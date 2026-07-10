# Priority LSMS-ISA Received Raw Semantics Review

Status: official DDI/catalog semantics aligned to received raw value-profile
evidence. No raw microdata are persisted and no country-wave is promoted by
this review.

## Summary

| metric | value | interpretation |
|---|---:|---|
| priority_lsms_received_raw_semantics_dataset_rows | 3 | Datasets with received raw semantics review evidence. |
| priority_lsms_received_raw_semantics_variable_rows | 435 | Variable-level semantics review rows from value and utility profiles. |
| priority_lsms_received_raw_semantics_ddi_documented_variable_rows | 0 | Profiled variables matched to official DDI documentation. |
| priority_lsms_received_raw_semantics_requirement_rows | 24 | Requirement-level semantics review rows. |
| priority_lsms_received_raw_semantics_documentation_scope_rows | 6 | Study-level documentation scope rows. |
| priority_lsms_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows | 3 | Documentation-semantics gate rows now backed by review evidence. |
| priority_lsms_received_raw_semantics_raw_value_verified_rows | 0 | Semantics review does not value-verify any country-wave. |
| priority_lsms_received_raw_semantics_data_write_status | blocked_semantics_review_only | Semantics review evidence does not write promoted analysis data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_received_raw_semantics_status_missing_ddi_documentation_for_profiled_variable | 435 | Variable-level semantics review status count. |
| priority_lsms_received_raw_semantics_requirement_status_semantics_review_available_not_value_verified | 24 | Requirement-level semantics review status count. |
| priority_lsms_received_raw_semantics_handoff_readmes_written | 3 | Per-dataset semantics review handoffs written. |

## Documentation Scope

| documentation_domain | documentation_evidence | review_status |
|---|---|---|
| collection_period | 2004-03-2005-03 | official_metadata_available |
| analysis_unit | - Households - Individuals - Communities | official_metadata_available |
| geographic_coverage | National | official_metadata_available |
| sampling_design |  | official_metadata_available |
| research_instrument |  | official_metadata_available |
| survey_topics_and_recall_modules | The 2004-2005 Malawi Integrated Household Survey II covered the following topics: Household: - Characteristics and Co... | official_metadata_available |

## Requirement Review

| country | wave | idno | requirement | semantics_variable_rows | ddi_documented_variable_rows | documentation_recall_periods | documentation_units_or_scales | semantics_requirement_status |
|---|---|---|---|---|---|---|---|---|
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | climate_geography | 122 | 0 |  |  | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | consumption_or_income | 12 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | health_need_and_access | 12 | 0 | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation; month | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | household_person_keys | 104 | 0 |  |  | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | missing_codes_units_recall_skip_patterns | 280 | 0 | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation; month; survey_weight | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | oop_health_expenditure | 6 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | survey_timing | 12 | 0 |  |  | semantics_review_available_not_value_verified |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | weights_and_design | 12 | 0 |  | survey_weight | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | climate_geography | 11 | 0 |  | unit_variable | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | consumption_or_income | 4 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation; year | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | health_need_and_access | 9 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | household_person_keys | 16 | 0 |  | year | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | missing_codes_units_recall_skip_patterns | 69 | 0 | past_12_months | money_amount_local_currency_needs_malawi_kwacha_confirmation; money_amount_local_currency_needs_malawi_kwacha_confirm... | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | oop_health_expenditure | 8 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | survey_timing | 10 | 0 | past_12_months | money_amount_local_currency_needs_malawi_kwacha_confirmation; money_amount_local_currency_needs_malawi_kwacha_confirm... | semantics_review_available_not_value_verified |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | weights_and_design | 11 | 0 |  | survey_weight | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | climate_geography | 14 | 0 |  |  | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | consumption_or_income | 12 | 0 | past_12_months | money_amount_local_currency_needs_malawi_kwacha_confirmation; month | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | health_need_and_access | 12 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | household_person_keys | 12 | 0 |  |  | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | missing_codes_units_recall_skip_patterns | 86 | 0 | past_12_months; past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation; month; survey_weight; year | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | oop_health_expenditure | 12 | 0 | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation; year | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | survey_timing | 12 | 0 | past_12_months | month | semantics_review_available_not_value_verified |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | weights_and_design | 12 | 0 |  | survey_weight | semantics_review_available_not_value_verified |

## Selected Variable Review

| review_source | requirement | actual_member_name | variable_name | ddi_file_content | documentation_recall_period | documentation_unit_or_scale | documentation_missing_code_evidence | documentation_skip_evidence | semantics_review_status |
|---|---|---|---|---|---|---|---|---|---|
| raw_value_profile | weights_and_design | cons_agg_wave3_visit1.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | cons_agg_wave3_visit1.dta | hhweight |  |  | survey_weight |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit1.dta | totcons |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit1.dta | nfdfoth |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit1.dta | fdfishpr |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit1.dta | fdothpr |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit1.dta | fdrestby |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | cons_agg_wave3_visit1.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | cons_agg_wave3_visit2.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | cons_agg_wave3_visit2.dta | hhweight |  |  | survey_weight |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit2.dta | totcons |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit2.dta | nfdfoth |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit2.dta | fdfishpr |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit2.dta | fdothpr |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | cons_agg_wave3_visit2.dta | fdrestby |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | cons_agg_wave3_visit2.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | HHTrack.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_combined |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_w1_w2_w3 |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_w1_w3 |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_w1v1 |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_w1v2 |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | HHTrack.dta | wt_w2_w3 |  |  | survey_weight |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | NGA_HouseholdGeovars_Y3.dta | LAT_DD_MOD |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | NGA_HouseholdGeovars_Y3.dta | LON_DD_MOD |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect10b_harvestw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect11a1_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect11a_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect12_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect1_harvestw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sect1_harvestw3.dta | s1q31a |  |  |  | raw_possible_codes=99 | question_text_suggests_skip_or_universe | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sect1_harvestw3.dta | s1q31b |  |  |  |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sect1_harvestw3.dta | s1q31c |  |  |  |  | question_text_suggests_skip_or_universe | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sect1_harvestw3.dta | s1q31d |  |  |  |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect1_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect3_plantingw3.dta | s3q9b |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq20 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | raw_possible_codes=4=4. OTHER RELATIVE; 8=8. OTHER ORGANISATION; 11=11. OTHER (SPECIFY) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq20b |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq13 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | question_text_suggests_skip_or_universe; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq35a |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq35b |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | sect4a_harvestw3.dta | s4aq35c |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq15 |  |  | month |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq16 |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq17 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq1 |  | past_4_weeks |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq6a |  |  |  | raw_possible_codes=13=13. OTHER (SPECIFY) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq6a_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq6b |  |  |  | raw_possible_codes=13=13. OTHER (SPECIFY) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq6b_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq3 |  | past_4_weeks |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq3b |  |  |  | raw_possible_codes=12=12. OTHER (SPECIFY) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | sect4a_harvestw3.dta | s4aq3b_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect7a_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | sect7b_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | sect8a_plantingw3.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | consumption_or_income | sect8a_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | secta10_harvestw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | secta_harvestw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq14ah |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq14am |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq14bh |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq14bm |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq17ah |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq17am |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq17bh |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq17bm |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq20ah |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq20am |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq20bh |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | secta_harvestw3.dta | saq20bm |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | secta_plantingw3.dta | hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | sectc1_harvestw3.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sectc1_harvestw3.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sectc1_harvestw3.dta | lga |  |  |  |  | question_text_suggests_skip_or_universe; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | sectc2_harvestw3.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sectc2_harvestw3.dta | ea |  |  |  | raw_possible_codes=96; 998 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | sectc2_harvestw3.dta | lga |  |  |  |  | question_text_suggests_skip_or_universe; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | AG_SEC10B.dta | y2_hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | AG_SEC7A.dta | y2_hhid |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |

## Interpretation

The audit advances Malawi 2004 from value-profile evidence to structured
documentation-semantics review. It still does not accept any variable or
requirement. Promotion remains blocked until reviewer acceptance, harmonized
outcome construction, and climate-linkage evidence pass.
