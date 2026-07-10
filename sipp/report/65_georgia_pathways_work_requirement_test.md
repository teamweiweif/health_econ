# Georgia Pathways to Coverage Work-Requirement Quick Screen

## Purpose

This screen tests whether SIPP can support a current adult Medicaid work-requirement paper using
Georgia Pathways to Coverage. Georgia launched Pathways in 2023 as a partial Medicaid expansion for
adults age 19-64 with income up to 100% FPL, conditioned on qualifying activities.

## Policy Design Checked

Official Georgia Pathways pages say eligible adults must:

- be Georgia residents;
- be ages 19-64;
- have household income up to 100% FPL;
- not qualify for another Medicaid category;
- complete at least 80 hours of qualifying activities per month.

The program began in 2023; this screen uses July 2023 as the main start month and September 2023 as
a sensitivity because early implementation and coverage start timing may lag application.

## Empirical Design

- Unit: person-month.
- Years: 2022-2023 only.
- Treated state: Georgia.
- Controls: never-expansion comparison states with no full ACA expansion in this period.
- Main sample: adults age 19-64, non-Medicare, 0-200% monthly FPL.
- Target group: <=100% FPL.
- Comparison income group: 100-200% FPL.
- Main term: `Georgia x post-July-2023 x <=100% FPL`.
- Fixed effects: state and calendar year-month.
- Controls: FPL quadratic, age quadratic, sex, Black, Hispanic, disability, work-activity proxy.
- Inference: state-clustered and person-clustered standard errors.

## Support

| spec | person_months | persons | states | ga_target_person_months | ga_target_persons | ga_post_target_person_months | ga_post_target_persons | ga_post_target_medicaid_months | ga_post_target_uninsured_months | ga_post_target_work_proxy_months |
|---|---|---|---|---|---|---|---|---|---|---|
| monthly_000_200_postjul_low100 | 36376 | 3267 | 10 | 2149 | 231 | 494 | 92 | 129 | 191 | 155 |
| monthly_000_200_postsep_low100 | 36376 | 3267 | 10 | 2149 | 231 | 329 | 88 | 88 | 122 | 107 |
| monthly_work_proxy_postjul_low100 | 19288 | 2032 | 10 | 697 | 106 | 155 | 35 | 38 | 52 | 155 |
| annual_000_200_postjul_low100 | 35006 | 2539 | 10 | 1968 | 152 | 479 | 81 | 123 | 198 | 151 |
| monthly_050_150_postjul_low100 | 15865 | 1811 | 10 | 738 | 109 | 177 | 38 | 66 | 83 | 66 |

## Raw Cell Means

Main monthly-FPL support cells:

| georgia | period | target_low100 | person_months | persons | work_activity_proxy | medicaid | uninsured | any_coverage | private | direct_purchase | snap_month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | post_jul_dec2023 | 0 | 3829 | 844 | 0.6731 | 0.1998 | 0.3011 | 0.6989 | 0.5354 | 0.2260 | 0.1210 |
| 0 | post_jul_dec2023 | 1 | 3475 | 717 | 0.4099 | 0.2383 | 0.3814 | 0.6186 | 0.3912 | 0.2147 | 0.1923 |
| 0 | pre_2022_to_jun2023 | 0 | 12873 | 1811 | 0.6902 | 0.2576 | 0.2989 | 0.7011 | 0.4894 | 0.2000 | 0.1517 |
| 0 | pre_2022_to_jun2023 | 1 | 12229 | 1610 | 0.4075 | 0.2787 | 0.3814 | 0.6186 | 0.3530 | 0.1841 | 0.2461 |
| 1 | post_jul_dec2023 | 0 | 480 | 94 | 0.7459 | 0.1490 | 0.2965 | 0.7035 | 0.5862 | 0.1602 | 0.1545 |
| 1 | post_jul_dec2023 | 1 | 494 | 92 | 0.3230 | 0.2393 | 0.4169 | 0.5831 | 0.3443 | 0.1991 | 0.1498 |
| 1 | pre_2022_to_jun2023 | 0 | 1341 | 194 | 0.6399 | 0.1596 | 0.2999 | 0.7001 | 0.5691 | 0.1387 | 0.1816 |
| 1 | pre_2022_to_jun2023 | 1 | 1655 | 226 | 0.2860 | 0.2805 | 0.4324 | 0.5676 | 0.3271 | 0.1816 | 0.2893 |

## State Support For Target <=100% FPL

