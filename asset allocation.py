# app.py
import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# try plotly, fall back gracefully if missing
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Premium Investment Dashboard", page_icon="💠", layout="wide")

# -------------------------
# DARK THEME (Theme A)
# -------------------------
dark_css = """
<style>
/* background gradient and base colors */
html, body, .stApp { background: linear-gradient(180deg,#061026 0%, #031226 100%); color: #e6f7ff; }
h1, h2, h3 { color: #e6f7ff; font-family: Inter, Roboto, Arial; }
.stButton>button { background-color:#06b6b4; color:#021226; border-radius:8px; padding:6px 10px; }
.stSidebar .sidebar-content { background:#021226; color:#cdeef0; padding:12px; border-radius:8px; }
.stDataFrame table { color: #dff6ff; }
.metric-value { color: #bfefff; }
hr { border: none; border-top: 1px solid rgba(191,239,255,0.06); }
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# -------------------------
# Typing animation (titles & insights only), no sound
# -------------------------
typing_html = """
<div id="typed_title" style="font-family:Inter, Roboto, Arial; font-size:32px; color:#bfefff; font-weight:700;"></div>
<script>
const textTitle = "💠 Premium Investment Dashboard";
const speed = 30; // fast typing
let idx = 0;
function typeTitle() {
  if (idx < textTitle.length) {
    document.getElementById('typed_title').innerHTML += textTitle.charAt(idx);
    idx++;
    setTimeout(typeTitle, speed);
  } else {
    // add subtle cursor blink
    const el = document.getElementById('typed_title');
    let vis = true;
    setInterval(() => { el.style.borderRight = vis ? '2px solid rgba(191,239,255,0.7)' : 'none'; vis = !vis; }, 700);
  }
}
typeTitle();
</script>
"""
st.components.v1.html(typing_html, height=70)

st.markdown(" ")
st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------------
# Predefined portfolios (data from you)
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

df_profiles = {
    "Low Risk Profile": pd.DataFrame(LOW_DATA),
    "Moderate Risk Profile": pd.DataFrame(MODERATE_DATA),
    "High Risk Profile": pd.DataFrame(HIGH_DATA),
}

# -------------------------
# Sidebar controls & upload
# -------------------------
st.sidebar.header("Profile & Controls")
selected_profile = st.sidebar.selectbox("Choose portfolio profile", list(df_profiles.keys()))

uploaded = st.sidebar.file_uploader("Upload CSV (optional) to replace profile", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        required_cols = {"Asset Class", "Allocation (%)", "Returns (%)"}
        if not required_cols.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must include: {', '.join(required_cols)}")
        else:
            df_profiles[selected_profile] = uploaded_df.copy()
            st.sidebar.success("CSV loaded for selected profile.")
    except Exception as e:
        st.sidebar.error(f"CSV read error: {e}")

# keep dataframe in session state per profile
if "profile_name" not in st.session_state or st.session_state.profile_name != selected_profile:
    st.session_state.profile_name = selected_profile
    st.session_state.current_df = df_profiles[selected_profile].copy()

st.sidebar.markdown("---")
if st.sidebar.button("Reset to default for profile"):
    st.session_state.current_df = df_profiles[selected_profile].copy()
    st.sidebar.success("Reset done.")

st.sidebar.markdown("---")
st.sidebar.subheader("Presentation")
show_icons = st.sidebar.checkbox("Show icons for asset categories", value=True)
st.sidebar.caption("Icons are small inline SVGs/emoji for visual cue.")

# -------------------------
# Inline editor with fallback
# -------------------------
st.header(f"Selected Profile — {selected_profile}")
st.markdown("Edit inline (if supported) or use the manual fallback form. Click **Apply changes** to save edits.")

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
        raise AttributeError
except Exception:
    editor_mode = "manual"
    st.warning("Inline editor unavailable — using manual edit form.")
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
        manual_submit = st.form_submit_button("Submit manual edits")
    if manual_submit:
        edited_df = pd.DataFrame(rows)

if edited_df is not None:
    if st.button("Apply changes"):
        if "Allocation (%)" in edited_df.columns:
            edited_df["Allocation (%)"] = pd.to_numeric(edited_df["Allocation (%)"], errors="coerce").fillna(0.0)
        st.session_state.current_df = edited_df.copy()
        st.success("Changes applied.")
    else:
        st.info(f"Editor active: {editor_mode}. Make edits then press 'Apply changes'.")

# Normalize & download
col_norm, col_dl = st.columns([1,1])
with col_norm:
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df.get("Allocation (%)", pd.Series(dtype=float)).sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] / total * 100).round(2)
            st.success("Allocations normalized.")
with col_dl:
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current table (CSV)", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

st.subheader("Current Portfolio Table")
if show_icons:
    # small legend with emojis / simple SVG icons for categories
    legend_html = """
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="font-size:18px">💵</div><small>Debt</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="font-size:18px">📈</div><small>Equity</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="font-size:18px">🏠</div><small>Real Assets</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="font-size:18px">🟨</div><small>Alternatives</small></div>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

