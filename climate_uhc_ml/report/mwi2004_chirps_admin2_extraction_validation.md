# Malawi 2004 CHIRPS ADM2 Extraction Validation

Dataset: `MWI_2004_IHS-II_v01_M` - Malawi 2004-2005

This artifact extracts CHIRPS v2.0 Africa monthly rainfall to Malawi ADM2
district polygons using only local CHIRPS GeoTIFF files and the cached
geoBoundaries Malawi ADM2 geometry. It does not write a promoted household
dataset to `data/`.

## Summary

| metric | value | interpretation |
| --- | --- | --- |
| country_wave | MWI_2004_IHS-II_v01_M | Country-wave covered by CHIRPS ADM2 extraction. |
| chirps_files_required | 24 | Required CHIRPS monthly GeoTIFF files from the route manifest. |
| chirps_files_downloaded_readable | 24 | Downloaded files read successfully as GeoTIFF with PIL. |
| boundary_adm2_features | 28 | ADM2 boundary features used for district masks. |
| district_month_exposure_rows | 672 | ADM2 district-month rainfall exposure rows. |
| sampled_raw_districts | 26 | Raw Malawi 2004 districts observed in household data and mapped to ADM2. |
| observed_raw_district_interview_month_rows | 329 | Observed raw district by interview-month cells in the household sample. |
| lag_window_exposure_rows | 1316 | District-interview-month lag-window exposure rows. |
| lag_window_complete_rows | 1316 | Lag-window rows with all required months available. |
| mean_precip_min_mm | 0.292594 | Minimum extracted district-month mean precipitation. |
| mean_precip_max_mm | 404.831726 | Maximum extracted district-month mean precipitation. |
| geotiff_grid_consistent | 1 | Whether all CHIRPS rasters share the same georeference. |
| accepted_chirps_route | 1 | Whether the CHIRPS ADM2 route passes extraction validation. |
| accepted_chirps_era5_route | 1 | Promotion gate flag for accepted CHIRPS or ERA5 route; this is CHIRPS-only. |
| current_climate_linkage_gate_status | accepted_chirps_admin2_extraction_validated | Current climate linkage gate after raster extraction validation. |
| data_write_gate_status | closed | This extraction artifact does not write promoted household-climate data by itself. |

## Validation

| validation_component | status | evidence | required_action |
| --- | --- | --- | --- |
| download_manifest_fulfilled | pass | downloaded_readable=24/24 |  |
| geotiff_grid_consistency | pass | reference_grid=(1500, 1600, -20.0, 40.0, 0.0500000007, 0.0500000007); raster_files=24 |  |
| adm2_polygon_masks_nonempty | pass | adm2_masks=28; min_pixels=1; max_pixels=357 |  |
| sampled_raw_district_month_coverage | pass | sampled_districts=26; sampled_district_month_rows=624; valid_rows=624 |  |
| lag_windows_complete | pass | lag_rows=1316; complete_rows=1316 |  |
| precipitation_values_nonnegative | pass | mean_precip_min=0.292594; mean_precip_max=404.831726 |  |

## Download Audit Preview

| chirps_month | chirps_file | bytes | read_status | valid_value_min | valid_value_max |
| --- | --- | --- | --- | --- | --- |
| 2003-03 | chirps-v2.0.2003.03.tif.gz | 4504288 | readable_geotiff | 0.000000 | 989.441650 |
| 2003-04 | chirps-v2.0.2003.04.tif.gz | 4485489 | readable_geotiff | 0.000000 | 708.143188 |
| 2003-05 | chirps-v2.0.2003.05.tif.gz | 4491549 | readable_geotiff | 0.000000 | 675.260742 |
| 2003-06 | chirps-v2.0.2003.06.tif.gz | 4530803 | readable_geotiff | 0.000000 | 1063.740479 |
| 2003-07 | chirps-v2.0.2003.07.tif.gz | 4554585 | readable_geotiff | 0.000000 | 1195.601074 |
| 2003-08 | chirps-v2.0.2003.08.tif.gz | 4551725 | readable_geotiff | 0.000000 | 1021.615417 |
| 2003-09 | chirps-v2.0.2003.09.tif.gz | 4544202 | readable_geotiff | 0.000000 | 1031.115723 |
| 2003-10 | chirps-v2.0.2003.10.tif.gz | 4508253 | readable_geotiff | 0.000000 | 945.088013 |
| 2003-11 | chirps-v2.0.2003.11.tif.gz | 4515538 | readable_geotiff | 0.000000 | 617.578735 |
| 2003-12 | chirps-v2.0.2003.12.tif.gz | 4522809 | readable_geotiff | 0.000000 | 685.512878 |
| 2004-01 | chirps-v2.0.2004.01.tif.gz | 4430227 | readable_geotiff | 0.000000 | 919.339966 |
| 2004-02 | chirps-v2.0.2004.02.tif.gz | 4513538 | readable_geotiff | 0.000000 | 521.624634 |
| ... | ... | ... | ... | ... | ... |

