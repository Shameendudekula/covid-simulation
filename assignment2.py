import random
from pathlib import Path

import pandas as pd

import helper
from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES


AGE_GROUPS = ["less_5", "5_to_14", "15_to_24", "25_to_64", "over_65"]
STATES = ["H", "I", "S", "M", "D"]


def _file_path(filename):
    """Return a path relative to this Python file."""
    return Path(__file__).resolve().parent / filename


def _load_countries(filename):
    """Read the country demographic data."""
    return pd.read_csv(_file_path(filename))


def _create_samples(country_row, sample_ratio, start_person_id):
    """
    Create one dictionary per simulated person.

    The total number of samples is population / sample_ratio, rounded to
    the nearest integer, and then divided among age groups using the
    percentages in the country data.
    """
    population = float(country_row["population"])
    total_samples = int(round(population / sample_ratio))

    age_counts = {}
    for age_group in AGE_GROUPS:
        percentage = float(country_row[age_group])
        age_counts[age_group] = int(round(total_samples * percentage / 100))

    # Rounding each age group independently can make the sum differ from
    # total_samples. Adjust the largest age group so the total is exact.
    difference = total_samples - sum(age_counts.values())
    if difference != 0:
        largest_group = max(AGE_GROUPS, key=lambda group: age_counts[group])
        age_counts[largest_group] += difference

    samples = []
    person_id = start_person_id

    for age_group in AGE_GROUPS:
        for _ in range(max(0, age_counts[age_group])):
            samples.append({
                "person_id": person_id,
                "age_group_name": age_group,
                "country": country_row["country"],
            })
            person_id += 1

    return samples


def _choose_next_state(age_group, current_state):
    """Choose the next state using the transition probabilities."""
    probabilities = TRANSITION_PROBS[age_group][current_state]
    states = list(probabilities.keys())
    weights = list(probabilities.values())
    return random.choices(states, weights=weights, k=1)[0]


def _simulate_person(age_group, dates):
    """
    Simulate one person's state for all dates.

    A holding time of 0 is treated as one day.
    staying_days counts how many days the person has already
    stayed in the current state.
    """
    state = "H"
    prev_state = "H"
    staying_days = 0
    holding_time = max(1, HOLDING_TIMES[age_group][state])

    rows = []

    for date in dates:
        rows.append({
            "date": date.strftime("%Y-%m-%d"),
            "state": state,
            "staying_days": staying_days,
            "prev_state": prev_state,
        })

        # Save the state shown on today's row.
        current_state = state

        staying_days += 1

        if staying_days >= holding_time:
            next_state = _choose_next_state(age_group, state)

            state = next_state
            holding_time = max(1, HOLDING_TIMES[age_group][state])
            staying_days = 0

        # Tomorrow's prev_state is today's state.
        prev_state = current_state

    return rows


def _create_simulation(countries, dates, samples):
    """Run the Markov-chain simulation for every sampled person."""
    records = []

    for person in samples:
        person_rows = _simulate_person(person["age_group_name"], dates)

        for row in person_rows:
            records.append({
                "person_id": person["person_id"],
                "age_group_name": person["age_group_name"],
                "country": person["country"],
                **row,
            })

    return pd.DataFrame(
        records,
        columns=[
            "person_id",
            "age_group_name",
            "country",
            "date",
            "state",
            "staying_days",
            "prev_state",
        ],
    )


def _create_summary(simulation_df):
    """Count H, I, S, M and D for every country and date."""
    summary = (
        simulation_df
        .pivot_table(
            index=["date", "country"],
            columns="state",
            values="person_id",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )

    for state in STATES:
        if state not in summary.columns:
            summary[state] = 0

    summary = summary[
        ["date", "country", "D", "H", "I", "M", "S"]
    ]

    return summary


def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    """
    Run the complete COVID-19 simulation.

    Required public interface:
    run(countries_csv_name, countries, sample_ratio, start_date, end_date)
    """
    if sample_ratio <= 0:
        raise ValueError("sample_ratio must be greater than zero")

    if not countries:
        raise ValueError("At least one country must be selected")

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)

    if start > end:
        raise ValueError("start_date must be before or equal to end_date")

    country_df = _load_countries(countries_csv_name)

    missing = [country for country in countries
               if country not in set(country_df["country"])]
    if missing:
        raise ValueError(f"Country/countries not found: {missing}")

    selected_df = country_df[country_df["country"].isin(countries)]

    samples = []
    next_person_id = 0

    for _, row in selected_df.iterrows():
        country_samples = _create_samples(row, sample_ratio, next_person_id)
        samples.extend(country_samples)
        next_person_id += len(country_samples)

    dates = pd.date_range(start=start, end=end, freq="D")

    simulation_df = _create_simulation(countries, dates, samples)
    summary_df = _create_summary(simulation_df)

    simulation_path = _file_path("a2-covid-simulated-timeseries.csv")
    summary_path = _file_path("a2-covid-summary-timeseries.csv")

    simulation_df.to_csv(simulation_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    helper.create_plot(
        "a2-covid-summary-timeseries.csv",
        countries,
    )

    print("Simulation completed.")
    print(f"Samples: {len(samples)}")
    print(f"Days: {len(dates)}")
    print(f"Simulation records: {len(simulation_df)}")
    print(f"Saved: {simulation_path.name}")
    print(f"Saved: {summary_path.name}")
    print(f"Saved: {helper.OUTPUT_NAME}")

    return simulation_df, summary_df
