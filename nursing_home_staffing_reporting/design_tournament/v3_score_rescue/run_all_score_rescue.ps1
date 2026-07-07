$ErrorActionPreference = "Stop"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $here
try {
    python .\script\v3_common.py
    python .\script\90_self_check_v3.py
}
finally {
    Pop-Location
}
