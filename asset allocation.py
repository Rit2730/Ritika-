# asset_allocation_pro_fixed.py
import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# Matplotlib for charts (no Plotly)
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (required for 3D)
import matplotlib.colors as mcolors

st.set_page_config(page_title="Asset Allocation - Professional (Fixed)", layout="wide", page_icon="💠")

# -------------------------
# Dark styling (simple)
# -------------------------
st.markdown(
    """
<style>
body { background: linear-gradient(180deg,#061026 0%, #031226 100%); color: #e6f7ff; }
h1, h2, h3 { color: #e6f7ff; }
.stButton>button { background-color:#06b6b4; color:#021226; border-radius:8px; padding:6px 10px; }
.stSidebar .sidebar-content { background:#021226; color:#cdeef0; padding:10px; border-radius:8px; }
</style>
""", unsafe_allow_html=True
)

# -------------------------
# Typing animation for title & insights (JS, silent)
# -------------------------
title_js = """
<div id="typed_title" style="font-family:Inter, Roboto, Arial; font-size:32px; color:#bfefff; font-weight:700;"></div>
<script>
const textTitle = "💠 Premium Asset Allocation Dashboard";
const speed = 28;
let idx = 0;
function typeTitle() {
  if (idx < textTitle.length) {
    document.getElementById('typed_title').innerHTML += textTitle.charAt(idx);
    idx++;
    setTimeout(typeTitle, speed);
  } else {
    const el = document.getElementById('typed_title');
    let vis = true;
    setInterval(()=>{ el.style.borderRight = vis ? '2px solid rgba(191,239,255,0.7)' : 'none'; vis = !vis; }, 700);
  }
}
typeTitle();
</script>
"""
st.components.v1.html(title_js, height=70)

st.markdown("---")

# -------------------------
# Portfolio data (your data)
# -------------------------
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

profiles = {
    "Low Risk Profile": pd.DataFrame(LOW_DATA),
    "Moderate Risk Profile": pd.DataFrame(MODERATE_DATA),
    "High Risk Profile": pd.DataFrame(HIGH_DATA),
}

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Profile & Data")
selected_profile = st.sidebar.selectbox("Choose portfolio profile", list(profiles.keys()))

uploaded = st.sidebar.file_uploader("Upload CSV to replace this profile (optional)", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        required = {"Asset Class", "Allocation (%)", "Returns (%)"}
        if not required.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must contain columns: {', '.join(required)}")
        else:
            profiles[selected_profile] = uploaded_df.copy()
            st.sidebar.success("CSV loaded for profile.")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

# initialize session state for current df
if "profile_name" not in st.session_state or st.session_state.get("profile_name") != selected_profile:
    st.session_state.profile_name = selected_profile
    st.session_state.current_df = profiles[selected_profile].copy()

st.sidebar.markdown("---")
if st.sidebar.button("Reset to default for profile"):
    st.session_state.current_df = profiles[selected_profile].copy()
    st.sidebar.success("Reset to default for selected profile.")

st.sidebar.markdown("---")
st.sidebar.caption("Tip: Edit values inline where supported, otherwise use manual editor fallback below.")

# -------------------------
# Editor fallback
# -------------------------
st.header(f"Selected Profile — {selected_profile}")
st.markdown("Edit inline (if `st.data_editor` is available) or use the manual editor form. Click **Apply changes** to save edits.")

edited_df = None
editor_mode = None

try:
    if hasattr(st, "data_editor"):
        edited_df = st.data_editor(st.session_state.current_df, num_rows="dynamic")
        editor_mode = "data_editor"
    elif hasattr(st, "experimental_data_editor"):
        edited_df = st.experimental_data_editor(st.session_state.current_df, num_rows="dynamic")
        editor_mode = "experimental_data_editor"
    else:
        raise AttributeError("No inline editor")
except Exception:
    editor_mode = "manual"
    st.warning("Inline editor not available — using manual edit form.")
    manual_df = st.session_state.current_df.copy()
    with st.form("manual_edit"):
        rows = []
        for i, r in manual_df.iterrows():
            st.markdown(f"**Row {i+1}: {r.get('Asset Class','')}**")
            ac = st.text_input(f"Asset Class [{i}]", value=str(r.get("Asset Class", "")))
            risk = st.text_input(f"Risk [{i}]", value=str(r.get("Risk", "")))
            ret = st.text_input(f"Returns (%) [{i}]", value=str(r.get("Returns (%)", "")))
            hor = st.text_input(f"Horizon [{i}]", value=str(r.get("Horizon", "")))
            purp = st.text_input(f"Purpose [{i}]", value=str(r.get("Purpose", "")))
            alloc = st.number_input(f"Allocation (%) [{i}]", value=float(r.get("Allocation (%)", 0.0)), step=0.1, key=f"alloc_{i}")
            rows.append({
                "Asset Class": ac,
                "Risk": risk,
                "Returns (%)": ret,
                "Horizon": hor,
                "Purpose": purp,
                "Allocation (%)": alloc
            })
            st.markdown("---")
        submitted = st.form_submit_button("Submit manual edits")
    if submitted:
        edited_df = pd.DataFrame(rows)

if edited_df is not None:
    if st.button("Apply changes"):
        if "Allocation (%)" in edited_df.columns:
            edited_df["Allocation (%)"] = pd.to_numeric(edited_df["Allocation (%)"], errors="coerce").fillna(0.0)
        st.session_state.current_df = edited_df.copy()
        st.success("Changes applied.")
    else:
        st.info(f"Editor active: {editor_mode}. After editing, click 'Apply changes' to save.")

# normalize and download
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df.get("Allocation (%)", pd.Series(dtype=float)).sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] / total * 100.0).round(2)
            st.success("Allocations normalized to 100%")
