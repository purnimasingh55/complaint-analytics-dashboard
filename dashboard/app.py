"""
app.py — Complaint Monitoring Dashboard
----------------------------------------
An interactive dashboard for monitoring consumer complaints: volume trends,
category breakdown, resolution performance, and a live text-classification
demo. Built with Streamlit + Plotly (both free/open-source — no Power BI
subscription required to run or share this).

Run with:
    streamlit run dashboard/app.py
"""

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Consumer Complaint Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = "data/complaints.csv"
MODEL_PATH = "models/complaint_classifier.joblib"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date_filed"])
    df["month"] = df["date_filed"].dt.to_period("M").astype(str)
    return df


@st.cache_resource
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        return None


df = load_data()
model = load_model()

st.title("📊 Consumer Complaint Monitoring Dashboard")
st.caption(
    "Demo analytics platform for tracking complaint volume, category trends, "
    "and resolution performance — built as a portfolio project modelled on "
    "consumer-grievance monitoring workflows."
)

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

categories = sorted(df["category"].unique())
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories
)

states = sorted(df["state"].unique())
selected_states = st.sidebar.multiselect("State", states, default=states)

date_min, date_max = df["date_filed"].min(), df["date_filed"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max
)

filtered = df[
    df["category"].isin(selected_categories) & df["state"].isin(selected_states)
]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[(filtered["date_filed"] >= start) & (filtered["date_filed"] <= end)]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
total_complaints = len(filtered)
resolved_pct = (
    (filtered["status"].isin(["Resolved", "Closed - No Action"]).sum() / total_complaints * 100)
    if total_complaints else 0
)
avg_resolution = filtered["resolution_days"].dropna()
avg_resolution = avg_resolution[avg_resolution != ""]
avg_resolution_days = pd.to_numeric(avg_resolution, errors="coerce").mean()
escalated_pct = (
    (filtered["status"].eq("Escalated").sum() / total_complaints * 100)
    if total_complaints else 0
)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Complaints", f"{total_complaints:,}")
k2.metric("Resolved / Closed", f"{resolved_pct:.1f}%")
k3.metric("Avg. Resolution Time", f"{avg_resolution_days:.1f} days" if pd.notna(avg_resolution_days) else "N/A")
k4.metric("Escalated", f"{escalated_pct:.1f}%")

st.divider()

# ---------------------------------------------------------------------------
# Row 1: category breakdown + status breakdown
# ---------------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Complaints by Category")
    cat_counts = filtered["category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig_cat = px.bar(
        cat_counts.sort_values("count"),
        x="count", y="category", orientation="h",
        text="count", color="count", color_continuous_scale="Blues",
    )
    fig_cat.update_layout(showlegend=False, coloraxis_showscale=False, height=400)
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    st.subheader("Status Breakdown")
    status_counts = filtered["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig_status = px.pie(status_counts, names="status", values="count", hole=0.45)
    fig_status.update_layout(height=400)
    st.plotly_chart(fig_status, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 2: monthly trend (with drill-through-style interaction)
# ---------------------------------------------------------------------------
st.subheader("Monthly Complaint Volume Trend")
monthly = filtered.groupby(["month", "category"]).size().reset_index(name="count")
fig_trend = px.line(
    monthly, x="month", y="count", color="category", markers=True,
)
fig_trend.update_layout(height=450, xaxis_title="Month", yaxis_title="Complaints")
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(
    "Tip: click a category in the legend to isolate its trend line — a simple "
    "stand-in for Power BI's drill-through interactivity."
)

# ---------------------------------------------------------------------------
# Row 3: state-wise heatmap-style table
# ---------------------------------------------------------------------------
st.subheader("Top States by Complaint Volume")
state_counts = filtered["state"].value_counts().reset_index().head(10)
state_counts.columns = ["state", "count"]
fig_state = px.bar(state_counts, x="state", y="count", color="count", color_continuous_scale="Oranges")
fig_state.update_layout(height=350, coloraxis_showscale=False)
st.plotly_chart(fig_state, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Live classification demo
# ---------------------------------------------------------------------------
st.subheader("🔎 Live Complaint Classifier")
st.caption(
    "Type a complaint narrative below to see the model automatically classify "
    "it into a category — this is the kind of automation that could support "
    "systematic complaint triage."
)

user_text = st.text_area(
    "Enter a complaint narrative",
    placeholder="e.g. My UPI payment failed but the amount was still deducted from my account.",
)

if st.button("Classify Complaint"):
    if model is None:
        st.error("Model file not found. Run `python src/train_classifier.py` first.")
    elif not user_text.strip():
        st.warning("Please enter some complaint text first.")
    else:
        pred = model.predict([user_text])[0]
        proba = model.predict_proba([user_text])[0]
        classes = model.classes_
        top_idx = proba.argsort()[::-1][:3]
        st.success(f"Predicted category: **{pred}**")
        st.write("Top matches:")
        for i in top_idx:
            st.write(f"- {classes[i]}: {proba[i]*100:.1f}%")

st.divider()
with st.expander("About this dashboard"):
    st.markdown(
        """
        **Data:** Synthetic complaint records generated to mirror realistic
        consumer-banking complaint categories, phrasing, channels, and
        resolution patterns (see `data/generate_data.py`).

        **Model:** TF-IDF + Logistic Regression trained on the complaint
        narratives (see `src/train_classifier.py`).

        **Stack:** Python, pandas, scikit-learn, Streamlit, Plotly — fully
        open-source, no paid licenses required to build or share.
        """
    )
