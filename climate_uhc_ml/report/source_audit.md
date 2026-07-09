# Source Audit

Generated: 2026-07-08T16:54:01+00:00

## Official Anchors Verified

| Claim | Status | Evidence |
|---|---|---|
| SDG 3.8.2 uses the 2025 revised 40% discretionary-budget definition | accepted | WHO financial protection page states that the page presents the revised 2025 definition. UNSD metadata defines the indicator as the proportion of population with positive OOP household expenditure on health exceeding 40% of household discretionary budget. |
| Discretionary budget equals total household consumption expenditure or income minus the societal poverty line | accepted | UNSD metadata defines discretionary household budget this way and specifies the SPL using 2017 PPPs. |
| CHE10 and CHE25 remain useful older/common financial hardship indicators | accepted as auxiliary, not the 2025 SDG definition | WHO notes data based on the 2017 definition are archived. The project will use CHE10/CHE25 as comparability and robustness outcomes, not as the current SDG 3.8.2 definition. |
| Climate-resilient health systems and UHC are connected in WHO documentation | accepted | WHO's operational framework says climate-resilient health systems contribute to UHC, global health security, and SDG targets. |
| Climate change can reduce capacity to provide UHC and worsen financial hardship/access barriers | accepted as policy rationale, not empirical proof for this project | WHO's climate fact sheet states climate change affects health systems and can reduce capacity to provide UHC; empirical effects must still be estimated from data. |
| Household microdata can support a multi-country causal ML paper | not yet verified | Requires country-wave inventory, raw schema inspection, usable timing/geography, outcome construction, and falsification tests. |
| Climate shocks cause UHC failure in the candidate data | not yet verified | No causal claim is accepted until exposure construction and reduced-form/placebo tests pass. |

## Extracted Evidence Notes

### WHO financial protection

The WHO financial protection page was snapshotted at `temp/source_snapshots/who_financial_protection_sdg382_2025.md`. It identifies the current SDG 3.8.2 series as the revised 2025 definition and links to the official UNSD metadata PDF. The raw WHO page extraction contains some malformed smart-quote characters from HTML parsing, so the exact definitional text below is taken from the cleaner UNSD PDF extraction.

### UNSD SDG 3.8.2 metadata

Official 2025 indicator definition recorded from the metadata:

> Proportion of the population with positive out-of-pocket household expenditure on health exceeding 40% of household discretionary budget.

Denominator rule: Household discretionary budget is total household consumption expenditure or income minus the societal poverty line. The metadata specifies the SPL using 2017 PPPs and the greater of the international poverty line or a median-consumption-based societal line.

The extracted PDF text is saved at `temp/source_snapshots/unstats_sdg_3_8_2_metadata.txt` for traceability.

### WHO climate-resilient health systems

The WHO operational framework on climate-resilient and low-carbon health systems was snapshotted at `temp/source_snapshots/who_climate_resilient_health_systems.md`. It explicitly frames climate-resilient health systems as contributing to UHC, global health security, and SDG targets.

### WHO climate change and health

The WHO climate change and health fact sheet was snapshotted at `temp/source_snapshots/who_climate_change_health_factsheet.md`. It links climate shocks, health-system capacity, and UHC as policy motivation; this is not treated as evidence that the empirical effect exists in the candidate microdata.

## Current Go/No-Go

Go for Phase 1 inventory and screening. No go for causal modeling, causal ML, or policy-learning claims until microdata variables, geography, timing, and placebo tests are audited.
