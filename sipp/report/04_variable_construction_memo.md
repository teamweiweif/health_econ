            # Variable Construction Memo

            ## Coverage Measures

            - `any_coverage_it`: `RHLTHMTH == 1`
            - `uninsured_it`: `RHLTHMTH == 2`
            - `medicaid_it`: primary, `EMDMTH == 1`
            - `medicaid_alt_rpubtype2_it`: sensitivity, `RPUBTYPE2 == 1`
            - `direct_purchase_or_marketplace_it`: `RPRITYPE2 == 1` or `RMARKTPLACE == 1`
            - `exchange_or_subsidized_private_it`: exchange/subsidy indicators from private and Medicaid exchange variables.

            Primary Medicaid agreement between `EMDMTH` and `RPUBTYPE2`: 0.9883

            ## Income Shocks

            The primary running variable is `TFINCPOV`, stored as a ratio where `1.38` equals 138% FPL. The main threshold is 1.38 and the main near-boundary window is 1.00-1.75 ratio units, equivalent to 100-175% FPL. Temporary cross-up events return below threshold within 1, 2, or 3 contiguous months.

            ## Core Counts

            rows                     4051455
medicaid_months           795459
medicaid_exits              4654
exit_to_uninsured           1612
temporary_cross_up_1m       3093
temporary_cross_up_2m       4768
temporary_cross_up_3m       6252

            ## Outputs

            - `data/analysis_ready/coverage_transition_panel.parquet`
            - `data/analysis_ready/exposure_temporary_crossing_panel.parquet`
            - `result/tables/coverage_transition_matrix_by_year.csv`
            - `result/tables/coverage_outcome_counts_by_year_regime.csv`
