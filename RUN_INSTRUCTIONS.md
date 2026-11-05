# How to run ExpClaim on Windows

Open PowerShell in the repository root, then run either of these commands:

- .\run_demo.ps1
- .\run_demo.bat

The scripts use the existing Miniforge environment at C:\Users\sanch\miniforge3\envs\expclaim\python.exe directly, so no conda activation is required.

The demo runs:

python scripts/test.py --relation spouse --num_claims 2 --bing_evidence 0 --inference_mode ASP

It prints the Python version, dependency versions, live pipeline output, and the final ASP result files from the newest Results/spouse/Experiments folder.