## District-Month Exposure Preview

| adm2_name | chirps_month | valid_pixel_count | mean_precip_mm | extraction_status |
| --- | --- | --- | --- | --- |
| Balaka | 2003-03 | 73 | 220.883743 | pass |
| Blantyre | 2003-03 | 65 | 199.795303 | pass |
| Chikwawa | 2003-03 | 168 | 169.506226 | pass |
| Chiradzulu | 2003-03 | 26 | 213.846420 | pass |
| Chitipa | 2003-03 | 139 | 196.814682 | pass |
| Dedza | 2003-03 | 128 | 257.740356 | pass |
| Dowa | 2003-03 | 101 | 259.092468 | pass |
| Karonga | 2003-03 | 109 | 173.113663 | pass |
| Kasungu | 2003-03 | 266 | 261.419952 | pass |
| Likoma | 2003-03 | 1 | 147.532913 | pass |
| Lilongwe | 2003-03 | 209 | 264.313721 | pass |
| Machinga | 2003-03 | 129 | 292.844757 | pass |
| Mangochi | 2003-03 | 224 | 274.475983 | pass |
| Mchinji | 2003-03 | 104 | 268.634430 | pass |
| Mulanje | 2003-03 | 65 | 255.649521 | pass |
| Mwanza | 2003-03 | 24 | 244.410019 | pass |
| Mzimba | 2003-03 | 357 | 205.874908 | pass |
| Neno | 2003-03 | 55 | 239.549591 | pass |
| Nkhata Bay | 2003-03 | 134 | 317.138153 | pass |
| Nkhotakota | 2003-03 | 147 | 351.986603 | pass |
| ... | ... | ... | ... | ... |

## Lag-Window Exposure Preview

| raw_dist_code | raw_dist_label | interview_month | lag_months | precip_total_mm | window_complete |
| --- | --- | --- | --- | --- | --- |
| 101 | Chitipa | 2004-03 | 1 | 158.292236 | 1 |
| 101 | Chitipa | 2004-03 | 3 | 562.848114 | 1 |
| 101 | Chitipa | 2004-03 | 6 | 609.003766 | 1 |
| 101 | Chitipa | 2004-03 | 12 | 954.116274 | 1 |
| 101 | Chitipa | 2004-04 | 1 | 196.987671 | 1 |
| 101 | Chitipa | 2004-04 | 3 | 571.330475 | 1 |
| 101 | Chitipa | 2004-04 | 6 | 803.078895 | 1 |
| 101 | Chitipa | 2004-04 | 12 | 954.289263 | 1 |
| 101 | Chitipa | 2004-05 | 1 | 194.659653 | 1 |
| 101 | Chitipa | 2004-05 | 3 | 549.939560 | 1 |
| 101 | Chitipa | 2004-05 | 6 | 987.032387 | 1 |
| 101 | Chitipa | 2004-05 | 12 | 1029.174761 | 1 |
| 101 | Chitipa | 2004-06 | 1 | 16.173792 | 1 |
| 101 | Chitipa | 2004-06 | 3 | 407.821115 | 1 |
| 101 | Chitipa | 2004-06 | 6 | 970.669230 | 1 |
| 101 | Chitipa | 2004-06 | 12 | 1022.179188 | 1 |
| 101 | Chitipa | 2004-07 | 1 | 2.196071 | 1 |
| 101 | Chitipa | 2004-07 | 3 | 213.029515 | 1 |
| 101 | Chitipa | 2004-07 | 6 | 784.359990 | 1 |
| 101 | Chitipa | 2004-07 | 12 | 1022.121427 | 1 |
| ... | ... | ... | ... | ... | ... |

## Remaining Promotion Work

- Merge lag-window exposures onto the verified Malawi 2004 household outcome
  construction.
- Review rainfall shock definitions before any model run.
- Keep modeling blocked until the multi-country registry thresholds pass.
