# Skill Usage Log

## Skill Discovery

- Inspected `C:\Users\admin\.codex\skills` and plugin cache for `Auto-Empirical Research Skills`, `AERS`, `auto-empirical-research-skills`, `empirical research`, `causal inference`, `econometrics`, `reproducibility`, `research audit`, `Econ Writing Skill`, `economics writing`, `empirical paper writing`, and `journal writing`.
- No installed skill with those exact empirical/economics-writing names was found.
- Read `C:\Users\admin\.codex\skills\research-station\SKILL.md` as the closest available research-workflow skill.

## Advice Adopted

- Read local files before relying on conversation memory.
- Keep source material and messy audit artifacts out of clean report/data folders.
- Preserve a reproducible local control plane through scripts and generated reports.

## Advice Rejected Or Limited

- GitHub/LaTeX-specific synchronization instructions from `research-station` were not adopted because this project is not the Melbourne RP Writing repository and the current workspace is not a normal Git repository.
- No custom skill was created, per the user's instruction.

## Use In This Project

- The empirical workflow is implemented internally through `script/00_setup.py` through `script/10_write_report.py`.
- Final report writing is automated after empirical outputs exist; no absent Econ Writing skill was simulated.
