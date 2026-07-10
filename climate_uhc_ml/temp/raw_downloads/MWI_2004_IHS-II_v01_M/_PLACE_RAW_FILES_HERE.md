# Raw Intake Folder: MWI_2004_IHS-II_v01_M

Dataset: Malawi - Second Integrated Household Survey 2004-2005 (2004-2005; MWI_2004_IHS-II_v01_M)

Access URL: https://microdata.worldbank.org/catalog/2307/get-microdata

Place the original downloaded raw archive(s), tabular file(s), and documentation for this dataset in this folder.

Rules:

- Keep original filenames and archives intact.
- Download the full available package where terms permit; do not cherry-pick only the modules listed below.
- Do not put raw files in `data/`.
- Do not redistribute raw microdata.
- After placing files here, run `powershell -ExecutionPolicy Bypass -File script/run_all.ps1` from the project root.

First modules to verify after download:

| File/module | Role | Categories | Example variables |
|---|---|---|---|
| `ihs2_ag` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `reside;hhwght;hhsize;Gbean;Gbean;Gburtob;Gburtob;Gcabbage;Gcabbage;Gcassava;Gcassava;Gcmaize` |
| `ihs2_household` | core_main_sample_module_candidate | consumption;demographics;geography;health_need_access;shocks;survey_design | `rexpnfd;rexp_cat07;add;dist;region;reside;strata;strata;type;V51;decile;ea` |
| `sec_r` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `sec_d` | core_main_sample_module_candidate | demographics;geography;health_expenditure;health_need_access;shocks;survey_design | `d16;d19;d04;d05a;d05aoth;d05b;d05both;d06a;d06b;d07a;d07b;d26` |
| `sec_o` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `mod_f` | core_main_sample_module_candidate | geography;health_need_access;shocks;survey_design | `cf9a;cf9b;dist;ta;ta;village;ea;cf1;cf11;cf12;cf12;cf13` |
| `sec_g` | core_main_sample_module_candidate | demographics;geography;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `sec_s` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `sec_ac` | core_main_sample_module_candidate | demographics;geography;health_need_access;survey_design | `ac08;ac09;ac09oth;ac10a;ac10aoth;ac10b;ac10both;ac11a;ac11b;add;dist;region` |
| `sec_ab` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `sec_p` | core_main_sample_module_candidate | demographics;geography;shocks;survey_design | `add;dist;region;reside;strata;strata;type;ea;hhid;hhwght;psu;strata` |
| `sec_q1` | core_main_sample_module_candidate | demographics;geography;health_need_access;shocks;survey_design | `q06g;q10a;q10aoth;q10b;q10both;add;dist;region;reside;strata;strata;type` |

Expected post-download checks:

1. `temp/raw_download_file_manifest.csv` should show raw tabular or archive files in this target folder.
2. `temp/raw_schema_inventory/raw_file_inventory.csv` should list inspected raw files after schema extraction.
3. `temp/raw_schema_inventory/raw_variable_catalog.csv` should list raw variables and labels.
4. `temp/harmonization_recipe.csv` should only be built after raw variables, units, recall periods, missing codes, and merge keys are verified.
