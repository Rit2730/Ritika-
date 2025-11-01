# asset_allocation_glossy_blue.py
import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO

# Try plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", page_icon="📊")

# ======================================
# Glossy Dark Blue Theme Enhancement ✨
# ======================================
st.markdown(
    """
    <style>
    .stApp {
      background: radial-gradient(circle at top, #001c38 0%, #00152a 40%, #000b14 100%);
      color: #e8f6ff;
      font-family: 'Segoe UI', sans-serif;
    }
    .card {
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(8px);
      border-radius: 14px;
      padding: 18px;
      border: 1px solid rgba(255,255,255,0.12);
      box-shadow: 0 0 18px rgba(0,94,255,0.28);
    }
    .stSidebar .sidebar-content {
      background: linear-gradient(180deg,#021423,#001d33);
      color: #cfeef0;
      border-radius: 10px;
      padding: 12px;
      border: 1px solid rgba(0,94,255,0.35);
    }
    h1, h2, h3 {
      color: #b9ddff;
      text-shadow: 0px 0px 8px rgba(0,123,255,0.65);
    }
    </style>
    """, unsafe_allow_html=True
)

# ======================================
# Heading (Updated)
# ======================================
title_html = """
<div id='main-title' style='font-size:36px;font-weight:750;margin-bottom:10px' class='fade-in'>
🚀 Asset Allocation Dashboard
</div>
"""
st.components.v1.html(title_html, height=80)

st.markdown("<hr/>", unsafe_allow_html=True)

# ======================================
# Sound Toggle persists ✔
# ======================================
st.sidebar.header("Presentation & Controls")
enable_sound = st.sidebar.checkbox("Enable typing click sound", value=False)

sound_js = """
<script>
window.playSoftClick = (enable) => {
  if (!enable) return;
  const ctx = new (window.AudioContext||window.webkitAudioContext)();
  const o = ctx.createOscillator();
  const g = ctx.createGain();
  o.type = 'triangle';
  o.frequency.value = 750;
  g.gain.value = 0.003;
  o.connect(g);
  g.connect(ctx.destination);
  o.start();
  setTimeout(()=>{ o.stop(); ctx.close(); }, 30);
};
</script>
"""
st.components.v1.html(sound_js, height=0)

def click():
    st.components.v1.html(f"<script>window.playSoftClick({str(enable_sound).lower()});</script>", height=0)

# ======================================
# Profiles Data (same)
# ======================================
profiles = {
    "Low Risk (45–65 yrs)": pd.DataFrame({
        "Asset Class":["Government Bonds","AAA Corporate Bonds","PPF / NSC","FD","Debt Funds","REITs","Gold","Debt ETFs","Pension Income","Infra Debt"],
        "Risk":["Very Low","Low","Very Low","Very Low","Low","Low–Mod","Moderate","Low","Very Low","Low–Mod"],
        "Returns (%)":["4–7","5–8","6–7","5–7","4–7","6–9","3–8","4–7","3–6","6–9"],
        "Horizon":["3–10 yrs","2–7 yrs","5–15 yrs","1–5 yrs","1–5 yrs","5–10 yrs","3–10 yrs","3–10 yrs","Lifetime","5–10 yrs"],
        "Purpose":["Income"]*10,
        "Allocation (%)":[30,20,10,10,10,7,5,3,3,2]
    }),
    "Moderate Risk (30–45 yrs)": pd.DataFrame({
        "Asset Class":["Large-Cap Equity","Mid/Small Cap","Global Equity","Hybrid Funds","Corporate Bonds","REITs","Gold","Private Credit","Farmland","Digital Assets"],
        "Risk":["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
        "Returns (%)":["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
        "Horizon":["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
        "Purpose":["Growth"]*10,
        "Allocation (%)":[25,15,10,10,10,7,5,5,5,3]
    }),
    "High Risk (25–30 yrs)": pd.DataFrame({
        "Asset Class":[
            "Domestic Equity","International Equity","Venture Capital","Private Equity",
            "Crypto","Commodities","Real Assets","Hedge Funds","IP Royalties","Derivatives"
        ],
        "Risk":["Very High"]*10,
        "Returns (%)":["10–15","8–15","20+","15+","Variable","Variable","6–12","Variable","Variable","Variable"],
        "Horizon":["10+ yrs"]*10,
        "Purpose":["Growth"]*10,
        "Allocation (%)":[50,15,10,7,5,5,3,3,1,1]
    })
}

st.sidebar.header("Investor Profile")
profile_selected = st.sidebar.selectbox("Risk Profile", list(profiles.keys()))
click()

if "df" not in st.session_state or st.session_state.profile != profile_selected:
    st.session_state.df = profiles[profile_selected].copy()
    st.session_state.profile = profile_selected

df = st.session_state.df

# ======================================
# Charts Section Updated ✅ PIE + 3D BAR
# ======================================
st.subheader("Portfolio Analytics")

if PLOTLY_OK:
    # PIE (Donut)
    pie = px.pie(df, names="Asset Class", values="Allocation (%)", hole=.45)
    pie.update_layout(title="Allocation Distribution - Donut Pie")
    st.plotly_chart(pie, use_container_width=True)

    # 3D BAR CHART ✅
    df_num = df.copy()
    df_num["_val"] = df_num["Allocation (%)"]

    bar3d = go.Figure(data=[go.Bar3d(
        x=df_num["Asset Class"],
        y=["Portfolio"]*len(df_num),
        z=[0]*len(df_num),
        dx=[0.5]*len(df_num),
        dy=[0.5]*len(df_num),
        dz=df_num["_val"],
        text=df_num["Allocation (%)"],
        hoverinfo='text'
    )])
    bar3d.update_layout(
        title="3D Allocation Bar Graph",
        scene=dict(
            xaxis_title="Assets", yaxis_title="Group", zaxis_title="Allocation (%)"
        ),
        margin=dict(l=0,r=0,b=0,t=30)
    )
    st.plotly_chart(bar3d, use_container_width=True)

else:
    st.warning("Plotly missing: install plotly to unlock pie + 3D bar features.")
    st.bar_chart(df.set_index("Asset Class")["Allocation (%)"])

st.dataframe(df, use_container_width=True)
