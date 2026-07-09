# Validation Reference Sources

Status: external validation/reference sources were probed. These data are for later comparison, PPP/CPI context, and denominator feasibility checks; they do not construct household outcomes.

## Probe Status

| Status | Count |
|---|---:|
| indicator_metadata_available | 8 |
| reachable_snapshot_saved | 4 |

## Source Roles

| Source role | Count |
|---|---:|
| oop_macro_context | 3 |
| country_validation_portal | 1 |
| country_validation_catalog | 1 |
| hefpi_indicator_api_catalog | 1 |
| hefpi_bulk_csv_reference | 1 |
| che10_country_validation | 1 |
| che25_country_validation | 1 |
| poverty_line_context | 1 |
| ppp_conversion_context | 1 |
| cpi_context | 1 |

## Indicator Sample

- Sample rows: 3122
- Countries with sample records: 20

| Indicator sample records | Count |
|---|---:|
| SH.XPD.OOPC.CH.ZS | 520 |
| SH.XPD.OOPC.PC.CD | 520 |
| SH.XPD.OOPC.PP.CD | 520 |
| SI.POV.DDAY | 520 |
| PA.NUS.PRVT.PP | 520 |
| FP.CPI.TOTL | 520 |

## HEFPI UHC Reference Extract

- HEFPI UHC series rows: 59
- HEFPI UHC country-year records for priority countries: 1288
- Priority countries with HEFPI UHC records: 20

| HEFPI UHC indicator | Count |
|---|---:|
| HF.UHC.NOP1.CG | 92 |
| HF.UHC.NOP4.CG | 92 |
| HF.UHC.NOP2.CG | 92 |
| HF.UHC.NOP3.CG | 92 |
| HF.UHC.OOP.CG | 92 |
| HF.UHC.OOP.ZS | 92 |
| HF.UHC.NOP1.ZS | 92 |
| HF.UHC.NOP4.ZS | 92 |
| HF.UHC.NOP2.ZS | 92 |
| HF.UHC.NOP3.ZS | 92 |
| HF.UHC.CONS.ZS | 92 |
| HF.UHC.NOPX.ZS | 92 |
| HF.UHC.OOPC.10.ZS | 92 |
| HF.UHC.OOPC.25.ZS | 92 |

## Guardrails

- HEFPI/WDI country indicators are validation/context sources, not replacements for survey microdata outcomes.
- CHE10/CHE25 WDI archive indicators may be useful external comparators, but project estimates must be constructed from audited raw survey OOP and household budget variables.
- SDG 3.8.2 discretionary-budget construction still requires household OOP, consumption/income, societal poverty line, PPP/CPI assumptions, and survey-specific unit checks.

## Machine-Readable Outputs

- `temp/validation_reference_source_probe.csv`
- `temp/validation_reference_indicator_sample.csv`
- `temp/hefpi_uhc_series_catalog.csv`
- `temp/hefpi_uhc_reference_sample.csv`
- Snapshots under `temp/source_snapshots/validation_reference_sources/`
