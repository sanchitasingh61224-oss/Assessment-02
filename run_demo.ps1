Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

function Resolve-ExpclaimPython {
    $candidates = @(
        "$env:USERPROFILE\miniforge3\envs\expclaim\python.exe",
        "C:\Users\sanch\miniforge3\envs\expclaim\python.exe",
        "C:\Users\sanch\miniforge3\envs\expclaim\python",
        "$env:USERPROFILE\miniforge3\envs\expclaim\python"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return (Resolve-Path $candidate).Path
        }
    }

    throw "Could not find expclaim Python environment at $env:USERPROFILE\miniforge3\envs\expclaim\python.exe or C:\Users\sanch\miniforge3\envs\expclaim\python.exe. Create the env first or fix the Miniforge install path."
}

$python = Resolve-ExpclaimPython
$command = @(
    $python,
    'scripts/test.py',
    '--relation', 'spouse',
    '--num_claims', '2',
    '--bing_evidence', '0',
    '--inference_mode', 'ASP'
)

Write-Host '============================'
Write-Host 'ExpClaim Demo Runner'
Write-Host '============================'
Write-Host ''
Write-Host 'Python path:'
Write-Host $python
Write-Host ''
Write-Host 'Python version:'
& $python --version
Write-Host ''
Write-Host 'Installed versions:'
& $python -c "import clingo, numpy, pandas, SPARQLWrapper; print('clingo=' + clingo.__version__); print('numpy=' + numpy.__version__); print('pandas=' + pandas.__version__); print('SPARQLWrapper=' + SPARQLWrapper.__version__)"
Write-Host ''
Write-Host 'Exact command:'
Write-Host (($command | ForEach-Object { if ($_ -match ' ') { '"' + $_ + '"' } else { $_ } }) -join ' ')
Write-Host ''
Write-Host 'Running sample ASP inference...'
$runOutput = & $python @('scripts/test.py', '--relation', 'spouse', '--num_claims', '2', '--bing_evidence', '0', '--inference_mode', 'ASP') 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ''
    $runOutput | ForEach-Object { Write-Host $_ }
    Write-Host ''
    Write-Host 'FAILED: ASP sample inference failed.'
    exit 1
}

$runOutput | ForEach-Object { Write-Host $_ }

Write-Host ''
Write-Host 'Newest Results/spouse/Experiments folder:'
$newestDir = Get-ChildItem -Path (Join-Path $repoRoot 'Results\spouse\Experiments') -Directory | Sort-Object LastWriteTimeUtc -Descending | Select-Object -First 1
if (-not $newestDir) {
    Write-Host 'FAILED: no experiment directory found.'
    exit 1
}
Write-Host $newestDir.FullName

$resultsCsv = Join-Path $newestDir.FullName 'ASP_results.csv'
$statsTxt = Join-Path $newestDir.FullName 'ASP_stats.txt'

if (-not (Test-Path $resultsCsv)) {
    Write-Host 'FAILED: missing ASP_results.csv in newest experiment folder.'
    exit 1
}
if (-not (Test-Path $statsTxt)) {
    Write-Host 'FAILED: missing ASP_stats.txt in newest experiment folder.'
    exit 1
}

Write-Host ''
Write-Host 'ASP_results.csv contents:'
Get-Content -Path $resultsCsv -Raw | Write-Host
Write-Host ''
Write-Host 'ASP_stats.txt contents:'
Get-Content -Path $statsTxt -Raw | Write-Host

Write-Host ''
Write-Host 'SUCCESS: demo finished and generated ASP output.'
