# Georouting Design Audit

## Policy and Technical Change

Before georouting, 988 wireless calls could be routed by area code/exchange rather than by the caller's current physical area. Voice georouting changes this by sending generalized cell-based routing information so the Lifeline administrator can route calls to a more local crisis center without transmitting precise handset location. This is more plausibly external to state fee-adoption decisions, but public data still provide only national timing and no state-level treatment intensity.

## Official Timeline

| date | event | modality | scope | source |
| --- | --- | --- | --- | --- |
| 2024-09-17 | Voice georouting launched for cellular 988 calls in the 988 Lifeline network | voice calls | national launch, carrier implementation not fully state-specific in public data | 988 Lifeline About page |
| 2024-10-18 | FCC adopted rules requiring georouting for all wireless calls to 988 | voice calls | all covered wireless carriers | FCC 24-111 |
| 2024-12-12 | FCC 988 voice georouting rules became effective | voice calls | regulatory effective date | FCC DA-25-233 |
| 2025-01-13 | Nationwide CMRS providers required to comply with 988 voice georouting | voice calls | nationwide carriers | FCC DA-25-233 |
| 2026-12-14 | Non-nationwide CMRS providers required to comply with 988 voice georouting | voice calls | smaller/non-nationwide carriers | FCC DA-25-233 |
| 2025-07-24 | FCC approved rules requiring georouting for text messages to 988 | text | covered wireless text providers; implementation follows effective date | FCC DOC-413211 |
| 2025-10-16 | Text-to-988 georouting rules effective | text | regulatory effective date | FCC DA-25-879 |
| 2027-04-16 | Nationwide CMRS text-to-988 georouting compliance deadline | text | future relative to current outcome window | FCC DA-25-879 |
| 2028-10-16 | Non-nationwide text-to-988 georouting compliance deadline | text | future relative to current outcome window | FCC DA-25-879 |

## Exposure Construction

The rescue layer constructed ACS proxy measures for routing mismatch: percent of residents who moved from another state in the prior year and percent born in a different state. These are public proxies for likely phone-number/geography mismatch, not actual phone-number or area-code data.

Top states by proxy mismatch:

_No rows._

## Model Results

_No rows._

## Diagnostics

- Raw high-vs-low proxy trends were saved to `result/rescue/georouting_raw_trends_by_mismatch_proxy.png`.
- Event-time proxy coefficients were saved to `result/rescue/georouting_event_proxy_answer_rate.csv`.
- Leave-one-state-out checks were saved to `result/rescue/georouting_leave_one_state_out.csv`.
- Pretrend diagnostic status: not clearly failed, but underpowered and proxy-based.
- Modality contrast is unavailable because the public state KPI panel used here is not separated into call, text, and chat outcomes.

## Decision

Weak/infeasible as a top-journal rescue design. Georouting has a more credible national technical shock than state fee adoption, but the public data lack actual routing-mismatch exposure, carrier-by-state implementation intensity, and a visible first-stage-like routing measure. The available ACS proxies are too indirect to support a strong causal claim.
