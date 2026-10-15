# COVID-19 Simulation Lab

An interactive Streamlit dashboard for exploring an age-group-based COVID-19 health-state simulation using a Markov-chain model. The app runs the simulation, summarizes country-level daily counts, visualizes trends, and exports CSV results.

> **Important:** This is an educational simulation, not a clinical forecast or a source of real-world medical advice.

## Features

- Interactive country, date-range, and population-sampling controls
- Markov-chain simulation using age-group-specific transition probabilities and holding times
- Country-level health-state summaries and individual-level time-series output
- Animated dashboard styling, responsive metric cards, and tabbed navigation
- Time-series area chart and country comparison charts
- Filterable summary table and CSV downloads
- Input validation, progress feedback, and model limitations documented in the UI

## Tech stack

Python 3.11+, Pandas, Streamlit, Matplotlib.

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate       # macOS/Linux
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run streamlit_ui.py
```

Open the local URL printed by Streamlit.

## Run the assignment test

```bash
python -m unittest test.py
```

The assignment test runs a full simulation and regenerates the CSV and PNG output files. Because the model is stochastic, the exact values can vary between runs.

## Project structure

```text
.
├── assignment2.py                 # Simulation implementation
├── streamlit_ui.py                # Interactive dashboard
├── sim_parameters.py              # State transitions and holding times
├── helper.py                      # Plot generation helper
├── a2-countries.csv                # Country demographic input
├── test.py                        # Assignment test
├── a2-covid-summary-timeseries.csv # Aggregated output (generated)
├── a2-covid-simulated-timeseries.csv # Person-level output (generated)
└── a2-covid-simulation.png         # Plot output (generated)
```

## Model states

| Code | Meaning |
|---|---|
| H | Healthy |
| I | Infected without symptoms |
| S | Infected with symptoms |
| M | Immune |
| D | Deceased |

## Notes on reproducibility

The simulation uses Python's `random` module without a fixed seed, so repeated runs may produce different outcomes. Outputs are written next to the Python source files. Do not interpret summed state-days as unique people or as a real-world mortality estimate.

## Academic integrity and attribution

If this project was developed for a course, follow the course's rules on permitted modifications and public repository sharing. Clearly distinguish course-provided starter files from your own changes, and do not publish restricted assignment materials or claim features you did not implement.
