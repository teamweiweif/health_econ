# Final Breakthrough Report

## Executive Judgment

No strong causal paper yet. The project has a stronger conceptual route than the old exposure DID, but the first empirical pass does not justify strong causal language unless the staffing-score emulator reaches the 95% validation threshold or an official score field is found.

## What Improved

- The paper is reframed around algorithmic labels and staffing reliability, not generic public reporting.
- Official CMS sources verify January 2022 as transparency and July 2022 as the Five-Star algorithmic-label shock.
- The July 2022 archived Technical Users' Guide is now snapshotted and used as the algorithm source.
- Reliability/lower-tail PBJ outcomes are constructed or cached by script.
- RD, RD-DID, formula-label shock, metric-salience, shadow-price, and bunching scripts are reproducible under `design_tournament/`.

## Key Empirical Signals

- July 2022 score proxy matches official staffing stars at 0.899, below the pre-specified 0.950 primary-use threshold. October 2022 match is 0.967, which supports the algorithm logic once adjusted weekend HPRD is available.
- Reliability outcomes cover 287,602 facility-quarter rows and 15,397 facilities for 2019Q1-2023Q4.
- At the 320 cutoff, simple post-July RD estimates are not robust enough for a strong claim; RD-DID shows adverse reliability movements but inherits the July running-variable limitation.
- Formula-induced-loss homes have a larger April-to-July actual overall-star decline of -0.481 stars relative to controls. In post-minus-pre outcomes, they also show census change -1.042, weekend RN<8h share change 0.0085, and weekend p10 total HPRD change -0.081 relative to controls. Treat this as conditional mechanism evidence until matched/local diagnostics are strengthened.

## Best Manuscript Path

The strongest path is still Strategy 1 if the running variable can be improved: RD-DID around the 320 staffing-star cutoff, supported by the formula-induced overall-star shock and metric-salience DDD. If emulator validation stays weak, pivot to a cautious algorithmic score-management paper using bunching and mechanism evidence, not a strong causal paper.

## Stop-Loss

Do not return to tuning the old composite exposure DID. If no official score can be recovered and the emulator remains below threshold, label RD/RD-DID as exploratory and write the project as transparent no-go or conditional mechanism evidence.
