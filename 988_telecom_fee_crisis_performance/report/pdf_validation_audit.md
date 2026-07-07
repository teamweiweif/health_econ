# PDF Validation Audit

## Finding

Manual-style validation of the 30 sampled rows found no evidence that the row text, counts, or time fields were misread from the official PDFs. The important issue is correctable: for several 2022 transition months, the official PDF answer rate aligns with `answered_in_state / received_in_state`, while the current pipeline stored `answered_in_state / routed_in_state` as `in_state_answer_rate`.

This affects answer-rate values, not the parsed count fields. Flowout, abandonment, speed-to-answer, and talk-time fields in the sampled rows match the PDF text.

## Sample Audit

| year_month | state | raw_row_text | received_in_state | in_state_answer_rate_reported | answer_rate_routed_calc | answer_rate_received_calc | validation_class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2022-10 | TX | TX 14,325 14,325 8,485 59% 1,402 4,438 00:21 12:52 | 14325.0 | 0.5900 | 0.5923 | 0.5923 | verified_against_pdf_text_with_rounding |
| 2022-03 | NM | NM 1,463 1,463 1,036 71% 378 49 01:03 16:10 | 1463.0 | 0.7100 | 0.7081 | 0.7081 | verified_against_pdf_text_with_rounding |
| 2023-01 | CA | CA 27,716 27,716 24,260 88% 3,387 69 00:37 12:08 | 27716.0 | 0.8800 | 0.8753 | 0.8753 | verified_against_pdf_text_with_rounding |
| 2022-06 | MP | MP 21 21 0 0% 8 13 00:00 00:00 | 21.0 | 0.0000 | 0.0000 | 0.0000 | verified_against_pdf_text_with_rounding |
| 2023-08 | TN | TN 4,069 4,069 3,585 88% 439 45 00:26 10:47 | 4069.0 | 0.8800 | 0.8811 | 0.8811 | verified_against_pdf_text_with_rounding |
| 2024-05 | LA | LA 3,604 3,604 3,220 89% 324 60 00:20 12:45 | 3604.0 | 0.8900 | 0.8935 | 0.8935 | verified_against_pdf_text_with_rounding |
| 2023-04 | MS | MS 1,168 1,168 1,137 97% 19 12 00:06 08:05 | 1168.0 | 0.9700 | 0.9735 | 0.9735 | verified_against_pdf_text_with_rounding |
| 2024-12 | NC | NC 7,673 6,083 79% 953 637 21.1 sec 13.2 min |  | 0.7900 | 0.7928 | NA | verified_against_pdf_text_with_rounding |
| 2024-09 | CA | CA 37,138 30,436 82% 4,138 2,481 29.5 sec 12.4 min |  | 0.8200 | 0.8195 | NA | verified_against_pdf_text_with_rounding |
| 2022-09 | OH | OH 6,855 6,712 5,683 85% 442 587 00:18 11:22 | 6712.0 | 0.8500 | 0.8290 | 0.8467 | correctable_denominator_error_in_current_pipeline |
| 2025-01 | DC | DC 1,312 722 55% 119 467 21.1 sec 9.1 min |  | 0.5500 | 0.5503 | NA | verified_against_pdf_text_with_rounding |
| 2022-07 | WI | WI 6,271 6,012 4,550 76% 789 673 00:26 14:52 | 6012.0 | 0.7600 | 0.7256 | 0.7568 | correctable_denominator_error_in_current_pipeline |
| 2026-04 | IA | IA 4,057 3,721 92% 299 37 24.3 sec 13.6 min |  | 0.9200 | 0.9172 | NA | verified_against_pdf_text_with_rounding |
| 2022-06 | AK | AK 467 467 298 64% 120 49 00:34 14:19 | 467.0 | 0.6400 | 0.6381 | 0.6381 | verified_against_pdf_text_with_rounding |
| 2023-07 | VT | VT 828 828 655 79% 53 120 00:14 18:19 | 828.0 | 0.7900 | 0.7911 | 0.7911 | verified_against_pdf_text_with_rounding |
| 2023-09 | AL | AL 2,697 2,697 1,858 69% 435 404 00:31 12:22 | 2697.0 | 0.6900 | 0.6889 | 0.6889 | verified_against_pdf_text_with_rounding |
| 2025-06 | CO | CO 9,379 8,639 92% 564 173 18.5 sec 15.2 min |  | 0.9200 | 0.9211 | NA | verified_against_pdf_text_with_rounding |
| 2022-08 | SC | SC 3,804 3,600 2,506 70% 559 535 00:30 11:35 | 3600.0 | 0.7000 | 0.6588 | 0.6961 | correctable_denominator_error_in_current_pipeline |
| 2021-11 | TX | TX 12,336 12,336 4,776 39% 2,476 5,084 00:24 13:50 | 12336.0 | 0.3900 | 0.3872 | 0.3872 | verified_against_pdf_text_with_rounding |
| 2025-03 | MN | MN 7,298 5,979 82% 1,206 103 20.8 sec 13.9 min |  | 0.8200 | 0.8193 | NA | verified_against_pdf_text_with_rounding |
| 2022-05 | MS | MS 1,100 1,100 974 89% 114 12 00:22 07:43 | 1100.0 | 0.8900 | 0.8855 | 0.8855 | verified_against_pdf_text_with_rounding |
| 2023-06 | HI | HI 1,520 1,520 1,477 97% 38 5 00:07 08:35 | 1520.0 | 0.9700 | 0.9717 | 0.9717 | verified_against_pdf_text_with_rounding |
| 2023-03 | NM | NM 1,968 1,968 1,537 78% 245 186 00:23 18:09 | 1968.0 | 0.7800 | 0.7810 | 0.7810 | verified_against_pdf_text_with_rounding |
| 2024-01 | WA | WA 7,400 7,400 6,747 91% 521 132 00:22 12:19 | 7400.0 | 0.9100 | 0.9118 | 0.9118 | verified_against_pdf_text_with_rounding |
| 2022-10 | AR | AR 1,324 1,324 893 67% 196 235 00:24 11:10 | 1324.0 | 0.6700 | 0.6745 | 0.6745 | verified_against_pdf_text_with_rounding |
| 2025-07 | NH | NH 1,373 1,249 91% 103 20 22.5 sec 14.1 min |  | 0.9100 | 0.9097 | NA | verified_against_pdf_text_with_rounding |
| 2023-06 | MI | MI 6,862 6,862 6,118 89% 546 198 00:25 11:48 | 6862.0 | 0.8900 | 0.8916 | 0.8916 | verified_against_pdf_text_with_rounding |
| 2024-08 | OR | OR 5,834 5,834 4,653 80% 581 600 00:25 16:23 | 5834.0 | 0.8000 | 0.7976 | 0.7976 | verified_against_pdf_text_with_rounding |
| 2022-02 | UT | UT 1,854 1,854 1,517 82% 190 147 00:24 15:20 | 1854.0 | 0.8200 | 0.8182 | 0.8182 | verified_against_pdf_text_with_rounding |
| 2026-02 | CO | CO 9,807 8,948 91% 679 180 18.9 sec 13.2 min |  | 0.9100 | 0.9124 | NA | verified_against_pdf_text_with_rounding |

## Month-Level Denominator Check

| year_month | states | max_current_routed_abs_diff | max_received_abs_diff | rows_with_current_diff_gt_1pp |
| --- | --- | --- | --- | --- |
| 2022-07 | 56 | 0.08750293358366579 | 0.004896965763426908 | 52 |
| 2022-08 | 56 | 0.11555030703826163 | 0.004931506849314982 | 52 |
| 2022-09 | 56 | 0.08465346534653473 | 0.004943820224719175 | 51 |

## Classification

- Harmless: ordinary rounding differences within roughly 0.5 percentage points.
- Correctable: answer-rate denominator mismatch in launch-transition rows where received contacts differ from routed contacts.
- Fatal: none found in the sampled rows.

## Rescue-Layer Action

`data/rescue/analysis_panel_rescue.csv` retains the original answer-rate variable and adds `in_state_answer_rate_rescue`, calculated as `answered_in_state / received_in_state` when the received denominator is available and positive, otherwise falling back to the reported/current rate.
