            # Main Results Memo

            ## Analytic Sample

            Primary sample: expansion-state adults age 19-64, no Medicare, not flagged SSI/disability/non-MAGI proxy, valid family income-to-poverty ratio, and in the 1.00-1.75 ratio-unit near-boundary window (100-175% FPL).

            - Rows: 89,079
            - Persons: 10,835
            - Temporary cross-up 1-month events: 343
            - Medicaid exits: 212
            - Exit to uninsured: 99

            ## Conventional Hazard Model

            Weighted linear probability models include state, reference-year, and month fixed effects, plus baseline controls. `statsmodels` is not installed, so robust standard errors are computed directly.

            - medicaid_exit_it h=0: beta=0.01814, se=0.01162, p=0.118, n=89,079, events=212
- exit_to_uninsured_it h=0: beta=0.02003, se=0.01177, p=0.089, n=89,079, events=99
- exit_to_direct_purchase_exchange_it h=0: beta=-0.00055, se=0.00023, p=0.018, n=89,079, events=27
- persistent_uninsured_2m h=0: beta=0.02003, se=0.01177, p=0.089, n=89,079, events=97
- persistent_uninsured_3m h=0: beta=0.02008, se=0.01177, p=0.088, n=89,079, events=93
- medicaid_exit_it_h1 h=1: beta=0.01185, se=0.00979, p=0.226, n=78,244, events=123
- exit_to_uninsured_it_h1 h=1: beta=0.01318, se=0.00999, p=0.187, n=78,244, events=55
- exit_to_direct_purchase_exchange_it_h1 h=1: beta=-0.00024, se=0.00013, p=0.071, n=78,244, events=14
- persistent_uninsured_2m_h1 h=1: beta=0.01318, se=0.00999, p=0.187, n=78,244, events=55
- persistent_uninsured_3m_h1 h=1: beta=0.01323, se=0.01000, p=0.186, n=78,244, events=53
- medicaid_exit_it_h2 h=2: beta=-0.00204, se=0.00064, p=0.001, n=69,225, events=107
- exit_to_uninsured_it_h2 h=2: beta=-0.00109, se=0.00034, p=0.001, n=69,225, events=50
- exit_to_direct_purchase_exchange_it_h2 h=2: beta=-0.00013, se=0.00011, p=0.238, n=69,225, events=12
- persistent_uninsured_2m_h2 h=2: beta=-0.00109, se=0.00034, p=0.001, n=69,225, events=50
- persistent_uninsured_3m_h2 h=2: beta=-0.00104, se=0.00033, p=0.002, n=69,225, events=48
- medicaid_exit_it_h3 h=3: beta=-0.00140, se=0.00049, p=0.004, n=61,132, events=94
- exit_to_uninsured_it_h3 h=3: beta=-0.00083, se=0.00029, p=0.004, n=61,132, events=43
- exit_to_direct_purchase_exchange_it_h3 h=3: beta=-0.00002, se=0.00009, p=0.793, n=61,132, events=11
- persistent_uninsured_2m_h3 h=3: beta=-0.00083, se=0.00029, p=0.004, n=61,132, events=43
- persistent_uninsured_3m_h3 h=3: beta=-0.00078, se=0.00028, p=0.006, n=61,132, events=41

            ## Interpretation Boundary

            These are transparent conventional specifications, not proof of causal effects. Event-study outputs are descriptive crossers-only profiles unless and until a credible matched control/event design is established.
