# Thirty-Eighth Round Decision: ARPA 400% FPL Paper Section Draft

## Verdict

`PAPER-SECTION PACKAGE DRAFTED; CONDITIONAL GO MAINTAINED`

The ARPA 400% FPL idea now has:

- consolidated empirical design memo;
- source and literature-gap memo;
- specification lock;
- paper-section draft.

This is enough to move from idea screening into a controlled manuscript-building stage.

## What Is Now Drafted

New artifact:

- `sipp/report/92_arpa_400fpl_paper_section_draft.md`

It includes:

- working title;
- abstract paragraph;
- introduction skeleton;
- literature/gap paragraph;
- data and empirical design subsection;
- main results narrative;
- mechanism narrative;
- robustness narrative;
- identification-threat paragraph;
- table captions;
- figure captions;
- claim-discipline rules.

## Decision

Keep as the lead idea.

The current manuscript framing should be:

> ARPA's removal of the ACA 400% FPL subsidy cliff is associated with lower uninsurance near the threshold in national SIPP person-month data, with direct-market mechanism evidence concentrated among adults not coming from employer-related coverage.

Do not upgrade beyond conditional go until:

1. the locked scripts are rerun from a clean session;
2. table shells are exported in manuscript-ready format;
3. placebo thresholds are shown in full;
4. annual-FPL measurement limitations are written explicitly;
5. a high-premium geography extension is tested only as a pre-specified extension, not as tuning.

## Next Best Work Unit

Produce a manuscript-ready table/figure export package:

- Table 1: support and cell means.
- Table 2: primary diff-in-disc estimates.
- Table 3: source-decomposition mechanism.
- Table 4: robustness summary.
- Table 5: placebo/falsification estimates.
- Figure 1-4 captions matched to existing PNGs.

Then write a compact `README_FOR_WEB_GPT_ARPA400.md` so the user can upload one report plus the relevant CSV/PNG outputs to web GPT for further brainstorming.
