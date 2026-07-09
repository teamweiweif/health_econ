# Public External Raw Candidate Downloads

Status: direct public-link acquisition audit. This step downloads only screened external candidate links that resolve to raw/archive files and match an existing country-wave screening row. It does not bypass login, registration, data access agreements, or terms forms.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| public_external_candidate_rows | 4 | Matched public external raw candidate links. |
| public_external_downloaded_or_existing_rows | 4 | Public external raw archives downloaded or already present. |
| public_external_dataset_rows | 4 | Datasets with public external raw archives present. |
| public_external_failed_or_skipped_rows | 0 | Candidate links not downloaded. |
| public_external_downloaded_bytes | 19395105 | Total bytes of present public external raw archives. |

## Downloads

| idno | survey_name | wave | candidate_url | download_status | file_size_bytes | local_path |
|---|---|---|---|---|---|---|
| ALB_2002_LSMS_v01_M | Living Standards Measurement Survey 2002 (Wave 1 Panel) | 2002 | https://www.instat.gov.al/media/1544/lsms2002en.rar | already_exists | 4893622 | temp/raw_downloads/ALB_2002_LSMS_v01_M/lsms2002en.rar |
| ALB_2005_LSMS_v01_M | Living Standards Measurement Survey 2005 | 2005 | https://www.instat.gov.al/media/1545/lsms2005en.rar | already_exists | 4875038 | temp/raw_downloads/ALB_2005_LSMS_v01_M/lsms2005en.rar |
| ALB_2008_LSMS_v01_M | Living Standards Measurement Survey 2008 | 2008 | https://www.instat.gov.al/media/1546/lsms_2008_eng.rar | already_exists | 3484292 | temp/raw_downloads/ALB_2008_LSMS_v01_M/lsms_2008_eng.rar |
| ALB_2012_LSMS_v01_M_v01_A_PUF | Living Standards Measurement Survey 2012 | 2012 | https://www.instat.gov.al/media/1547/lsms_2012_eng.rar | already_exists | 6142153 | temp/raw_downloads/ALB_2012_LSMS_v01_M_v01_A_PUF/lsms_2012_eng.rar |

## Guardrails

- Downloaded archives are raw acquisition evidence only.
- RAR archives still require extraction before Stata/SPSS files can be schema-inspected.
- No harmonized dataset, outcomes, climate exposure, model, causal estimate, or policy simulation is justified by archive presence alone.

## Machine-Readable Outputs

- `temp/public_external_raw_candidate_downloads.csv`
- `result/public_external_raw_candidate_download_summary.csv`
