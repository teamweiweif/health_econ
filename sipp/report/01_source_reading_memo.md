            # Source Reading Memo

            ## Controlling Source

            The controlling instruction for this run is the pasted goal file:

            `C:\Users\admin\.codex\attachments\3657460f-baf5-436a-8680-f6d6b587838e\pasted-text-1.txt`

            It selects the SIPP-only adult Medicaid eligibility-boundary design as the immediate design to audit, with child continuous eligibility and 2023 unwinding burden as backups.

            ## Prior Local Materials Read

            - `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\HIGH_REASONING_MODEL_HANDOFF.md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions
- `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\docs\current_exploration_handoff.md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions
- `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\docs\churn_unwinding_post_round4_path_decision.md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions
- `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\docs\research_directions_analysis.md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions
- `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\docs\deep-research-report(1).md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions
- `D:\GlobalHealthPolicy Dropbox\Fan Bowei\US Insurance Project\docs\deep-research-report(2).md`: read. Opening lines indicate: older unwinding diagnostic/risk branch and anti-overclaiming cautions

            The available prior local files mostly document an older SIPP + CMS unwinding diagnostic/risk-ranking branch. They explicitly warn against causal-effect, DML, causal-forest, and deployment-targeting claims unless identification improves. I therefore treat those files as cautionary background, not as the active design frame. The pasted objective is the active pivot to a SIPP-only adult-boundary audit.

            ## Verified Policy And Data Logic

            - Public SIPP files available locally and on Census cover survey file years 2018-2024, approximately reference years 2017-2023.
            - The 2024 SIPP file covers January-December 2023, so public SIPP does not yet fully evaluate the 2024 child 12-month CE mandate.
            - The PHE continuous enrollment condition ended on March 31, 2023; eligibility terminations after renewal can be effective on or after April 1, 2023.
            - ACA adult expansion eligibility is generally operationalized around 138% FPL in expansion states.

            ## Designs Recommended For Audit

            - Primary: adult near-boundary temporary income crossing around 138% FPL in expansion states.
            - Regime contrast: pre-PHE, PHE continuous enrollment, early unwinding through December 2023.
            - Outcomes: Medicaid exit, exit to uninsured, bridge to private/direct-purchase/exchange, and persistent uninsured gaps.
            - Backup 1: pre-2024 child continuous eligibility if adult-boundary event support fails.
            - Backup 2: 2023 early unwinding administrative-burden design only as early evidence unless state-month metrics provide credible support.

            ## Must Be Verified Rather Than Assumed

            - Exact variable meanings and availability from the local compact metadata JSON and official codebooks.
            - Whether `EMDMTH` and `RPUBTYPE2` agree enough to support a stable Medicaid measure.
            - Whether temporary cross-up events and exit-to-uninsured outcomes have enough support.
            - Whether conventional designs produce credible variation before any causal ML is considered.
