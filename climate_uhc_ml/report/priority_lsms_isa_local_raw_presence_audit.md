# Priority LSMS/ISA Local Raw Presence Audit

Status: local raw-file presence audit for all 19 promoted-registry rows plus
raw-like files found outside the current promotion registry.

It does not download, copy, extract, write promoted `data/`, or run models.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| local_raw_presence_registry_rows | 19 | Promotion registry rows audited for local raw-like files. |
| local_raw_presence_registry_raw_present_rows | 1 | Registry rows with at least one local raw-like file. |
| local_raw_presence_registry_raw_absent_rows | 18 | Registry rows with no local raw-like files in their target folder. |
| local_raw_presence_minimum_batch_raw_absent_rows | 10 | Minimum-batch rows still lacking local raw-like files. |
| local_raw_presence_nonregistry_raw_file_rows | 4 | Raw-like files under temp/raw_downloads that are outside the current promotion registry. |
| local_raw_presence_diagnostic_albania_raw_file_rows | 4 | Albania raw-like files retained as diagnostic-only, not a main empirical sample. |
| local_raw_presence_promoted_rows | 1 | Registry rows currently promoted analysis-ready. |
| data_write_gate_status | blocked_no_data_write | This audit writes only result/report artifacts and does not promote datasets. |
| modeling_gate_status | blocked | No predictive, reduced-form, causal ML, or policy learning is opened. |

## Registry Rows

| country | wave | idno | minimum_batch_row | analysis_ready_status | raw_like_file_count | local_raw_presence_status |
| --- | --- | --- | --- | --- | --- | --- |
| Ethiopia | 2021-2022 | ETH_2021_ESPS-W5_v02_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Ethiopia | 2018-2019 | ETH_2018_ESS_v04_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Malawi | 2004-2005 | MWI_2004_IHS-II_v01_M | 0 | promoted_analysis_ready | 1 | raw_present_promoted |
| Nigeria | 2012-2013 | NGA_2012_GHSP-W2_v02_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Nigeria | 2015-2016 | NGA_2015_GHSP-W3_v02_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Nigeria | 2010-2011 | NGA_2010_GHSP-W1_v03_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Tanzania | 2008-2009 | TZA_2008_NPS-R1_v03_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Tanzania | 2010-2011 | TZA_2010_NPS-R2_v03_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Tanzania | 2012-2013 | TZA_2012_NPS-R3_v01_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Uganda | 2019-2020 | UGA_2019_UNPS_v03_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Jamaica | 1997 | JAM_1997_SLC_v01_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Kyrgyz Republic | 1993 | KGZ_1993_KMPS_v01_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Nepal | 2010-2011 | NPL_2010_LSS-III_v01_M | 1 | not_promoted | 0 | raw_absent_blocks_promotion |
| Malawi | 2019-2020 | MWI_2019_IHS-V_v06_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Malawi | 2016-2017 | MWI_2016_IHS-IV_v04_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Malawi | 2010-2011 | MWI_2010_IHS-III_v01_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Uganda | 2011-2012 | UGA_2011_UNPS_v02_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Uganda | 2018-2019 | UGA_2018_UNPS_v02_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |
| Uganda | 2015-2016 | UGA_2015_UNPS_v02_M | 0 | not_promoted | 0 | raw_absent_blocks_promotion |

## Nonregistry Raw-Like Files

| folder_id | relative_path | extension | bytes | nonregistry_raw_status |
| --- | --- | --- | --- | --- |
| ALB_2002_LSMS_v01_M | temp/raw_downloads/ALB_2002_LSMS_v01_M/lsms2002en.rar | .rar | 4893622 | diagnostic_nonregistry_raw_not_main_sample |
| ALB_2005_LSMS_v01_M | temp/raw_downloads/ALB_2005_LSMS_v01_M/lsms2005en.rar | .rar | 4875038 | diagnostic_nonregistry_raw_not_main_sample |
| ALB_2008_LSMS_v01_M | temp/raw_downloads/ALB_2008_LSMS_v01_M/lsms_2008_eng.rar | .rar | 3484292 | diagnostic_nonregistry_raw_not_main_sample |
| ALB_2012_LSMS_v01_M_v01_A_PUF | temp/raw_downloads/ALB_2012_LSMS_v01_M_v01_A_PUF/lsms_2012_eng.rar | .rar | 6142153 | diagnostic_nonregistry_raw_not_main_sample |

## Use

Treat rows with `raw_absent_blocks_promotion` as acquisition blockers. Treat
Albania rows in the nonregistry table as diagnostic-only under the active
dataset-promotion objective. A registry row can only move toward `data/` after
the complete official package passes receipt, schema, value-profile,
semantics, timing/geography, and climate-linkage gates.
