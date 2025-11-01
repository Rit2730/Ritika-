import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Asset Allocation", layout="wide", page_icon="📊")

# --- CUSTOM STYLING ---
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white !important;
    font-family: 'Segoe UI', sans-serif;
}
.css-1d391kg, .css-ffhzg2, .stMarkdown, .css-10trblm, .css-q8sbsg {
    color: white !important;
}
h1, h2, h3 {
    text-shadow: 1px 1px 2px black;
}
</style>
""", unsafe_allow_html=True)

# --- SOUND EFFECT ---
sound_html = """
<audio autoplay>
  <source src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg" type="audio/ogg">
</audio>
"""

# --- DATASETS ---
low_risk = pd.DataFrame({
    "Asset Class": ["Government Bonds (G-sec)", "AAA Corporate Bonds", "PPF / NSC",
                    "Fixed Deposits", "Short/Mid Debt Funds", "REITs",
                    "Gold", "Target Maturity ETFs", "Annuity Plans", "Infra Debt"],
    "Allocation %": [30, 20, 10, 10, 10, 7, 5, 3, 3, 2]
})

moderate_risk = pd.DataFrame({
    "Asset Class": ["Large-Cap Funds", "Mid/Small-Cap Funds", "Global Equity",
                    "Hybrid Funds", "Corporate Bond Funds", "REITs", "Gold",
                    "Private Credit", "Farmland Assets", "Digital Assets"],
    "Allocation %": [25, 15, 10, 10, 10, 7, 5, 5, 5, 3]
})

high_risk = pd.DataFrame({
    "Asset Class": ["Domestic Equity", "International Equity", "Venture Capital",
                    "Private Equity", "Crypto", "Commodities", "Real Assets",
                    "Hedge Funds", "IP Royalties", "Active Derivatives"],
    "Allocation %": [50, 15, 10, 7, 5, 5, 3, 3, 1, 1]
})

risk_options = {"Low Risk (45–65 yrs)": low_risk,
                "Moderate Risk (30–45 yrs)": moderate_risk,
                "High Risk (25–30 yrs)": high_risk}

# --- HEADER with Animated Typing ---
title_text = "💼 Smart Asset Allocation Advisor"
for char in title_text:
    st.markdown(f"<span style='font-size:38px; font-weight:700;'>{char}</span>", unsafe_allow_html=True)
    time.sleep(0.02)

st.markdown("### Choose Profile to View Suggested Portfolio")

# --- USER INPUT ---
selected_risk = st.selectbox("Select Investor Profile:", list(risk_options.keys()))

# Play sound
st.markdown(sound_html, unsafe_allow_html=True)

df = risk_options[selected_risk]

# --- EDITABLE TABLE ---
st.subheader("📋 Suggested Asset Allocation")
edited_df = st.data_editor(df, use_container_width=True)

# --- CHARTS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Allocation Pie Chart")
    fig1 = px.pie(edited_df, names="Asset Class", values="Allocation %")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📌 3D Asset Allocation")
    fig2 = go.Figure(data=[go.Scatter3d(
        x=edited_df["Allocation %"],
        y=list(range(1, 11)),
        z=[i*2 for i in range(10)],
        mode='markers+text',
        marker=dict(size=10),
        text=edited_df["Asset Class"]
    )])
    fig2.update_layout(scene=dict(
        xaxis_title="Allocation %",
        yaxis_title="Asset Index",
        zaxis_title="Risk Layer")
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("✅ Developed by **Himanshu** | Powered by 📊 Streamlit & Plotly")