| state_name | person_months | persons | post_person_months | post_persons | medicaid_pre | medicaid_post | uninsured_pre | uninsured_post |
|---|---|---|---|---|---|---|---|---|
| Alabama | 877 | 97 | 195 | 35 | 0.3424 | 0.3653 | 0.2132 | 0.2187 |
| Florida | 3566 | 394 | 706 | 152 | 0.2330 | 0.1903 | 0.3777 | 0.3742 |
| Georgia | 2149 | 231 | 494 | 92 | 0.2805 | 0.2393 | 0.4324 | 0.4169 |
| Kansas | 363 | 45 | 63 | 16 | 0.2132 | 0.1265 | 0.2217 | 0.2296 |
| Mississippi | 1320 | 121 | 250 | 46 | 0.4590 | 0.3943 | 0.2460 | 0.4041 |
| South Carolina | 1126 | 139 | 223 | 48 | 0.3629 | 0.2816 | 0.3521 | 0.3873 |
| Tennessee | 1436 | 145 | 355 | 69 | 0.3933 | 0.3785 | 0.2995 | 0.3380 |
| Texas | 6016 | 656 | 1443 | 297 | 0.2104 | 0.1910 | 0.5028 | 0.4672 |
| Wisconsin | 848 | 97 | 205 | 49 | 0.5388 | 0.2917 | 0.0850 | 0.1293 |
| Wyoming | 152 | 14 | 35 | 6 | 0.2017 | 0.0000 | 0.2586 | 0.1753 |

## Main Estimates

Monthly FPL 0-200%, target <=100%, post July 2023:

- `medicaid`: -0.0455, state-cluster se 0.0306, t -1.49; person-cluster se 0.0675, t -0.67.
- `uninsured`: -0.0327, state-cluster se 0.0397, t -0.82; person-cluster se 0.0791, t -0.41.
- `any_coverage`: +0.0327, state-cluster se 0.0397, t 0.82; person-cluster se 0.0791, t 0.41.
- `public`: -0.0331, state-cluster se 0.0402, t -0.83; person-cluster se 0.0679, t -0.49.
- `private`: +0.0339, state-cluster se 0.0257, t 1.32; person-cluster se 0.0745, t 0.46.
- `direct_purchase`: -0.0150, state-cluster se 0.0137, t -1.10; person-cluster se 0.0612, t -0.25.
- `marketplace_flag`: -0.0241, state-cluster se 0.0111, t -2.17; person-cluster se 0.0555, t -0.43.
- `market_or_subsidy`: -0.0171, state-cluster se 0.0157, t -1.09; person-cluster se 0.0613, t -0.28.
- `snap_month`: -0.1042, state-cluster se 0.0139, t -7.50; person-cluster se 0.0582, t -1.79.
- `work_activity_proxy`: -0.0000, state-cluster se 0.0000, t -0.96; person-cluster se 0.0000, t -2.45.

Post September 2023 sensitivity:

- `medicaid`: -0.0456, state-cluster se 0.0271, t -1.68; person-cluster se 0.0630, t -0.72.
- `uninsured`: -0.0676, state-cluster se 0.0424, t -1.59; person-cluster se 0.0752, t -0.90.
- `any_coverage`: +0.0676, state-cluster se 0.0424, t 1.59; person-cluster se 0.0752, t 0.90.
- `public`: -0.0352, state-cluster se 0.0347, t -1.02; person-cluster se 0.0635, t -0.56.
- `private`: +0.0711, state-cluster se 0.0292, t 2.43; person-cluster se 0.0710, t 1.00.
- `direct_purchase`: -0.0041, state-cluster se 0.0175, t -0.24; person-cluster se 0.0579, t -0.07.
- `marketplace_flag`: -0.0185, state-cluster se 0.0145, t -1.28; person-cluster se 0.0528, t -0.35.
- `market_or_subsidy`: -0.0058, state-cluster se 0.0199, t -0.29; person-cluster se 0.0580, t -0.10.
- `snap_month`: -0.0906, state-cluster se 0.0150, t -6.04; person-cluster se 0.0568, t -1.59.
- `work_activity_proxy`: -0.0000, state-cluster se 0.0000, t -0.99; person-cluster se 0.0000, t -7.20.

Work-activity proxy sample:

