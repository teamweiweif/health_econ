# Priority LSMS-ISA Received Raw Value Profile

IDNO: `MWI_2004_IHS-II_v01_M`

Country-wave: Malawi 2004-2005

Status: value-distribution, key/design, and geography prefill evidence is
available for manual raw-value review. This file does not certify promotion.

## Requirement Profile

| requirement | profiled_variable_rows | variables_with_nonmissing_values | detected_recall_periods | detected_units_or_scales | value_profile_requirement_status |
|---|---|---|---|---|---|
| climate_geography | 12 | 12 |  |  | value_profile_available_not_value_verified |
| consumption_or_income | 12 | 12 | past_month; past_week | local_currency_amount_needs_unit_confirmation; month; local_currency_amount_needs_unit_confirmati... | value_profile_available_not_value_verified |
| health_need_and_access | 12 | 12 | past_2_weeks | distance_measure_needs_unit_confirmation; unit_variable | value_profile_available_not_value_verified |
| household_person_keys | 12 | 12 |  |  | value_profile_available_not_value_verified |
| oop_health_expenditure | 12 | 12 | past_2_weeks; past_4_weeks | local_currency_amount_needs_unit_confirmation | value_profile_available_not_value_verified |
| survey_timing | 12 | 12 | calendar_year; interview_date; interview_month | month; month; year; unit_variable; month; year; year | value_profile_available_not_value_verified |
| weights_and_design | 12 | 12 |  |  | value_profile_available_not_value_verified |

## Key / Design / Geography Profile

| actual_member_name | variable_name | variable_role | nonmissing_count | distinct_nonmissing_count | profile_status |
|---|---|---|---|---|---|
| Filters.dta | add | admin_geography_ag_development_district | 11252 | 8 | geography_variable_present_needs_linkage_review |
| Filters.dta | case_id | household_key | 11252 | 11252 | unique_key_at_file_level |
| Filters.dta | dist | admin_geography_district | 11252 | 26 | geography_variable_present_needs_linkage_review |
| Filters.dta | ea | cluster_or_enumeration_area | 11252 | 110 | geography_variable_present_needs_linkage_review |
| Filters.dta | hhid | household_key_component | 11252 | 578 | repeated_key_requires_secondary_line_key |
| Filters.dta | hhwght | survey_design_household_weight | 11252 | 30 | weight_positive_candidate |
| Filters.dta | psu | survey_design_psu | 11252 | 563 | survey_design_variable_present |
| Filters.dta | region | admin_geography_region | 11252 | 3 | geography_variable_present_needs_linkage_review |
| Filters.dta | strata | survey_design_strata | 11252 | 30 | survey_design_variable_present |
| Filters.dta | ta | admin_geography_traditional_authority | 11252 | 48 | geography_variable_present_needs_linkage_review |
| Filters.dta | type | urban_rural_ea_type | 11252 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_ag.dta | case_id | household_key | 11280 | 11280 | unique_key_at_file_level |
| ihs2_ag.dta | hhwght | survey_design_household_weight | 11280 | 29 | weight_positive_candidate |
| ihs2_anthro.dta | case_id | household_key | 6808 | 5153 | repeated_key_requires_secondary_line_key |
| ihs2_anthro.dta | dist | admin_geography_district | 6808 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | ea | cluster_or_enumeration_area | 6808 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | hhwght | survey_design_household_weight | 6808 | 30 | weight_positive_candidate |
| ihs2_anthro.dta | region | admin_geography_region | 6808 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_anthro.dta | ta | admin_geography_traditional_authority | 6808 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_ea_data.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | add | admin_geography_ag_development_district | 11280 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | case_id | household_key | 11280 | 11280 | unique_key_at_file_level |
| ihs2_exp.dta | dist | admin_geography_district | 11280 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | ea | cluster_or_enumeration_area | 11280 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | hhwght | survey_design_household_weight | 11280 | 30 | weight_positive_candidate |
| ihs2_exp.dta | region | admin_geography_region | 11280 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | strata | survey_design_strata | 11280 | 30 | survey_design_variable_present |
| ihs2_exp.dta | ta | admin_geography_traditional_authority | 11280 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_exp.dta | type | urban_rural_ea_type | 11280 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | add | admin_geography_ag_development_district | 11280 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | case_id | household_key | 11280 | 11280 | unique_key_at_file_level |
| ihs2_household.dta | dist | admin_geography_district | 11280 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | ea | cluster_or_enumeration_area | 11280 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | hhmemid | household_head_member_id | 11280 | 1 | utility_variable_present |
| ihs2_household.dta | hhwght | survey_design_household_weight | 11280 | 30 | weight_positive_candidate |
| ihs2_household.dta | region | admin_geography_region | 11280 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | strata | survey_design_strata | 11280 | 30 | survey_design_variable_present |
| ihs2_household.dta | ta | admin_geography_traditional_authority | 11280 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_household.dta | type | urban_rural_ea_type | 11280 | 5 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | case_id | household_key | 51288 | 11280 | repeated_key_requires_secondary_line_key |
| ihs2_individ.dta | dist | admin_geography_district | 51288 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | ea | cluster_or_enumeration_area | 51288 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_individ.dta | strata | survey_design_strata | 51288 | 30 | survey_design_variable_present |
| ihs2_individ.dta | ta | admin_geography_traditional_authority | 51288 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | add | admin_geography_ag_development_district | 11280 | 8 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | case_id | household_key | 11280 | 11280 | unique_key_at_file_level |
| ihs2_pov.dta | dist | admin_geography_district | 11280 | 26 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | ea | cluster_or_enumeration_area | 11280 | 110 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | hhwght | survey_design_household_weight | 11280 | 30 | weight_positive_candidate |
| ihs2_pov.dta | region | admin_geography_region | 11280 | 3 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | strata | survey_design_strata | 11280 | 30 | survey_design_variable_present |
| ihs2_pov.dta | ta | admin_geography_traditional_authority | 11280 | 48 | geography_variable_present_needs_linkage_review |
| ihs2_pov.dta | type | urban_rural_ea_type | 11280 | 5 | geography_variable_present_needs_linkage_review |
| mod_a.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_a.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_a.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_b.dta | dist | admin_geography_district | 4427 | 26 | geography_variable_present_needs_linkage_review |
| mod_b.dta | ea | cluster_or_enumeration_area | 4427 | 110 | geography_variable_present_needs_linkage_review |
| mod_b.dta | ta | admin_geography_traditional_authority | 4427 | 48 | geography_variable_present_needs_linkage_review |
| mod_c.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_c.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_c.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_d.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_d.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_d.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_e.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_e.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_e.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_f.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_f.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_f.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_g.dta | dist | admin_geography_district | 564 | 26 | geography_variable_present_needs_linkage_review |
| mod_g.dta | ea | cluster_or_enumeration_area | 564 | 110 | geography_variable_present_needs_linkage_review |
| mod_g.dta | ta | admin_geography_traditional_authority | 564 | 48 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | dist | admin_geography_district | 986 | 26 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | ea | cluster_or_enumeration_area | 986 | 104 | geography_variable_present_needs_linkage_review |
| mod_g50better.dta | ta | admin_geography_traditional_authority | 986 | 46 | geography_variable_present_needs_linkage_review |
| mod_g50worse.dta | dist | admin_geography_district | 2058 | 26 | geography_variable_present_needs_linkage_review |

## Remaining Gate Meaning

This profile can prefill review, but the country-wave remains unpromoted until
documentation confirms units, recall periods, missing codes, skip universes,
merge levels, outcome formulas, and an accepted CHIRPS/ERA5 linkage route.
