# Manual Data Access Guide

Status: raw schema/value verification is the binding blocker. The project has public metadata, module-level candidate maps, and some inspected public raw schema files, but no harmonized analytical dataset has been promoted.

## Priority Datasets

| Rank | IDNO | Dataset | URL |
|---:|---|---|---|
| 1 | `ETH_2021_ESPS-W5_v02_M` | Ethiopia - Socio-Economic Panel Survey 2021-2022 (2021-2022; ETH_2021_ESPS-W5_v02_M) | https://microdata.worldbank.org/catalog/6161/get-microdata |
| 2 | `ETH_2018_ESS_v04_M` | Ethiopia - Socioeconomic Survey 2018-2019 (2018-2019; ETH_2018_ESS_v04_M) | https://microdata.worldbank.org/catalog/3823/get-microdata |
| 3 | `MWI_2007-2009_MTM_v01_M` | Malawi - Marriage Transitions in Malawi 2007-2009, Panel Data (2007-2009; MWI_2007-2009_MTM_v01_M) | https://microdata.worldbank.org/catalog/3462/get-microdata |
| 4 | `MLI_2021_EHCVM-2_v01_M` | Mali - Enquête Harmonisée sur le Conditions de Vie des Ménages, 2021-2022 (2021-2022; MLI_2021_EHCVM-2_v01_M) | https://microdata.worldbank.org/catalog/6275/get-microdata |
| 5 | `NER_2021_EHCVM-2_v01_M` | Niger - Enquête Harmonisée sur le Conditions de Vie des Ménages, 2021-2022 (2021-2022; NER_2021_EHCVM-2_v01_M) | https://microdata.worldbank.org/catalog/6276/get-microdata |
| 6 | `NGA_2012_GHSP-W2_v02_M` | Nigeria - General Household Survey, Panel  2012-2013, Wave 2 (2012-2013; NGA_2012_GHSP-W2_v02_M) | https://microdata.worldbank.org/catalog/1952/get-microdata |
| 7 | `NGA_2015_GHSP-W3_v02_M` | Nigeria - General Household Survey, Panel  2015-2016, Wave 3 (2015-2016; NGA_2015_GHSP-W3_v02_M) | https://microdata.worldbank.org/catalog/2734/get-microdata |
| 8 | `NGA_2010_GHSP-W1_v03_M` | Nigeria - General Household Survey, Panel 2010-2011, Wave 1 (2010-2011; NGA_2010_GHSP-W1_v03_M) | https://microdata.worldbank.org/catalog/1002/get-microdata |
| 9 | `TZA_2008_NPS-R1_v03_M` | Tanzania - National Panel Survey 2008-2009, Wave 1 (2008-2009; TZA_2008_NPS-R1_v03_M) | https://microdata.worldbank.org/catalog/76/get-microdata |
| 10 | `TZA_2010_NPS-R2_v03_M` | Tanzania - National Panel Survey 2010-2011, Wave 2 (2010-2011; TZA_2010_NPS-R2_v03_M) | https://microdata.worldbank.org/catalog/1050/get-microdata |
| 11 | `TZA_2012_NPS-R3_v01_M` | Tanzania - National Panel Survey 2012-2013, Wave 3 (2012-2013; TZA_2012_NPS-R3_v01_M) | https://microdata.worldbank.org/catalog/2252/get-microdata |
| 12 | `TZA_2014_NPS-R4_v03_M_v03_A_EXT` | Tanzania - National Panel Survey 2014-2015 (2013-2016; TZA_2014_NPS-R4_v03_M_v03_A_EXT) | https://microdata.worldbank.org/catalog/3455/get-microdata |
| 13 | `TZA_2014_NPS-R4_v03_M` | Tanzania - National Panel Survey 2014-2015, Wave 4 (2014-2015; TZA_2014_NPS-R4_v03_M) | https://microdata.worldbank.org/catalog/2862/get-microdata |
| 14 | `TZA_2020_NPS-R5_v02_M` | Tanzania - National Panel Survey 2020-21, Wave 5 (2020-2022; TZA_2020_NPS-R5_v02_M) | https://microdata.worldbank.org/catalog/5639/get-microdata |
| 15 | `UGA_2014_SAGE-EL_v01_M` | Uganda - Social Assistance Grants for Empowerment  Programme 2014, Endline: Impact After Two Years of Programme Operations (2014; UGA_2014_SAGE-EL_v01_M) | https://microdata.worldbank.org/catalog/2654/get-microdata |

## File/Module Checklist

