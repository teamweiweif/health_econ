# Outcome Reconstruction Audit

## Data Source

PBJ Daily Nurse Staffing quarterly CSV URLs recorded in the existing source inventory are streamed from CMS and aggregated to facility-month and facility-quarter reliability outcomes.

## Constructed Outcomes

- `rn_lt8_days`: days with positive resident census and RN hours below 8.
- `weekend_rn_lt8_days`: weekend days with positive resident census and RN hours below 8.
- `zero_rn_days`: days with positive resident census and zero RN hours.
- `zero_total_nurse_days`: days with positive resident census and zero RN/LPN/aide hours.
- `weekend_p10_total_hprd`, `weekend_p25_total_hprd`: lower-tail weekend total nurse HPRD.
- `worst_weekend_total_hprd`, `worst_weekend_rn_hprd`: minimum weekend daily HPRD within period.
- `weekend_low_facility_p25_share`: share of weekend days below a facility's 2019-2021 monthly weekend HPRD p25.
- `weekend_low_national_p10_share`: share of weekend days below the national 2019-2021 monthly weekend HPRD p10.
- `weekend_share_total_hours`: weekend share of total nursing hours, used for reallocation/gaming.
- `contract_share_total_hours`: contract nursing hours share.
- `avg_daily_census`: resident census demand proxy.

These are policy-proximal staffing reliability and lower-tail staffing-risk outcomes, not resident clinical outcomes. The low-staffing thresholds are derived from the existing 2019-2021 facility-month PBJ panel to avoid a second full pass over remote daily CSV files.
