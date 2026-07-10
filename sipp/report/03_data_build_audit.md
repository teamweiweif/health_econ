      # Data Build Audit

      ## Input

      - Raw local SIPP directory: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp\temp\raw_downloads\census_sipp`
      - Metadata JSON: `D:\GlobalHealthPolicy Dropbox\Fan Bowei\nh_staffing\sipp\temp\source_metadata\sipp_2018_2024_raw_variable_metadata.enriched.compact.json`
      - Ingested format: Census pipe-delimited primary CSV files inside zip archives.

      ## Output

      - `data/analysis_ready/sipp_2018_2024_person_month_panel.parquet`
      - Yearly selected extracts in `temp/scratch/sipp_YYYY_selected.parquet`
      - Audit tables in `data/sample_audits/`

      ## File-Year Mapping

      SIPP file year is mapped to reference year as `file_year - 1`, consistent with the 2024 SIPP page stating that 2024 covers January-December 2023.

      ## Counts

       file_year  reference_year   rows  unique_persons_seen  duplicate_ssuid_pnum_monthcode_within_file  selected_variable_count                            parquet_path                                               raw_zip_path  raw_zip_bytes
2018            2017 763186                63915                                           0                       86 temp\scratch\sipp_2018_selected.parquet temp\raw_downloads\census_sipp\2018\primary\pu2018_csv.zip      164090517
2019            2018 593604                50212                                           0                       86 temp\scratch\sipp_2019_selected.parquet temp\raw_downloads\census_sipp\2019\primary\pu2019_csv.zip      135068548
2020            2019 622339                52572                                           0                       86 temp\scratch\sipp_2020_selected.parquet temp\raw_downloads\census_sipp\2020\primary\pu2020_csv.zip      139336635
2021            2020 670678                56872                                           0                       87 temp\scratch\sipp_2021_selected.parquet temp\raw_downloads\census_sipp\2021\primary\pu2021_csv.zip      157173933
2022            2021 487736                41070                                           0                       89 temp\scratch\sipp_2022_selected.parquet temp\raw_downloads\census_sipp\2022\primary\pu2022_csv.zip      116681072
2023            2022 476744                40263                                           0                       89 temp\scratch\sipp_2023_selected.parquet temp\raw_downloads\census_sipp\2023\primary\pu2023_csv.zip      109036604
2024            2023 437168                36915                                           0                       89 temp\scratch\sipp_2024_selected.parquet temp\raw_downloads\census_sipp\2024\primary\pu2024_csv.zip      102122301

      ## Key Integrity Notes

      - `SSUID + PNUM + MONTHCODE` is checked within each file year.
      - The final technical row key includes `file_year` because the same `SSUID + PNUM + MONTHCODE` can recur across annual SIPP waves.
      - Replicate and longitudinal weights are noted by Census but not fully populated locally; this run uses `WPFINWGT` and reports unweighted robustness.