with col2:
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current table (CSV)", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

st.subheader("Current Portfolio Table")
st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

# -------------------------
# Helpers: parse returns to numeric when possible
# -------------------------
def parse_return_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("%","").replace("–","-").replace("—","-")
    if "+" in s:
        s = s.replace("+","")
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

df_calc = st.session_state.current_df.copy()
df_calc["_ParsedReturn"] = df_calc.get("Returns (%)", pd.Series()).apply(parse_return_value)
total_alloc = df_calc.get("Allocation (%)", pd.Series(dtype=float)).sum()
if total_alloc > 0 and df_calc["_ParsedReturn"].notna().any():
    weighted_sum = (df_calc.loc[df_calc["_ParsedReturn"].notna(), "_ParsedReturn"] * df_calc.loc[df_calc["_ParsedReturn"].notna(), "Allocation (%)"]).sum()
    weighted_avg_return = weighted_sum / total_alloc
else:
    weighted_avg_return = None

# -------------------------
# Filters
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filters (view)")
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

# -------------------------
# Summary metrics and typing insight (JS)
# -------------------------
st.subheader("Portfolio Summary & Metrics")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Allocation (%)", f"{total_alloc:.2f}")
with c2:
    st.metric("Weighted Avg Return (%)", f"{weighted_avg_return:.2f}" if weighted_avg_return is not None else "N/A")
with c3:
    rc = st.session_state.current_df.get("Risk", pd.Series()).value_counts().to_dict()
    top_risk = max(rc, key=rc.get) if rc else "N/A"
    st.metric("Dominant Risk Type", str(top_risk))

insight = ""
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insight = "Conservative portfolio — lower expected returns."
    elif weighted_avg_return < 10:
        insight = "Balanced portfolio — blend of safety and growth."
    else:
        insight = "Aggressive portfolio — higher expected returns with higher volatility."

insight_html = f"""
<div id="typed_ins" style="font-family:Inter, Roboto, Arial; font-size:16px; color:#dffaff; font-weight:600;"></div>
<script>
const txt = {insight!r};
let i = 0; const sp = 28;
function typeIns() {{
  if (i < txt.length) {{
    document.getElementById('typed_ins').innerHTML += txt.charAt(i);
    i++; setTimeout(typeIns, sp);
  }}
}}
typeIns();
</script>
"""
st.components.v1.html(insight_html, height=50)

# -------------------------
# Visuals using Matplotlib: Donut (pie), 3D scatter/bar, heatmap-like
# -------------------------
st.markdown("---")
st.subheader("Visual Insights (Matplotlib)")

# Donut chart
allocs = st.session_state.current_df["Allocation (%)"].values
labels = st.session_state.current_df["Asset Class"].values
fig1, ax1 = plt.subplots(figsize=(6, 4), facecolor="#061026")
ax1.set_facecolor("#061026")
# color palette
colors = plt.cm.viridis(np.linspace(0, 1, len(labels)))
wedges, texts = ax1.pie(allocs, labels=None if len(labels)>12 else labels, startangle=90, colors=colors)
# draw circle for donut
centre_circle = plt.Circle((0,0),0.65,fc='#061026')
ax1.add_artist(centre_circle)
ax1.axis('equal')
ax1.set_title("Allocation (Donut)", color='white')
# legend to right
ax1.legend(wedges, labels, title="Asset Classes", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize='small')
st.pyplot(fig1)