- `medicaid`: -0.0459, state-cluster se 0.0328, t -1.40; person-cluster se 0.0965, t -0.48.
- `uninsured`: +0.0445, state-cluster se 0.0370, t 1.20; person-cluster se 0.1111, t 0.40.
- `any_coverage`: -0.0445, state-cluster se 0.0370, t -1.20; person-cluster se 0.1111, t -0.40.
- `public`: -0.0464, state-cluster se 0.0391, t -1.19; person-cluster se 0.0973, t -0.48.
- `private`: -0.0145, state-cluster se 0.0259, t -0.56; person-cluster se 0.1100, t -0.13.
- `direct_purchase`: -0.1000, state-cluster se 0.0151, t -6.64; person-cluster se 0.1016, t -0.98.
- `marketplace_flag`: -0.0242, state-cluster se 0.0184, t -1.32; person-cluster se 0.0979, t -0.25.
- `market_or_subsidy`: -0.1023, state-cluster se 0.0150, t -6.84; person-cluster se 0.1016, t -1.01.
- `snap_month`: -0.1318, state-cluster se 0.0194, t -6.78; person-cluster se 0.0764, t -1.73.
- `work_activity_proxy`: -0.0000, state-cluster se 0.0000, t -1.50; person-cluster se 0.0000, t -4.40.

Annual-FPL sensitivity:

- `medicaid`: -0.0815, state-cluster se 0.0243, t -3.35; person-cluster se 0.0723, t -1.13.
- `uninsured`: +0.0757, state-cluster se 0.0245, t 3.09; person-cluster se 0.0803, t 0.94.
- `any_coverage`: -0.0757, state-cluster se 0.0245, t -3.09; person-cluster se 0.0803, t -0.94.
- `public`: -0.0776, state-cluster se 0.0251, t -3.10; person-cluster se 0.0727, t -1.07.
- `private`: -0.0491, state-cluster se 0.0250, t -1.97; person-cluster se 0.0785, t -0.63.
- `direct_purchase`: -0.0113, state-cluster se 0.0121, t -0.93; person-cluster se 0.0675, t -0.17.
- `marketplace_flag`: -0.0002, state-cluster se 0.0094, t -0.02; person-cluster se 0.0625, t -0.00.
- `market_or_subsidy`: -0.0177, state-cluster se 0.0115, t -1.54; person-cluster se 0.0675, t -0.26.
- `snap_month`: -0.2114, state-cluster se 0.0073, t -28.84; person-cluster se 0.0662, t -3.19.
- `work_activity_proxy`: -0.0000, state-cluster se 0.0000, t -1.09; person-cluster se 0.0000, t -13.12.

Local 50-150% FPL sensitivity:

- `medicaid`: -0.1441, state-cluster se 0.0468, t -3.08; person-cluster se 0.1181, t -1.22.
- `uninsured`: +0.2097, state-cluster se 0.0676, t 3.10; person-cluster se 0.1299, t 1.61.
- `any_coverage`: -0.2097, state-cluster se 0.0676, t -3.10; person-cluster se 0.1299, t -1.61.
- `public`: -0.1277, state-cluster se 0.0504, t -2.54; person-cluster se 0.1180, t -1.08.
- `private`: -0.1318, state-cluster se 0.0455, t -2.90; person-cluster se 0.1155, t -1.14.
- `direct_purchase`: -0.0325, state-cluster se 0.0247, t -1.32; person-cluster se 0.1023, t -0.32.
- `marketplace_flag`: -0.0744, state-cluster se 0.0146, t -5.09; person-cluster se 0.0989, t -0.75.
- `market_or_subsidy`: -0.0338, state-cluster se 0.0308, t -1.10; person-cluster se 0.1026, t -0.33.
- `snap_month`: -0.1746, state-cluster se 0.0155, t -11.29; person-cluster se 0.1081, t -1.62.
- `work_activity_proxy`: -0.0000, state-cluster se 0.0000, t -0.64; person-cluster se 0.0000, t -1.64.

## Initial Interpretation

A viable SIPP paper would need enough Georgia post-launch target observations and a coherent pattern:
Medicaid/public coverage rising for <=100% FPL adults relative to 100-200% FPL adults and comparable
non-expansion states, or a precisely estimated null consistent with administrative barriers. If the
Georgia post-launch target cell has very few Medicaid months, the policy is important but SIPP is
not the right main dataset.

## Artifacts

- `script/11_idea_scan/32_georgia_pathways_work_requirement_test.py`
- `result/idea_scan/georgia_pathways_estimates.csv`
- `result/idea_scan/georgia_pathways_support.csv`
- `result/idea_scan/georgia_pathways_cell_means.csv`
- `result/idea_scan/georgia_pathways_state_support.csv`
