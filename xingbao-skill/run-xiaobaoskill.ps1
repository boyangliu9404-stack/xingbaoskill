$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

chcp 65001 | Out-Null
python .\xiaobaoskill.py @args

