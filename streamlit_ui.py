from pathlib import Path
from datetime import date
import io

import pandas as pd
import streamlit as st
import altair as alt

import assignment2

BASE_DIR = Path(__file__).resolve().parent
COUNTRIES_FILE = BASE_DIR / "a2-countries.csv"
SIMULATION_FILE = BASE_DIR / "a2-covid-simulated-timeseries.csv"
SUMMARY_FILE = BASE_DIR / "a2-covid-summary-timeseries.csv"
PLOT_FILE = BASE_DIR / "a2-covid-simulation.png"

st.set_page_config(
    page_title="COVID-19 | Simulation Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root { --ink:#172033; --muted:#667085; --teal:#0f9b8e; --violet:#7667f4; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f7f9fc 0%,#eef5f7 55%,#f5f2ff 100%); }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.035em; }
.hero { padding:2rem 2.1rem; border-radius:24px; color:white; background:linear-gradient(120deg,#101b36,#155e75 65%,#0f9b8e); box-shadow:0 16px 45px rgba(16,27,54,.18); animation:rise .65s ease-out both; }
.hero h1 { color:white; font-size:2.45rem; margin:0; }
.hero p { color:#d8f3f2; margin:.65rem 0 0; font-size:1.04rem; max-width:760px; }
.eyebrow { color:#8ff0df; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; margin-bottom:.7rem; }
.metric-card { background:rgba(255,255,255,.88); border:1px solid rgba(222,230,239,.9); border-radius:18px; padding:1rem 1.15rem; box-shadow:0 8px 24px rgba(28,45,75,.05); transition:transform .2s ease, box-shadow .2s ease; animation:rise .5s ease-out both; }
.metric-card:hover { transform:translateY(-4px); box-shadow:0 14px 30px rgba(28,45,75,.10); }
.metric-label { color:#667085; font-size:.82rem; font-weight:600; }
.metric-value { color:#172033; font-family:'Space Grotesk',sans-serif; font-size:1.8rem; font-weight:700; margin-top:.28rem; }
.metric-note { color:#667085; font-size:.76rem; margin-top:.15rem; }
.section-kicker { color:#0f9b8e; text-transform:uppercase; font-size:.72rem; font-weight:700; letter-spacing:.12em; }
div[data-testid="stTabs"] button { font-weight:600; }
.stButton > button { border-radius:12px; min-height:2.8rem; font-weight:700; transition:all .18s ease; }
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 7px 18px rgba(15,155,142,.18); }
div[data-testid="stSidebar"] { background:rgba(255,255,255,.8); }
.footer { text-align:center; color:#7b8495; font-size:.8rem; padding:1.8rem 0 .6rem; }
@keyframes rise { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
@media (prefers-reduced-motion: reduce) { *,*::before,*::after { animation:none !important; transition:none !important; } }
</style>
""", unsafe_allow_html=True)

def metric_card(label, value, note=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
        unsafe_allow_html=True,
    )

def read_csv_if_exists(path):
    if path.exists():
        try:
            return pd.read_csv(path)
        except (OSError, pd.errors.ParserError, UnicodeDecodeError):
            return pd.DataFrame()
    return pd.DataFrame()

countries_df = pd.read_csv(COUNTRIES_FILE)
country_options = sorted(countries_df["country"].dropna().unique().tolist())

with st.sidebar:
    st.markdown("## 🧪 Simulation controls")
    st.caption("Configure the experiment, then run the model.")
    selected_countries = st.multiselect(
        "Countries",
        options=country_options,
        default=[c for c in ["Sweden", "Japan", "Afghanistan"] if c in country_options],
        help="Choose one or more countries to compare.",
    )
    start_date = st.date_input("Start date", value=date(2021, 4, 1))
    end_date = st.date_input("End date", value=date(2022, 4, 30))
    sample_ratio = st.number_input(
        "Population sample ratio",
        min_value=1.0,
        value=1_000_000.0,
        step=100_000.0,
        format="%.0f",
        help="A larger ratio produces fewer simulated people. Samples are approximate.",
    )
    run_clicked = st.button("▶ Run simulation", type="primary", width="stretch")
    st.divider()
    st.markdown("**Model states**")
    st.markdown("🟢 **H** · Healthy")
    st.markdown("🟠 **I** · Infected, asymptomatic")
    st.markdown("🔴 **S** · Symptomatic")
    st.markdown("🟦 **M** · Immune")
    st.markdown("⚫ **D** · Deceased")
    st.caption("Educational Markov-chain simulation — not a clinical forecast.")

st.markdown("""
<div class="hero">
  <div class="eyebrow">Interactive epidemiology workspace</div>
  <h1>COVID-19 Simulation Lab</h1>
  <p>Explore how health states evolve over time using an age-group-based Markov model.
  Configure a run, compare country-level outcomes, and export the underlying data.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

if run_clicked:
    if not selected_countries:
        st.error("Select at least one country before running the simulation.")
    elif start_date > end_date:
        st.error("The start date must be on or before the end date.")
    elif sample_ratio <= 0:
        st.error("The sample ratio must be greater than zero.")
    else:
        try:
            with st.spinner("Simulating individual health-state transitions…"):
                with st.status("Running simulation", expanded=True) as status:
                    st.write("Sampling people from country age distributions")
                    sim_df, summary_df = assignment2.run(
                        countries_csv_name=COUNTRIES_FILE.name,
                        countries=selected_countries,
                        sample_ratio=sample_ratio,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    st.write("Aggregating country-level daily counts")
                    status.update(label="Simulation complete", state="complete", expanded=False)
            st.session_state["last_run"] = {
                "countries": selected_countries,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "sample_ratio": sample_ratio,
                "records": len(sim_df),
                "people": int(sim_df["person_id"].nunique()) if not sim_df.empty else 0,
            }
            st.success("Simulation completed. Results are ready below.")
        except (ValueError, OSError, KeyError) as exc:
            st.error(f"Simulation could not be completed: {exc}")

summary_df = read_csv_if_exists(SUMMARY_FILE)
sim_df = read_csv_if_exists(SIMULATION_FILE)
last_run = st.session_state.get("last_run")

if summary_df.empty:
    st.info("Choose countries and select **Run simulation** to generate your first result.")
    st.markdown("### How to use this workspace")
    st.write("1. Select countries and a date range in the sidebar.")
    st.write("2. Run the simulation to generate daily person-level and country-level CSV files.")
    st.write("3. Explore the charts and download the outputs for further analysis.")
else:
    summary_df["date"] = pd.to_datetime(summary_df["date"], errors="coerce")
    summary_df = summary_df.dropna(subset=["date"])
    available_countries = sorted(summary_df["country"].dropna().unique().tolist())
    default_filter = last_run["countries"] if last_run else available_countries
    default_filter = [c for c in default_filter if c in available_countries] or available_countries
    with st.container():
        filter_col, note_col = st.columns([2, 3])
        with filter_col:
            visible_countries = st.multiselect(
                "Countries shown in charts",
                options=available_countries,
                default=default_filter,
                key="chart_country_filter",
            )
        with note_col:
            if last_run:
                st.caption(f"Latest run: {last_run['start_date']} → {last_run['end_date']} · "
                           f"Sample ratio {last_run['sample_ratio']:,.0f}")
            else:
                st.caption("Showing the latest result files currently available in this folder.")

    view = summary_df[summary_df["country"].isin(visible_countries)].copy()
    state_cols = [c for c in ["H", "I", "S", "M", "D"] if c in view.columns]
    people_count = int(sim_df["person_id"].nunique()) if "person_id" in sim_df.columns and not sim_df.empty else 0
    total_records = len(sim_df)
    total_days = view["date"].nunique()
    total_countries = view["country"].nunique()
    latest_date = view["date"].max() if not view.empty else None
    latest_total = int(view[view["date"] == latest_date][state_cols].sum().sum()) if latest_date is not None else 0
    deaths = int(view["D"].sum()) if "D" in view.columns else 0
    symptomatic = int(view["S"].sum()) if "S" in view.columns else 0

    cols = st.columns(4)
    with cols[0]: metric_card("Simulated people", f"{people_count:,}", "Unique person IDs")
    with cols[1]: metric_card("Daily time points", f"{total_days:,}", "Dates in current view")
    with cols[2]: metric_card("Countries in view", f"{total_countries:,}", "Selected for analysis")
    with cols[3]: metric_card("Person-day records", f"{total_records:,}", "Individual-level output")
    st.write("")

    tab_overview, tab_compare, tab_data, tab_about = st.tabs(
        ["📈 Overview", "🌍 Country comparison", "🧾 Data explorer", "ℹ️ Model notes"]
    )
    with tab_overview:
        st.markdown('<div class="section-kicker">Time-series analysis</div>', unsafe_allow_html=True)
        st.subheader("Health-state distribution over time")
        if view.empty or not state_cols:
            st.warning("No data available for the selected countries.")
        else:
            # Keep country data separate: do not sum countries into one misleading total.
            for country in visible_countries:
                country_daily = (
                    view[view["country"] == country]
                    .groupby("date", as_index=False)[state_cols]
                    .sum()
                    .sort_values("date")
                )
                if country_daily.empty:
                    continue
                st.markdown(f"#### {country}")
                chart_data = country_daily.melt(
                    id_vars="date", value_vars=state_cols,
                    var_name="state", value_name="people",
                )
                chart_data["state_name"] = chart_data["state"].map({
                    "H": "Healthy", "I": "Infected (asymptomatic)",
                    "S": "Symptomatic", "M": "Immune", "D": "Deceased",
                })
                state_order = {
                    "Healthy": 0,
                    "Infected (asymptomatic)": 1,
                    "Symptomatic": 2,
                    "Immune": 3,
                    "Deceased": 4,
                }
                chart_data["state_order"] = chart_data["state_name"].map(state_order)
                chart = (
                    alt.Chart(chart_data)
                    .mark_area(opacity=0.82, interpolate="monotone")
                    
                    .encode(
                        x=alt.X(
                            "date:T",
                            title="Date",
                            axis=alt.Axis(format="%b %Y", labelAngle=-35, tickCount=7),
                        ),
                        y=alt.Y(
                            "people:Q",
                            stack="zero",
                            title="Simulated people",
                        ),
                        color=alt.Color(
                            "state_name:N",
                            title="Health state",
                            scale=alt.Scale(
                                domain=[
                                    "Healthy",
                                    "Infected (asymptomatic)",
                                    "Symptomatic",
                                    "Immune",
                                    "Deceased",
                                ],
                                range=[
                                    "green",
                                    "darkorange",
                                    "indianred",
                                    "lightseagreen",
                                    "slategray",
                                ],
                            ),
                        ),
                        order=alt.Order("state_order:Q", sort="ascending"),
                        tooltip=[
                            alt.Tooltip("date:T", title="Date", format="%d %b %Y"),
                            alt.Tooltip("state_name:N", title="State"),
                            alt.Tooltip("people:Q", title="People", format=",.0f"),
                        ],
                    )

                    .properties(height=270)
                )
                st.altair_chart(chart, width="stretch")
            st.caption("Each country is charted separately. Axis labels include month and year; hover for exact dates and counts.")
        left, right = st.columns(2)
        with left:
            st.subheader("Latest state counts")
            if latest_date is not None:
                latest = view[view["date"] == latest_date].groupby("country")[state_cols].sum()
                st.dataframe(latest, width="stretch")
        with right:
            st.subheader("Outcome snapshot")
            st.markdown(f"**Symptomatic state-days:** {symptomatic:,}")
            st.markdown(f"**Deceased state-days:** {deaths:,}")
            st.caption("These totals sum daily counts across the selected time range; they are not unique people or a real-world mortality estimate.")
    with tab_compare:
        st.markdown('<div class="section-kicker">Compare geographies</div>', unsafe_allow_html=True)
        st.subheader("Country-level trends")
        if view.empty:
            st.info("Select at least one country.")
        else:
            compare_metric = st.selectbox(
                "State to compare",
                options=state_cols,
                format_func=lambda x: {
                    "H": "Healthy", "I": "Infected (asymptomatic)",
                    "S": "Symptomatic", "M": "Immune", "D": "Deceased"
                }.get(x, x),
            )
            compare_df = view[["date", "country", compare_metric]].copy()
            compare_df = compare_df.sort_values("date")
            compare_chart = (
                alt.Chart(compare_df)
                .mark_line(point=False, strokeWidth=2)
                .encode(
                    x=alt.X("date:T", title="Date",
                            axis=alt.Axis(format="%b %Y", labelAngle=-35, tickCount=7)),
                    y=alt.Y(f"{compare_metric}:Q", title="Simulated people"),
                    color=alt.Color("country:N", title="Country"),
                    tooltip=[
                        alt.Tooltip("country:N", title="Country"),
                        alt.Tooltip("date:T", title="Date", format="%d %b %Y"),
                        alt.Tooltip(f"{compare_metric}:Q", title="People", format=",.0f"),
                    ],
                )
                .properties(height=360)
            )
            st.altair_chart(compare_chart, width="stretch")
            country_totals = view.groupby("country")[state_cols].sum().sort_index()
            st.subheader("Aggregated state-days by country")
            st.bar_chart(country_totals, width="stretch")
    with tab_data:
        st.markdown('<div class="section-kicker">Inspect and export</div>', unsafe_allow_html=True)
        st.subheader("Country summary data")
        if view.empty:
            st.info("No rows match the selected countries.")
        else:
            display_df = view.copy()
            display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
            st.dataframe(display_df, width="stretch", hide_index=True)
            st.download_button(
                "⬇ Download filtered summary CSV",
                data=display_df.to_csv(index=False).encode("utf-8"),
                file_name="covid-summary-filtered.csv",
                mime="text/csv",
                width="content",
            )
        if not sim_df.empty:
            st.subheader("Individual-level simulation records")
            st.caption(f"{len(sim_df):,} records available in the full generated dataset.")
            st.download_button(
                "⬇ Download individual-level CSV",
                data=sim_df.to_csv(index=False).encode("utf-8"),
                file_name="covid-individual-timeseries.csv",
                mime="text/csv",
            )
    with tab_about:
        st.markdown('<div class="section-kicker">Interpretation & limitations</div>', unsafe_allow_html=True)
        st.subheader("How the model works")
        st.write("Each simulated person starts in the healthy (H) state. Age-group-specific transition probabilities and holding times determine when a person can move between states. Daily records are aggregated into country-level counts.")
        st.write("The transition probabilities and holding times are configured in `sim_parameters.py`; demographic proportions are read from `a2-countries.csv`.")
        st.warning("This is a simplified educational stochastic simulation. It is not calibrated for real-world prediction, does not represent current epidemiological evidence, and should not be used for medical or policy decisions.")
        st.markdown("**State definitions**")
        st.dataframe(pd.DataFrame([
            {"Code":"H","Meaning":"Healthy"},
            {"Code":"I","Meaning":"Infected without symptoms"},
            {"Code":"S","Meaning":"Infected with symptoms"},
            {"Code":"M","Meaning":"Immune"},
            {"Code":"D","Meaning":"Deceased"},
        ]), width="stretch", hide_index=True)

st.markdown('<div class="footer">COVID-19 Simulation Lab · Python · Pandas · Streamlit · Matplotlib<br>Educational simulation, not medical advice.</div>', unsafe_allow_html=True)
