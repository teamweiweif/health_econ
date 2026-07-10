# Thirty-Third Round Decision: ARPA 400% FPL Robustness

## Verdict

`ARPA 400% FPL REMAINS CONDITIONAL GO, SUBJECT TO PRE-ANALYSIS-STYLE ROBUSTNESS WRITEUP`

This robustness pack does not replace the source-decomposition conclusion. It tests whether that conclusion is fragile.

## Stability Read

- Main uninsured bandwidth specs: median -0.0260, range -0.0283 to -0.0255, negative share 1.00.
- Lagged non-employer market/subsidy bandwidth specs: median +0.0739, range +0.0667 to +0.0869, positive share 1.00.
- Placebo-threshold uninsured specs: median +0.0004, range -0.0255 to +0.0058.
- Donut specifications do not reverse the main uninsured result, but the lagged non-employer market/subsidy mechanism loses precision as the donut grows.
- Annual-FPL specifications keep the uninsured decline but do not keep the market/subsidy mechanism.

## Interpretation Rule

Keep the project as the lead if the true 400% main uninsured and lagged non-employer market/subsidy patterns are more systematic than placebo thresholds and pre-ARPA fake-policy tests. Downgrade if placebo thresholds look equally strong or if donut specifications reverse the main signal.

## Caution

This is still conditional, not final. The 3.5 FPL placebo uninsured coefficient is also negative, and the 3.0 FPL placebo market/subsidy coefficient is strongly negative. These do not match the full 400% pattern, but they imply the identification section must treat broader ARPA-era income-gradient changes as a serious threat.

## Next Required Step

Convert this from idea-screen evidence into a paper-ready design table: pre-specify the primary bandwidth, report all bandwidths/donuts, show binned event-study/RD plots, and write the identification threat section around income measurement, employer-source mixing, and older-adult nulls.
