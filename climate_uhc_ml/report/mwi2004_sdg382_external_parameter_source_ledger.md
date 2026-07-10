# Malawi 2004 SDG 3.8.2 External Parameter Source Ledger

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact records official external parameter candidates for the Malawi
2004 SDG 3.8.2 discretionary-budget denominator. It captures World Bank WDI
PPP/CPI values and derives a candidate local-currency SPL bridge, but it keeps
the SDG gate closed because the annual CPI bridge has not yet been reconciled
with the survey's February/March 2004 real-currency base and the final
discretionary-budget denominator rule has not been accepted.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by the SDG 3.8.2 external parameter ledger. |
| source_capture_date | 2026-07-10 | Date these official parameter candidates were captured for the project ledger. |
| parameter_rows | 9 | External and derived parameter rows in the source ledger. |
| household_rows_with_internal_sdg382_inputs | 11280 | Internal Malawi raw rows inherited from the SDG parameter audit. |
| positive_oop_household_rows | 7765 | Households with positive OOP in the internal SDG frame. |
| wdi_ppp_private_consumption_2017 | 249.104888916 | Candidate private consumption PPP from World Bank WDI PA.NUS.PRVT.PP. |
| wdi_cpi_2004 | 55.6247640619 | Candidate CPI 2004 from World Bank WDI FP.CPI.TOTL. |
| wdi_cpi_2017 | 340.242124548 | Candidate CPI 2017 from World Bank WDI FP.CPI.TOTL. |
| candidate_cpi_ratio_2017_to_2004 | 6.11673829608 | Annual CPI bridge candidate; not accepted as final. |
| median_excluding_oop_2017_ppp_private_candidate | 1.03044759734 | Converted median using candidate annual CPI bridge and private consumption PPP. |
| candidate_relative_spl_2017_ppp | 1.66522379867 | Relative SPL candidate from the current official formula. |
| candidate_spl_2017_ppp | 2.15 | Candidate SPL after max with the 2017 IPL. |
| candidate_spl_daily_raw_2004_mwk | 87.5590037117 | Candidate SPL converted back to real 2004 MWK per person per day. |
| private_consumption_ppp_source_verified | 1 | World Bank API value captured, but concept still needs final acceptance. |
| annual_cpi_bridge_source_verified | 1 | World Bank CPI values captured, but annual bridge remains candidate. |
| external_parameter_bridge_accepted | 0 | PPP/CPI bridge is not accepted for final SDG 3.8.2 classification. |
| sdg382_ready | 0 | External parameter source ledger does not open the SDG 3.8.2 gate. |
| data_write_gate_status | closed | This artifact writes no promoted household-level data. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Source Ledger

| parameter | value | source | acceptance_status | remaining_blocker |
| --- | --- | --- | --- | --- |
| wdi_ppp_private_consumption_2017 | 249.104888916 | World Bank WDI indicator PA.NUS.PRVT.PP | candidate_preferred_not_final | Confirm this is the correct PPP concept for the official SDG 3.8.2 household consumption/income denominator. |
| wdi_ppp_gdp_2017_backup | 262.308654785 | World Bank WDI indicator PA.NUS.PPP | backup_not_selected | GDP PPP is kept only as a contrast; private consumption PPP is the preferred candidate for household welfare. |
| wdi_cpi_2004 | 55.6247640619 | World Bank WDI indicator FP.CPI.TOTL | candidate_not_final | Annual CPI 2004 may not exactly match the survey's February/March 2004 real-currency base. |
| wdi_cpi_2017 | 340.242124548 | World Bank WDI indicator FP.CPI.TOTL | candidate_not_final | Annual CPI bridge still needs reconciliation with the survey deflator and real-currency base. |
| candidate_cpi_ratio_2017_to_2004 | 6.11673829608 | derived from WDI FP.CPI.TOTL 2017 / 2004 | candidate_not_final | Use only as a candidate bridge until monthly/base-period consistency is checked. |
| official_ipl_2017_ppp | 2.15 | UNSD SDG 3.8.2 metadata | official_formula_input | Formula input is official, but Malawi local-currency conversion is not final. |
| candidate_relative_spl_2017_ppp | 1.66522379867 | 1.15 + 0.50 * median consumption/income excluding OOP | candidate_not_final | Median is converted with the candidate annual CPI bridge; final SPL requires accepted PPP/CPI policy. |
| candidate_spl_2017_ppp | 2.15 | max(2.15, candidate relative SPL) | candidate_not_final | Local-currency SPL remains candidate because the CPI/base-period bridge is not accepted. |
| candidate_spl_daily_raw_2004_mwk | 87.5590037117 | candidate_spl_2017_ppp * PPP private 2017 / CPI ratio | candidate_not_final | Do not use for final SDG 3.8.2 classification until the bridge policy and denominator rule are accepted. |

## Gate Decision

The ledger narrows the SDG 3.8.2 blocker from missing external parameters to a
specific unresolved bridge: World Bank 2017 private-consumption PPP and annual
CPI values are captured, but the annual CPI 2004 value is not enough by itself
to accept the survey's February/March 2004 real-currency base. Therefore
`sdg382_ready` remains `0`, `data_write_gate_status` remains `closed`, and
`modeling_gate_status` remains `blocked`.
