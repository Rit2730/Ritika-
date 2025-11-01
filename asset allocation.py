import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ✅ Streamlit Page Config
st.set_page_config(
    page_title="Asset Allocation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ✅ Custom Dark Glossy CSS Theme
st.markdown("""
    <style>
    body {background: linear-gradient(135deg, #001b33, #002b55);}
    .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #ffffff !important;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #61dafb !important;
        text-shadow: 0px 0px 8px #000;
        font-family: 'Helvetica';
    }
    .typing{
        overflow: hidden;
        border-right: .15em solid #61dafb;
        white-space: nowrap;
        animation: typing 3.5s steps(40, end), blink .65s infinite;
        font-size: 42px;
    }
    @keyframes typing { from { width: 0 } to { width: 100% } }
    @keyframes blink { 50% { border-color: transparent } }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='typing'>Asset Allocation</h1>", unsafe_allow_html=True)

# ✅ Initialize session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Asset Class": ["Government Bonds", "Tax-Free Bonds", "POMIS", "SCSS"],
        "Risk": ["Low", "Low", "Low", "Very Low"],
        "Reward (%)": [6.5, 6.2, 7.4, 8.2],
        "Time (Yrs)": [5, 10, 5, 5],
        "Allocation (%)": [25, 25, 25, 25],
        "Purpose": ["Safety", "Tax-Free", "Monthly Income", "Senior Safety"]
    })

sidebar = st.sidebar
profile = sidebar.radio(
    "Select Risk Profile",
    ["Low Risk", "Moderate Risk", "High Risk"],
    key="profile_select"
)

investment_amount = sidebar.number_input(
    "Enter Investment Amount (₹)",
    min_value=1000,
    step=500,
    key="inv_input"
)

# ✅ Table Editable
st.subheader("Portfolio Table")
st.session_state.df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    key="table_editor"
)

# ✅ Pie Chart
st.subheader("Asset Allocation Distribution - Pie Chart")
fig_pie = px.pie(
    st.session_state.df,
    names="Asset Class",
    values="Allocation (%)",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.Blues
)
st.plotly_chart(fig_pie, use_container_width=True)

# ✅ 3D Bar Chart (Advanced)
st.subheader("Risk vs Reward vs Allocation - 3D Chart")
fig3d = go.Figure(data=[go.Bar3d(
    x=st.session_state.df["Risk"],
    y=st.session_state.df["Asset Class"],
    z=st.session_state.df["Reward (%)"],
    opacity=0.8
)])
fig3d.update_layout(
    width=900,
    height=500,
    scene=dict(
        xaxis_title="Risk",
        yaxis_title="Asset Class",
        zaxis_title="Reward (%)"
    ),
    template="plotly_dark"
)
st.plotly_chart(fig3d)

# ✅ Investment Growth Calculator
st.subheader("Investment Growth Calculator")
rate = sidebar.number_input("Expected Annual Return (%)", min_value=1, max_value=20, value=10)
years = sidebar.slider("Investment Duration (Years)", 1, 30)
future_value = investment_amount * ((1 + rate/100) ** years)
st.success(f"Future Value of ₹{investment_amount:,} in {years} years: **₹{future_value:,.2f}**")

# ✅ Add New Asset Class
st.subheader("Add New Asset Class")
with st.form("add_asset"):
    asset = st.text_input("Asset Name")
    risk = st.selectbox("Risk Level", ["Very Low", "Low", "Moderate", "High", "Very High"])
    reward = st.number_input("Expected Return (%)", 1.0, 25.0)
    time = st.number_input("Time Duration (Years)", 1, 30)
    alloc = st.number_input("Allocation (%)", 0, 100)
    purpose = st.text_input("Purpose")
    submit = st.form_submit_button("Add Asset")
    if submit:
        st.session_state.df.loc[len(st.session_state.df)] = [asset, risk, reward, time, alloc, purpose]
        st.rerun()

# ✅ Downloads with Unique Keys
csv = st.session_state.df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", data=csv,
                   file_name="Portfolio.csv",
                   mime="text/csv", key="csv_dl1")

excel_buffer = pd.ExcelWriter("portfolio.xlsx", engine="openpyxl")
st.session_state.df.to_excel(excel_buffer, index=False)
excel_buffer.close()
st.download_button(
    "Download Excel",
    data=open("portfolio.xlsx", "rb").read(),
    file_name="Portfolio.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key="excel_dl1"
)

st.caption("Created with ❤️ using Streamlit + Plotly")
