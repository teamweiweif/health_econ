# Empirical Design Memo

## Primary Design

The primary design tests whether temporary cross-up events around the adult Medicaid expansion boundary translate into Medicaid exits, exit-to-uninsured, bridge coverage, and persistent uninsured gaps.

## Regime Logic

- Pre-PHE: January 2017 through February 2020.
- PHE continuous enrollment: March 2020 through March 2023.
- Early unwinding: April 2023 through December 2023.

CMS SHO-23-002 verifies that the continuous enrollment condition ended March 31, 2023 and that terminations after renewal could occur on or after April 1, 2023.

## Expansion Boundary

The main adult MAGI boundary is 138% FPL in expansion states. In SIPP `TFINCPOV`, this is stored as `1.38`, not `138`. Robustness checks use 1.00, 1.33, 1.38, and 1.50 ratio units and multiple bandwidths.

## Identification Standard

This is not assumed to be causal. The pipeline first checks support, transition counts, pre-period behavior, and robustness. Causal ML is prohibited unless conventional estimates pass the support and credibility screens.
