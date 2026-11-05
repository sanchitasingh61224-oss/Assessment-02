Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$python = 'C:\Users\sanch\miniforge3\envs\expclaim\python.exe'

Write-Host '============================'
Write-Host 'ExpClaim Demo Runner'
Write-Host '============================'
Write-Host ""
Write-Host "Python: $python"
& $python --version

Write-Host ""
Write-Host 'Running tests...'
& $python -m pytest -q tests
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }

Write-Host ""
Write-Host 'Running sample ASP inference...'
& $python scripts/test.py --relation spouse --num_claims 2 --bing_evidence 0 --inference_mode ASP
if ($LASTEXITCODE -ne 0) { throw 'ASP sample inference failed.' }

Write-Host ""
Write-Host 'Result files:'
Get-ChildItem -Recurse -Path Results | Where-Object { $_.Name -match 'ASP_.*(results|stats)\.(csv|txt)$' } | Select-Object -ExpandProperty FullName

Write-Host ""
Write-Host 'Demo completed successfully.'