# 3D scatter & bar
fig3 = plt.figure(figsize=(8, 5), facecolor="#061026")
ax3 = fig3.add_subplot(111, projection='3d', facecolor="#061026")
# risk -> numeric mapping
unique_risks = list(st.session_state.current_df["Risk"].unique())
risk_map = {r: i+1 for i, r in enumerate(unique_risks)}
risknum = st.session_state.current_df["Risk"].map(risk_map).fillna(0).values
parsed_ret = df_calc["_ParsedReturn"].fillna(0).values
alloc_vals = st.session_state.current_df["Allocation (%)"].fillna(0).values
# scatter
sc = ax3.scatter(risknum, parsed_ret, alloc_vals, s=np.clip(alloc_vals*4, 20, 300),
                 c=parsed_ret, cmap='viridis', depthshade=True)
ax3.set_xlabel('Risk (categorical)', color='white')
ax3.set_ylabel('Parsed Return (%)', color='white')
ax3.set_zlabel('Allocation (%)', color='white')
ax3.set_title('3D Scatter: Risk vs Return vs Allocation', color='white')
# set x ticks to risk labels
ax3.set_xticks(list(risk_map.values()))
ax3.set_xticklabels(list(risk_map.keys()), rotation=25, fontsize=8)
fig3.colorbar(sc, ax=ax3, pad=0.1)
st.pyplot(fig3)

# Heatmap-like: simple 2D average return by risk
heat_df = df_calc.copy()
heat_df["_ParsedReturn"] = heat_df["_ParsedReturn"]
group = heat_df.groupby("Risk")["_ParsedReturn"].mean().reset_index()
if not group.empty:
    fig_h, axh = plt.subplots(figsize=(8, 1.5), facecolor="#061026")
    axh.set_facecolor("#061026")
    vals = group["_ParsedReturn"].values
    # create a horizontal color bar
    cmap = plt.cm.RdYlGn
    norm = mcolors.Normalize(vmin=np.nanmin(vals), vmax=np.nanmax(vals))
    axh.imshow([vals], aspect='auto', cmap=cmap, norm=norm)
    axh.set_yticks([])
    axh.set_xticks(range(len(group)))
    axh.set_xticklabels(group["Risk"], rotation=45, color='white', fontsize=9)
    axh.set_title("Avg Parsed Return by Risk (heatbar)", color='white')
    st.pyplot(fig_h)
else:
    st.info("Not enough numeric return data to build heat visualization.")

# -------------------------
# Projection calculator
# -------------------------
st.markdown("---")
st.subheader("Projection Calculator (1 / 3 / 5 / 10 yrs)")
initial = st.number_input("Initial investment (₹)", min_value=1000.0, value=100000.0, step=1000.0)
yrs = st.selectbox("Projection horizon (years)", [1, 3, 5, 10], index=1)

proj_df = df_calc.copy()
total_alloc_now = proj_df["Allocation (%)"].sum()
if total_alloc_now <= 0:
    st.warning("Allocations sum to 0 — set allocations before projecting returns.")
else:
    proj_df["Weight"] = proj_df["Allocation (%)"] / total_alloc_now
    fallback = proj_df["_ParsedReturn"].median() if proj_df["_ParsedReturn"].notna().any() else 6.0
    proj_df["_UseReturn"] = proj_df["_ParsedReturn"].fillna(fallback)
    portfolio_return_decimal = (proj_df["_UseReturn"] * proj_df["Weight"]).sum() / 100.0
    future_val = initial * ((1 + portfolio_return_decimal) ** yrs)
    st.metric(f"Projected value after {yrs} years", f"₹{future_val:,.0f}")
    st.caption(f"Portfolio average annual return used: {(portfolio_return_decimal*100):.2f}% (fallback {fallback:.2f}% for non-numeric assets)")

# -------------------------
# Insights
# -------------------------
st.markdown("---")
st.subheader("Automatic Insights")
insights = []
if total_alloc < 90:
    insights.append("Total allocation less than 90% — consider deploying idle cash or adjust allocations.")
if total_alloc > 110:
    insights.append("Total allocation > 110% — allocations not normalized.")
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insights.append("Conservative expected returns (<6%).")
    elif weighted_avg_return < 10:
        insights.append("Balanced expected returns (6–10%).")
    else:
        insights.append("Aggressive expected returns (>10%).")

if not st.session_state.current_df.empty:
    top_idx = st.session_state.current_df["Allocation (%)"].idxmax()
    top_asset = st.session_state.current_df.loc[top_idx, "Asset Class"]
    top_alloc = st.session_state.current_df.loc[top_idx, "Allocation (%)"]
    if top_alloc >= 35:
        insights.append(f"High concentration: {top_asset} at {top_alloc:.1f}% allocation.")

if insights:
    for it in insights:
        st.info(it)
else:
    st.write("No immediate insights — portfolio looks balanced.")

st.markdown("---")
st.caption("Fixed version — removed Plotly dependency. Save as asset_allocation_pro_fixed.py and deploy with the requirements.txt provided.")
