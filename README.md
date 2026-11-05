# Explainable Fact Checking with Probabilistic Answer Set Programming

This project is a research prototype for checking whether a fact is likely true or false, and explaining the reason using logic-based rules and evidence.

The repository is based on the paper:
[Explainable Fact Checking with Probabilistic Answer Set Programming](https://arxiv.org/abs/1906.09198)

## What this project does

In simple words, the system:

- reads a relation such as `spouse`, `almaMater`, or `vicePresident`
- loads logic rules from the `Results` folder
- generates claims from a set of examples
- gathers supporting evidence from DBpedia and optionally Bing
- runs probabilistic ASP inference
- writes a result CSV and summary statistics for each experiment

The goal is not just to say “true” or “false”, but to show which rule and evidence led to the decision.

## Project structure

- `main.py` – entry script
- `processor.py` – loads arguments and runs the solver
- `scripts/` – utilities for claim generation, evidence retrieval, and inference
- `Results/` – rule files and experiment results
- `claims/` – claim datasets by relation
- `bing_caches/` – stored Bing evidence cache

## Setup on Windows

This project originally targeted older Python and Unix-style tooling, so we updated the code to work more reliably with modern Python and Windows file handling.

### 1) Install Miniforge / Conda

Install Miniforge from:
https://github.com/conda-forge/miniforge/releases

Then open a terminal and create the environment:

```powershell
C:\Users\sanch\miniforge3\condabin\conda.bat create -y -n expclaim python=3.11
C:\Users\sanch\miniforge3\condabin\conda.bat activate expclaim
```

### 2) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

If needed, the project dependencies are:

- clingo
- numpy
- pandas
- scipy
- matplotlib
- networkx
- requests
- sympy
- ply
- ipdb
- SPARQLWrapper

## Run the project

The repository’s sample command is:

```powershell
cd C:\Users\sanch\expclaim
python scripts/test.py --relation spouse --num_claims 2 --bing_evidence 0 --inference_mode ASP
```

### Explanation of the arguments

- `--relation`: relation to use, such as `spouse`, `almaMater`, or `deathPlace`
- `--num_claims`: number of claims to evaluate
- `--bing_evidence`: `0` uses KB-only evidence, `1` adds Bing evidence
- `--inference_mode`: `ASP` or `MAP`

## Expected output

The project writes output inside folders like:

- `Results/spouse/Experiments/.../ASP_results.csv`
- `Results/spouse/Experiments/.../ASP_stats.txt`

A sample result file looks like this:

```csv
Id,Subject,Object,Label,Predicted Label,Execution Time (mins)
1433,Victoria_Hislop,Ian_Hislop,1,UNSATISFIABLE,0.2172391414642334
2562,Carolina_Benedicks-Bruce,William_Blair_Bruce,1,1,0.03366851806640625
```

A summary file looks like this:

```text
True Positives: 25/43
True Negatives: 18/58
Precision :1.0
Recall :0.4257422517403448
F_score :0.5970436211355723
```

This means the system predicted some claims correctly, while some remained uncertain (`Can't Decide`) or unsatisfied.

## Important notes

- The project uses live DBpedia/SPARQL queries during evidence generation.
- If Bing evidence is enabled, you also need a Bing API key and configuration in the Bing module.
- The project may take time to finish when it queries external sources.
- The code was updated to avoid the Windows/UTF-8 crash caused by default encoding and the Unix-only `killall` behavior.

## Screenshots

Add screenshots of:

1. the environment creation
2. the dependency installation
3. the sample command running
4. the generated result CSV and summary file

Example placeholder:

```text
![Environment setup](docs/setup.png)
![Running experiment](docs/run.png)
![Results summary](docs/results.png)
```

## GitHub push steps

Once the project works locally:

```powershell
git init
git add .
git commit -m "ExpClaim setup and compatibility fixes"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

## License

MIT

## Contacts

Original project contact information is included in the source repository and paper link.






##Screenshot(Input dataset/Output)
<img width="1483" height="672" alt="image" src="https://github.com/user-attachments/assets/35729b58-5ca6-4078-ad79-dc6093ab6932" />
<img width="1470" height="1077" alt="image" src="https://github.com/user-attachments/assets/b72fb46b-5b31-409b-8019-82feae2fe7eb" />


