# app.py
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Multi-Profile Investment Dashboard", layout="wide", page_icon="💼")

st.title("💼 Multi-Profile Investment Dashboard")
st.markdown(
    "This app contains three sample portfolios (Low, Moderate, High risk). "
    "Choose a profile, upload CSV to replace it, edit values, normalize allocations, and export as CSV."
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

df_profiles = {
    "Low Risk Profile": pd.DataFrame(LOW_DATA),
    "Moderate Risk Profile": pd.DataFrame(MODERATE_DATA),
    "High Risk Profile": pd.DataFrame(HIGH_DATA),
}

# ---------------------------
# Sidebar - profile selection + upload
# ---------------------------
st.sidebar.header("Profile & Data")
selected_profile = st.sidebar.selectbox("Choose portfolio profile", list(df_profiles.keys()))

st.sidebar.markdown("**Upload CSV** (optional) to replace this profile")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        required = {"Asset Class", "Allocation (%)", "Returns (%)"}
        if not required.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must contain columns: {', '.join(required)}")
            uploaded_df = None
        else:
            df_profiles[selected_profile] = uploaded_df.copy()
            st.sidebar.success("CSV loaded for the selected profile.")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")
        uploaded_df = None

# Initialize session state
if "profile_name" not in st.session_state or st.session_state.get("profile_name") != selected_profile:
    st.session_state.profile_name = selected_profile
    st.session_state.current_df = df_profiles[selected_profile].copy()

st.sidebar.markdown("---")
if st.sidebar.button("Reset to default for profile"):
    st.session_state.current_df = df_profiles[selected_profile].copy()
    st.sidebar.success("Reset to default data for selected profile.")

normalize_mode = st.sidebar.checkbox("Auto-normalize allocations to 100% on request", value=True)
st.sidebar.info("Edit values using the editor below (method depends on Streamlit version).")

# ---------------------------
# Editor: try modern APIs then fallback
# ---------------------------
st.header(f"Selected Profile: {selected_profile}")
st.markdown("Edit the table using the editor below, then press **Apply changes**. If inline editor isn't available, use the manual edit form.")

editor_used = None
edited_df = None

# Attempt modern data editor first, with fallbacks
try:
    # try new st.data_editor (Streamlit >=1.23)
    if hasattr(st, "data_editor"):
        edited_df = st.data_editor(st.session_state.current_df, num_rows="dynamic")
        editor_used = "data_editor"
    elif hasattr(st, "experimental_data_editor"):
        # older experimental API
        edited_df = st.experimental_data_editor(st.session_state.current_df, num_rows="dynamic")
        editor_used = "experimental_data_editor"
    else:
        raise AttributeError("No data editor available")
except Exception:
    # Fallback manual editor: render a form with fields per row
    editor_used = "manual_form"
    st.warning("Inline editor not available in this Streamlit version. Using manual edit form below.")
    manual_df = st.session_state.current_df.copy()
    with st.form("manual_edit_form"):
        rows = []
        for i, row in manual_df.iterrows():
            st.markdown(f"**Row {i+1}: {row.get('Asset Class', '')}**")
            ac = st.text_input(f"Asset Class [{i}]", value=str(row.get("Asset Class", "")))
            risk = st.text_input(f"Risk [{i}]", value=str(row.get("Risk", "")))
            returns = st.text_input(f"Returns (%) [{i}]", value=str(row.get("Returns (%)", "")))
            horizon = st.text_input(f"Horizon [{i}]", value=str(row.get("Horizon", "")))
            purpose = st.text_input(f"Purpose [{i}]", value=str(row.get("Purpose", "")))
            alloc = st.number_input(f"Allocation (%) [{i}]", value=float(row.get("Allocation (%)", 0.0)), step=0.1, key=f"alloc_{i}")
            rows.append({
                "Asset Class": ac,
                "Risk": risk,
                "Returns (%)": returns,
                "Horizon": horizon,
                "Purpose": purpose,
                "Allocation (%)": alloc
            })
            st.markdown("---")
        submitted_manual = st.form_submit_button("Submit manual edits")
    if submitted_manual:
        edited_df = pd.DataFrame(rows)

# If an editor was used and returned a DataFrame, show Apply button
if edited_df is not None:
    if st.button("Apply changes"):
        # Basic cleaning
        if "Allocation (%)" in edited_df.columns:
            edited_df["Allocation (%)"] = pd.to_numeric(edited_df["Allocation (%)"], errors="coerce").fillna(0.0)
        st.session_state.current_df = edited_df.copy()
        st.success("Changes applied to the profile data.")
    else:
        st.info(f"Editor in use: {editor_used}. Make edits then click 'Apply changes' to save.")
else:
    st.error("No editor available and no manual edits submitted. Data is read-only until you edit.")

# Normalize allocations button
st.write("")  # spacing
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df.get("Allocation (%)", pd.Series(dtype=float)).sum()
        if total == 0:
            st.error("Total allocation is 0; can't normalize.")
        else:
            factor = 100.0 / total
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] * factor).round(2)
            st.success("Allocations normalized to sum to 100%.")

