import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline_lib import ensure_structure, write_source_memos

ensure_structure()
write_source_memos()
