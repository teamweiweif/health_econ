# ARPA 400% FPL Raw-Data Quality Sensitivity

> The invalid `TSSSAMT` fallback was removed from all 35 matching idea-screen source files on 2026-07-16. This memo intentionally retains the old-code scenario as an audit comparator; the preferred scenario uses positive official `WPFINWGT` plus the health correction.

## Scope

This is a data-quality sensitivity for the existing local-linear difference-in-discontinuities screen. It is not a final survey-design analysis because it still uses person-clustered standard errors rather than Census Fay-BRR replicate inference.

## Scenarios

1. `original_screen_code`: reproduces the existing script, including its invalid `TSSSAMT`/unit-weight fallback.
2. `official_positive_wpfinwgt_only`: retains only positive official `WPFINWGT` values.
3. `official_positive_wpfinwgt_plus_health_usernote_correction`: also applies the Census monthly-health user-note patch for affected 2018-2023 files.

## Main Uninsured Result

- Original: coef=-0.026256, person-cluster SE=0.014275, t=-1.839, N=217,096.
- Corrected: coef=-0.027105, person-cluster SE=0.014294, t=-1.896, N=216,857.
- Coefficient change (corrected minus original): -0.000849.

## Outcome Comparison

- `uninsured` original: coef=-0.026256, person-cluster SE=0.014275, t=-1.839, N=217,096; corrected: coef=-0.027105, person-cluster SE=0.014294, t=-1.896, N=216,857.
- `any_coverage` original: coef=0.026256, person-cluster SE=0.014275, t=1.839, N=217,096; corrected: coef=0.027105, person-cluster SE=0.014294, t=1.896, N=216,857.
- `private` original: coef=0.023719, person-cluster SE=0.017061, t=1.390, N=217,096; corrected: coef=0.023754, person-cluster SE=0.017064, t=1.392, N=216,857.
- `public` original: coef=0.008150, person-cluster SE=0.013185, t=0.618, N=217,096; corrected: coef=0.006599, person-cluster SE=0.013046, t=0.506, N=216,857.
- `medicaid` original: coef=0.003273, person-cluster SE=0.011724, t=0.279, N=217,096; corrected: coef=0.002034, person-cluster SE=0.011557, t=0.176, N=216,857.

## Interpretation Boundary

The correction follows the official begin/end-month logic and uses `EPR1MTH/EPR2MTH` as the private-plan monthly indicators. The Census web table prints `EHEMPLY{1:2}=1`, but that conflicts with the official data dictionary, observed raw `RPRIMTH`, and the note's own affected-record range. That documentation inconsistency remains an open issue and is not concealed by this sensitivity.

The Marketplace flag is also not an insurance-type variable: Census states that private, Medicaid, and other coverage can all be reported as Marketplace coverage. It must not be interpreted as clean nongroup Marketplace enrollment without additional source logic.

## Outputs

- `result\data_audit\arpa400_health_weight_data_quality_sensitivity.csv`
- `result\data_audit\arpa400_health_correction_patch_support.csv`
- `data\analysis_ready\sipp_2018_2023_health_insurance_official_usernote_correction_patch.parquet`
