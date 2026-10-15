# 🧬 COVID-19 Simulation Lab

An interactive web application for exploring simulated COVID-19 health-state transitions across multiple countries. Built with Python, Pandas, Streamlit, and Altair, this project combines stochastic simulation, data processing, and interactive visualisation in a browser-based dashboard.

<p align="center">
  <a href="https://covid-simulation.streamlit.app/"><strong>🚀 Live Demo</strong></a>
  &nbsp; · &nbsp;
  <a href="https://github.com/Shameendudekula/covid-simulation"><strong>GitHub Repository</strong></a>
</p>

## Overview

COVID-19 Simulation Lab allows users to configure a simulation, explore country-level health-state distributions over time, compare outcomes, and export the generated data for further analysis.

The application uses an educational, age-group-based Markov simulation model. It is intended for learning and experimentation, not for predicting real-world COVID-19 outcomes.

## Features

- **Configurable simulations:** Select countries, start and end dates, and a population sample ratio.
- **Country-level visualisation:** Explore separate health-state time-series charts for each selected country.
- **Interactive dashboard:** View simulation metrics and navigate between analysis, comparison, data exploration, and model information.
- **Country comparison:** Compare a selected health state across countries.
- **Data exploration:** Inspect generated country-level summary data.
- **CSV exports:** Download filtered summary data and individual-level simulation records.
- **Input validation:** Detect invalid date ranges, missing country selections, and invalid sample ratios.
- **Reproducible outputs:** Generate simulation datasets and a PNG visualisation through the project's Python workflow.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Simulation logic and application development |
| Pandas | Data processing and aggregation |
| Streamlit | Interactive web application |
| Altair | Interactive charts |
| Matplotlib | Static visualisation output |
| Git and GitHub | Version control and source hosting |

## Model States

The dashboard represents the following health states:

| Code | State | Description |
|---|---|---|
| H | Healthy | Healthy state |
| I | Infected, asymptomatic | Infected without symptoms |
| S | Symptomatic | Infected with symptoms |
| M | Immune | Immune state |
| D | Deceased | Deceased state |

The model uses age-group-specific transition probabilities and holding times to simulate movement between health states. Country-level daily counts are aggregated from individual-level simulation records.

## Getting Started

### Prerequisites

- Python 3.11 recommended
- Git
- A terminal or command-line interface

### 1. Clone the repository

```bash
git clone https://github.com/Shameendudekula/covid-simulation.git
cd covid-simulation
```

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run streamlit_ui.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

## How to Use the Dashboard

1. Open the application.
2. Select one or more countries in the sidebar.
3. Choose the simulation start date and end date.
4. Set the population sample ratio.
5. Click **Run simulation**.
6. Explore the country-level charts and country comparison tab.
7. Inspect the generated summary data and download the available CSV files.

A larger population sample ratio generally produces fewer simulated people, because the ratio controls how the population is sampled.

## Project Structure

```text
covid-simulation/
├── assignment2.py
├── streamlit_ui.py
├── helper.py
├── sim_parameters.py
├── a2-countries.csv
├── requirements.txt
├── test.py
├── README.md
└── .gitignore
```

### Generated outputs

The simulation can generate the following files in the project directory:

- `a2-covid-simulated-timeseries.csv` — individual-level simulation records.
- `a2-covid-summary-timeseries.csv` — country-level daily health-state counts.
- `a2-covid-simulation.png` — static visualisation of the simulation results.

These are generated outputs rather than required source files, so they do not need to be committed to GitHub.

## Deployment

The application is deployed using Streamlit Community Cloud.

**Live application:** https://covid-simulation.streamlit.app/

The deployed app is connected to the GitHub repository, allowing the application to be updated when changes are pushed to the configured branch.

## Limitations

- This is a simplified educational stochastic simulation.
- Results depend on the model's transition probabilities, holding times, population sampling, and simulation settings.
- Simulated results should not be interpreted as observed COVID-19 statistics.
- The model is not calibrated for real-world epidemiological forecasting and should not be used for medical or public-policy decisions.
- Generated files and application state may not persist across hosted application restarts.

## Future Improvements

- Add automated tests for simulation and data-processing behaviour.
- Improve validation and reporting for simulation edge cases.
- Expand visualisation and statistical comparison options.
- Improve reproducibility through explicit random-seed controls where supported by the simulation implementation.

## Author

**Shameen Dudekula**

- GitHub: https://github.com/Shameendudekula
- Project repository: https://github.com/Shameendudekula/covid-simulation
- Live demo: https://covid-simulation.streamlit.app/

---

*Built as a Python-based simulation and data visualisation project for learning and experimentation.*