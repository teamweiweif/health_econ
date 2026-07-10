import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline_lib import causal_ml_audit

causal_ml_audit()
