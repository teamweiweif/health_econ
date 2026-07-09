# ALB_2002 Health Questionnaire Semantics Audit

Status: fail-closed questionnaire and raw skip-path audit. This report reads the ALB_2002 health questionnaire workbook and SPSS health modules to document payment units, recall periods, payment-scope exclusions, gift rows, access-barrier value codes, and skip/missing evidence. It does not write `data/`, does not construct outcomes, and does not promote any row to harmonization, SDG 3.8.2, or climate linkage.

## Bottom Line

- The ALB_2002 health questionnaire is readable in the current Python environment.
- Health payment items are recorded in `NEW LEKS`, not old lek, and are split across past-four-week outpatient/self-medication contexts and past-12-month hospital/dentist contexts.
- Provider total-payment questions explicitly exclude gifts, medicines, laboratory work, and transport, while gift values are separate variables. OOP aggregation therefore needs a documented inclusion policy.
- Raw skip paths show no positive payment values when visit/stay/dentist triggers are negative, but a few skipped downstream fields are nonmissing zeros, so zero/missing semantics still require review.
- Health module B confirms cost, distance, supply/availability, refusal, medicine-discount, and health-financing/coping codes, but denominator rules remain blocked.
- Recipe-ready, outcome-ready, SDG 3.8.2-ready, and climate-linkage-ready rows from this audit: 0.
- Current decision: `blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready`.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_health_questionnaire_semantics_rows | 65 | Rows in the ALB_2002 health questionnaire and skip-path audit. |
| alb2002_health_questionnaire_questionnaire_rows | 53 | Questionnaire-backed health variable rows. |
| alb2002_health_questionnaire_oop_item_rows | 25 | Questionnaire-backed OOP payment item rows excluding gift-value rows. |
| alb2002_health_questionnaire_gift_item_rows | 6 | Gift/payment-scope rows that require inclusion-policy review. |
| alb2002_health_questionnaire_new_lek_unit_rows | 31 | Rows where the questionnaire explicitly records new-lek units. |
| alb2002_health_questionnaire_four_week_oop_rows | 17 | OOP item rows with past-four-week recall. |
| alb2002_health_questionnaire_twelve_month_oop_rows | 8 | OOP item rows with past-12-month recall. |
| alb2002_health_questionnaire_exclusion_note_rows | 6 | Questionnaire rows with explicit exclusion notes for gifts, medicines, laboratory, or transport. |
| alb2002_health_questionnaire_zero_instruction_rows | 10 | Questionnaire rows with explicit zero-payment instructions. |
| alb2002_health_questionnaire_access_rows | 8 | Access, affordability, delayed-care, referral, refusal, or medicine-discount rows. |
| alb2002_health_questionnaire_cost_barrier_rows | 5 | Access rows whose questionnaire options include cost or affordability barriers. |
| alb2002_health_questionnaire_distance_barrier_rows | 2 | Access rows whose questionnaire options include distance barriers. |
| alb2002_health_questionnaire_supply_barrier_rows | 3 | Access rows whose questionnaire options include availability, service-region, referral, document, or shortage barriers. |
| alb2002_health_questionnaire_payment_skip_rows | 7 | Person-level OOP payment skip-path rows audited. |
| alb2002_health_questionnaire_payment_nonmissing_when_not_triggered_rows | 11 | Payment downstream rows nonmissing when the visit/drug/stay/dentist trigger is negative. |
| alb2002_health_questionnaire_payment_positive_when_not_triggered_rows | 0 | Payment downstream rows positive when the trigger is negative. |
| alb2002_health_questionnaire_payment_zero_or_missing_when_triggered_rows | 274 | Triggered payment rows with no positive downstream payment; requires zero/missing-code review. |
| alb2002_health_questionnaire_conditional_skip_rows | 5 | Household access/coping conditional skip rows audited. |
| alb2002_health_questionnaire_conditional_nonmissing_when_not_triggered_rows | 0 | Conditional downstream rows nonmissing when the trigger condition is false. |
| alb2002_health_questionnaire_conditional_missing_when_triggered_rows | 0 | Conditional downstream rows missing when the trigger condition is true. |
| alb2002_health_questionnaire_outcome_semantics_ready_observed | 0 | Outcome-ready rows observed in the upstream raw outcome-semantics audit. |
| alb2002_health_questionnaire_core_recipe_ready_observed | 0 | Recipe-ready rows observed in the upstream household-core audit. |
| alb2002_health_questionnaire_boundary_climate_ready_observed | 0 | Climate-linkage-ready rows observed in the GADM boundary lead audit. |
| alb2002_health_questionnaire_recipe_ready_rows | 0 | Rows promoted to a harmonization recipe by this audit; intentionally zero. |
| alb2002_health_questionnaire_outcome_ready_rows | 0 | Rows promoted to final outcome construction by this audit; intentionally zero. |
| alb2002_health_questionnaire_sdg382_ready_rows | 0 | Rows promoted to SDG 3.8.2 construction by this audit; intentionally zero. |
| alb2002_health_questionnaire_climate_linkage_ready_rows | 0 | Rows promoted to climate linkage by this audit; intentionally zero. |
| alb2002_health_questionnaire_current_decision | blocked_alb2002_questionnaire_semantics_seen_but_outcome_not_ready | Current fail-closed decision for ALB_2002 questionnaire-backed health semantics. |

