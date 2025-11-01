import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import base64
from io import BytesIO

# -----------------------------------------------------------
# ✅ Page Configuration - Premium Blue Gloss Theme UI
# -----------------------------------------------------------
st.set_page_config(
    page_title="Asset Allocation",
    layout="wide"
)

# Custom CSS Styling
st.markdown("""
<style>
body {
    background-color: #0A0F24;
    color: white;
}
.sidebar .sidebar-content {
    background-color: #0D132F;
}
div.stButton > button {
    background-color: #0052cc;
    color: white;
    font-size: 18px;
    border-radius: 8px;
}
div.stButton > button:hover {
    background-color: #0073ff;
}
h1, h2, h3 {
    color: #66B2FF;
}
</style>
""", unsafe_allow_html=True)

# Heading with typing effect
typing_text = "Asset Allocation"
placeholder = st.empty()
for i in range(len(typing_text) + 1):
    placeholder.markdown(f"## {typing_text[:i]}|")
    st.sleep(0.05)

st.markdown("### Build Diversified & Smart Investment Strategy")

# -----------------------------------------------------------
# ✅ Sidebar Controls
# -----------------------------------------------------------
st.sidebar.header("🧩 Select Profile & Preferences")

risk_profile = st.sidebar.selectbox(
    "Select Risk Profile",
    ["Low Risk", "Moderate Risk", "High Risk"]
)

investment_amount = st.sidebar.number_input(
    "Total Investment Amount (₹)",
    min_value=1000, value=100000, step=5000
)

years = st.sidebar.slider("Investment Duration (Years)", 1, 30, 5)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Visualization Options")

chart_type = st.sidebar.selectbox(
    "Choose Chart Type",
    ["Pie Chart", "3D Bar Chart"]
)

st.sidebar.markdown("---")
st.sidebar.info("✅ All features enabled")

# -----------------------------------------------------------
# ✅ Default Model Portfolio Based on Risk Profile
# -----------------------------------------------------------
model_allocations = {
    "Low Risk": {
        "Equity": 20, "Bonds": 40, "Fixed Deposits": 25,
        "Gold": 10, "Real Estate": 5
    },
    "Moderate Risk": {
        "Equity": 40, "Bonds": 25, "Fixed Deposits": 10,
        "Gold": 10, "Real Estate": 15
    },
    "High Risk": {
        "Equity": 60, "Bonds": 10, "Fixed Deposits": 5,
        "Gold": 10, "Crypto": 15
    }
}

df = pd.DataFrame({
    "Asset Class": list(model_allocations[risk_profile].keys()),
    "Allocation %": list(model_allocations[risk_profile].values())
})

# -----------------------------------------------------------
# ✅ Investment Calculator
# -----------------------------------------------------------
df["Investment Amount (₹)"] = (df["Allocation %"] / 100) * investment_amount

st.subheader("📌 Recommended Asset Allocation")
st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------
# ✅ Plotly Visualizations
# -----------------------------------------------------------
st.subheader("📊 Portfolio Visual Charts")

if chart_type == "Pie Chart":
    fig = go.Figure(data=[go.Pie(
        labels=df["Asset Class"],
        values=df["Allocation %"],
        hole=0.3
    )])
    fig.update_layout(
        title="Portfolio Composition",
        title_font_color="white",
        paper_bgcolor="#0A0F24",
        font_color="white"
    )
else:  # 3D Bar Chart
    fig = go.Figure(data=[go.Bar3d(
        x=df["Asset Class"],
        y=["Allocation"] * len(df),
        z=[0] * len(df),
        dx=[0.5] * len(df),
        dy=[0.5] * len(df),
        dz=df["Allocation %"]
    )])
    fig.update_layout(
        scene=dict(
            xaxis_title="Asset Class",
            zaxis_title="Allocation %",
            bgcolor="#0A0F24",
        ),
        title="3D Allocation Chart",
        title_font_color="white",
        paper_bgcolor="#0A0F24",
        font_color="white"
    )

st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# ✅ Download Excel Button
# -----------------------------------------------------------
def to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Asset Allocation")
    return buffer.getvalue()

excel_file = to_excel(df)
b64 = base64.b64encode(excel_file).decode()

st.markdown(f"""
📥 **Download Allocation Data:**
<a href="data:application/octet-stream;base64,{b64}" download="asset_allocation.xlsx">
🎯 Download Excel
</a>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# ✅ Footer
# -----------------------------------------------------------
st.markdown("---")
st.caption("⚡ Professional Investment Dashboard • Powered by Streamlit & Plotly")

