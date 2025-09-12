# Neuro-Symbolic Planning for Enhancing Coherence and Believability in Large Language Model-Driven Agents

<p align="center" width="100%">
<img src="cover.png" alt="Neuro-Symbolic Planning" style="width: 80%; min-width: 300px; display: block; margin: auto;">
</p>

This repository accompanies our master’s thesis project, **“Neuro-Symbolic Planning for Enhancing Coherence and Believability in Large Language Model-Driven Agents.”**
It extends the [Generative Agents](https://arxiv.org/abs/2304.03442) framework to explore how **neuro-symbolic planning** can improve logical consistency, environmental constraint adherence, and human-perceived believability in LLM-driven agents.

---

## 📖 Project Overview

### Problem Statement
Large Language Model-powered generative agents can simulate human-like behavior in interactive environments. However, they often suffer from:
- **Logical inconsistencies** (e.g., taking impossible actions),
- **Incoherent action sequences**, and
- **Reduced believability** from a human perspective.

To address these issues, this project replaces hierarchical planning with a **neuro-symbolic planning framework**, where:
- LLMs generate **PDDL schemas** to encode domain knowledge,
- A **symbolic planner** ensures logical and environmental coherence, and
- LLMs handle **natural language reasoning and commonsense grounding**.

The effectiveness of this approach will be evaluated in simulation environments, measuring:
1. **Environmental constraint adherence**, and
2. **Human-perceived believability** of agents.

### Project Details
- **Title:** Neuro-Symbolic Planning for Enhancing Coherence and Believability in Large Language Model-Driven Agents
- **ECTS:** 30
- **Period:** September 1, 2025 – February 1, 2026
- **Students:**
  - Jeremi Wojciech Ledwon (s232952)
  - Alexandre Comas Gispert (s233148)

---

## ⚙️ Setup Instructions

This repository builds on the original **Generative Agents** codebase. You will need to set up the simulation environment and connect your OpenAI API key.

### Step 1. Generate `utils.py`
In the `reverie/backend_server` folder (where `reverie.py` is located), create a file called `utils.py` with the following content:

```python
# Copy and paste your OpenAI API Key
openai_api_key = "<Your OpenAI API>"
# Put your name
key_owner = "<Name>"

maze_assets_loc = "../../environment/frontend_server/static_dirs/assets"
env_matrix = f"{maze_assets_loc}/the_ville/matrix"
env_visuals = f"{maze_assets_loc}/the_ville/visuals"

fs_storage = "../../environment/frontend_server/storage"
fs_temp_storage = "../../environment/frontend_server/temp_storage"

collision_block_id = "32125"

# Verbose
debug = True
```

Replace `<Your OpenAI API>` and `<Name>` accordingly.

### Step 2. Install Dependencies

This project uses **uv** as the package manager for faster dependency management and better reproducibility.

#### Option 1: Using uv (Recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync
```

#### Option 2: Using pip (Legacy)
```bash
pip install -r requirements.txt
```

> Tested with **Python 3.9.12**. The project now uses `pyproject.toml` for dependency management with uv.

---

## ▶️ Running the Simulation

The simulation requires running both the **environment server** and the **agent simulation server**.

1. **Start the Environment Server**
```bash
cd environment/frontend_server
uv run python manage.py runserver
# OR with activated environment: python manage.py runserver
```
Visit [http://localhost:8000/](http://localhost:8000/) to verify it is running.

2. **Start the Simulation Server**
```bash
cd reverie/backend_server
uv run python reverie.py
```
Follow the prompts to load or create a simulation (e.g., `base_the_ville_isabella_maria_klaus`).

3. **Run a Simulation**
At the simulation server prompt:
```bash
run <step-count>
```
Each step represents 10 seconds in-game.

4. **Replay or Demo a Simulation**
- Replay: [http://localhost:8000/replay/<simulation-name>/<step>](http://localhost:8000/replay/<simulation-name>/<step>)
- Demo: [http://localhost:8000/demo/<simulation-name>/<step>/<speed>](http://localhost:8000/demo/<simulation-name>/<step>/<speed>)

---

## 🛠 Customization

- **Agent Histories:** Initialize agents with unique past experiences by loading history CSV files.
- **Base Simulations:** Author new base environments or modify existing ones using [Tiled](https://www.mapeditor.org/).
- **Neuro-Symbolic Planning Extensions (Thesis Contribution):**
  - LLM → PDDL schema generation
  - Symbolic planner integration for action validation
  - Comparative evaluation metrics

---

## 👩‍🎓 Authors

- Jeremi Wojciech Ledwon (s232952)
- Alexandre Comas Gispert (s233148)

Master’s Thesis, 30 ECTS
September 2025 – February 2026

---

## 📚 References

If you build on this work, please also cite the original **Generative Agents** paper:

```bibtex
@inproceedings{Park2023GenerativeAgents,
author = {Park, Joon Sung and O'Brien, Joseph C. and Cai, Carrie J. and Morris, Meredith Ringel and Liang, Percy and Bernstein, Michael S.},
title = {Generative Agents: Interactive Simulacra of Human Behavior},
year = {2023},
booktitle = {UIST '23},
publisher = {ACM},
location = {San Francisco, CA, USA},
keywords = {Human-AI interaction, agents, generative AI, large language models}
}
```

---

## 🙏 Acknowledgements

This project builds on the [Generative Agents repository](https://github.com/joonspk-research/generative-agents).
We thank the original authors and artists for releasing their code, assets, and insights.