## Concept Counts

| Concept | Count |
|---|---:|
| oop_health_expenditure_item | 25 |
| care_visit_selection_or_denominator | 8 |
| oop_payment_skip_path | 7 |
| gift_payment_scope | 6 |
| care_or_barrier | 6 |
| coping_or_health_financing | 5 |
| access_or_coping_skip_path | 5 |
| access_affordability | 1 |
| medicine_discount_coverage | 1 |
| medicine_discount_access | 1 |

## Semantic Status Counts

| Semantic status | Count |
|---|---:|
| questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready | 19 |
| questionnaire_confirms_visit_selection_skip_path_but_denominator_not_ready | 8 |
| questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport | 6 |
| questionnaire_confirms_gift_value_item_scope_policy_required | 6 |
| questionnaire_confirms_access_barrier_codes_but_denominator_not_ready | 5 |
| questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready | 5 |
| raw_skip_path_consistent_no_downstream_values_when_not_triggered | 5 |
| raw_conditional_skip_path_consistent | 5 |
| questionnaire_context_seen_not_recipe_ready | 3 |
| raw_skip_path_positive_values_absent_when_not_triggered_but_zero_nonmissing_review_required | 2 |
| questionnaire_confirms_medicine_discount_entitlement_but_not_failure_outcome | 1 |

## OOP And Gift Questionnaire Rows

