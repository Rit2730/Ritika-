# asset_allocation_final.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import datetime

# Try to import Plotly for advanced visuals; app will gracefully fallback if not present.
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", page_icon="📊")

# -------------------------
# CSS: Cyber Tech theme (black + cyan glow)
# -------------------------
st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg,#000814 0%, #00121b 40%, #001a26 100%); color: #e6fbff; font-family: Inter, Roboto, Arial; }
    .card { background: rgba(255,255,255,0.03); border-radius:12px; padding:16px; border:1px solid rgba(0,255,230,0.06); box-shadow: 0 10px 30px rgba(0,255,230,0.02); }
    .muted { color:#bfefff; opacity:0.9 }
    h1 { color:#bff7ff; text-shadow: 0 6px 24px rgba(0,255,230,0.06); font-weight:800; }
    .section-title{ color:#dffcff; font-weight:700; margin-bottom:6px; }
    .small { font-size:0.9rem; color:#cfeff0 }
    .sidebar .sidebar-content { background: linear-gradient(180deg,#001117,#001825); border-radius:10px; padding:12px; }
    .glow { box-shadow: 0 8px 32px rgba(0,255,230,0.08); border:1px solid rgba(0,255,230,0.06); }
    </style>
    """, unsafe_allow_html=True
)

# -------------------------
# Typing animation + soft click sound (synthesized in browser)
# -------------------------
st.sidebar.header("UI Settings")
enable_sound = st.sidebar.checkbox("Enable soft click sound", value=True)
enable_typing = st.sidebar.checkbox("Enable typing animation", value=True)

# JS for typing + click sound
typing_sound_js = """
<script>
window.playSoftClick = (enabled) => {
  if (!enabled) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = 1000;
    g.gain.value = 0.0025;
    o.connect(g);
    g.connect(ctx.destination);
    o.start();
    setTimeout(()=>{ o.stop(); ctx.close(); }, 40);
  } catch(e) {}
};

window.typeText = (elId, text, speed, enabled) => {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = "";
  let i = 0;
  const doType = () => {
    if (i < text.length) {
      el.innerHTML += text.charAt(i);
      if (enabled) { window.playSoftClick(enabled); }
      i++;
      setTimeout(doType, speed);
    } else {
      el.style.borderRight = '2px solid rgba(0,255,230,0.25)';
      setInterval(()=>{ el.style.borderRight = el.style.borderRight ? '' : '2px solid rgba(0,255,230,0.25)'; }, 700);
    }
  };
  doType();
};
</script>
"""
st.components.v1.html(typing_sound_js, height=0)

# Heading (typing or static based on toggle)
heading_text = "🚀 Asset Allocation"
if enable_typing:
    # Inject an element and start typing
    st.markdown("<div id='main-heading' style='font-size:34px; font-weight:800; color:#bff7ff'></div>", unsafe_allow_html=True)
    st.components.v1.html(f"<script>window.typeText('main-heading', {heading_text!r}, 20, {str(enable_sound).lower()});</script>", height=40)
else:
    st.markdown(f"<h1>{heading_text}</h1>", unsafe_allow_html=True)

st.markdown("<div class='small muted'>Cyber Tech theme · interactive analytics · calculators · export (Excel & CSV)</div>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------------
# Profile templates (preset lists)
# -------------------------
TEMPLATES = {
    "Low Risk (45-65)": pd.DataFrame({
        "Asset Class": ["Government Bonds (G-sec)","AAA Corporate Bonds","PPF/NSC","Fixed Deposits","Short/Mid Debt Funds","REITs","Gold (SGB)","Debt ETFs","Pension/Annuity","Infra Debt"],
        "Risk": ["Very Low","Low","Very Low","Very Low","Low","Low–Mod","Moderate","Low","Very Low","Low–Mod"],
        "Returns (%)": ["4–7","5–8","6–7","5–7","4–7","6–9","3–8","4–7","3–6","6–9"],
        "Horizon": ["3–10 yrs","2–7 yrs","5–15 yrs","1–5 yrs","1–5 yrs","5–10 yrs","3–10 yrs","3–10 yrs","Lifetime","5–10 yrs"],
        "Purpose": ["Income","Income","Retirement","Capital protection","Stable returns","Property income","Inflation hedge","Predictable returns","Guaranteed income","Diversification"],
        "Allocation (%)": [30,20,10,10,10,7,5,3,3,2]
    }),
    "Moderate Risk (30-45)": pd.DataFrame({
        "Asset Class": ["Large-Cap Equity","Mid/Small Cap","Global Equity","Hybrid Funds","Corporate Bonds","REITs","Gold","Private Credit","Farmland","Digital Asset Basket"],
        "Risk": ["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
        "Returns (%)": ["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
        "Horizon": ["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
        "Purpose": ["Growth","Alpha","Diversification","Stability","Income","Property income","Hedge","Yield","Real assets","Asymmetric payoff"],
        "Allocation (%)":[25,15,10,10,10,7,5,5,5,3]
    }),
    "High Risk (25-30)": pd.DataFrame({
        "Asset Class": ["Domestic Equity","International Equity","Venture Capital","Private Equity","Crypto","Commodities","Real Assets","Hedge Funds","IP Royalties","Derivatives"],
        "Risk": ["Very High"]*10,
        "Returns (%)": ["10–15","8–15","20+","15+","Variable","Variable","6–12","Variable","Variable","Variable"],
        "Horizon": ["10+ yrs"]*10,
        "Purpose": ["Growth"]*10,
        "Allocation (%)":[50,15,10,7,5,5,3,3,1,1]
    })
}

# -------------------------
# Sidebar navigation (tabs via selectbox)
# -------------------------
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Asset Builder", "Calculators", "Analysis & Rebalancer"])

# Sidebar controls: profile and import/export
st.sidebar.markdown("---")
profile_choice = st.sidebar.selectbox("Load Profile Preset", list(TEMPLATES.keys()))
if st.sidebar.button("Load preset to workspace"):
    st.session_state['df'] = TEMPLATES[profile_choice].copy()
    st.session_state['profile_name'] = profile_choice
    # ensure numeric
    st.session_state['df']["Allocation (%)"] = pd.to_numeric(st.session_state['df']["Allocation (%)"], errors='coerce').fillna(0.0)
    st.success(f"Loaded preset: {profile_choice}")
    # click sound
    st.components.v1.html(f"<script>window.playSoftClick({str(enable_sound).lower()});</script>", height=0)

uploaded = st.sidebar.file_uploader("Upload CSV to replace workspace", type=["csv"])
if uploaded:
    try:
        uploaded_df = pd.read_csv(uploaded)
        required = {"Asset Class","Allocation (%)","Returns (%)"}
        if not required.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must contain columns: {', '.join(required)}")
        else:
            st.session_state['df'] = uploaded_df.copy()
            st.session_state['df']["Allocation (%)"] = pd.to_numeric(st.session_state['df']["Allocation (%)"], errors='coerce').fillna(0.0)
            st.success("CSV uploaded to workspace")
    except Exception as e:
        st.sidebar.error(f"Failed to read CSV: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("Export options")
download_excel = st.sidebar.checkbox("Enable Excel export", value=True)
download_csv = st.sidebar.checkbox("Enable CSV export", value=True)

# initialize working dataframe
if 'df' not in st.session_state:
    st.session_state['df'] = TEMPLATES["Moderate Risk (30-45)"].copy()
    st.session_state['profile_name'] = "Moderate Risk (30-45)"

df = st.session_state['df']

# Utility functions
def parse_return(v):
    if pd.isna(v): return None
    if isinstance(v, (int,float)): return float(v)
    s = str(v).replace("%","").replace("–","-").strip()
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

def weighted_avg_return(df_):
    tmp = df_.copy()
    tmp["_r"] = tmp["Returns (%)"].apply(parse_return)
    total = tmp["Allocation (%)"].sum()
    if total <= 0 or tmp["_r"].dropna().empty: return None
    return (tmp.loc[tmp["_r"].notna(), "_r"] * tmp.loc[tmp["_r"].notna(), "Allocation (%)"]).sum() / total

def excel_bytes(df_):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_.to_excel(writer, index=False, sheet_name="Portfolio")
    buf.seek(0)
    return buf

def html_report(df_, profile_name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = ""
    for _, r in df_.iterrows():
        rows += f"<tr><td>{r['Asset Class']}</td><td>{r['Risk']}</td><td>{r['Returns (%)']}</td><td>{r['Horizon']}</td><td>{r['Purpose']}</td><td style='text-align:right'>{r['Allocation (%)']}</td></tr>"
    html = f"""
    <html><head><meta charset='utf-8'><title>Portfolio Report</title></head><body>
    <h2>Portfolio Report — {profile_name}</h2>
    <p>Generated: {now}</p>
    <table border='1' cellpadding='6' cellspacing='0'>
    <thead><tr><th>Asset Class</th><th>Risk</th><th>Returns</th><th>Horizon</th><th>Purpose</th><th>Allocation (%)</th></tr></thead>
    <tbody>{rows}</tbody></table></body></html>
    """
    return html

# -------------------------
# Pages
# -------------------------
# --- Dashboard Page
if page == "Dashboard":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Overview</div>", unsafe_allow_html=True)
    total_alloc = df["Allocation (%)"].sum()
    wavg = weighted_avg_return(df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Allocation (%)", f"{total_alloc:.2f}")
    c2.metric("Weighted Avg Return (%)", f"{wavg:.2f}" if wavg is not None else "N/A")
    # simple diversification metric (1 - HHI)
    weights = df["Allocation (%)"] / (total_alloc if total_alloc>0 else 1)
    hhi = (weights**2).sum()
    divers = round((1 - hhi) * 100, 1)
    c3.metric("Diversification Score", f"{divers}%")
    st.markdown("---")

    st.markdown("<div class='section-title'>Charts</div>", unsafe_allow_html=True)
    if PLOTLY_OK:
        # Donut
        fig_donut = px.pie(df, names="Asset Class", values="Allocation (%)", hole=0.45, title="Allocation (Donut)")
        fig_donut.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True, height=420)

        # Pie (alternate view)
        fig_pie = px.pie(df, names="Asset Class", values="Allocation (%)", title="Allocation (Pie)")
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True, height=420)

        # 3D Bar Chart
        st.markdown("3D Allocation (Interactive)")
        tmp = df.reset_index().rename(columns={"index":"idx"})
        x = tmp.index.tolist()
        z = tmp["Allocation (%)"].tolist()
        names = tmp["Asset Class"].tolist()
        fig3d = go.Figure(data=[go.Bar3d(
            x=x, y=[0]*len(x), z=[0]*len(x), dx=0.6, dy=0.6, dz=z, text=names, hovertemplate="%{text}<br>Allocation: %{dz}%<extra></extra>"
        )])
        fig3d.update_layout(scene=dict(
            xaxis=dict(title="Asset (index)", tickmode='array', tickvals=x, ticktext=names, tickangle=45),
            yaxis=dict(title="Group"),
            zaxis=dict(title="Allocation (%)")
        ), margin=dict(l=0,r=0,b=0,t=30), height=520)
        st.plotly_chart(fig3d, use_container_width=True, height=520)

        # Line / Area (simulate allocation shift timeline — simple sample)
        st.markdown("Allocation Trend (simulated)")
        # build a simple timeseries for the allocation share across 6 months by keeping same allocation but show lines
        months = pd.date_range(end=pd.Timestamp.today(), periods=6, freq='M').strftime("%b %Y").tolist()
        trend_df = pd.DataFrame({m: df["Allocation (%)"].values for m in months})
        trend_df["Asset Class"] = df["Asset Class"]
        trend_df = trend_df.set_index("Asset Class").T  # months x assets
        fig_line = px.line(trend_df, x=trend_df.index, y=trend_df.columns, labels={'value':'Allocation (%)','variable':'Asset'})
        fig_line.update_layout(title="Allocation by Month (simulated)", legend_title_text='Asset')
        st.plotly_chart(fig_line, use_container_width=True, height=420)

        fig_area = px.area(trend_df, x=trend_df.index, y=trend_df.columns)
        fig_area.update_layout(title="Area view (simulated allocation)", legend_title_text='Asset')
        st.plotly_chart(fig_area, use_container_width=True, height=420)

    else:
        st.warning("Plotly not installed — showing fallback charts.")
        st.bar_chart(df.set_index("Asset Class")["Allocation (%)"])
    st.markdown("</div>", unsafe_allow_html=True)

# --- Asset Builder Page
elif page == "Asset Builder":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Asset Builder & Editor</div>", unsafe_allow_html=True)
    # Use data_editor if available; fallback to controlled inputs
    try:
        if hasattr(st, "data_editor"):
            edited = st.data_editor(df, num_rows="dynamic")
            if st.button("Apply table edits"):
                # sanitize allocation
                edited["Allocation (%)"] = pd.to_numeric(edited["Allocation (%)"], errors="coerce").fillna(0.0)
                st.session_state['df'] = edited.copy()
                st.success("Applied table edits")
        else:
            raise AttributeError
    except Exception:
        st.warning("Inline data editor not available — using field-based editor.")
        cols = st.columns(2)
        with cols[0]:
            # select asset to edit
            asset = st.selectbox("Select asset", df["Asset Class"].tolist())
            idx = df.index[df["Asset Class"] == asset].tolist()[0]
            row = df.loc[idx]
            risk = st.selectbox("Risk", options=["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"], index=0)
            horizon = st.selectbox("Horizon", options=sorted(df["Horizon"].unique().tolist()), index=0)
            purpose = st.selectbox("Purpose", options=sorted(df["Purpose"].unique().tolist()), index=0)
            ret = st.text_input("Returns (%)", value=str(row["Returns (%)"]))
            alloc = st.slider("Allocation (%)", 0.0, 100.0, float(row["Allocation (%)"]), step=0.1)
            if st.button("Apply changes"):
                st.session_state['df'].at[idx, "Risk"] = risk
                st.session_state['df'].at[idx, "Horizon"] = horizon
                st.session_state['df'].at[idx, "Purpose"] = purpose
                st.session_state['df'].at[idx, "Returns (%)"] = ret
                st.session_state['df'].at[idx, "Allocation (%)"] = alloc
                st.success(f"Updated {asset}")

        with cols[1]:
            st.markdown("### Add new asset")
            name = st.text_input("Asset Class name")
            nrisk = st.selectbox("Risk (new)", options=["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"])
            nhorizon = st.selectbox("Horizon (new)", options=["1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"])
            npurpose = st.selectbox("Purpose (new)", options=["Growth","Income","Retirement","Tax Saving","Hedge"])
            nret = st.text_input("Returns (%) (new)")
            nalloc = st.slider("Allocation (%) (new)", 0.0, 100.0, 0.0, step=0.1)
            if st.button("Add asset"):
                if name.strip()=="":
                    st.error("Asset name required")
                else:
                    new_row = {"Asset Class": name.strip(), "Risk": nrisk, "Returns (%)": nret, "Horizon": nhorizon, "Purpose": npurpose, "Allocation (%)": float(nalloc)}
                    st.session_state['df'] = pd.concat([st.session_state['df'], pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"Added {name.strip()}")
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.dataframe(st.session_state['df'].reset_index(drop=True), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Calculators
elif page == "Calculators":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Investment Calculators</div>", unsafe_allow_html=True)

    st.markdown("### Lumpsum projection")
    lumpsum = st.number_input("Initial amount (₹)", min_value=100.0, value=100000.0, step=1000.0)
    yrs = st.selectbox("Horizon (years)", [1,3,5,10,15,20], index=2, key="lv_yrs")
    # use weighted avg return as default if available
    defret = weighted_avg_return(st.session_state['df'])
    rate = st.number_input("Expected annual return (%)", min_value=0.0, value=float(defret) if defret else 7.0)
    fv = lumpsum * ((1 + rate/100.0) ** yrs)
    st.metric(f"Future value after {yrs} yrs", f"₹{fv:,.0f}")

    st.markdown("---")
    st.markdown("### SIP projection (monthly)")
    sip = st.number_input("Monthly SIP amount (₹)", min_value=100.0, value=5000.0, step=100.0)
    sip_years = st.selectbox("SIP horizon (years)", [1,3,5,10,15,20], index=2, key="sip_years")
    sip_rate = st.number_input("Expected annual return (%)", min_value=0.0, value=float(defret) if defret else 7.0, key="sip_rate")
    months = sip_years * 12
    r = sip_rate / 100.0 / 12.0
    if r == 0:
        fv_sip = sip * months
    else:
        fv_sip = sip * (( (1 + r) ** months - 1) / r) * (1 + r)
    st.metric(f"SIP projected value in {sip_years} yrs", f"₹{fv_sip:,.0f}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Analysis & Rebalancer
elif page == "Analysis & Rebalancer":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Analysis & Quick Rebalancer</div>", unsafe_allow_html=True)
    st.markdown("Current portfolio snapshot:")
    st.dataframe(st.session_state['df'].reset_index(drop=True), use_container_width=True)
    st.markdown("---")
    st.markdown("Choose a target preset to compare and get rebalance steps:")
    target = st.selectbox("Target preset", list(TEMPLATES.keys()))
    if st.button("Generate rebalance suggestion"):
        target_df = TEMPLATES[target].copy()
        merged = pd.merge(st.session_state['df'][["Asset Class","Allocation (%)"]], target_df[["Asset Class","Allocation (%)"]], on="Asset Class", how="outer", suffixes=("_cur","_tgt")).fillna(0)
        merged["Delta"] = merged["Allocation (%)_tgt"] - merged["Allocation (%)_cur"]
        sells = merged[merged["Delta"]<0]
        buys = merged[merged["Delta"]>0]
        st.markdown("**Sell (reduce)**")
        if sells.empty: st.write("No sells necessary.")
        else:
            for _, r in sells.iterrows():
                st.write(f"- {r['Asset Class']}: reduce by {abs(r['Delta']):.2f}%")
        st.markdown("**Buy (increase)**")
        if buys.empty: st.write("No buys necessary.")
        else:
            for _, r in buys.iterrows():
                st.write(f"- {r['Asset Class']}: increase by {r['Delta']:.2f}%")
    st.markdown("---")
    # Export HTML report
    st.markdown("Download printable HTML report:")
    html = html_report(st.session_state['df'], st.session_state.get('profile_name','Workspace'))
    b64 = base64.b64encode(html.encode()).decode()
    st.markdown(f'<a href="data:text/html;base64,{b64}" download="portfolio_report.html">Download HTML report (open & Print → Save as PDF)</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Global export buttons (visible on all pages)
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Export / Save</div>", unsafe_allow_html=True)
if download_csv:
    csv_bytes = st.session_state['df'].to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.csv", mime="text/csv")
if download_excel:
    try:
        buf = excel_bytes(st.session_state['df'])
        st.download_button("Download Excel (.xlsx)", data=buf, file_name=f"{st.session_state.get('profile_name','portfolio')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error("Excel export failed — ensure openpyxl is installed. Error: " + str(e))
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.caption("Final app — Cyber Tech theme · All requested features included. If charts don't render, add 'plotly' to requirements.txt and redeploy.")
