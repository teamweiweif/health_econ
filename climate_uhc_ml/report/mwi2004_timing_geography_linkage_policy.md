# Malawi 2004 Timing/Geography Linkage Policy

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact accepts the raw interview timing and admin/EA geography fields
needed to review a climate-linkage route. It does not extract climate values,
does not accept CHIRPS/ERA5 linkage, and does not write promoted data.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by this timing/geography linkage policy. |
| household_rows | 11280 | Household rows with raw timing/geography fields. |
| idate_nonmissing_rows | 11280 | Rows with convertible interview date. |
| interview_date_min | 2004-03-08 | Earliest converted household interview date. |
| interview_date_max | 2005-03-31 | Latest converted household interview date. |
| interview_month_count | 13 | Distinct interview months. |
| interview_month_distribution | 2004-03:915;2004-04:938;2004-05:825;2004-06:977;2004-07:728;2004-08:1141;2004-09:1045;2004-10:918;2004-11:770;2004-12:640;2005-01:545;2005-02:896;2005-03:942 | Household counts by interview month. |
| household_ea_distinct | 564 | Distinct household dist+ta+ea keys. |
| household_ea_matched_to_ea_file | 564/564 | Household EA/admin keys matched to ihs2_ea_data. |
| household_psu_distinct | 564 | Distinct household V51 EA/PSU identifiers. |
| health_households_unmatched_to_household | 0 | Health-module households absent from household file. |
| health_ea_unmatched_to_household_ea | 0 | Health-module dist+ta+ea keys absent from household EA set. |
| survey_timing_final_verified | 1 | Raw survey timing is accepted for climate-window anchoring. |
| climate_geography_final_verified | 1 | Raw admin/EA geography is accepted as the candidate climate-linkage geography. |
| timing_geography_ready_for_climate | 1 | Raw timing and admin/EA geography are ready for climate-route review. |
| gps_coordinate_ready | 0 | No GPS coordinate field is accepted. |
| accepted_chirps_era5_route | 0 | A CHIRPS/ERA5 route is still blocked by boundary/crosswalk and aggregation policy. |
| timing_geography_policy_status | raw_timing_admin_ea_geography_verified_climate_route_blocked | Timing/geography raw values accepted; climate route remains blocked. |
| data_write_gate_status | closed | No promoted dataset may be written from this policy artifact alone. |

## Policy Rows

| policy_component | accepted_rule | raw_variables | aggregate_count | acceptance_status | remaining_blocker |
| --- | --- | --- | --- | --- | --- |
| interview_date_anchor | Use ihs2_household.idate as the household interview date, converted from Stata days since 1960-01-01. | idate | 11280 | raw_value_verified_for_climate_timing | Climate exposure windows are not extracted yet; this only accepts the raw timing anchor. |
| interview_month_window_policy | Anchor climate exposure windows to interview month; candidate windows are 1, 3, 6, and 12 complete months before interview month. | idate | 13 | raw_value_verified_for_climate_timing | Exact climate values still require CHIRPS/ERA5 extraction after geography route acceptance. |
| household_admin_ea_geography | Use dist+ta+ea as the household EA/admin geography key; use V51 as the 8-digit EA/PSU identifier. | dist;ta;ea;V51;region;type | 564 | raw_value_verified_for_admin_ea_geography | No household or cluster coordinates are accepted; boundary/crosswalk source remains required for climate extraction. |
| ea_auxiliary_join | Join household dist+ta+ea to ihs2_ea_data for auxiliary EA attributes only; do not treat access fields as coordinates. | dist;ta;ea;access;access2;lz_code | 564 | raw_value_verified_for_admin_ea_geography | EA auxiliary data improve geography context but do not solve historical boundary geometry. |
| person_module_geography_inheritance | For person-level health/access work, inherit household geography through case_id after confirming health households join to ihs2_household. | case_id;dist;ta;ea;psu | 11280 | raw_value_verified_for_admin_ea_geography | Person-key exceptions remain a separate health/access blocker; geography inheritance does not resolve person-level construct validity. |
| chirps_era5_route_status | Do not mark a CHIRPS or ERA5 route accepted yet; use admin/EA geography only after a boundary/crosswalk and aggregation method are documented. | dist;ta;ea;V51;psu;idate | 0 | blocked_boundary_crosswalk_and_exposure_aggregation_required | Need historical or defensible current boundary/crosswalk for district/TA/EA, plus CHIRPS/ERA5 aggregation choice. |

## Accepted Raw Inputs

- Timing: `idate` converted as Stata days since 1960-01-01 and anchored at
  interview month.
- Geography: household `dist + ta + ea` and `V51` as the EA/admin geography;
  health-module rows inherit household geography through `case_id`.
- EA auxiliary data: `ihs2_ea_data.dta` joins completely to household
  `dist + ta + ea`, but `access`, `access2`, and `lz_code` are context fields,
  not coordinates.

## Still Blocked

- No GPS coordinate field is accepted.
- CHIRPS/ERA5 linkage remains blocked until a defensible boundary/crosswalk and
  exposure aggregation level are documented.
- Person-key exceptions, access outcome policy, missing/skip/unit/recall policy,
  and data writes remain blocked.