# Download current table
with col2:
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current table as CSV", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

# ---------------------------
# Show current table
# ---------------------------
st.subheader("Portfolio Table (current)")
st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

# ---------------------------
# Helper: parse returns to numeric average when possible
# ---------------------------
def parse_return_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    s = s.replace("%", "").replace("–", "-").replace("—", "-")
    if "+" in s:
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
                return (nums[0] + nums[1]) / 2.0
        except:
            return None
    try:
        return float(s)
    except:
        return None

# Compute parsed returns and weighted avg
df_calc = st.session_state.current_df.copy()
if "Returns (%)" in df_calc.columns:
    df_calc["_ParsedReturn"] = df_calc["Returns (%)"].apply(parse_return_value)
else:
    df_calc["_ParsedReturn"] = None

total_alloc = df_calc["Allocation (%)"].sum() if "Allocation (%)" in df_calc.columns else 0.0
if total_alloc > 0:
    mask = df_calc["_ParsedReturn"].notna()
    if mask.any():
        weighted_sum = (df_calc.loc[mask, "_ParsedReturn"] * df_calc.loc[mask, "Allocation (%)"]).sum()
        weighted_avg_return = weighted_sum / total_alloc
    else:
        weighted_avg_return = None
else:
    weighted_avg_return = None

# Filters (Horizon / Purpose)
st.sidebar.markdown("---")
st.sidebar.subheader("View Filters")
horizons = sorted(st.session_state.current_df.get("Horizon", pd.Series()).dropna().unique().tolist())
selected_horizons = st.sidebar.multiselect("Horizon", options=horizons, default=horizons if horizons else [])
purposes = sorted(st.session_state.current_df.get("Purpose", pd.Series()).dropna().unique().tolist())
selected_purposes = st.sidebar.multiselect("Purpose", options=purposes, default=purposes if purposes else [])

view_df = st.session_state.current_df.copy()
if selected_horizons:
    view_df = view_df[view_df["Horizon"].isin(selected_horizons)]
if selected_purposes:
    view_df = view_df[view_df["Purpose"].isin(selected_purposes)]

st.subheader("Filtered View")
st.dataframe(view_df.reset_index(drop=True), use_container_width=True)

# ---------------------------
# Summaries and visuals (built-in)
# ---------------------------
st.subheader("Portfolio Summary & Metrics")
col_a, col_b, col_c = st.columns([1, 1, 1])

with col_a:
    st.metric("Total Allocation (%)", f"{total_alloc:.2f}")

with col_b:
    st.metric("Weighted Avg Return (%)", f"{weighted_avg_return:.2f}" if weighted_avg_return is not None else "N/A")

with col_c:
    risk_counts = st.session_state.current_df.get("Risk", pd.Series()).value_counts().to_dict()
    top_risk = max(risk_counts, key=risk_counts.get) if risk_counts else "N/A"
    st.metric("Dominant Risk Type", str(top_risk))

st.subheader("Visuals")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Allocation (%) by Asset Class**")
    if st.session_state.current_df.get("Allocation (%)", pd.Series()).sum() == 0:
        st.info("No allocation data to chart.")
    else:
        st.bar_chart(st.session_state.current_df.set_index("Asset Class")["Allocation (%)"])

with col2:
    st.markdown("**Parsed Returns (%) by Asset Class (numeric only)**")
    if df_calc["_ParsedReturn"].dropna().empty:
        st.info("No numeric returns parsed to show chart.")
    else:
        st.bar_chart(df_calc.set_index("Asset Class")["_ParsedReturn"].fillna(0))

# Automatic insights
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
st.caption("Created with ❤️ — save as app.py and deploy on Streamlit Cloud. This version includes fallbacks if your Streamlit runtime lacks the inline data editor.")
