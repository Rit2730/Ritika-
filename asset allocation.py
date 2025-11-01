# app.py
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Multi-Profile Investment Dashboard", layout="wide", page_icon="💼")

st.title("💼 Multi-Profile Investment Dashboard")
st.markdown(
    "This app contains three sample portfolios (Low, Moderate, High risk) based on the data you provided. "
    "Choose a profile, edit values inline, normalize allocations, filter, and export as CSV."
)

# ---------------------------
# Predefined portfolio data
# ---------------------------
LOW_DATA = {
    "Asset Class": [
        "Government Bonds (G-sec)", "AAA Corporate Bonds", "PPF / NSC / Small Savings",
        "Fixed Deposits", "Short/Mid-Term Debt Funds", "REITs", "Gold (SGB/ETF)",
        "Target Maturity Debt ETFs", "Annuity Plans / Pension Income", "Infra Debt / InvIT Debt"
    ],
    "Risk": [
        "Very Low", "Low", "Very Low", "Very Low", "Low",
        "Low–Mod", "Moderate", "Low", "Very Low", "Low–Mod"
    ],
    "Returns (%)": ["4–7", "5–8", "6–7", "5–7", "4–7", "6–9", "3–8", "4–7", "3–6", "6–9"],
    "Horizon": [
        "3–10 yrs", "2–7 yrs", "5–15 yrs", "1–5 yrs", "1–5 yrs",
        "5–10 yrs", "3–10 yrs", "3–10 yrs", "Lifetime", "5–10 yrs"
    ],
    "Purpose": [
        "Secure income", "Higher income low risk", "Tax-efficient retirement corpus",
        "Capital protection", "Stable returns", "Monthly/quarterly income",
        "Inflation hedge", "Predictable maturity returns", "Guaranteed income", "Stability + diversification"
    ],
    "Allocation (%)": [30, 20, 10, 10, 10, 7, 5, 3, 3, 2]
}

MODERATE_DATA = {
    "Asset Class": [
        "Large-Cap Equity Funds", "Mid/Small-Cap Funds", "Global Equity ETFs/Funds",
        "Hybrid/Balanced Funds", "Corporate Bond Funds", "REITs",
        "Gold", "Private Credit / Debt AIF", "Farmland / Agro Real Assets", "Digital Asset Basket (tiny)"
    ],
    "Risk": ["High", "High", "High", "Moderate", "Moderate", "Moderate", "Moderate", "Mod–High", "Moderate", "High"],
    "Returns (%)": ["8–12", "10–15", "7–12", "7–10", "6–9", "6–10", "3–8", "8–12", "4–8", "Varies"],
    "Horizon": ["7–10 yrs", "7–12 yrs", "7–10 yrs", "5–8 yrs", "3–7 yrs", "5–10 yrs", "3–7 yrs", "3–7 yrs", "5–15 yrs", "5–10 yrs"],
    "Purpose": [
        "Core growth", "Higher alpha", "Geographic diversification", "Smoother volatility", "Income stability",
        "Property income", "Risk hedge", "Enhanced yield", "Real asset diversification", "Asymmetric payoff"
    ],
    "Allocation (%)": [25, 15, 10, 10, 10, 7, 5, 5, 5, 3]
}

HIGH_DATA = {
    "Asset Class": [
        "Domestic Equity (Large/Mid/Small)", "International Equities", "Venture Capital / Startup Investments",
        "Private Equity Funds", "Crypto / Blockchain Assets", "Commodities (Energy/Metals ETFs)",
        "Real Assets (Timber/Renewables)", "Structured Products / Hedge Funds", "IP / Music Royalties", "Active Derivatives (Hedged)"
    ],
    "Risk": ["Very High"] * 10,
    "Returns (%)": ["10–15", "8–15", "20+", "15+", "Highly variable", "Varies", "6–12", "Varies", "Variable", "Variable"],
    "Horizon": ["10–20 yrs"] * 10,
    "Purpose": [
        "Primary growth source", "Global growth exposure", "High innovation upside",
        "Superior alpha potential", "Speculative moonshot", "Cycle & inflation hedge",
        "Alternative diversifier", "Non-correlated returns", "Uncorrelated cash-flows", "Tactical"
    ],
    "Allocation (%)": [50, 15, 10, 7, 5, 5, 3, 3, 1, 1]
}