The machine-readable checklist is `temp/manual_download_file_checklist.csv` with 2000 metadata-derived file/module rows. It prioritizes modules that contain candidate consumption, OOP health expenditure, health-need/access, geography, survey-design, demographic, or shock variables.

### ETH_2021_ESPS-W5_v02_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `sect8_3_ls_w5.dta` | geography;health_expenditure;health_need_access;shocks;survey_design | `ls_s8_3q04;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1;ls_s8_3q12_2;ls_s8_3q14;ls_s8_3q17_1;ls_s8_3q17_10;ls_s8_3q17_11;ls_s8_3q17_2` |
| `sect11_ph_w5.dta` | geography;health_need_access;shocks;survey_design | `s11q16;s11q17;s11q17b;saq01;saq14;ea_id;pw_w5;saq07;saq08;harvestedcrop_id;s11q00a;s11q01b` |
| `sect3_pp_w5.dta` | geography;health_need_access;shocks;survey_design | `s3q31e2;s3q08;s3q09__Accuracy;s3q09__Altitude;s3q09__Latitude;s3q09__Longitude;s3q09__Timestamp;s3q37;saq01;saq14;ea_id;pw_w5` |
| `sect06_com_w5.dta` | geography;health_need_access;shocks;survey_design | `cs6q09;saq01;saq14;ea_id;saq07;cs6q01;cs6q02_1;cs6q02_2;cs6q02_3;cs6q03_1;cs6q03_2;cs6q03_3` |
| `sect04_com_w5.dta` | demographics;geography;health_need_access;shocks;survey_design | `cs4q04__0;cs4q04__1;cs4q04__10;cs4q04__11;cs4q04__12;cs4q04__13;cs4q04__2;cs4q04__3;cs4q04__4;cs4q04__5;cs4q04__6;cs4q04__7` |
| `sect4_pp_w5.dta` | geography;shocks;survey_design | `saq01;saq14;ea_id;pw_w5;saq07;saq08;crop_id;s4q01a;s4q01b;s4q02;s4q03;s4q04` |
| `sect9_ph_w5.dta` | geography;shocks;survey_design | `saq01;saq14;ea_id;pw_w5;saq07;saq08;crop_id;s9q00b;s9q01;s9q02;s9q03;s9q04` |
| `sect8_2_ls_w5.dta` | consumption;geography;health_need_access;shocks;survey_design | `ls_s8_2q14;ls_s8_2q18;ls_s8_2q19;ls_s8_2q20;saq01;saq14;ea_id;pw_w5;saq07;saq08;ls_code;ls_s8_2q01` |

### ETH_2018_ESS_v04_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `sect8_3_ls_w4.dta` | geography;health_expenditure;health_need_access;shocks;survey_design | `ls_s8_3q04;ls_s8_3q06;ls_s8_3q10a;ls_s8_3q10b;ls_s8_3q11;ls_s8_3q12_1;ls_s8_3q12_2;ls_s8_3q14;ls_s8_3q22;ls_s8_3q24;ls_s8_3q23;ls_s8_3q24` |
| `sect10c_hh_w4.dta` | demographics;geography;shocks;survey_design | `saq01;saq14;ea_id;individual_id;pw_w4;saq07;saq08;s10bq04;s10c_q02d;s10c_q02e;s10c_q05b;s10c_q05c` |
| `sect11_ph_w4.dta` | geography;health_need_access;shocks;survey_design | `s11q16;s11q17;saq01;saq14;ea_id;pw_w4;saq07;saq08;harvestedcrop_id;s11q01;s11q02a1;s11q02a2` |
| `sect04_com_w4.dta` | demographics;geography;health_need_access;shocks;survey_design | `cs4q04__0;cs4q04__1;cs4q04__10;cs4q04__11;cs4q04__12;cs4q04__13;cs4q04__2;cs4q04__3;cs4q04__4;cs4q04__5;cs4q04__6;cs4q04__7` |
| `sect06_com_w4.dta` | geography;health_need_access;shocks;survey_design | `cs6q09;saq01;saq14;ea_id;saq07;cs6q01;cs6q02;cs6q03_1;cs6q03_2;cs6q03_3;cs6q04_1;cs6q04_2` |
| `sect3_pp_w4.dta` | geography;shocks;survey_design | `s3q08;s3q09__Accuracy;s3q09__Altitude;s3q09__Latitude;s3q09__Longitude;s3q09__Timestamp;s3q37;saq01;saq14;ea_id;pw_w4;saq07` |
| `sect5b2_hh_w4.dta` | demographics;geography;survey_design | `saq01;saq14;ea_id;individual_id;pw_w4;saq07;saq08;asset_id;asset_type;s5bq03a;s5bq04a;s5bq04b` |
| `sect4_pp_w4.dta` | geography;shocks;survey_design | `saq01;saq14;ea_id;pw_w4;saq07;saq08;crop_id;s4q01a;s4q01b;s4q02;s4q03;s4q04` |

