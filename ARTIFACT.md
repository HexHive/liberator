# LIBERATOR Artifact – Replication Guide

This guide summarizes how to reproduce the experiments from the paper:  
**"Liberating libraries through automated fuzz driver generation"**

- DOI: [10.5281/zenodo.13752276](https://doi.org/10.5281/zenodo.13752276})  
- Repository: [github.com/HexHive/liberator](https://github.com/HexHive/liberator)  
- Containerized setup via Docker  
- Authors: Flavio Toffalini, Nicolas Badoux, Zurab Tsinadze, Mathias Payer

---

## Requirements

### Hardware
- At least **64 GB of RAM**
- Minimum **4 TB of disk space**
- Multi-core server recommended (~2–3 days runtime)

### Software
- **Ubuntu 20.04**
- Ability to run **Docker**
- Internet connection

### Dependencies
- `curl`, `git`, `docker`, `pip`
- Python dependencies:
  ```bash
  ./preinstall.sh
  ```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/HexHive/liberator.git
cd liberator

# Switch to the artifact tag
git checkout fse-25-artifact

# Install Python dependencies (on the host)
pip install -r requirements_host.txt
```

> All experiments run in Docker containers. Local runs are not supported.

---

## Experiment 1 (E1): Trade-off Analysis

- **Goal**: Measure the impact of driver generation time (`tgen`) vs test time (`ttest`)
- **Claim supported**: (C1)
- **Time**: 2 min human, ~60 compute-hours

### Steps

```bash
# Optional: Install static analysis results (faster)
./install_analysis_result.sh

# Run all 4 campaigns
./run_campaign_artifact.sh

# Generate results
./fig3.sh
./tab4.py
```

### Output
- `fig3.png` (matches Figure 3 in the paper)
- Table similar to first 5 columns of Table 4

---

## Experiment 2 (E2): Library Exploration

- **Goal**: Evaluate how LIBERATOR explores library internals
- **Claim supported**: (C2)
- **Time**: 2 min human, ~10 compute-hours
- **Depends on**: E1 results

### Steps

```bash
./fig4.sh
./fig5.sh
```

### Output
- `edge_coverage.png` (per library)
- `api_function_coverage.png` (per library)

---

## Experiment 3 (E3): Ablation Study

- **Goal**: Measure contribution of each module in LIBERATOR
- **Claim supported**: (C3)
- **Time**: 2 min human, ~24 compute-hours
- **Depends on**: E1 results

### Steps

```bash
./tab9.sh
./tab10.sh
```

### Output
- Tables similar to Table 9 and Table 10 from the paper

---

## Major Claims Supported

- **(C1)** LIBERATOR captures the trade-off between creating and testing drivers  
- **(C2)** LIBERATOR diversifies coverage across libraries  
- **(C3)** LIBERATOR’s design is modular and effective (confirmed by ablation)

---

## Resources

- Main repo: [github.com/HexHive/liberator](https://github.com/HexHive/liberator)
- Artifact version: `fse-25-artifact`
- Competitor instructions: [`COMPETITORS.md`](https://github.com/HexHive/liberator/blob/main/COMPETITORS.md)
- Paper DOI: [10.5281/zenodo.14888072](https://doi.org/10.5281/zenodo.14888072)

---
