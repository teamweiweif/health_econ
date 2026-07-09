# ALB_2002 Local Geography Artifact Audit

Status: temp-only local geography artifact gap audit. This audit scans the extracted ALB_2002 raw package, raw schema catalog, and questionnaire workbook for coordinate, GPS, EA, district, commune, map, boundary, and GIS evidence. It does not create centroids, does not write `data/`, and does not construct climate exposures.

## Summary

| Metric | Value | Interpretation |
|---|---:|---|
| alb2002_local_geo_artifact_files_scanned | 44 | Files scanned under the extracted ALB_2002 package. |
| alb2002_local_geo_artifact_raw_tabular_files | 44 | Raw tabular/document workbook files observed locally. |
| alb2002_local_geo_artifact_gis_file_candidate_rows | 0 | Local GIS/boundary file candidates with recognized GIS suffixes; zero means no shapefile/GeoJSON/KML/GPX/GPKG candidate was found. |
| alb2002_local_geo_artifact_coordinate_raw_variable_rows | 0 | Raw schema variables with coordinate/GPS keywords. |
| alb2002_local_geo_artifact_questionnaire_coordinate_field_rows | 2 | Questionnaire cells documenting coordinate/GPS fields. |
| alb2002_local_geo_artifact_admin_variable_rows | 55 | Raw schema variables documenting admin/sampling geography but not coordinates. |
| alb2002_local_geo_artifact_psu_ea_variable_rows | 43 | Raw schema variables documenting PSU or enumerator-area identifiers. |
| alb2002_local_geo_artifact_district_commune_variable_rows | 9 | Raw schema variables documenting district/commune/municipality fields. |
| alb2002_local_geo_artifact_questionnaire_admin_text_rows | 13 | Questionnaire cells documenting admin geography fields. |
| alb2002_local_geo_artifact_questionnaire_map_text_rows | 0 | Questionnaire cells documenting map/boundary/GIS language. |
| alb2002_local_geo_artifact_official_gps_documented_rows | 1 | Upstream source-alternatives rows documenting GPS/longitude/latitude evidence. |
| alb2002_local_geo_artifact_official_ea_map_documented_rows | 1 | Upstream source-alternatives rows documenting EA boundary-map evidence. |
| alb2002_local_geo_artifact_local_coordinate_ready_rows | 0 | Local raw coordinate artifacts ready for climate linkage after this audit; intentionally zero. |
| alb2002_local_geo_artifact_local_boundary_ready_rows | 0 | Local boundary/GIS artifacts ready for climate linkage after this audit; intentionally zero. |
| alb2002_local_geo_artifact_climate_linkage_ready_rows | 0 | ALB_2002 rows ready for climate-linkage input promotion after this audit; intentionally zero. |
| alb2002_local_geo_artifact_current_decision | blocked_questionnaire_gps_fields_not_present_as_raw_coordinate_artifacts | Current fail-closed decision for local ALB_2002 geography artifacts. |

## Questionnaire Coordinate Fields

| source_path | sheet_name | row_number | column_number | variable_label | blocking_reason |
|---|---|---|---|---|---|
| temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Questionnaire 2002/LSMS02_Questionnaire.xls | COVER | 25 | 3 | Longitude | Questionnaire contains coordinate fields, but no corresponding raw coordinate variables or values are verified in the... |
| temp/raw_extracted/lsms2002en_4dbf0b087520/lsms2002en/Questionnaire 2002/LSMS02_Questionnaire.xls | COVER | 25 | 10 | Latitude | Questionnaire contains coordinate fields, but no corresponding raw coordinate variables or values are verified in the... |

## Raw Coordinate Variable Candidates

No raw coordinate/GPS variables found in the extracted ALB_2002 raw schema catalog.

## Raw Admin/Sampling Geography Variables

| source_path | variable_name | variable_label | evidence_role | blocking_reason |
|---|---|---|---|---|
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\filters.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | psu | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q1a | District | raw_district_or_commune_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q1b | District Label | raw_district_or_commune_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q02 | Municipality/Comune | raw_district_or_commune_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_q09 | Enumerator Area | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_0_identification.sav | m0_ur | Urban/Rural | raw_admin_geography_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_11A_nonfoodexp_1m_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_11B_nonfoodexp_6m_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_11C_nonfoodexp_12m_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12A_agr_a1_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12A_agr_a2_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12A_agr_a3_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12B_agr_b_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12C_agr_c_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12D_agr_d_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12E_agr_e_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_12F_agr_f_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_13A_nonag_a_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_13B_nonag_b_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_13C_nonag_c_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_13D_nonag_d_cl_2.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_13E_nonag_e_cl.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_14_income.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_15A_anthro1_cld.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_15B_anthro2d.sav | PSU | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_1_hhroster.sav | psu | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_2_Migration.sav | psu | PSU | raw_psu_or_ea_variable | PSU/enumerator-area identifiers are useful for sampling design but are not coordinates or polygons. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_2_Migration.sav | m2_q01 | Born in current municipality / commune | raw_district_or_commune_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |
| temp\raw_extracted\lsms2002en_4dbf0b087520\lsms2002en\Data_2002\Modul_2_Migration.sav | m2_q02 | Continously lived in current municipality / commune | raw_district_or_commune_variable | Admin labels/codes are observed, but no verified historical polygon or coordinate artifact is attached. |

## Interpretation

- The ALB_2002 questionnaire workbook contains coordinate design fields, including longitude and latitude on the cover sheet.
- The extracted raw schema catalog contains admin/sampling geography fields such as district, municipality/commune, PSU, enumerator area, stratum, and urban/rural.
- The extracted local package does not currently expose raw coordinate variables or a recognized GIS/boundary file candidate.
- This creates a specific gap: GPS was documented in source/questionnaire evidence, but the local raw value artifact needed for point climate extraction has not been verified.
- Climate-linkage-ready rows remain zero.

## Machine-Readable Outputs

- `temp/alb2002_local_geography_artifact_audit.csv`
- `result/alb2002_local_geography_artifact_summary.csv`
