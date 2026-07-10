# Late Medicaid Expansion Robustness Checks

## Purpose

The first late-expansion screen found large Medicaid gains and uninsured declines around the
100-138% FPL eligibility band. Because Medicaid expansion is a saturated literature, this file
stress-tests whether the signal is one-state driven or visible before implementation.

## Checks

- Baseline narrow design: monthly FPL 100-250%, eligible 100-138%.
- Leave one late-expansion state out.
- Drop early 2019/2020 adopters.
- Drop 2021 PHE adopters.
- Drop 2023 adopters.
- Keep only Oklahoma and Missouri as 2021 PHE adopters against never-expansion states.
- Fake pre-period placebo: move implementation 12 months earlier and remove true post months.

## Medicaid / Uninsured Summary

| check | coef_medicaid | coef_uninsured | t_state_cluster_medicaid | t_state_cluster_uninsured |
|---|---|---|---|---|
| baseline | 0.0891 | -0.0735 | 3.0369 | -4.8030 |
| drop_2019_2020_adopters | 0.0813 | -0.0421 | 1.5115 | -2.4276 |
| drop_2021_phe_adopters | 0.0944 | -0.0816 | 3.0628 | -4.2518 |
| drop_2023_adopters | 0.0885 | -0.0765 | 2.9513 | -4.6963 |
| drop_Idaho | 0.0908 | -0.0714 | 2.8909 | -4.4810 |
| drop_Maine | 0.0898 | -0.0641 | 2.9690 | -5.1183 |
| drop_Missouri | 0.1077 | -0.0784 | 4.4446 | -4.8330 |
| drop_Nebraska | 0.0848 | -0.0797 | 2.7400 | -5.3819 |
| drop_North Carolina | 0.0882 | -0.0752 | 2.9510 | -4.6733 |
| drop_Oklahoma | 0.0755 | -0.0757 | 2.1866 | -4.3613 |
| drop_South Dakota | 0.0895 | -0.0748 | 3.0422 | -4.8513 |
| drop_Utah | 0.1011 | -0.0736 | 3.5671 | -4.3924 |
| drop_Virginia | 0.0625 | -0.0713 | 1.6885 | -3.2752 |
| fake_12m_pre_placebo | 0.0132 | -0.0535 | 0.2207 | -1.7701 |
| only_2021_phe_adopters_vs_never | 0.0716 | -0.0603 | 1.0658 | -4.8163 |

## Interpretation

The leave-one checks should preserve a positive Medicaid effect and negative uninsured effect if the
design is not dominated by a single treated state. The fake pre-period placebo should be much smaller
than the true effect; a large placebo would indicate anticipatory trends or treated-state pre-trend
differences that weaken causal interpretation.

## Artifacts

- `script/11_idea_scan/30_late_medicaid_expansion_robustness.py`
- `result/idea_scan/late_medicaid_expansion_robustness.csv`
- `result/idea_scan/late_medicaid_expansion_robustness_pivot.csv`
