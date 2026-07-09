# ALB_2005 Health Questionnaire Semantics Audit

Status: fail-closed questionnaire semantics audit. This report reads the ALB_2005 health questionnaire workbook and SPSS health modules to document recall periods, old-lek unit notes, payment-scope exclusions, zero-payment instructions, access-barrier value codes, and raw variable coverage. It does not write `data/`, does not construct outcomes, and does not promote any row to a harmonization recipe or climate linkage.

## Bottom Line

- The ALB_2005 health questionnaire is readable in the current Python environment.
- OOP payment questions are documented as old-lek payment items, split across past-four-week outpatient/self-medication contexts and past-12-month inpatient/dental contexts.
- Several provider-charge questions explicitly exclude gifts, medicines, laboratory work, and transport, so OOP aggregation must preserve item scope rather than blindly summing provider totals and components.
- Health module B documents 12-month access, delayed-care, referral, refusal, cost, distance, and service-availability barriers, but denominator and skip-pattern reconstruction still requires raw-value review.
- Recipe-ready, outcome-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2005_health_questionnaire_semantics_rows | 58 | Rows in the ALB_2005 health questionnaire semantics audit. |
| alb2005_health_questionnaire_oop_item_rows | 36 | Questionnaire-backed OOP payment item rows. |
| alb2005_health_questionnaire_visit_selection_rows | 8 | Visit/stay/purchase selection rows needed for OOP denominators. |
| alb2005_health_questionnaire_access_rows | 7 | Access, delayed-care, referral, refusal, and barrier rows from health module B. |
| alb2005_health_questionnaire_four_week_oop_rows | 26 | OOP item rows with past-four-week recall. |
| alb2005_health_questionnaire_twelve_month_oop_rows | 10 | OOP item rows with past-12-month recall. |
| alb2005_health_questionnaire_old_lek_unit_rows | 36 | Rows where the questionnaire explicitly records old-lek units. |
| alb2005_health_questionnaire_exclusion_note_rows | 7 | Rows with explicit exclusion notes for gifts, medicines, laboratory, or transport. |
| alb2005_health_questionnaire_zero_instruction_rows | 5 | Rows with explicit zero-payment instructions. |
| alb2005_health_questionnaire_cost_barrier_rows | 3 | Access rows whose questionnaire options include cost or affordability barriers. |
| alb2005_health_questionnaire_distance_barrier_rows | 2 | Access rows whose questionnaire options include distance or transport barriers. |
| alb2005_health_questionnaire_supply_barrier_rows | 2 | Access rows whose questionnaire options include availability, service-region, referral, or shortage barriers. |
| alb2005_health_questionnaire_recipe_ready_rows | 0 | Rows promoted to a harmonization recipe by this audit; intentionally zero. |
| alb2005_health_questionnaire_outcome_ready_rows | 0 | Rows promoted to constructed outcomes by this audit; intentionally zero. |
| alb2005_health_questionnaire_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2005_health_questionnaire_required_value_key_recipe_ready_observed | 0 | Recipe-ready rows observed in the required value/key audit. |
| alb2005_health_questionnaire_required_value_key_climate_ready_observed | 0 | Climate-linkage-ready rows observed in the required value/key audit. |
| alb2005_health_questionnaire_value_decision_recipe_ready_observed | 0 | Recipe-ready rows observed in the value-decision audit. |
| alb2005_health_questionnaire_current_decision | blocked_alb2005_questionnaire_semantics_seen_but_recipe_not_ready | Current fail-closed decision for questionnaire-backed ALB_2005 health semantics. |
| alb2005_health_questionnaire_status_questionnaire_confirms_access_barrier_codes_but_denominator_not_ready | 3 | Rows by questionnaire semantic status. |
| alb2005_health_questionnaire_status_questionnaire_confirms_access_question_but_skip_pattern_not_ready | 4 | Rows by questionnaire semantic status. |
| alb2005_health_questionnaire_status_questionnaire_confirms_health_financing_coping_item_but_not_minimum_recipe | 5 | Rows by questionnaire semantic status. |
| alb2005_health_questionnaire_status_questionnaire_confirms_medicine_discount_access_item_but_not_minimum_recipe | 2 | Rows by questionnaire semantic status. |
| alb2005_health_questionnaire_status_questionnaire_confirms_old_lek_payment_item_but_aggregation_not_ready | 36 | Rows by questionnaire semantic status. |
| alb2005_health_questionnaire_status_questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready | 8 | Rows by questionnaire semantic status. |

## Concept Counts

| Concept | Count |
|---|---:|
| oop_health_expenditure | 44 |
| care_or_barrier | 7 |
| coping_or_access_financing | 5 |
| insurance_or_medicine_access | 2 |

## Semantic Status Counts

