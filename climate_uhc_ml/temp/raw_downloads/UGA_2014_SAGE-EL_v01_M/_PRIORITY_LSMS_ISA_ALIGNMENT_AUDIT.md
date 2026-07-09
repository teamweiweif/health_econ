# Priority LSMS-ISA Alignment Audit

Dataset: `UGA_2014_SAGE-EL_v01_M` - Uganda 2014

Current family: `non_lsms_social_protection_evaluation`

Alignment status: `off_family_needs_unps_lsms_isa_replacement_or_augmentation`

Risk: `high`

Recommended action: Do not treat SAGE impact evaluation waves as the Uganda LSMS/ISA core wave. Replace or augment with Uganda UNPS before main downloads.

Replacement search: Prefer Uganda National Panel Survey candidates already in country_wave_screening.csv.

Guardrail: this audit does not promote any data and does not permit ML. Raw
package receipt, raw value review, outcome construction, and climate linkage
must pass before any country-wave is written into `data/`.
