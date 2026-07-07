# Official Policy and Algorithm Audit

Access date: 2026-07-08

## Source Snapshots

| Source | Status | Local path | SHA-256 |
|---|---:|---|---|
| CMS QSO-22-08-NH | cached | `temp\raw_downloads\CMS_QSO-22-08-NH.pdf` | `34681632512c85f4907a25167755061f330417087daea3dcb8ce7daf6d0530a1` |
| CMS Updates to the Care Compare Website July 2022 | cached | `temp\raw_downloads\CMS_Updates_to_the_Care_Compare_Website_July_2022.html` | `98c8ae2a4c656012181e2c4aad370186c3de847c4202494462d8ec9efefc22ee` |
| CMS Five-Star Quality Rating System Archives | cached | `temp\raw_downloads\CMS_Five-Star_Quality_Rating_System_Archives.html` | `f75cb2a78cf6eeb1131e35229417ff299acd831c8ae8fe5e19488dabfb4a6c77` |
| CMS PBJ Daily Nurse Staffing data catalog | cached | `temp\raw_downloads\CMS_PBJ_Daily_Nurse_Staffing_data_catalog.html` | `11612c367d9de8eaa47ad3b9cda178477e7fc9e12a30113d0e52b3eb029a7ab2` |
| CMS Provider Data Catalog nursing homes archive API | cached | `temp\raw_downloads\CMS_Provider_Data_Catalog_nursing_homes_archive_API.json` | `ef50a4721733a875b3ae1d357b056e2b829afe7fc478d44bb4ff5c0927e8ce93` |
| HHS OIG 2020 nursing home staffing transparency | cached | `temp\raw_downloads\HHS_OIG_2020_nursing_home_staffing_transparency.html` | `4bf49267405763f5d802bc6719f5ab5cf863379454aa466374da8987b02ba0cf` |
| HHS OIG 2025 CMS use of staffing data | cached | `temp\raw_downloads\HHS_OIG_2025_CMS_use_of_staffing_data.html` | `b632f2addb13af40db050af6feaa7eb9dfbd985a5e26053f53f4884a61e7c38a` |
| Previous versions of Technical Users Guide ZIP | cached | `temp\raw_downloads\previous_versions_nhcc_technical_users_guide.zip` | `14499abd809a6135601f0b0a5ed3c44101edf18df8c3f12c5c4e38dd85fb2eba` |
| Current Five-Star Technical Users Guide | cached | `temp\raw_downloads\current_usersguide.pdf` | `787c2c41bf6b1cc9f6a2ffff6cfc3ce0b7aa625583fc77681a3db7c9080120c5` |

## Verified Policy Facts

| Claim | Verified | Evidence note |
|---|---:|---|
| January 7, 2022 QSO memo issued | True | CMS QSO-22-08-NH text includes DATE: January 07, 2022. |
| January 2022 Care Compare public reporting of weekend staffing and turnover | True | QSO memo and July 2022 guide describe January 2022 Care Compare posting. |
| January 26, 2022 employee-level PBJ staffing data posting | True | QSO memo states employee-level data will be posted on January 26, 2022. |
| July 2022 staffing domain switched to six-measure point score | True | July 2022 guide states the new rating is based on six separate staffing measures. |
| July 2022 staffing-star thresholds are 155, 205, 255, and 320 | True | July 2022 guide Table 3 lists <155, 155-204, 205-254, 255-319, 320-380. |
| July 2022 overall-rating rule removes four-star staffing bonus | True | July 2022 guide states only five-star staffing gets an overall-rating increase. |
| January 2022 old formula allowed four- or five-star staffing bonus if greater than health inspection | True | January 2022 guide Step 2 describes four- or five-star staffing bonus. |

## Algorithm Facts Used in the Tournament

- January 2022 is treated as the transparency shock: weekend total nurse/RN staffing and turnover became public on Care Compare.
- July 27, 2022 is treated as the main algorithmic-label shock: the staffing-domain rating changed to a point score based on six staffing/turnover measures.
- Staffing-star thresholds used for RD/RD-DID are 155, 205, 255, and 320 on the rounded 0-380 staffing score.
- The July 2022 overall-rating rule gives the staffing bonus only for five-star staffing; the January 2022 rule allowed a four- or five-star staffing bonus when staffing exceeded health inspection.

## Uncertainties

- Provider Data Catalog archives publish staffing stars and component measures, but not the facility-level 0-380 staffing score. The tournament therefore attempts a score proxy/emulator and downgrades RD if the star match rate is below 95%.
- The July 2022 ProviderInfo file does not contain a separate adjusted weekend total nurse HPRD column; it contains reported weekend total nurse HPRD. The emulator uses the reported field for July and treats that as a proxy limitation.
- The local `.git` directory is a Dropbox reparse placeholder and `git status` does not recognize the workspace as a repository. The requested branch could not be safely created; all outputs are isolated under `design_tournament/`.