| Semantic status | Count |
|---|---:|
| questionnaire_confirms_old_lek_payment_item_but_aggregation_not_ready | 36 |
| questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready | 8 |
| questionnaire_confirms_health_financing_coping_item_but_not_minimum_recipe | 5 |
| questionnaire_confirms_access_question_but_skip_pattern_not_ready | 4 |
| questionnaire_confirms_access_barrier_codes_but_denominator_not_ready | 3 |
| questionnaire_confirms_medicine_discount_access_item_but_not_minimum_recipe | 2 |

## OOP Questionnaire Rows

| raw_variable | raw_label | question_text | recall_period | unit_or_value_note | skip_or_instruction_note | raw_nonmissing_rows | raw_positive_numeric_rows |
|---|---|---|---|---|---|---|---|
| m9a_q16 | Amount paid for all costs associated with outpatent visits | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to the public ambulatory during t... | past_4_weeks | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 1591 | 664 |
| m9a_q17 | Value of gifts made to medical staff | What was the value of any gifts ( money, food, services) made to the medical staff of public ambulatory during the past 4 weeks ? | past_4_weeks | OLD LEKS | IF NO GIFTS PAID WRITE "0", (>>19) | 1591 | 298 |
| m9a_q20 | Amount paid for medicines | How much did you pay for these medicines? | past_4_weeks | OLD LEKS |  | 1482 | 1296 |
| m9a_q22 | Amount paid for lab work | How much did you pay, either in money or in kind for laboratory work (e.g. X-rays, blood tests, ?)? | past_4_weeks | OLD LEKS |  | 1591 | 316 |
| m9a_q23 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport (related with visits)? | past_4_weeks | OLD LEKS |  | 1591 | 304 |
| m9a_q28 | Amount paid | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to the hospital during the past 4... | past_4_weeks | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 653 | 430 |
| m9a_q29 | Value of gifts | What was the value of any gifts ( money, food, services) made to the medical staff of the hospital during the past 4 weeks ? | past_4_weeks | OLD LEKS | IF NO GIFTS PAID WRITE "0", (>>31) | 653 | 197 |
| m9a_q32 | Amount paid for medicines | How much did you pay for these medicines? | past_4_weeks | OLD LEKS |  | 561 | 492 |
| m9a_q34 | Amount paid for laboratory work | How much did you pay, either in money or in kind for laboratory work (e.g. X-rays, blood tests, ?)? | past_4_weeks | OLD LEKS |  | 653 | 201 |
| m9a_q35 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport (related with visits)? | past_4_weeks | OLD LEKS |  | 653 | 286 |
| m9a_q38 | Amount paid for all costs associated | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to a private doctor during the pa... | past_4_weeks | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 205 | 187 |
| m9a_q39 | Value of gifts | What was the value of any gifts ( money, food, services) made to the private doctor and staff during the past 4 weeks ? | past_4_weeks | OLD LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, (>>41) | 205 | 9 |
| m9a_q41 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | OLD LEKS |  | 205 | 133 |
| m9a_q42 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | OLD LEKS |  | 205 | 69 |
| m9a_q43 | Amount paid for transport | How much did you pay, either in money or in kind, for transport? | past_4_weeks | OLD LEKS |  | 205 | 77 |
| m9a_q46 | Amount paid | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to the private medical provider d... | past_4_weeks | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 210 | 106 |
| m9a_q47 | Value of gifts | What was the value of any gifts ( money, food, services) made to the medical provider during the past 4 weeks ? | past_4_weeks | OLD LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, (>>49) | 210 | 43 |
| m9a_q49 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | OLD LEKS |  | 210 | 57 |
| m9a_q50 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | OLD LEKS |  | 210 | 19 |
| m9a_q51 | Amount paid for transport | How much did you pay, either in money or in kind for transport? | past_4_weeks | OLD LEKS |  | 210 | 29 |
| m9a_q54 | Amount paid for all costs associated | How much did you pay, either in money or in kind, for all costs associated with these outpatient visits to a popular doctor/alternative m... | past_4_weeks | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 56 | 53 |
| m9a_q55 | Value of gifts | What was the value of any gifts ( money, food, services) made to the popular doctor/ alternative medicine provider during the past 4 weeks ? | past_4_weeks | OLD LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, (>>57) | 56 | 7 |
| m9a_q57 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | OLD LEKS |  | 56 | 16 |
| m9a_q58 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | OLD LEKS |  | 56 | 1 |
| m9a_q59 | Amount paid for transport | How much did you pay, either in money or in kind for transport? | past_4_weeks | OLD LEKS |  | 56 | 18 |
| m9a_q61 | Amount paid for all drugs in past 4 weeks | How much did you pay for all drugs purchased on your own without presciption in the past 4 weeks? | past_4_weeks | OLD LEKS |  | 2630 | 2619 |
| m9a_q68 | Amount paid for hospital stays | How much did you pay, either in money or in kind, for all costs related to these hospital stays during the last 12 months?(declare in val... | past_12_months | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 710 | 425 |
| m9a_q69 | Value of gifts | What was the value of any gifts ( money, food, services) made to the hospital staff during the past 12 months ? | past_12_months | OLD LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, (>>71) | 710 | 372 |
| m9a_q71 | Amount paid for medicines | How much did you pay, either in money or in-kind, for all medicines prescribed during these hospital stays, including those purchased and... | past_12_months | OLD LEKS |  | 710 | 424 |
| m9a_q72 | Amount paid for lab work | How much did you pay, either in money or in kind for laboratory work? | past_12_months | OLD LEKS |  | 710 | 319 |
| m9a_q73 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport? | past_12_months | OLD LEKS |  | 710 | 452 |
| m9a_q76 | Amount paid | How much did you pay, either in money or in-kind, for all costs of these visits to a dentist during the last 12 months?( Declare in value... | past_12_months | OLD LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT | 3425 | 3313 |
| m9a_q77 | Value of gift | What was the value of any gifts (money, food, services) made to the dental staff during the past 12months ? | past_12_months | OLD LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>79) | 3425 | 28 |
| m9a_q79 | Amount paid for medicine | How much did you pay, either in money or in kind, for all medicines prescribed by the dentist, during the last 12 months? | past_12_months | OLD LEKS |  | 3425 | 232 |
| m9a_q80 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_12_months | OLD LEKS |  | 3425 | 259 |
| m9a_q81 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport? | past_12_months | OLD LEKS |  | 3425 | 731 |

## Access And Barrier Rows

| raw_variable | raw_label | question_text | value_code_evidence | skip_or_instruction_note | raw_nonmissing_rows | semantic_evidence_status |
|---|---|---|---|---|---|---|
| m9b_q01 | Difficulty to pay for health | During the last 12 months, finding the money to pay for health care for the members of your family has been ? | VERY DIFFICULT=1; DIFFICULT=2; NOT DIFFICULT=3; NO-ONE HAS NEEDED ANY HEALTH CARE=4 | >>3; >>7 | 3840 | questionnaire_confirms_access_question_but_skip_pattern_not_ready |
| m9b_q03 | Times HH Member has been ill but delayed seeking help | In the past 12 months, how many times has someone in your household been ill but you delayed seeking help (or did not seek help at all)? | NONE=1; ONCE=2; TWICE=3; THREE TIMES=4; FOUR TIMES OR MORE=5 | >>5 | 3463 | questionnaire_confirms_access_question_but_skip_pattern_not_ready |
| m9b_q04 | Reason for delaying help | What was the reason for delaying/not seeking help? | THOUGHT THEY WOULD GET BETTER WITHOUT SEEKING HELP=1; THOUGHT THEY WOULD GET BETTER USING TRADITIONAL HERBS=2; THOUGHT THEY WOULD GET BET... |  | 268 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m9b_q05 | Times HH Member has been referred to hospital but not gone | In the past 12 months, how many times has someone in your household been referred to the hospital but not gone? | NONE=1; ONCE=2; TWICE=3; THREE TIMES=4; FOUR TIMES OR MORE=5 | >>7 | 3463 | questionnaire_confirms_access_question_but_skip_pattern_not_ready |
| m9b_q06 | Reason for not going to Hospital | What was the reason for not going to the hospital? | THOUGHT THAT THINGS WOULD GET BETTER=1; UNABLE TO AFFORD TREATMENT=2; UNABLE TO GET TO WHERE SERVICES WERE AVAILABLE=3; REFERRED TO ANOTH... |  | 182 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m9b_q07 | HH Member refused health services | Has anyone in your household ever been refused health services? | YES=1; NO=2 | >>9 | 3840 | questionnaire_confirms_access_question_but_skip_pattern_not_ready |
| m9b_q08 | Reason for refusal | What was the reason for this refusal? | COULD NOT AFFORD TO PAY=1; UNABLE TO GET TO WHERE SERVICES WERE AVAILABLE=2; SERVICES ONLY PROVIDED TO RESIDENTS OF PARTICULAR REGIONS=3;... |  | 143 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |

## Interpretation

- This audit resolves one narrow documentation question: the questionnaire text is readable and confirms important health-module semantics for ALB_2005.
- It does not resolve household interview timing, GPS/coordinate absence, partial district coverage, household-level OOP aggregation, missing/zero coding, or whether gift/transport components should enter each final outcome family.
- Four-week and twelve-month OOP items must remain separate until an outcome protocol explicitly defines comparable recall-period transformations.
- Access-barrier rows must remain denominator-blocked until raw skip paths establish which households/persons were eligible for each question.

## Machine-Readable Outputs

- `temp/alb2005_health_questionnaire_semantics_audit.csv`
- `result/alb2005_health_questionnaire_semantics_summary.csv`