| raw_variable | raw_label | question_text | recall_period | unit_or_value_note | skip_or_instruction_note | raw_nonmissing_rows | raw_positive_numeric_rows | semantic_evidence_status |
|---|---|---|---|---|---|---|---|---|
| m5a_q14 | Amount paid for all costs associated with outpatent visits | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to the public ambulatory during the past 4 ... | past_4_weeks | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; IF NO GIFTS PAID WRITE "0", THEN (>>17) | 2120 | 861 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q18 | Amount paid for medicines | How much did you pay for these medicines? | past_4_weeks | NEW LEKS |  | 2019 | 1948 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q20 | Amount paid for lab work | How much did you pay, either in money or in kind for laboratory work (e.g. X-rays, blood tests, ?)? | past_4_weeks | NEW LEKS |  | 2125 | 620 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q21 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport (related with visits)? | past_4_weeks | NEW LEKS |  | 2123 | 648 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q24 | Amount paid for all costs associated | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to a private doctor during the past 4 weeks? | past_4_weeks | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>27) | 219 | 184 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q27 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | NEW LEKS |  | 219 | 169 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q28 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | NEW LEKS |  | 219 | 98 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q29 | Amount paid for transport | How much did you pay, either in money or in kind, for transport? | past_4_weeks | NEW LEKS |  | 219 | 89 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q32 | Amount paid | How much did you pay, either in money or in-kind, for all costs associated with these outpatient visits to the medical provider during the past 4 w... | past_4_weeks | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>35) | 375 | 137 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q35 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | NEW LEKS |  | 375 | 138 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q36 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | NEW LEKS |  | 375 | 42 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q37 | Amount paid for transport | How much did you pay, either in money or in kind for transport? | past_4_weeks | NEW LEKS |  | 375 | 49 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q40 | Amount paid for all costs associated | How much did you pay, either in money or in kind, for all costs associated with these outpatient visits to a popular doctor/alternative medicine pr... | past_4_weeks | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>43) | 53 | 45 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q43 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed during these visits, even if purchased elsewhere? | past_4_weeks | NEW LEKS |  | 53 | 13 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q44 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_4_weeks | NEW LEKS |  | 53 | 3 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q45 | Amount paid for transport | How much did you pay, either in money or in kind for transport? | past_4_weeks | NEW LEKS |  | 53 | 31 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q47 | Amount paid for all drugs in past 4 weeks | How much did you pay for all drugs purchased on your own in the past 4 weeks? | past_4_weeks | NEW LEKS |  | 2445 | 2439 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q53 | Amount paid for all costs related to hospital | How much did you pay, either in money or in kind, for all costs related to these hospital stays during the last 12 months? | past_12_months | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>56) | 707 | 316 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q56 | Amount paid for medicines | How much did you pay, either in money or in-kind, for all medicines prescribed during these hospital stays, even if purchased and consumed elsewhere? | past_12_months | NEW LEKS |  | 710 | 447 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q57 | Amount paid for lab work | How much did you pay, either in money or in kind for laboratory work? | past_12_months | NEW LEKS |  | 707 | 362 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q58 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport? | past_12_months | NEW LEKS |  | 707 | 465 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q61 | Amount paid for all costs related to dentist visits | How much did you pay, either in money or in-kind, for all costs for these visits to a dentist during the last 12 months? | past_12_months | NEW LEKS | EXCLUDE GIFTS, EXCLUDE MEDICINES, EXCLUDE LABORATORY, EXCLUDE TRANSPORT; PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>64) | 3352 | 3193 | questionnaire_confirms_provider_payment_excludes_gifts_medicines_lab_transport |
| m5a_q64 | Amount paid for medicines | How much did you pay, either in money or in kind, for all medicines prescribed by the dentist, during the last 12 months? | past_12_months | NEW LEKS |  | 3352 | 377 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q65 | Amount paid for lab work | How much did you pay, either in money or in kind for the laboratory? | past_12_months | NEW LEKS |  | 3352 | 284 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q66 | Amount paid for transport | How much did you pay, either in money or in-kind, for transport? | past_12_months | NEW LEKS |  | 3352 | 1018 | questionnaire_confirms_new_lek_payment_item_but_recall_scope_not_ready |
| m5a_q15 | Value of gifts made to medical staff | What was the value of any gifts ( money, food, services) made to the medical staff of public ambulatory during the past 4 weeks ? | past_4_weeks | NEW LEKS | IF NO GIFTS PAID WRITE "0", THEN (>>17) | 2120 | 611 | questionnaire_confirms_gift_value_item_scope_policy_required |
| m5a_q25 | Value of gifts | What was the value of any gifts ( money, food, services) made to the private doctor and staff during the past 4 weeks ? | past_4_weeks | NEW LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>27) | 219 | 22 | questionnaire_confirms_gift_value_item_scope_policy_required |
| m5a_q33 | Value of gifts | What was the value of any gifts ( money, food, services) made to the medical provider during the past 4 weeks ? | past_4_weeks | NEW LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>35) | 375 | 90 | questionnaire_confirms_gift_value_item_scope_policy_required |
| m5a_q41 | Value of gifts | What was the value of any gifts ( money, food, services) made to the popular doctor/ alternative medicine provider during the past 4 weeks ? | past_4_weeks | NEW LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>43) | 53 | 11 | questionnaire_confirms_gift_value_item_scope_policy_required |
| m5a_q54 | Value of gifts | What was the value of any gifts ( money, food, services) made to the hospital staff during the past 12 months ? | past_12_months | NEW LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>56) | 707 | 404 | questionnaire_confirms_gift_value_item_scope_policy_required |
| m5a_q62 | Value of gifts | What was the value of any gifts (money, food, services) made to the dental staff during the past 12months ? | past_12_months | NEW LEKS | PLEASE REPORT ZERO IF NO PAYMENT WAS MADE, THEN (>>64) | 3352 | 31 | questionnaire_confirms_gift_value_item_scope_policy_required |