# Convert to DataFrames
df_profiles = {
    "Low Risk Profile": pd.DataFrame(LOW_DATA),
    "Moderate Risk Profile": pd.DataFrame(MODERATE_DATA),
    "High Risk Profile": pd.DataFrame(HIGH_DATA),
}

# ---------------------------
# Sidebar - profile + upload
# ---------------------------
st.sidebar.header("Profile & Data")
selected_profile = st.sidebar.selectbox("Choose portfolio profile", list(df_profiles.keys()))

st.sidebar.markdown("**Upload CSV** (optional) to replace this profile")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        # Basic validation: must have at least Asset Class and Allocation (%) and Returns (%) columns
        required = {"Asset Class", "Allocation (%)", "Returns (%)"}
        if not required.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must contain columns: {', '.join(required)}")
            uploaded_df = None
        else:
            # Use uploaded as profile data
            df_profiles[selected_profile] = uploaded_df.copy()
            st.sidebar.success("CSV loaded for the selected profile.")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")
        uploaded_df = None

# Persist currently selected profile's dataframe in session state
if "current_df" not in st.session_state:
    st.session_state.current_df = df_profiles[selected_profile].copy()
else:
    # when profile changes, update
    if st.session_state.get("profile_name", None) != selected_profile:
        st.session_state.current_df = df_profiles[selected_profile].copy()

st.session_state.profile_name = selected_profile

st.sidebar.markdown("---")
st.sidebar.subheader("Edit / Manage")
if st.sidebar.button("Reset to default for profile"):
    st.session_state.current_df = df_profiles[selected_profile].copy()
    st.sidebar.success("Reset to default data for selected profile.")

normalize_mode = st.sidebar.checkbox("Auto-normalize allocations to 100% on request", value=True)

st.sidebar.markdown("---")
st.sidebar.info("Tip: Edit values inline in the table below. Use 'Normalize allocations' to scale allocations to 100%.")

# ---------------------------
# Main - show and edit table
# ---------------------------
st.header(f"Selected Profile: {selected_profile}")
st.markdown("Edit the fields directly in the table (double-click a cell). When you're done, press **Apply changes**.")

# Use experimental_data_editor for inline editing (will work on Streamlit)
edited_df = st.experimental_data_editor(st.session_state.current_df, num_rows="dynamic")

# Apply changes to session_state
if st.button("Apply changes"):
    # Basic cleaning: ensure Allocation (%) numeric
    if "Allocation (%)" in edited_df.columns:
        edited_df["Allocation (%)"] = pd.to_numeric(edited_df["Allocation (%)"], errors="coerce").fillna(0.0)
    if "Returns (%)" in edited_df.columns:
        # Keep returns as strings typically (range like '4–7'), but try to parse average if in numeric form
        # For later numeric calculation we will attempt to compute avg numeric return if possible
        pass
    st.session_state.current_df = edited_df.copy()
    st.success("Changes applied to the profile data.")

# Offer Normalize allocations button
st.write("")  # spacing
col_norm, col_download = st.columns([1, 1])

with col_norm:
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df.get("Allocation (%)", pd.Series(dtype=float)).sum()
        if total == 0:
            st.error("Total allocation is 0; can't normalize.")
        else:
            factor = 100.0 / total
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] * factor).round(2)
            st.success("Allocations normalized to sum to 100%.")

with col_download:
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current table as CSV", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

# Show table (read-only copy)
st.subheader("Portfolio Table (current)")
st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

# ---------------------------
# Helper: compute numeric weighted average return
# We'll try to interpret `Returns (%)` column if numeric or ranges.
# ---------------------------
def parse_return_value(val):
    """
    Accepts strings like '4–7' or '4-7' or '6.5' or '20+' or 'Varies'
    Returns numeric average if parseable, else None.
    """
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    # remove percent sign if present
    s = s.replace("%", "")
    # replace unicode dash with hyphen
    s = s.replace("–", "-").replace("—", "-")
    if "+" in s:
        # e.g., "20+"
        s = s.replace("+", "")
        try:
            return float(s)
        except:
            return None
    if "-" in s:
        parts = s.split("-")
        try:
            nums = [float(p) for p in parts if p != ""]
            if len(nums) >= 2:
                return sum(nums[:2]) / 2.0
        except:
            return None
    try:
        return float(s)
    except:
        return None

