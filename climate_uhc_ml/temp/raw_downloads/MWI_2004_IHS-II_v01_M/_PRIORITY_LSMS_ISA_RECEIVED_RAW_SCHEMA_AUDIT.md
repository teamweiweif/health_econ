# Priority LSMS-ISA Received Raw Schema Audit

IDNO: `MWI_2004_IHS-II_v01_M`

Country-wave: Malawi 2004-2005

Status: metadata and selected value-stat scan of received raw archive members.
This handoff does not promote the dataset and does not persist raw microdata.

## File Readability

| member_name | read_status | row_count | column_count | read_error |
|---|---|---|---|---|
| Filters.dta | readable_metadata | 11252 | 22 |  |
| ihs2_ag.dta | readable_metadata | 11280 | 54 |  |
| ihs2_anthro.dta | readable_metadata | 6808 | 18 |  |
| ihs2_ea_data.dta | readable_metadata | 564 | 8 |  |
| ihs2_exp.dta | readable_metadata | 11280 | 79 |  |
| ihs2_household.dta | readable_metadata | 11280 | 76 |  |
| ihs2_individ.dta | readable_metadata | 51288 | 19 |  |
| ihs2_pov.dta | readable_metadata | 11280 | 34 |  |
| mod_a.dta | readable_metadata | 564 | 28 |  |
| mod_b.dta | readable_metadata | 4427 | 13 |  |
| mod_c.dta | readable_metadata | 564 | 20 |  |
| mod_d.dta | readable_metadata | 564 | 88 |  |
| mod_e.dta | readable_metadata | 564 | 25 |  |
| mod_f.dta | readable_metadata | 564 | 46 |  |
| mod_g.dta | readable_metadata | 564 | 53 |  |
| mod_g50better.dta | readable_metadata | 986 | 8 |  |
| mod_g50worse.dta | readable_metadata | 2058 | 8 |  |
| mod_h.dta | readable_metadata | 26508 | 9 |  |
| sec_a.dta | readable_metadata | 11280 | 38 |  |
| sec_aa.dta | readable_metadata | 11280 | 35 |  |
| sec_ab.dta | readable_metadata | 203044 | 28 |  |
| sec_ac.dta | readable_metadata | 1731 | 35 |  |
| sec_ad.dta | readable_metadata | 52644 | 32 |  |
| sec_b.dta | readable_metadata | 52707 | 53 |  |
| sec_c.dta | readable_metadata | 52707 | 62 |  |
| sec_d.dta | readable_metadata | 51292 | 70 |  |
| sec_e.dta | readable_metadata | 52702 | 52 |  |
| sec_f.dta | readable_metadata | 52679 | 50 |  |
| sec_g.dta | readable_metadata | 11280 | 73 |  |
| sec_h.dta | readable_metadata | 67680 | 22 |  |
| sec_i.dta | readable_metadata | 1297199 | 31 |  |
| sec_j1.dta | readable_metadata | 67676 | 18 |  |
| sec_j2.dta | readable_metadata | 203040 | 18 |  |
| sec_k.dta | readable_metadata | 439920 | 18 |  |
| sec_l.dta | readable_metadata | 191760 | 19 |  |
| sec_m1.dta | readable_metadata | 214319 | 22 |  |
| sec_m2.dta | readable_metadata | 191760 | 20 |  |
| sec_n.dta | readable_metadata | 11280 | 46 |  |
| sec_o.dta | readable_metadata | 20856 | 63 |  |
| sec_p.dta | readable_metadata | 186534 | 40 |  |
| sec_q1.dta | readable_metadata | 11280 | 68 |  |
| sec_q2.dta | readable_metadata | 9219 | 32 |  |
| sec_r.dta | readable_metadata | 5285 | 55 |  |
| sec_s.dta | readable_metadata | 54478 | 38 |  |
| sec_t.dta | readable_metadata | 40914 | 37 |  |
| sec_u.dta | readable_metadata | 56600 | 38 |  |
| sec_v.dta | readable_metadata | 3913 | 49 |  |
| sec_w.dta | readable_metadata | 11280 | 33 |  |
| sec_x.dta | readable_metadata | 11280 | 22 |  |
| sec_y.dta | readable_metadata | 146647 | 25 |  |
| sec_z1.dta | readable_metadata | 1331 | 28 |  |
| sec_z2.dta | readable_metadata | 10004 | 23 |  |

## Present Candidate Variables By Requirement

| requirement | present_candidate_rows |
|---|---|
| climate_geography | 12 |
| consumption_or_income | 12 |
| health_need_and_access | 12 |
| household_person_keys | 12 |
| oop_health_expenditure | 12 |
| survey_timing | 12 |
| weights_and_design | 12 |

## Remaining Gate Meaning

Confirmed raw schema presence is necessary but not sufficient. Promotion still
requires human-readable documentation, accepted merge keys, survey design,
units, recall periods, skip patterns, missing-value semantics, outcome
construction, and climate-linkage evidence.