## Access And Barrier Rows

| raw_variable | raw_label | question_text | value_code_evidence | skip_or_instruction_note | raw_nonmissing_rows | semantic_evidence_status |
|---|---|---|---|---|---|---|
| m5b_q01 | Finantial situation for paying for family health care | During the last 12 months, finding the money to pay for health care for the members of your family has been ? | VERY DIFFICULT=1; DIFFICULT=2; NOT DIFFICULT=3; NO-ONE HAS NEEDED ANY HEALTH CARE=4 | (>>3); (>>7) | 3599 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m5b_q02_ | Method to raise money to pay for family member's health care | Over the last year has it been necessary to do any of the following in order to raise money to pay for health care for members of your family? (CHE... |  |  | 1623 | questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready |
| m5b_q021 | Method to raise money to pay for family member's health care | Over the last year has it been necessary to do any of the following in order to raise money to pay for health care for members of your family? (CHE... |  |  | 1623 | questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready |
| m5b_q022 | Method to raise money to pay for family member's health care | Over the last year has it been necessary to do any of the following in order to raise money to pay for health care for members of your family? (CHE... |  |  | 1623 | questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready |
| m5b_q023 | Method to raise money to pay for family member's health care | Over the last year has it been necessary to do any of the following in order to raise money to pay for health care for members of your family? (CHE... |  |  | 1623 | questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready |
| m5b_q024 | Method to raise money to pay for family member's health care | Over the last year has it been necessary to do any of the following in order to raise money to pay for health care for members of your family? (CHE... |  |  | 1623 | questionnaire_confirms_health_financing_coping_item_but_denominator_not_ready |
| m5b_q03 | Times HH member has been ill but delayed seekikng help in pa | In the past 12 months, how many times has someone in your household been ill but you delayed seeking help (or did not seek help at all)? | NONE=1; ONCE=2; TWICE=3; THREE TIMES=4; FOUR TIMES OR MORE=5 | >>5 | 3247 | questionnaire_context_seen_not_recipe_ready |
| m5b_q04 | Reason for not seeking help | What was the reason for delaying/not seeking help? | THOUGHT THEY WOULD GET BETTER WITHOUT DOING ANYTHING=1; THOUGHT THEY WOULD GET BETTER USING TRADITIONAL HERBS=2; THOUGHT THEY WOULD GET BETTER USIN... |  | 144 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m5b_q05 | Times referred to hospital but did not go in past 12 months | In the past 12 months, how many times has someone in your household been referred to the hospital but not gone? | NONE=1; ONCE=2; TWICE=3; THREE TIMES=4; FOUR TIMES OR MORE=5 | >>7 | 3247 | questionnaire_context_seen_not_recipe_ready |
| m5b_q06 | Reason for not going to hospital | What was the reason for not going to the hospital? | THOUGHT THAT THINGS WOULD GET BETTER=1; UNABLE TO AFFORD TREATMENT=2; UNABLE TO GET TO WHERE SERVICES WERE AVAILABLE=3; REFERRED TO ANOTHER HOSPITA... |  | 161 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m5b_q07 | Family member ever been refused health services | Has anyone in your household ever been refused health services? | YES=1; NO=2 | (>>9) | 3599 | questionnaire_context_seen_not_recipe_ready |
| m5b_q08 | Reason | What was the reason for this refusal? | COULD NOT AFFORD TO PAY=1; UNABLE TO GET TO WHERE SERVICES WERE AVAILABLE=2; SERVICES ONLY PROVIDED TO RESIDENTS OF PARTICULAR REGIONS=3; UNABLE TO... |  | 68 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |
| m5b_q09 | Family member entilteled to purchase medicnes at discounts | Are any members of your family entitled to purchase medicines at a discount? | YES=1; NO=2 | (>>NEXT MODULE) | 3599 | questionnaire_confirms_medicine_discount_entitlement_but_not_failure_outcome |
| m5b_q10 | Always able to exercise this right when medicines are needed | Have they always been able to exercise this right when medicines are needed? And if not, why not? | YES, ALWAYS ABLE TO EXERCISE THIS RIGHT=1; NO, BECAUSE THEY CANNOT GET THE DOCUMENTS NEEDED TO EXERCISE THIS RIGHT DUE TO THE BUREAUCRATIC PROBLEMS... |  | 2044 | questionnaire_confirms_access_barrier_codes_but_denominator_not_ready |

