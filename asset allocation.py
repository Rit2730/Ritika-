# asset_allocation_pro_advanced.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import textwrap
import datetime

# Try Plotly for advanced interactive charts
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", page_icon="📈")

# -------------------------
# THEME: Royal Blue + Silver glossy
# -------------------------
st.markdown(
    """
    <style>
    /* page */
    .stApp {
      background: linear-gradient(180deg,#071a3a 0%, #032b5a 45%, #001831 100%);
      color: #eaf7ff;
      font-family: Inter, Roboto, Arial, sans-serif;
    }
    /* glass card */
    .card {
      background: rgba(255,255,255,0.04);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid rgba(255,255,255,0.06);
      box-shadow: 0 8px 30px rgba(0,0,0,0.6);
      backdrop-filter: blur(6px);
    }
    .muted { color:#cfefff; opacity:0.9; font-size:0.95rem; }
    .small { font-size:0.9rem; color:#dff7ff; opacity:0.9; }
    .section-title { color: #d8f4ff; font-weight:700; font-size:20px; margin-bottom:8px; }
    hr { border:none; border-top:1px solid rgba(255,255,255,0.04); margin:12px 0; }
    </style>
    """, unsafe_allow_html=True
)

# -------------------------
# Header with fade-in (no sound)
# -------------------------
st.markdown("<div style='font-size:34px; font-weight:800; color:#e8f9ff; text-shadow:0 4px 18px rgba(0,140,255,0.15)'>Asset Allocation</div>", unsafe_allow_html=True)
st.markdown("<div class='muted'>Professional portfolio dashboard — interactive charts, calculators, rebalancer & exports</div>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------------
# Predefined portfolio templates (detailed)
# -------------------------
LOW = {
    "Asset Class": ["Government Bonds (G-sec)", "AAA Corporate Bonds", "PPF / NSC / Small Savings", "Fixed Deposits",
                    "Short/Mid-Term Debt Funds", "REITs", "Gold (SGB/ETF)", "Target Maturity Debt ETFs",
                    "Annuity Plans / Pension Income", "Infra Debt / InvIT Debt"],
    "Risk": ["Very Low","Low","Very Low","Very Low","Low","Low–Mod","Moderate","Low","Very Low","Low–Mod"],
    "Returns (%)": ["4–7","5–8","6–7","5–7","4–7","6–9","3–8","4–7","3–6","6–9"],
    "Horizon": ["3–10 yrs","2–7 yrs","5–15 yrs","1–5 yrs","1–5 yrs","5–10 yrs","3–10 yrs","3–10 yrs","Lifetime","5–10 yrs"],
    "Purpose": ["Income","Income","Retirement","Capital protection","Stable returns","Property income","Hedge","Predictable returns","Guaranteed income","Diversification"],
    "Allocation (%)": [30,20,10,10,10,7,5,3,3,2]
}

MOD = {
    "Asset Class": ["Large-Cap Equity Funds","Mid/Small-Cap Funds","Global Equity ETFs/Funds","Hybrid/Balanced Funds",
                    "Corporate Bond Funds","REITs","Gold","Private Credit / Debt AIF","Farmland / Agro Real Assets","Digital Asset Basket (tiny)"],
    "Risk": ["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
    "Returns (%)": ["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
    "Horizon": ["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
    "Purpose": ["Growth","Alpha","Diversification","Stability","Income","Property income","Hedge","Yield","Real assets","Asymmetric payoff"],
    "Allocation (%)": [25,15,10,10,10,7,5,5,5,3]
}

HIGH = {
    "Asset Class": ["Domestic Equity (Large/Mid/Small)","International Equities","Venture Capital / Startup Investments",
                    "Private Equity Funds","Crypto / Blockchain Assets","Commodities (Energy/Metals ETFs)",
                    "Real Assets (Timber/Renewables)","Structured Products / Hedge Funds","IP / Music Royalties","Active Derivatives (Hedged)"],
    "Risk": ["Very High"]*10,
    "Returns (%)": ["10–15","8–15","20+","15+","Highly variable","Varies","6–12","Varies","Variable","Variable"],
    "Horizon": ["10–20 yrs"]*10,
    "Purpose": ["Growth"]*10,
    "Allocation (%)": [50,15,10,7,5,5,3,3,1,1]
}

PROFILE_TEMPLATES = {
    "Low Risk (45-65)": pd.DataFrame(LOW),
    "Moderate Risk (30-45)": pd.DataFrame(MOD),
    "High Risk (25-30)": pd.DataFrame(HIGH)
}

# -------------------------
# Sidebar: controls (Side Menu)
# -------------------------
st.sidebar.markdown("<div style='font-weight:700; font-size:16px; color:#d8f4ff'>Controls</div>", unsafe_allow_html=True)
profile_choice = st.sidebar.selectbox("Select Profile", list(PROFILE_TEMPLATES.keys()))
age_group = st.sidebar.selectbox("Investor Age Group", ["25-30","30-45","45-65"], index=1)
objective = st.sidebar.selectbox("Investment Objective", ["Growth","Income","Retirement","Tax Saving","Short-Term"], index=0)

# advanced options
st.sidebar.markdown("---")
st.sidebar.subheader("Display & Export")
enable_3d = st.sidebar.checkbox("Enable 3D charts (Plotly)", value=True)
enable_animations = st.sidebar.checkbox("Enable chart animations", value=True)
export_excel = st.sidebar.checkbox("Enable Excel export", value=True)
export_pdf = st.sidebar.checkbox("Include printable HTML report (save-as-PDF)", value=True)

# load template into session
if "current_profile" not in st.session_state or st.session_state.current_profile != profile_choice:
    st.session_state.current_profile = profile_choice
    st.session_state.df = PROFILE_TEMPLATES[profile_choice].copy()
    # ensure numeric Allocation
    st.session_state.df["Allocation (%)"] = pd.to_numeric(st.session_state.df["Allocation (%)"], errors="coerce").fillna(0.0)

df = st.session_state.df

# -------------------------
# Helper functions
# -------------------------
def parse_return_value(s):
    if pd.isna(s): return None
    if isinstance(s,(int,float)): return float(s)
    s = str(s).replace("%","").replace("–","-").replace("—","-").strip()
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

def df_weighted_return(df_):
    dfc = df_.copy()
    dfc["_ret"] = dfc["Returns (%)"].apply(parse_return_value)
    total = dfc["Allocation (%)"].sum()
    if total<=0 or dfc["_ret"].dropna().empty: return None
    weighted = (dfc.loc[dfc["_ret"].notna(), "_ret"] * dfc.loc[dfc["_ret"].notna(), "Allocation (%)"]).sum() / total
    return weighted

def get_download_link_excel(df_):
    # returns bytes (xlsx)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_.to_excel(writer, index=False, sheet_name="Portfolio")
    buffer.seek(0)
    return buffer

def get_html_report(df_, profile, objective, age_group, projection_summary=None):
    # Simple HTML report that the user can print to PDF
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = ""
    for _, r in df_.iterrows():
        rows += f"<tr><td>{r['Asset Class']}</td><td>{r['Risk']}</td><td>{r['Returns (%)']}</td><td>{r['Horizon']}</td><td>{r['Purpose']}</td><td style='text-align:right'>{r['Allocation (%)']}</td></tr>"
    proj_html = ""
    if projection_summary:
        proj_html = f"<h4>Projection</h4><p>{projection_summary}</p>"
    html = f"""
    <html><head><meta charset='utf-8'><title>Portfolio Report</title>
    <style>
      body{{font-family: Arial, Helvetica, sans-serif; color:#0b2033}}
      table{{border-collapse:collapse; width:100%}}
      td,th{{border:1px solid #ddd; padding:8px; font-size:13px}}
      th{{background:#f2f4f7; color:#021a33}}
    </style>
    </head>
    <body>
    <h2>Asset Allocation Report</h2>
    <p><strong>Profile:</strong> {profile} &nbsp;&nbsp; <strong>Objective:</strong> {objective} &nbsp;&nbsp; <strong>Age:</strong> {age_group}</p>
    <p>Generated: {now}</p>
    {proj_html}
    <h3>Holdings</h3>
    <table><thead><tr><th>Asset Class</th><th>Risk</th><th>Returns (%)</th><th>Horizon</th><th>Purpose</th><th>Allocation (%)</th></tr></thead>
    <tbody>{rows}</tbody></table>
    </body></html>
    """
    return html

# -------------------------
# Main: left controls card & right dashboard cards
# -------------------------
left_col, right_col = st.columns([1, 2.2])

with left_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio Manager</div>", unsafe_allow_html=True)

    # Asset selector (dropdown) + editable fields via selects
    asset_choices = df["Asset Class"].tolist()
    selected_asset = st.selectbox("Select asset to edit", options=asset_choices)

    idx = df.index[df["Asset Class"] == selected_asset].tolist()[0]
    row = df.loc[idx].copy()

    # Dropdowns and controlled inputs
    risk_options = ["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"]
    horizon_options = sorted(df["Horizon"].unique().tolist()) if not df["Horizon"].isna().all() else ["1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"]
    purpose_options = sorted(df["Purpose"].unique().tolist()) if not df["Purpose"].isna().all() else ["Growth","Income","Retirement","Tax Saving","Hedge"]

    new_risk = st.selectbox("Risk", options=risk_options, index=risk_options.index(row["Risk"]) if row["Risk"] in risk_options else 0)
    new_horizon = st.selectbox("Horizon", options=horizon_options, index=0)
    new_purpose = st.selectbox("Purpose", options=purpose_options, index=0)
    new_return = st.text_input("Returns (%) (range or single)", value=str(row.get("Returns (%)","")))
    new_alloc = st.number_input("Allocation (%)", value=float(row.get("Allocation (%)",0.0)), min_value=0.0, max_value=100.0, step=0.1)

    col_a, col_b = st.columns([1,1])
    if col_a.button("Apply changes"):
        st.session_state.df.at[idx, "Risk"] = new_risk
        st.session_state.df.at[idx, "Horizon"] = new_horizon
        st.session_state.df.at[idx, "Purpose"] = new_purpose
        st.session_state.df.at[idx, "Returns (%)"] = new_return
        st.session_state.df.at[idx, "Allocation (%)"] = float(new_alloc)
        st.success(f"Updated {selected_asset}")
    if col_b.button("Remove asset"):
        st.session_state.df = st.session_state.df.drop(index=idx).reset_index(drop=True)
        st.success(f"Removed {selected_asset}")

    st.markdown("---")
    st.markdown("**Add new asset**")
    add_name = st.text_input("Asset Class name")
    add_risk = st.selectbox("Risk (new)", options=risk_options, index=1)
    add_horizon = st.selectbox("Horizon (new)", options=horizon_options, index=0)
    add_purpose = st.selectbox("Purpose (new)", options=purpose_options, index=0)
    add_return = st.text_input("Returns (%) (new)")
    add_alloc = st.number_input("Allocation (%) (new)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    if st.button("Add asset"):
        if add_name.strip()=="":
            st.error("Enter an asset class name.")
        else:
            new_row = {"Asset Class": add_name.strip(), "Risk": add_risk, "Returns (%)": add_return,
                       "Horizon": add_horizon, "Purpose": add_purpose, "Allocation (%)": float(add_alloc)}
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Added {add_name.strip()}")

    st.markdown("---")
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.df["Allocation (%)"].sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state.df["Allocation (%)"] = (st.session_state.df["Allocation (%)"] / total * 100).round(2)
            st.success("Allocations normalized to 100%")

    st.markdown("---")
    if export_excel:
        excel_buffer = get_download_link_excel(st.session_state.df)
        st.download_button("Download portfolio (Excel)", data=excel_buffer, file_name=f"{profile_choice.replace(' ','_')}.xlsx", mime="application/vnd.ms-excel")
    # CSV always available
    csv = st.session_state.df.to_csv(index=False).encode()
    st.download_button("Download portfolio (CSV)", data=csv, file_name=f"{profile_choice.replace(' ','_')}.csv", mime="text/csv")

    # printable HTML
    if export_pdf:
        html = get_html_report(st.session_state.df, profile_choice, objective, age_group, None)
        b64 = base64.b64encode(html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="portfolio_report.html">Download printable HTML report (Save as PDF)</a>'
        st.markdown(href, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    # dashboard cards: metrics, charts, rebalancer, calculators
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)

    total_alloc = st.session_state.df["Allocation (%)"].sum()
    weighted_ret = df_weighted_return(st.session_state.df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Allocation (%)", f"{total_alloc:.2f}")
    c2.metric("Weighted Avg Return (%)", f"{weighted_ret:.2f}" if weighted_ret is not None else "N/A")
    # diversification score (simple Herfindahl)
    weights = st.session_state.df["Allocation (%)"] / (total_alloc if total_alloc>0 else 1)
    herf = (weights**2).sum()
    divers_score = round((1 - herf) * 100, 1)
    c3.metric("Diversification Score", f"{divers_score}%")

    st.markdown("---")

    # CHARTS area
    st.markdown("<div class='section-title'>Visuals</div>", unsafe_allow_html=True)
    if PLOTLY_OK and enable_3d:
        # interactive donut/pie (animated option)
        fig = px.pie(st.session_state.df, names="Asset Class", values="Allocation (%)", hole=0.45)
        if enable_animations:
            fig.update_traces(textinfo='percent+label', pull=[0.02]*len(st.session_state.df))
        else:
            fig.update_traces(textinfo='percent+label')
        fig.update_layout(title_text="Allocation (Donut)")
        st.plotly_chart(fig, use_container_width=True, height=420)

        # 3D Bar: x index, y group, z = allocation
        st.markdown("3D Allocation Bar")
        df3 = st.session_state.df.reset_index().rename(columns={"index":"idx"})
        # create numeric x axis
        x_vals = df3.index.tolist()
        y_vals = [0]*len(x_vals)
        z_vals = df3["Allocation (%)"].tolist()
        names = df3["Asset Class"].tolist()

        bar3d = go.Figure(data=[go.Bar3d(
            x=x_vals, y=y_vals, z=[0]*len(z_vals),
            dx=0.6, dy=0.6, dz=z_vals,
            text=names,
            hovertemplate="%{text}<br>Allocation: %{dz}%<extra></extra>"
        )])
        bar3d.update_layout(scene=dict(
            xaxis=dict(title="Asset index", tickmode='array', tickvals=x_vals, ticktext=names, tickangle=45),
            yaxis=dict(title="Group"),
            zaxis=dict(title="Allocation (%)")
        ), height=520, margin=dict(l=0,r=0,b=0,t=30))
        st.plotly_chart(bar3d, use_container_width=True, height=520)
    else:
        st.warning("Plotly not available or 3D disabled — showing fallback charts.")
        st.bar_chart(st.session_state.df.set_index("Asset Class")["Allocation (%)"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Calculator & projection card
    st.markdown("<div class='card' style='margin-top:12px'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Calculators</div>", unsafe_allow_html=True)

    st.markdown("**Lumpsum Projection**")
    lumpsum = st.number_input("Initial amount (₹)", min_value=100.0, value=100000.0, step=1000.0)
    years = st.selectbox("Projection years (lumpsum)", [1,3,5,10,15,20], index=2)
    rate = st.number_input("Expected annual return (%)", min_value=0.0, value=weighted_ret if weighted_ret else 7.0, step=0.1)
    fv = lumpsum * ((1 + rate/100.0) ** years)
    st.metric(f"Future value in {years} yrs", f"₹{fv:,.0f}")

    st.markdown("---")
    st.markdown("**SIP Projection (monthly)**")
    sip = st.number_input("Monthly SIP amount (₹)", min_value=100.0, value=5000.0, step=100.0)
    sip_years = st.selectbox("SIP horizon (years)", [1,3,5,10,15,20], index=2, key="sip_years")
    sip_rate = st.number_input("Expected annual return (%) for SIP", min_value=0.0, value=rate, step=0.1, key="sip_rate")
    months = sip_years * 12
    r = sip_rate / 100.0 / 12.0
    # future value of series
    if r == 0:
        fv_sip = sip * months
    else:
        fv_sip = sip * (( (1 + r) ** months - 1) / r) * (1 + r)
    st.metric(f"SIP projected value in {sip_years} yrs", f"₹{fv_sip:,.0f}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Rebalancer suggestions card
    st.markdown("<div class='card' style='margin-top:12px'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Quick Rebalancer</div>", unsafe_allow_html=True)
    target_profile = st.selectbox("Select target profile to rebalance to", list(PROFILE_TEMPLATES.keys()))
    if st.button("Suggest rebalance steps"):
        target_df = PROFILE_TEMPLATES[target_profile].copy()
        # Merge by Asset Class; simple approach: align exact names else suggest to add
        cur = st.session_state.df.copy()
        # create mapping for assets present in both
        merged = pd.merge(cur[['Asset Class','Allocation (%)']], target_df[['Asset Class','Allocation (%)']], on='Asset Class', how='outer', suffixes=('_cur','_tgt')).fillna(0)
        merged['Delta'] = merged['Allocation (%)_tgt'] - merged['Allocation (%)_cur']
        sells = merged[merged['Delta']<0]
        buys = merged[merged['Delta']>0]
        st.markdown("**Sell (reduce)**")
        if sells.empty:
            st.write("No sell suggestions — current allocations are below target.")
        else:
            for _, r in sells.iterrows():
                st.write(f"- {r['Asset Class']}: reduce by {abs(r['Delta']):.2f}%")
        st.markdown("**Buy (increase)**")
        if buys.empty:
            st.write("No buy suggestions — current allocations at or above target.")
        else:
            for _, r in buys.iterrows():
                st.write(f"- {r['Asset Class']}: increase by {r['Delta']:.2f}%")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Footer info
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.caption("Pro dashboard — Royal Blue + Silver theme · Interactive visuals (Plotly) · Exports & calculators. If Plotly charts do not render, ensure plotly is included in requirements.txt for Streamlit Cloud.")

