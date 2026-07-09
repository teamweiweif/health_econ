# Raw Download Audit

Status: this audit checks files placed under `temp/raw_downloads/`; it does not claim that raw microdata are available unless raw tabular files or raw archives are present in expected target folders.

## File Manifest

- Files under `temp/raw_downloads/`: 43
- Expected target folders: 37
- Targets with raw tabular/archive files: 1

| File role | Count |
|---|---:|
| documentation_or_metadata | 37 |
| archive | 4 |
| readme_or_instructions | 2 |

## Target Folder Status

| Target status | Count |
|---|---:|
| documentation_only_present | 36 |
| raw_or_archive_files_present | 1 |

## Machine-Readable Outputs

- `temp/raw_download_file_manifest.csv`
- `temp/raw_download_target_audit.csv`

## Guardrail

Only files in `temp/raw_downloads/` are considered raw acquisition inputs. Clean analytical datasets may be written to `data/` only after raw schema/value inspection and harmonization audits pass.