### MWI_2007-2009_MTM_v01_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `hh2_cmty` | demographics;geography;health_need_access;shocks | `ccq02_n;ccq02_u;ccq07_n;ccq07_u;ccq10_n;ccq10_u;ccq11;ccq13_n;ccq13_u;ccq14;ccq16_n;ccq16_u` |
| `hh3_cmty` | demographics;geography;health_need_access;shocks | `ccq11;ccq14;ccq16_n;ccq16_u;ccq18_n;ccq18_u;ccq20_n;ccq20_u;ccq22_n;ccq22_u;ccq24_n;ccq24_u` |
| `pi_s5a` | demographics;health_need_access;survey_design | `s5q17b_1;s5q17b_2;s5q17b_3;s5q17c_1;s5q17c_2;s5q17c_3;s5q17d_1;s5q17d_2;s5q17d_3;s5q17g_1;s5q17g_2;s5q17g_3` |
| `p2_s14a` | demographics;health_need_access;survey_design | `s14q19d_1;s14q19d_2;s14q19d_3;s14q19g_1;s14q19g_2;s14q19g_3;ea;hhid;hhid;pid;s14q11_1;s14q11_2` |
| `p2_s13` | demographics;geography;health_need_access;survey_design | `s13q25j;s13q41e;ea;hhid;hhid;pid;s13q05;s13q06;s13q08;s13q19;s13q20;s13q25f` |
| `hh2_mkts_location` | health_need_access;survey_design | `hlth_dist1;hlth_dist1u;hlth_dist2;hlth_dist2u;hlth_dist3;hlth_dist3u;hlth_dist4;hlth_dist4u;hlth_id1;hlth_id2;hlth_id3;hlth_id4` |
| `hh3_vct` | health_need_access;survey_design | `s1q15a;s1q15b;s1q15c;s1q15d;s1q15e;s1q15f;s1q15g;s1q15h;s1q15h_s;s1q1a_1_s;s1q1a_2_s;s1q1a_3_s` |
| `p2_s10` | demographics;health_expenditure;health_need_access;shocks;survey_design | `s10q35b;s10q23;s10q23_s;s10q39b;ea;hhid;hhid;pid;s10q12a;s10q12b;s10q13;s10q15` |

### MLI_2021_EHCVM-2_v01_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `s14b_me_mli2021` | consumption;demographics;health_expenditure;shocks;survey_design | `s14bq04e;s14bq04f;s14bq05__13;grappe;s14bq05__1;s14bq05__10;s14bq05__11;s14bq05__12;s14bq05__13;s14bq05__14;s14bq05__15;s14bq05__16` |
| `s03_me_mli2021` | demographics;health_expenditure;health_need_access;shocks;survey_design | `s03q24a;s03q24b;s03q27;s03q29;s03q30;s03q31;s03q32;s03q34;s03q36;s03q37__1;s03q48;s03q51` |
| `s03_co_mli2021` | geography;shocks;survey_design | `s03q16;grappe;s03q01;s03q03;s03q04__1;s03q04__2;s03q04__3;s03q04__4;s03q04__5;s03q04__6;s03q05;s03q06` |
| `s06_me_mli2021` | geography;shocks;survey_design | `s06q01__3;grappe;s06q03;s06q04;s06q05;s06q06;s06q08;s06q09;s06q10;s06q11;s06q12;s06q13a` |
| `ehcvm_individu_mli2021` | demographics;geography;health_need_access;survey_design | `arrmal;couvmal;durarr;commune;milieu;region;grappe;hhid;hhweight;age;agemar;educ_hi` |
| `ehcvm_welfare_mli2021` | demographics;geography;survey_design | `milieu;region;grappe;hhid;hhweight;month;hage;heduc;hgender` |
| `s02_me_mli2021` | demographics;geography;health_need_access;survey_design | `s02q26;s02q09b;grappe;s02q06;s02q07;s02q09d;s02q09e__2;s02q09e__3;s02q09e__4` |
| `s00_me_mli2021` | geography;survey_design | `GPS__Latitude;GPS__Longitude;s00q01;s00q03;s00q04;s00q22;grappe;s00q07f1` |

