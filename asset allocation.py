# asset_allocation_pro_final.py
import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# Try plotly, set flag if available
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", page_icon="📊")

# -------------------------
# THEME: Premium Classic Blue (matte)
# -------------------------
st.markdown(
    """
    <style>
    /* page background and cards */
    .stApp {
      background: linear-gradient(180deg, #0b1730 0%, #0f2a49 50%, #07203a 100%);
      color: #e8f6ff;
      font-family: Inter, Roboto, Arial, sans-serif;
    }
    .card {
      background: rgba(255,255,255,0.03);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 8px 30px rgba(2,8,23,0.6);
      border: 1px solid rgba(255,255,255,0.03);
    }
    .stSidebar .sidebar-content {
      background: linear-gradient(180deg,#062033, #032637);
      color: #cfeef0;
      padding: 12px;
      border-radius: 10px;
    }
    .muted { color: #bfefff; opacity:0.85; font-size:0.95rem; }
    .small { font-size:0.9rem; color:#cfeef0; opacity:0.9; }
    hr { border:none; border-top:1px solid rgba(191,239,255,0.06); margin:12px 0; }
    </style>
    """, unsafe_allow_html=True
)

# -------------------------
# Typing/Fade-in Title (fade-in) + sound toggle control
# Typing style: Fade-In chosen (we will animate opacity for title and insights).
# Soft keyboard click sound chosen: provide toggle to enable/disable sound.
# -------------------------
st.sidebar.header("Presentation & Controls")
enable_sound = st.sidebar.checkbox("Enable typing click sound", value=False)
st.sidebar.caption("Soft keyboard click sound (WebAudio). Toggle if you want the audio.")

# We will inject JS+CSS for fade-in + optionally play click sound on certain UI actions (profile switch, apply changes)
fade_js = """
<style>
@keyframes fadein { from { opacity: 0; transform: translateY(6px);} to { opacity: 1; transform: translateY(0);} }
.fade-in { animation: fadein 600ms ease-out both; }
</style>
<div id="title-wrap" class="fade-in" style="font-size:30px;font-weight:700;color:#dffcff">💠 Premium Asset Allocation — Classic Blue</div>
"""
st.components.v1.html(fade_js, height=70)