# Compute weighted average return
df_calc = st.session_state.current_df.copy()
df_calc["_ParsedReturn"] = df_calc["Returns (%)"].apply(parse_return_value)
total_alloc = df_calc["Allocation (%)"].sum()
if total_alloc > 0:
    # Only include rows that parsed to numeric return, others omitted from weighted calc
    mask = df_calc["_ParsedReturn"].notna()
    if mask.any():
        weighted_sum = (df_calc.loc[mask, "_ParsedReturn"] * df_calc.loc[mask, "Allocation (%)"]).sum()
        weighted_avg_return = weighted_sum / df_calc["Allocation (%)"].sum()
    else:
        weighted_avg_return = None
else:
    weighted_avg_return = None

# ---------------------------
# Filters (Horizon / Purpose)
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filters (view only)")
horizons = sorted(st.session_state.current_df["Horizon"].dropna().unique().tolist())
selected_horizons = st.sidebar.multiselect("Horizon", options=horizons, default=horizons)
purposes = sorted(st.session_state.current_df["Purpose"].dropna().unique().tolist())
selected_purposes = st.sidebar.multiselect("Purpose", options=purposes, default=purposes)

view_df = st.session_state.current_df[
    st.session_state.current_df["Horizon"].isin(selected_horizons) &
    st.session_state.current_df["Purpose"].isin(selected_purposes)
].reset_index(drop=True)

st.subheader("Filtered View")
st.dataframe(view_df, use_container_width=True)

# ---------------------------
# Summaries and charts
# ---------------------------
st.subheader("Portfolio Summary & Metrics")
col_a, col_b, col_c = st.columns([1, 1, 1])

with col_a:
    st.metric("Total Allocation (%)", f"{total_alloc:.2f}")

with col_b:
    if weighted_avg_return is not None:
        st.metric("Weighted Avg Return (%)", f"{weighted_avg_return:.2f}")
    else:
        st.metric("Weighted Avg Return (%)", "N/A")

with col_c:
    # Risk breakdown
    risk_counts = st.session_state.current_df["Risk"].value_counts().to_dict()
    top_risk = max(risk_counts, key=risk_counts.get) if len(risk_counts) > 0 else "N/A"
    st.metric("Dominant Risk Type", str(top_risk))

# Simple charts using streamlit built-ins
st.subheader("Visuals")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Allocation (%) by Asset Class**")
    chart_alloc = st.session_state.current_df.set_index("Asset Class")["Allocation (%)"]
    # Make a DataFrame for bar_chart
    if chart_alloc.sum() == 0:
        st.info("No allocation data to chart.")
    else:
        st.bar_chart(chart_alloc)

with col2:
    st.markdown("**Parsed Returns (%) by Asset Class (numeric only)**")
    chart_ret = st.session_state.current_df.set_index("Asset Class")["_ParsedReturn"]
    if chart_ret.dropna().empty:
        st.info("No numeric returns parsed to show chart (some returns are ranges or 'Varies').")
    else:
        st.bar_chart(chart_ret.fillna(0))

# ---------------------------
# Automatic insights
# ---------------------------
st.subheader("Automatic Insights")
insights = []
if total_alloc < 90:
    insights.append("Total allocation is less than 90% — consider deploying remaining capital or check data.")
if total_alloc > 110:
    insights.append("Total allocation exceeds 110% — allocations likely not normalized.")
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insights.append("Portfolio appears conservative with lower expected returns (< 6%).")
    elif weighted_avg_return < 10:
        insights.append("Portfolio has a balanced expected return (6–10%).")
    else:
        insights.append("Portfolio expected return is comparatively high (>10%).")

# Risk concentration
if not st.session_state.current_df.empty:
    top_alloc_row = st.session_state.current_df.loc[st.session_state.current_df["Allocation (%)"].idxmax()]
    top_asset = top_alloc_row["Asset Class"]
    top_alloc = top_alloc_row["Allocation (%)"]
    if top_alloc >= 35:
        insights.append(f"High concentration: {top_asset} has {top_alloc:.2f}% allocation.")

if insights:
    for it in insights:
        st.info(it)
else:
    st.write("No immediate insights. Data looks balanced.")

st.markdown("---")
st.caption("Created with ❤️ — edit allocations, normalize, and export. Save this file as app.py and deploy on Streamlit Cloud.")