# -------------------------
# Helper: parse return strings to numeric average
# -------------------------
def parse_return_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("%","").replace("–","-").replace("—","-")
    if "+" in s:
        s = s.replace("+","")
        try: return float(s)
        except: return None
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
# Filters for view
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Filters (view only)")
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
# Summary metrics + typing-insight animation (typing for insights only)
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

# typing animation for insights (no sound)
insight_text = ""
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insight_text = "The portfolio is conservative — expected returns are low."
    elif weighted_avg_return < 10:
        insight_text = "Balanced profile — good mix of safety and growth."
    else:
        insight_text = "Aggressive profile — higher expected returns with higher volatility."

insight_html = f"""
<div id="typed_ins" style="font-family:Inter, Roboto, Arial; font-size:18px; color:#dffaff; font-weight:600;"></div>
<script>
const txt = {insight_text!r};
const speed = 28;
let j = 0;
function typeInsight() {{
  if (j < txt.length) {{
    document.getElementById('typed_ins').innerHTML += txt.charAt(j);
    j++;
    setTimeout(typeInsight, speed);
  }}
}}
typeInsight();
</script>
"""
st.components.v1.html(insight_html, height=50)

# -------------------------
# Visuals: Donut pie, 3D scatter & 3D bar, heatmap (Plotly)
# -------------------------
st.markdown("---")
st.subheader("Visual Insights")

if not PLOTLY_OK:
    st.warning("Plotly is not installed. Add 'plotly' to requirements.txt and redeploy to see interactive charts.")
    st.markdown("Fallback: Allocation bar chart")
    st.bar_chart(st.session_state.current_df.set_index("Asset Class")["Allocation (%)"])
else:
    # Donut
    st.markdown("**Donut: Allocation (%)**")
    fig_donut = px.pie(
        st.session_state.current_df,
        names="Asset Class",
        values="Allocation (%)",
        hole=0.45,
        title="Portfolio Allocation (Donut)",
        color_discrete_sequence=px.colors.sequential.Tealgrn
    )
    fig_donut.update_traces(textposition="inside", textinfo="percent+label", insidetextorientation='radial')
    st.plotly_chart(fig_donut, use_container_width=True)

    # 3D scatter (Risk category numeric vs Return vs Allocation)
    st.markdown("**3D Scatter: Risk vs Return vs Allocation** (interactive)")
    unique_risks = list(st.session_state.current_df["Risk"].unique())
    risk_map = {r: i+1 for i, r in enumerate(unique_risks)}
    plot_df = df_calc.copy()
    plot_df["RiskNum"] = plot_df["Risk"].map(risk_map).fillna(0)
    scatter = go.Figure(data=[go.Scatter3d(
        x=plot_df["RiskNum"],
        y=plot_df["_ParsedReturn"],
        z=plot_df["Allocation (%)"],
        mode='markers',
        text=plot_df["Asset Class"],
        marker=dict(size=np.clip(plot_df["Allocation (%)"]*0.6, 6, 45), color=plot_df["_ParsedReturn"], colorscale='Viridis', showscale=True),
    )])
    scatter.update_layout(scene=dict(
        xaxis=dict(title="Risk (categorical)"),
        yaxis=dict(title="Parsed Return (%)"),
        zaxis=dict(title="Allocation (%)")
    ), margin=dict(l=0,r=0,b=0,t=30))
    st.plotly_chart(scatter, use_container_width=True)

    # 3D bar (both)
    st.markdown("**3D Bar: Allocation by Asset (interactive)**")
    # create simple 3D bar by stacking bars along an index (converted to numeric)
    idx = np.arange(len(plot_df))
    bar3d = go.Figure()
    bar3d.add_trace(go.Bar3d(
        x=idx, y=[0]*len(idx), z=[0]*len(idx),
        dx=0.6, dy=0.6, dz=plot_df["Allocation (%)"].fillna(0),
        text=plot_df["Asset Class"],
        hovertemplate="Asset: %{text}<br>Allocation: %{dz}%<extra></extra>"
    ))
    bar3d.update_layout(scene=dict(
        xaxis=dict(title="Asset Index", tickmode='array', tickvals=idx, ticktext=plot_df["Asset Class"]),
        yaxis=dict(title=""),
        zaxis=dict(title="Allocation (%)")
    ), margin=dict(l=0,r=0,b=0,t=30), height=500)
    st.plotly_chart(bar3d, use_container_width=True)

    # Heatmap: Risk vs Avg Parsed Return
    st.markdown("**Risk–Return Heatmap (Avg Return by Risk Category)**")
    heat_df = st.session_state.current_df.copy()
    heat_df["_ParsedReturn"] = heat_df["Returns (%)"].apply(parse_return_value)
    heat_group = heat_df.groupby("Risk")["_ParsedReturn"].mean().reset_index().dropna()
    if heat_group.empty:
        st.info("Not enough numeric return data to build heatmap.")
    else:
        fig_heat = go.Figure(data=go.Heatmap(
            z=[heat_group["_ParsedReturn"].values],
            x=heat_group["Risk"],
            y=["Avg Return"],
            colorscale='RdYlGn'
        ))
        fig_heat.update_layout(height=200, margin=dict(l=20,r=20,t=30,b=20))
        st.plotly_chart(fig_heat, use_container_width=True)