st.markdown("<div class='small muted'>Professional portfolio dashboards · interactive charts · rebalancer & projections</div>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# JavaScript for soft keyboard click sound (synthesized) and a function to call it
sound_js = """
<script>
window.playSoftClick = (enable) => {
  // if 'enable' is false, do nothing
  if (!enable) return;
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = 'sine';
  o.frequency.value = 1000; // soft click pitch
  g.gain.value = 0.002; // low volume
  o.connect(g);
  g.connect(ctx.destination);
  o.start();
  setTimeout(()=>{ o.stop(); ctx.close(); }, 40);
};
</script>
"""
st.components.v1.html(sound_js, height=10)

# helper to call the sound from python (we pass current enable_sound flag)
def play_click():
    st.components.v1.html(f"<script>window.playSoftClick({str(enable_sound).lower()});</script>", height=10)

# -------------------------
# Data: three profiles (from user-provided lists)
# -------------------------
LOW_DATA = {
    "Asset Class": [
        "Government Bonds (G-sec)", "AAA Corporate Bonds", "PPF / NSC / Small Savings",
        "Fixed Deposits", "Short/Mid-Term Debt Funds", "REITs", "Gold (SGB/ETF)",
        "Target Maturity Debt ETFs", "Annuity Plans / Pension Income", "Infra Debt / InvIT Debt"
    ],
    "Risk": ["Very Low", "Low", "Very Low", "Very Low", "Low", "Low–Mod", "Moderate", "Low", "Very Low", "Low–Mod"],
    "Returns (%)": ["4–7", "5–8", "6–7", "5–7", "4–7", "6–9", "3–8", "4–7", "3–6", "6–9"],
    "Horizon": ["3–10 yrs", "2–7 yrs", "5–15 yrs", "1–5 yrs", "1–5 yrs", "5–10 yrs", "3–10 yrs", "3–10 yrs", "Lifetime", "5–10 yrs"],
    "Purpose": ["Income","Income","Retirement","Capital protection","Stable returns","Property income","Inflation hedge","Predictable returns","Guaranteed income","Stability"],
    "Allocation (%)": [30,20,10,10,10,7,5,3,3,2]
}
MODERATE_DATA = {
    "Asset Class": ["Large-Cap Equity Funds","Mid/Small-Cap Funds","Global Equity ETFs/Funds","Hybrid/Balanced Funds","Corporate Bond Funds","REITs","Gold","Private Credit / Debt AIF","Farmland / Agro Real Assets","Digital Asset Basket (tiny)"],
    "Risk": ["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
    "Returns (%)": ["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
    "Horizon": ["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
    "Purpose": ["Growth","Alpha","Diversification","Smoother volatility","Income stability","Property income","Hedge","Enhanced yield","Real assets","Asymmetric payoff"],
    "Allocation (%)": [25,15,10,10,10,7,5,5,5,3]
}
HIGH_DATA = {
    "Asset Class": ["Domestic Equity (Large/Mid/Small)","International Equities","Venture Capital / Startup Investments","Private Equity Funds","Crypto / Blockchain Assets","Commodities (Energy/Metals ETFs)","Real Assets (Timber/Renewables)","Structured Products / Hedge Funds","IP / Music Royalties","Active Derivatives (Hedged)"],
    "Risk": ["Very High"]*10,
    "Returns (%)": ["10–15","8–15","20+","15+","Highly variable","Varies","6–12","Varies","Variable","Variable"],
    "Horizon": ["10–20 yrs"]*10,
    "Purpose": ["Primary growth","Global growth","High innovation upside","Superior alpha","Speculative","Cycle hedge","Alternative diversifier","Non-correlated","Uncorrelated cashflows","Tactical"],
    "Allocation (%)": [50,15,10,7,5,5,3,3,1,1]
}

profiles = {
    "Low Risk (45–65 yrs)" : pd.DataFrame(LOW_DATA),
    "Moderate Risk (30–45 yrs)" : pd.DataFrame(MODERATE_DATA),
    "High Risk (25–30 yrs)" : pd.DataFrame(HIGH_DATA)
}

# -------------------------
# Sidebar: profile selections (dropdowns), age group, investment objective (dropdown)
# -------------------------
st.sidebar.header("Investor Profile")
selected_profile = st.sidebar.selectbox("Risk Profile", list(profiles.keys()))
age_group = st.sidebar.selectbox("Age Group", ["25-30", "30-45", "45-65"], index=1)
investment_objective = st.sidebar.selectbox("Investment Objective", ["Growth", "Income", "Retirement", "Tax Saving", "Short-Term"], index=0)

# when profile changes, play soft click (if enabled)
play_click()

# load current df into session state
if "profile_name" not in st.session_state or st.session_state.profile_name != selected_profile:
    st.session_state.profile_name = selected_profile
    st.session_state.current_df = profiles[selected_profile].copy()

# upload CSV to replace profile
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Upload CSV to replace this profile (optional)", type=["csv"])
if uploaded is not None:
    try:
        df_up = pd.read_csv(uploaded)
        required = {"Asset Class","Allocation (%)","Returns (%)"}
        if not required.issubset(set(df_up.columns)):
            st.sidebar.error(f"CSV must contain: {', '.join(required)}")
        else:
            st.session_state.current_df = df_up.copy()
            st.sidebar.success("Uploaded and loaded for current profile.")
            play_click()
    except Exception as e:
        st.sidebar.error(f"CSV read error: {e}")

st.sidebar.markdown("---")
if st.sidebar.button("Reset profile defaults"):
    st.session_state.current_df = profiles[selected_profile].copy()
    st.sidebar.success("Reset to defaults.")
    play_click()

# -------------------------
# Main layout: left column controls, right column charts
# -------------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
left, right = st.columns((1.2, 1))

with left:
    st.subheader("Portfolio Editor")
    st.markdown("Pick an asset below to edit its fields using dropdowns (no free typing). This ensures valid selectable values.")
    # Select asset to edit
    asset_list = st.session_state.current_df["Asset Class"].tolist()
    selected_asset = st.selectbox("Select Asset to edit", options=asset_list)
    # fetch row
    row_idx = st.session_state.current_df.index[st.session_state.current_df["Asset Class"] == selected_asset].tolist()[0]
    row = st.session_state.current_df.loc[row_idx].copy()

    # Dropdown selects for fields instead of free text
    risk_options = ["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"]
    horizon_options = sorted(list(set(st.session_state.current_df["Horizon"].dropna().tolist())) )
    if not horizon_options:
        horizon_options = ["1–3 yrs","3–5 yrs","5–10 yrs","10+ yrs"]
    purpose_options = sorted(list(set(st.session_state.current_df["Purpose"].dropna().tolist())))
    if not purpose_options:
        purpose_options = ["Income","Growth","Retirement","Tax Saving","Hedge"]

    new_risk = st.selectbox("Risk", options=risk_options, index=risk_options.index(row["Risk"]) if row["Risk"] in risk_options else 0)
    new_horizon = st.selectbox("Horizon", options=horizon_options, index=0)
    new_purpose = st.selectbox("Purpose", options=purpose_options, index=0)
    # Reward input: allow a range string or numeric expected return
    new_return = st.text_input("Returns (%) (e.g. 4–7 or 6.5)", value=str(row.get("Returns (%)","")))
    new_alloc = st.number_input("Allocation (%)", min_value=0.0, max_value=100.0, value=float(row.get("Allocation (%)",0.0)), step=0.1)

    col_apply, col_del = st.columns([1,1])
    with col_apply:
        if st.button("Apply changes to asset"):
            st.session_state.current_df.at[row_idx, "Risk"] = new_risk
            st.session_state.current_df.at[row_idx, "Horizon"] = new_horizon
            st.session_state.current_df.at[row_idx, "Purpose"] = new_purpose
            st.session_state.current_df.at[row_idx, "Returns (%)"] = new_return
            st.session_state.current_df.at[row_idx, "Allocation (%)"] = new_alloc
            st.success(f"Updated {selected_asset}")
            play_click()
    with col_del:
        if st.button("Remove asset"):
            st.session_state.current_df = st.session_state.current_df.drop(index=row_idx).reset_index(drop=True)
            st.success(f"Removed {selected_asset}")
            play_click()

    st.markdown("---")
    # Add new asset form (with dropdown-guided fields)
    st.markdown("Add new asset")
    new_asset_name = st.text_input("Asset Class name", value="")
    new_asset_risk = st.selectbox("Risk (new)", options=risk_options, index=1)
    new_asset_horizon = st.selectbox("Horizon (new)", options=horizon_options, index=0)
    new_asset_purpose = st.selectbox("Purpose (new)", options=purpose_options, index=0)
    new_asset_return = st.text_input("Returns (%) (new)", value="")
    new_asset_alloc = st.number_input("Allocation (%) (new)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    if st.button("Add asset to portfolio"):
        if new_asset_name.strip() == "":
            st.error("Provide asset class name.")
        else:
            row_new = {
                "Asset Class": new_asset_name.strip(),
                "Risk": new_asset_risk,
                "Returns (%)": new_asset_return,
                "Horizon": new_asset_horizon,
                "Purpose": new_asset_purpose,
                "Allocation (%)": float(new_asset_alloc)
            }
            st.session_state.current_df = pd.concat([st.session_state.current_df, pd.DataFrame([row_new])], ignore_index=True)
            st.success(f"Added {new_asset_name}")
            play_click()

    st.markdown("---")
    # Normalize & Apply buttons
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df["Allocation (%)"].sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] / total * 100).round(2)
            st.success("Allocations normalized to 100%")
            play_click()

    # CSV download & show table
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current portfolio (CSV)", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

    st.markdown("Current portfolio (editable via asset editor above)")
    st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

with right:
    st.subheader("Visual Dashboard")
    # quick metrics
    total_alloc = st.session_state.current_df["Allocation (%)"].sum()
    # Parse returns to numeric where possible
    def parse_return_value(val):
        if pd.isna(val): return None
        if isinstance(val, (int,float)): return float(val)
        s = str(val).strip().replace("%","").replace("–","-").replace("—","-")
        if "+" in s:
            s = s.replace("+","")
            try: return float(s)
            except: return None
        if "-" in s:
            parts = s.split("-")
            try:
                nums = [float(p) for p in parts if p!=""]
                if len(nums)>=2: return (nums[0]+nums[1])/2.0
            except: return None
        try: return float(s)
        except: return None

    df_calc = st.session_state.current_df.copy()
    df_calc["_ParsedReturn"] = df_calc["Returns (%)"].apply(parse_return_value)
    weighted_avg_return = None
    if total_alloc > 0 and df_calc["_ParsedReturn"].notna().any():
        weighted_avg_return = (df_calc.loc[df_calc["_ParsedReturn"].notna(), "_ParsedReturn"] * df_calc.loc[df_calc["_ParsedReturn"].notna(), "Allocation (%)"]).sum() / total_alloc

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Allocation (%)", f"{total_alloc:.2f}")
    with c2:
        st.metric("Weighted Avg Return (%)", f"{weighted_avg_return:.2f}" if weighted_avg_return is not None else "N/A")

    st.markdown("---")
    # Charts: donut + 3D scatter/bar (Plotly if available)
    if PLOTLY_OK:
        # Donut
        st.markdown("**Donut: Allocation (%)**")
        fig_donut = px.pie(st.session_state.current_df, names="Asset Class", values="Allocation (%)", hole=0.45,
                           title="Portfolio Allocation (Donut)", color_discrete_sequence=px.colors.sequential.Tealgrn)
        fig_donut.update_traces(textinfo="percent+label", textposition="inside")
        st.plotly_chart(fig_donut, use_container_width=True)

        # 3D scatter (Risk category numeric vs Parsed Return vs Allocation)
        st.markdown("**3D: Risk vs Return vs Allocation (interactive)**")
        unique_risks = list(st.session_state.current_df["Risk"].unique())
        risk_map = {r: i+1 for i,r in enumerate(unique_risks)}
        plot_df = df_calc.copy()
        plot_df["RiskNum"] = plot_df["Risk"].map(risk_map).fillna(0)
        fig_3d = go.Figure(data=[go.Scatter3d(
            x=plot_df["RiskNum"],
            y=plot_df["_ParsedReturn"],
            z=plot_df["Allocation (%)"],
            text=plot_df["Asset Class"],
            mode='markers',
            marker=dict(size=np.clip(plot_df["Allocation (%)"]*0.6, 6, 40), color=plot_df["_ParsedReturn"], colorscale='Viridis', showscale=True)
        )])
        fig_3d.update_layout(scene=dict(xaxis=dict(title="Risk (categorical)"), yaxis=dict(title="Parsed Return (%)"), zaxis=dict(title="Allocation (%)")), margin=dict(l=0,r=0,b=0,t=30))
        st.plotly_chart(fig_3d, use_container_width=True)
    else:
        st.warning("Plotly not installed — showing fallback charts (Streamlit simple charts). Add 'plotly' to requirements.txt for interactive 3D visuals.")
        st.markdown("Allocation (fallback bar chart)")
        st.bar_chart(st.session_state.current_df.set_index("Asset Class")["Allocation (%)"])

    st.markdown("---")
    # Projection calculator
    st.subheader("Projection Calculator")
    initial = st.number_input("Initial investment (₹)", min_value=1000.0, value=100000.0, step=1000.0)
    years = st.selectbox("Years", [1,3,5,10], index=1)
    if total_alloc <= 0:
        st.warning("Set allocations to compute projections.")
    else:
        proj_df = df_calc.copy()
        proj_df["Weight"] = proj_df["Allocation (%)"] / total_alloc
        fallback = proj_df["_ParsedReturn"].median() if proj_df["_ParsedReturn"].notna().any() else 6.0
        proj_df["_UseReturn"] = proj_df["_ParsedReturn"].fillna(fallback)
        port_ret = (proj_df["_UseReturn"] * proj_df["Weight"]).sum() / 100.0
        future_val = initial * ((1 + port_ret) ** years)
        st.metric(f"Projected value in {years} yrs", f"₹{future_val:,.0f}")
        st.caption(f"Avg annual return used: {port_ret*100:.2f}% (fallback for non-numeric: {fallback:.2f}%)")

# -------------------------
# Automatic insights (fade-in)
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
insights = []
if total_alloc < 90:
    insights.append("Total allocation less than 90% — consider deploying idle cash.")
if total_alloc > 110:
    insights.append("Total allocation exceeds 110% — allocations not normalized.")
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insights.append("Conservative profile expected (low returns).")
    elif weighted_avg_return < 10:
        insights.append("Balanced expected returns (moderate).")
    else:
        insights.append("Aggressive expected returns (higher, with volatility).")

if not st.session_state.current_df.empty:
    top_idx = st.session_state.current_df["Allocation (%)"].idxmax()
    top_asset = st.session_state.current_df.loc[top_idx, "Asset Class"]
    top_alloc = st.session_state.current_df.loc[top_idx, "Allocation (%)"]
    if top_alloc >= 35:
        insights.append(f"High concentration: {top_asset} has {top_alloc:.1f}% allocation — consider diversification.")

# Fade-in insight text (JS)
first_insight = insights[0] if insights else "Portfolio looks balanced — no immediate actions required."
insight_js = f"""
<div id="ins-fade" style="opacity:0; transition: opacity 700ms ease-out; font-weight:600; color:#dffaff;"></div>
<script>
setTimeout(()=>{{ document.getElementById('ins-fade').innerText = {first_insight!r}; document.getElementById('ins-fade').style.opacity = 1; }}, 220);
</script>
"""
st.components.v1.html(insight_js, height=40)
for it in insights:
    st.info(it)

st.markdown("---")
st.caption("Built: Premium Classic Blue · Fade-in animations · selectable profile fields · interactive charts (Plotly) when available.")