### NER_2021_EHCVM-2_v01_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `s14b_me_ner2021` | consumption;demographics;health_expenditure;shocks;survey_design | `s14bq04e;s14bq04f;s14bq05__13;grappe;s14bq05__1;s14bq05__10;s14bq05__11;s14bq05__12;s14bq05__13;s14bq05__14;s14bq05__15;s14bq05__16` |
| `s03_me_ner2021` | demographics;health_expenditure;health_need_access;shocks;survey_design | `s03q24a;s03q24b;s03q27;s03q29;s03q30;s03q31;s03q32;s03q34;s03q36;s03q37__1;s03q48;s03q51` |
| `s03_co_ner2021` | geography;shocks;survey_design | `s03q16;grappe;s03q01;s03q03;s03q04__1;s03q04__2;s03q04__3;s03q04__4;s03q04__5;s03q04__6;s03q05;s03q06` |
| `s06_me_ner2021` | geography;shocks;survey_design | `s06q01__3;grappe;s06q03;s06q04;s06q05;s06q06;s06q08;s06q09;s06q10;s06q11;s06q12;s06q13a` |
| `ehcvm_individu_ner2021` | demographics;geography;health_need_access;survey_design | `arrmal;couvmal;durarr;commune;milieu;region;zaemil;grappe;hhid;hhweight;age;agemar` |
| `s02_me_ner2021` | demographics;geography;health_need_access;survey_design | `s02q26;s02q09b;grappe;s02q06;s02q07;s02q09d;s02q09e__2;s02q09e__3;s02q09e__4;s02q09e__9` |
| `ehcvm_welfare_ner2021` | demographics;geography;survey_design | `milieu;region;grappe;hhid;hhweight;month;hage;heduc;hgender` |
| `s00_me_ner2021` | geography;survey_design | `GPS__Latitude;GPS__Longitude;s00q01;s00q03;s00q04;s00q22;grappe;s00q07f1` |

### NGA_2012_GHSP-W2_v02_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `secta1_harvestw2` | geography;shocks;survey_design | `lga;sa1q9c;state;ea;hhid;plotid;sa1q10c;sa1q11;sa1q11b;sa1q12;sa1q13;sa1q14` |
| `sect11b1_plantingw2` | geography;shocks;survey_design | `lga;state;ea;hhid;s11b1q23b;s11b1q23c;s11b1q23d;plotid;s11b1q11;s11b1q12a;s11b1q12b;s11b1q12c` |
| `sect11h_plantingw2` | geography;health_need_access;shocks;survey_design | `s11hq15;s11hq16;s11hq16b;s11hq8;s11hq9;s11hq9b;lga;state;ea;hhid;s11hq7a;s11hq7b` |
| `sect4a_harvestw2` | demographics;geography;health_expenditure;health_need_access;survey_design | `s4aq20;s4aq20b;s4aq10;s4aq11a;s4aq11a;s4aq11b;s4aq11b;s4aq12a;s4aq12b;s4aq15;s4aq16;s4aq17` |
| `secta3_harvestw2` | geography;health_need_access;shocks;survey_design | `sa3q4;sa3q4b;lga;state;ea;hhid;cropcode;cropid;cropname;plotid;sa3q10;sa3q12b1` |
| `sect11d_plantingw2` | geography;health_need_access;shocks;survey_design | `s11dq10;s11dq11;s11dq11b;s11dq17;s11dq18;s11dq18b;s11dq30;s11dq30b;s11dq31;lga;state;ea` |
| `sect9_harvestw2` | demographics;geography;health_need_access;shocks;survey_design | `s9q28c;s9q3;lga;state;ea;hhid;s9q14a;s9q14b;s9q16;s9q17;s9q18;s9q19a` |
| `sect11e_plantingw2` | geography;health_need_access;shocks;survey_design | `s11eq12;s11eq13;s11eq13b;s11eq19;s11eq20;s11eq20b;s11eq31;s11eq32;s11eq32b;lga;state;ea` |