# -------------------------
# Projection calculator (1/3/5/10 yrs), uses parsed returns
# -------------------------
st.markdown("---")
st.subheader("Projection Calculator")
initial = st.number_input("Initial investment (₹)", min_value=1000.0, value=100000.0, step=1000.0)
yrs = st.selectbox("Projection horizon (years)", options=[1,3,5,10], index=1)

proj_df = df_calc.copy()
total_alloc_now = proj_df["Allocation (%)"].sum()
if total_alloc_now <= 0:
    st.warning("Allocations sum to 0 — set allocations to compute projections.")
else:
    proj_df["Weight"] = proj_df["Allocation (%)"] / total_alloc_now
    fallback = proj_df["_ParsedReturn"].median() if proj_df["_ParsedReturn"].notna().any() else 6.0
    proj_df["_UseReturn"] = proj_df["_ParsedReturn"].fillna(fallback)
    portfolio_return_decimal = (proj_df["_UseReturn"] * proj_df["Weight"]).sum() / 100.0
    future_val = initial * ((1 + portfolio_return_decimal) ** yrs)
    st.metric(f"Projected value after {yrs} years", f"₹{future_val:,.0f}")
    st.caption(f"Portfolio average annual return used: {portfolio_return_decimal*100:.2f}% (fallback {fallback:.2f}% for non-numeric assets)")

# -------------------------
# Automatic insights (typing style for short sentence)
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
        insights.append("Conservative portfolio expected (<6%).")
    elif weighted_avg_return < 10:
        insights.append("Balanced expected return (6–10%).")
    else:
        insights.append("Aggressive expected return (>10%).")

# typing animation for the first insight only (no sound)
first_insight = insights[0] if insights else "Portfolio looks balanced — no immediate actions required."
insight_type_html = f"""
<div id="typi" style="font-family:Inter, Roboto, Arial; font-size:16px; color:#dffaff; font-weight:600;"></div>
<script>
const ins = {first_insight!r};
let k=0;
const sp = 28;
function typeIns() {{
  if (k < ins.length) {{
    document.getElementById('typi').innerHTML += ins.charAt(k);
    k++;
    setTimeout(typeIns, sp);
  }}
}}
typeIns();
</script>
"""
st.components.v1.html(insight_type_html, height=50)

# show all insights below
for it in insights:
    st.info(it)

st.markdown("---")
st.caption("Created with 💠 — Dark Mode Premium. If interactive charts are missing, ensure 'plotly' is in requirements.txt and redeploy.")

