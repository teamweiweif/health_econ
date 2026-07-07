#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
python script/v3_common.py
python script/90_self_check_v3.py
