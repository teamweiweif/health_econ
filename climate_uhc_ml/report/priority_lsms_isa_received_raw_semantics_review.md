# Priority LSMS-ISA Received Raw Semantics Review

Status: official DDI/catalog semantics aligned to received raw value-profile
evidence. No raw microdata are persisted and no country-wave is promoted by
this review.

## Summary

| metric | value | interpretation |
|---|---:|---|
| priority_lsms_received_raw_semantics_dataset_rows | 5 | Datasets with received raw semantics review evidence. |
| priority_lsms_received_raw_semantics_variable_rows | 988 | Variable-level semantics review rows from value and utility profiles. |
| priority_lsms_received_raw_semantics_ddi_documented_variable_rows | 0 | Profiled variables matched to official DDI documentation. |
| priority_lsms_received_raw_semantics_requirement_rows | 40 | Requirement-level semantics review rows. |
| priority_lsms_received_raw_semantics_documentation_scope_rows | 6 | Study-level documentation scope rows. |
| priority_lsms_received_raw_semantics_missing_codes_units_recall_skip_requirement_rows | 5 | Documentation-semantics gate rows now backed by review evidence. |
| priority_lsms_received_raw_semantics_raw_value_verified_rows | 0 | Semantics review does not value-verify any country-wave. |
| priority_lsms_received_raw_semantics_data_write_status | blocked_semantics_review_only | Semantics review evidence does not write promoted analysis data. |
| modeling_gate_status | blocked | Models remain blocked until promoted registry thresholds and climate linkage pass. |
| priority_lsms_received_raw_semantics_status_missing_ddi_documentation_for_profiled_variable | 988 | Variable-level semantics review status count. |
| priority_lsms_received_raw_semantics_requirement_status_semantics_review_available_not_value_verified | 40 | Requirement-level semantics review status count. |
| priority_lsms_received_raw_semantics_handoff_readmes_written | 5 | Per-dataset semantics review handoffs written. |

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
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | climate_geography | 21 | 0 |  |  | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | consumption_or_income | 13 | 0 | past_month | money_amount_local_currency_needs_malawi_kwacha_confirmation; money_amount_local_currency_needs_malawi_kwacha_confirm... | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | health_need_and_access | 24 | 0 | past_2_weeks | distance_unit_pair_or_code_needs_category_check; distance_unit_pair_or_code_needs_category_check; unit_variable | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | household_person_keys | 175 | 0 |  |  | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | missing_codes_units_recall_skip_patterns | 288 | 0 | interview_date; interview_month; past_2_weeks; past_4_weeks; past_month | distance_unit_pair_or_code_needs_category_check; distance_unit_pair_or_code_needs_category_check; unit_variable; mone... | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | oop_health_expenditure | 10 | 0 | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | survey_timing | 23 | 0 | interview_date; interview_month | month | semantics_review_available_not_value_verified |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | weights_and_design | 22 | 0 |  | survey_weight | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | climate_geography | 17 | 0 |  |  | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | consumption_or_income | 12 | 0 |  | money_amount_local_currency_needs_malawi_kwacha_confirmation | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | health_need_and_access | 12 | 0 | past_2_weeks | distance_unit_pair_or_code_needs_category_check; money_amount_local_currency_needs_malawi_kwacha_confirmation; money_... | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | household_person_keys | 190 | 0 |  |  | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | missing_codes_units_recall_skip_patterns | 265 | 0 | interview_date; past_2_weeks; past_4_weeks | distance_unit_pair_or_code_needs_category_check; money_amount_local_currency_needs_malawi_kwacha_confirmation; money_... | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | oop_health_expenditure | 10 | 0 | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation; money_amount_local_currency_needs_malawi_kwacha_confirm... | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | survey_timing | 12 | 0 | interview_date |  | semantics_review_available_not_value_verified |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | weights_and_design | 12 | 0 |  |  | semantics_review_available_not_value_verified |
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
| raw_value_profile | survey_timing | ag_mod_b.dta | ag_b05a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_b.dta | ag_b05b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_b.dta | ag_b05a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_b.dta | ag_b05b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_g.dta | ag_g12a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_g.dta | ag_g12b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_g.dta | ag_g12a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_g.dta | ag_g12b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_m.dta | ag_m12a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_m.dta | ag_m12b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_m.dta | ag_m12a |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | ag_mod_m.dta | ag_m12b |  |  | month |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | com_ca.dta | com_ca07 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | com_ca.dta | com_ca07 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd60a |  |  | distance_unit_pair_or_code_needs_category_check | raw_possible_codes=98 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd60b |  |  | distance_unit_pair_or_code_needs_category_check; unit_variable |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd53 |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd54 |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd51a |  |  | distance_unit_pair_or_code_needs_category_check |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd51b |  |  | distance_unit_pair_or_code_needs_category_check; unit_variable |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd60a |  |  | distance_unit_pair_or_code_needs_category_check | raw_possible_codes=98 |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd60b |  |  | distance_unit_pair_or_code_needs_category_check; unit_variable |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd53 |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd54 |  |  |  |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd51a |  |  | distance_unit_pair_or_code_needs_category_check |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | com_cd.dta | com_cd51b |  |  | distance_unit_pair_or_code_needs_category_check; unit_variable |  | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_a_filt.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_a_filt.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23_1 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23_2 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23b_1 |  | interview_month | month |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23b_2 |  | interview_month | month |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_a_filt.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_a_filt.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_a_filt.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23_1 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23_2 |  | interview_date |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23b_1 |  | interview_month | month |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | survey_timing | hh_mod_a_filt.dta | hh_a23b_2 |  | interview_month | month |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_a_filt.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d11 |  | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d15 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d16 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d21 |  | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d14 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d04 |  | past_2_weeks |  |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05a |  |  |  | raw_possible_codes=30=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05a_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05b |  |  |  | raw_possible_codes=30=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05b_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d34a |  |  |  | raw_possible_codes=15=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d11 |  | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d15 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d16 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d21 |  | past_4_weeks | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | oop_health_expenditure | hh_mod_d.dta | hh_d14 |  |  | money_amount_local_currency_needs_malawi_kwacha_confirmation |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d04 |  | past_2_weeks |  |  | raw_conditional_nonmissing; question_text_suggests_skip_or_universe; conditional_missingness; questionnaire_skip_likely | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05a |  |  |  | raw_possible_codes=30=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05a_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05b |  |  |  | raw_possible_codes=30=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d05b_os |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | health_need_and_access | hh_mod_d.dta | hh_d34a |  |  |  | raw_possible_codes=15=Other (specify) | raw_conditional_nonmissing; conditional_missingness | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_h.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_h.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_h.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_h.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_h.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_h.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_i1.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_i1.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_i1.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_i1.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_i1.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_i1.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_i2.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_i2.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_i2.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | household_person_keys | hh_mod_i2.dta | case_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | weights_and_design | hh_mod_i2.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |
| raw_value_profile | climate_geography | hh_mod_i2.dta | ea_id |  |  |  |  |  | missing_ddi_documentation_for_profiled_variable |

## Interpretation

The audit advances Malawi 2004 from value-profile evidence to structured
documentation-semantics review. It still does not accept any variable or
requirement. Promotion remains blocked until reviewer acceptance, harmonized
outcome construction, and climate-linkage evidence pass.