### NGA_2015_GHSP-W3_v02_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `sect11b1_plantingw3` | geography;shocks;survey_design | `lga;state;ea;hhid;plotid;s11b1q1;s11b1q11;s11b1q12a;s11b1q12b;s11b1q12c;s11b1q12d;s11b1q13` |
| `secta3ii_harvestw3` | demographics;geography;shocks;survey_design | `lga;state;ea;hhid;sa3iiq26;sa3iiq27;crop_number;cropcode;cropname;sa3iiq11a;sa3iiq11b;sa3iiq11b_os` |
| `secta1_harvestw3` | geography;shocks;survey_design | `lga;sa1q10a;sa1q1a;sa1q9c;state;ea;hhid;plotid;sa1q10a;sa1q10b;sa1q10bb;sa1q10c` |
| `secta11d_harvestw3` | geography;health_need_access;shocks;survey_design | `s11dq10;s11dq11;s11dq17;s11dq18;s11dq18_os;s11dq30;s11dq30_os;s11dq31;s11dq41;lga;state;ea` |
| `sect4a_harvestw3` | demographics;geography;health_expenditure;health_need_access;survey_design | `s4aq20;s4aq20b;s4aq10;s4aq11a;s4aq11a;s4aq11b;s4aq11b;s4aq12a;s4aq12b;s4aq15;s4aq16;s4aq17` |
| `secta2_harvestw3` | geography;shocks;survey_design | `lga;state;ea;hhid;plotid;sa2q11a;sa2q11b;sa2q11c;sa2q12a;sa2q12b;sa2q12c;sa2q13a` |
| `sect11f_plantingw3` | geography;shocks;survey_design | `lga;state;ea;hhid;cropcode;cropid;cropname;plotid;s11fc5;s11fq11a;s11fq11b;s11fq11b_os` |
| `secta3i_harvestw3` | geography;health_need_access;shocks;survey_design | `sa3iq4;lga;state;ea;hhid;cropcode;cropid;cropname;plotid;sa3iq3;sa3iq4;sa3iq4a1` |

### NGA_2010_GHSP-W1_v03_M

| Candidate file/module | Categories | Example raw variables |
|---|---|---|
| `secta1_harvestw1` | geography;shocks;survey_design | `lga;sa1q9d;state;ea;hhid;plotid;sa1q10c;sa1q11;sa1q12;sa1q13;sa1q14;sa1q15` |
| `sect11h_plantingw1` | geography;health_need_access;shocks;survey_design | `s11hq15;s11hq16;s11hq16b;s11hq8;s11hq9;s11hq9b;lga;state;ea;hhid;cropcode;cropid` |
| `sect11c_plantingw1` | geography;shocks;survey_design | `lga;state;ea;hhid;plotid;s11cq1;s11cq10;s11cq11a;s11cq11b;s11cq11c;s11cq12a;s11cq12b` |
| `sect11b_plantingw1` | geography;shocks;survey_design | `lga;state;ea;hhid;s11bq2;plotid;s11bq1;s11bq10;s11bq11;s11bq12;s11bq13;s11bq14a` |
| `secta3_harvestw1` | geography;health_need_access;shocks;survey_design | `sa3q4;sa3q4b;lga;state;ea;hhid;cropid;plotid;sa3q1;sa3q10;sa3q14;sa3q15a` |
| `sect11e_plantingw1` | geography;health_need_access;shocks;survey_design | `s11eq12;s11eq13;s11eq13b;s11eq18;s11eq19;s11eq19b;s11eq29;s11eq30;s11eq30b;lga;state;ea` |
| `sect4a_harvestw1` | demographics;geography;health_expenditure;health_need_access;survey_design | `s4aq14;s4aq17;s4aq19;s4aq20;s4aq20b;s4aq11a;s4aq11a;s4aq11b;s4aq11b;s4aq15;s4aq16;s4aq17` |
| `sect8_harvestw1` | demographics;geography;survey_design | `lga;state;ea;hhid;s8q1;s8q14a;s8q14b;s8q17;s8q19;s8q2;s8q20;s8q24` |


## Manual Download Procedure

1. Open the priority dataset URL and complete the required World Bank Microdata Library login, registration, or Data Access Agreement steps.
2. Download all raw household, individual, expenditure, health, geography/GPS, survey design, and documentation files available for the study. Do not cherry-pick only modules that look useful from metadata.
3. Store the raw files or original archives under `temp/raw_downloads/`, preferably in a subfolder named by IDNO such as `temp/raw_downloads/ETH_2021_ESPS-W5_v02_M/`.
4. Run `make all` from the project root.
5. Inspect `temp/raw_schema_inventory/raw_file_inventory.csv`, `temp/raw_schema_inventory/raw_variable_catalog.csv`, `temp/harmonization_recipe_gate.csv`, and `temp/harmonization_value_audit_template.csv`.
6. Build `temp/harmonization_recipe.csv` from verified gate candidates only after raw variable names, labels, values, units, recall periods, missing codes, lineage, and merge keys are verified.

## Guardrails

- Do not put raw files in `data/`.
- Do not treat metadata-only variable hits as verified raw variables.
- Do not construct SDG 3.8.2 until the discretionary-budget denominator can be audited.
- Do not run or interpret causal ML until reduced-form estimates and placebo checks pass.
