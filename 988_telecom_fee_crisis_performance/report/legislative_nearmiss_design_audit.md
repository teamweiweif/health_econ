# Legislative Near-Miss Design Audit

## Bill-Level Dataset

| state | bill_number | year_session | introduced_date | committee_action | floor_vote_date | vote_margin | passed_failed | enacted_not_enacted | official_bill_source | narrowly_passed_or_failed | audit_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA | AB988 | 2021-2022 | 2021-02-18 | advanced through policy/fiscal committees | 2022-08-30 |  | passed | enacted | https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=202120220AB988 | 0 | Enacted fee state; not a near-miss comparator. |
| CO | SB21-154 | 2021 | 2021-03-03 | advanced |  |  | passed | enacted | https://leg.colorado.gov/bills/SB21-154 | 0 | Enacted fee state; not a near-miss comparator. |
| DE | HS1 for HB160 | 2023 | 2023-05-18 | advanced |  |  | passed | enacted | https://legis.delaware.gov/BillDetail/140522 | 0 | Enacted fee state; not a near-miss comparator. |
| MD | SB974/HB933 | 2024 | 2024-02-02 | favorable; passed both chambers | 2024-04-02 | Senate 42-3; House 110-26 | passed | enacted | https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/SB0974?ys=2024RS | 0 | Wide vote margins; unusable for close-vote RD. |
| AL | HB389 | 2023 | 2023-05-02 | referred; stalled after committee dispute over fee |  |  | failed/stalled | not enacted | https://www.legislature.state.al.us/pdf/SearchableInstruments/2023RS/HB389-int.pdf | 0 | Serious attempt, but no floor vote margin and not a close-vote near miss. |
| MI | HB5354 | 2021-2022 | 2021-09-30 | referred to House Health Policy |  |  | failed/stalled | not enacted | https://www.legislature.mi.gov/documents/2021-2022/billintroduced/House/pdf/2021-HIB-5354.pdf | 0 | Introduced/referred only; no close-vote variation. |
| WV | SB181 | 2022 | 2022-01-12 | introduced/substitute text available |  |  | failed/stalled | not enacted | https://www.wvlegislature.gov/Bill_Status/bills_text.cfm?billdoc=SB181+SUB1.htm&i=181&sesstype=RS&yr=2022 | 0 | No usable close margin. |
| TN | SB1789/HB2555 | 2023-2024 | 2024-01-01 | introduced |  |  | failed/stalled | not enacted | https://www.capitol.tn.gov/Bills/113/Bill/SB1789.pdf | 0 | No close-vote or late-stage failure evidence in source scan. |
| MA | H4084 | 2025-2026 | 2025 | committee stage |  |  | pending/stalled | not enacted | https://malegislature.gov/Bills/194/H4084 | 0 | Pending/introduced; not part of observed outcome window as a clean near miss. |

## Feasibility

The source scan found enacted fee bills and several serious but stalled attempts. It did not find enough close floor votes or narrow failures to support a regression discontinuity or credible near-miss DID. Maryland's enacted bill, for example, passed by wide margins. Alabama, Michigan, West Virginia, Tennessee, and Massachusetts attempts do not provide close-vote variation; most failed before a usable floor vote.

## Decision

Reject as a quasi-experimental design for the current public data. A matched DID among policy-intent states would still be selected on legislative agenda-setting and would have too few comparable treated/control states.
