# Pandemic UI Person-FE Event Study Fast Check

## Verdict

`LOW-POWER-BUT-MECHANISM-COHERENT`

This strengthens the UI early-termination screen by adding individual fixed effects and month
fixed effects. May 2021 is the reference month. February-April are pre leads, June is transition,
and July-August are post months.

## Primary UC At-Risk Summary

| outcome | pre_lead_mean_coef | transition_june_coef | post_mean_coef | max_abs_pre_lead_t | persons | early_persons |
|---|---|---|---|---|---|---|
| earnings_positive | 0.0145 | 0.0496 | 0.0564 | 0.9894 | 624 | 183 |
| employed_any_week | 0.0166 | 0.0495 | 0.0630 | 1.0084 | 624 | 183 |
| medicaid | -0.0119 | -0.0050 | -0.0073 | 1.6510 | 624 | 183 |
| oop_any | 0.0000 | 0.0000 | 0.0000 | nan | 624 | 183 |
| snap | 0.0090 | -0.0111 | -0.0154 | 0.8104 | 624 | 183 |
| uc_any | -0.0184 | -0.0336 | -0.1068 | 0.9760 | 624 | 183 |
| uninsured | 0.0274 | -0.0056 | 0.0035 | 2.3015 | 624 | 183 |

## Interpretation

- This is a better design check than the earlier pooled DiD because it compares each person to
  themselves within 2021.
- The primary at-risk sample remains small: roughly 624 UC-recipient prime-age adults, with about
  183 in early-exit states.
- If pre leads are quiet and post signs remain coherent, this is a valid backup idea, but still
  not a top-field main paper unless the insurance/safety-net spillovers are much stronger than the
  employment literature's already-known result.

## Outputs

- `result/idea_scan/pandemic_ui_person_fe_event_estimates.csv`
- `result/idea_scan/pandemic_ui_person_fe_event_summary.csv`
