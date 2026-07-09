# Priority LSMS-ISA Alignment Audit

Dataset: `MWI_2007-2009_MTM_v01_M` - Malawi 2007-2009

Current family: `non_lsms_specialized_panel`

Alignment status: `off_family_needs_lsms_isa_replacement_or_augmentation`

Risk: `high`

Recommended action: Do not treat the MTM specialized panel as the Malawi LSMS/ISA core wave. Replace or augment with Malawi IHS/IHPS before main downloads.

Replacement search: Prefer Malawi Integrated Household Survey or Integrated Household Panel Survey candidates already in country_wave_screening.csv.

Guardrail: this audit does not promote any data and does not permit ML. Raw
package receipt, raw value review, outcome construction, and climate linkage
must pass before any country-wave is written into `data/`.