## Skip-Path Rows

| audit_family | question_context | trigger_variable | downstream_variables | trigger_positive_rows | trigger_negative_rows | downstream_any_nonmissing_when_not_triggered_rows | downstream_any_positive_when_not_triggered_rows | downstream_zero_or_missing_when_triggered_rows | semantic_evidence_status |
|---|---|---|---|---|---|---|---|---|---|
| payment_skip_path | public_ambulatory_4w | m5a_q12 | m5a_q14;m5a_q15;m5a_q18;m5a_q20;m5a_q21 | 2120 | 13439 | 8 | 0 | 71 | raw_skip_path_positive_values_absent_when_not_triggered_but_zero_nonmissing_review_required |
| payment_skip_path | private_doctor_4w | m5a_q22 | m5a_q24;m5a_q25;m5a_q27;m5a_q28;m5a_q29 | 219 | 15340 | 0 | 0 | 5 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| payment_skip_path | nurse_paramedic_midwife_4w | m5a_q30 | m5a_q32;m5a_q33;m5a_q35;m5a_q36;m5a_q37 | 375 | 15184 | 0 | 0 | 100 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| payment_skip_path | popular_doctor_4w | m5a_q38 | m5a_q40;m5a_q41;m5a_q43;m5a_q44;m5a_q45 | 53 | 15506 | 0 | 0 | 2 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| payment_skip_path | own_drugs_4w | m5a_q46 | m5a_q47 | 2445 | 13114 | 0 | 0 | 6 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| payment_skip_path | hospital_stay_12m | m5a_q48 | m5a_q53;m5a_q54;m5a_q56;m5a_q57;m5a_q58 | 707 | 14852 | 3 | 0 | 31 | raw_skip_path_positive_values_absent_when_not_triggered_but_zero_nonmissing_review_required |
| payment_skip_path | dentist_12m | m5a_q59 | m5a_q61;m5a_q62;m5a_q64;m5a_q65;m5a_q66 | 3352 | 12207 | 0 | 0 | 59 | raw_skip_path_consistent_no_downstream_values_when_not_triggered |
| conditional_skip_path | raise_money_for_health_care_methods | m5b_q01 | m5b_q02_;m5b_q021;m5b_q022;m5b_q023;m5b_q024 | 1623 | 1976 | 0 | 0 |  | raw_conditional_skip_path_consistent |
| conditional_skip_path | delayed_or_no_help_reason | m5b_q03 | m5b_q04 | 144 | 3103 | 0 | 0 |  | raw_conditional_skip_path_consistent |
| conditional_skip_path | hospital_referral_not_gone_reason | m5b_q05 | m5b_q06 | 161 | 3086 | 0 | 0 |  | raw_conditional_skip_path_consistent |
| conditional_skip_path | refused_health_services_reason | m5b_q07 | m5b_q08 | 68 | 3531 | 0 | 0 |  | raw_conditional_skip_path_consistent |
| conditional_skip_path | medicine_discount_access_reason | m5b_q09 | m5b_q10 | 2044 | 1555 | 0 | 0 |  | raw_conditional_skip_path_consistent |

## Interpretation

- This audit moves ALB_2002 beyond raw value labels by tying candidate OOP/access variables to the questionnaire text.
- It does not resolve final OOP aggregation, gift/payment-scope policy, annualization, total-consumption denominator period, SDG discretionary-budget inputs, or person-to-household aggregation.
- The access-barrier evidence is promising, but denominator definitions must distinguish need, care seeking, delayed care, referral, refusal, medicine entitlement, and no-one-needed-care responses.
- Climate linkage remains independently blocked by the unresolved district-boundary/GPS evidence.

## Machine-Readable Outputs

- `temp/alb2002_health_questionnaire_semantics_audit.csv`
- `result/alb2002_health_questionnaire_semantics_summary.csv`
