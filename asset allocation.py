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
# asset_allocation_safe.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import datetime

# Try Plotly (graceful)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", page_icon="📊")

# -------------------------
# Theme CSS (cyber / glossy)
# -------------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(180deg,#000814 0%, #00121b 40%, #001a26 100%); color: #e6fbff; font-family: Inter, Roboto, Arial; }
.card { background: rgba(255,255,255,0.03); border-radius:12px; padding:14px; border:1px solid rgba(0,255,230,0.04); }
.section { padding:10px 12px; border-radius:10px; }
h1 { color:#bff7ff; font-weight:800; }
.small { color:#cfefff; opacity:0.9; }
.sidebar .sidebar-content { background: linear-gradient(180deg,#001117,#001825); border-radius:10px; padding:12px; }
hr { border:none; border-top:1px solid rgba(255,255,255,0.04); margin:12px 0; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Typing heading (with optional sound)
# -------------------------
enable_sound = st.sidebar.checkbox("Enable soft click sound", value=False)
enable_typing = st.sidebar.checkbox("Enable typing animation", value=True)

# small JS for typing and sound (safe if feature off)
st.components.v1.html("""
<script>
window.playSoftClick = (on) => {
  if (!on) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = 'sine';
    o.frequency.value = 1000;
    g.gain.value = 0.0025;
    o.connect(g); g.connect(ctx.destination);
    o.start(); setTimeout(()=>{ o.stop(); ctx.close(); }, 35);
  } catch(e) { }
};
window.typeText = (id, text, speed, sound) => {
  const el = document.getElementById(id);
  if(!el) return;
  el.innerHTML = "";
  let i=0;
  const step = () => {
    if (i < text.length) {
      el.innerHTML += text.charAt(i);
      if (sound) window.playSoftClick(true);
      i++; setTimeout(step, speed);
    } else {
      el.style.borderRight = '2px solid rgba(0,255,230,0.25)';
      setInterval(()=>{ el.style.borderRight = el.style.borderRight ? '' : '2px solid rgba(0,255,230,0.25)'; }, 700);
    }
  };
  step();
};
</script>
""", height=0)

heading_text = "Asset Allocation"
if enable_typing:
    st.markdown("<div id='main_head' style='font-size:34px; font-weight:800; color:#bff7ff'></div>", unsafe_allow_html=True)
    st.components.v1.html(f"<script>window.typeText('main_head', {heading_text!r}, 20, {str(enable_sound).lower()});</script>", height=40)
else:
    st.markdown(f"## {heading_text}")

st.markdown("<div class='small'>Professional portfolio dashboard · charts adapt if Plotly missing</div>", unsafe_allow_html=True)
st.markdown("<hr/>", unsafe_allow_html=True)

# -------------------------
# Preset templates (user selected "A" earlier)
# -------------------------
TEMPLATES = {
    "Low Risk (45-65)": pd.DataFrame({
        "Asset Class": ["Government Bonds (G-sec)","AAA Corporate Bonds","PPF / NSC","Fixed Deposits","Short/Mid Debt Funds","REITs","Gold (SGB/ETF)","Target Maturity ETFs","Annuity/Pension","Infra Debt"],
        "Risk": ["Very Low","Low","Very Low","Very Low","Low","Low–Mod","Moderate","Low","Very Low","Low–Mod"],
        "Returns (%)": ["4–7","5–8","6–7","5–7","4–7","6–9","3–8","4–7","3–6","6–9"],
        "Horizon": ["3–10 yrs","2–7 yrs","5–15 yrs","1–5 yrs","1–5 yrs","5–10 yrs","3–10 yrs","3–10 yrs","Lifetime","5–10 yrs"],
        "Purpose": ["Income","Income","Retirement","Protection","Stability","Property income","Hedge","Predictable","Guaranteed","Diversify"],
        "Allocation (%)": [30,20,10,10,10,7,5,3,3,2]
    }),
    "Moderate Risk (30-45)": pd.DataFrame({
        "Asset Class":["Large-Cap Equity","Mid/Small-Cap Funds","Global Equity","Hybrid/Balanced","Corporate Bond Funds","REITs","Gold","Private Credit","Farmland","Digital Asset Basket"],
        "Risk":["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
        "Returns (%)":["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
        "Horizon":["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
        "Purpose":["Growth","Alpha","Diversify","Stability","Income","Property income","Hedge","Yield","Real assets","Asymmetric"],
        "Allocation (%)":[25,15,10,10,10,7,5,5,5,3]
    }),
    "High Risk (25-30)": pd.DataFrame({
        "Asset Class":["Domestic Equity","International Equity","Venture Capital","Private Equity","Crypto","Commodities","Real Assets","Hedge Funds","IP Royalties","Derivatives"],
        "Risk":["Very High"]*10,
        "Returns (%)":["10–15","8–15","20+","15+","Varies","Varies","6–12","Varies","Varies","Varies"],
        "Horizon":["10+ yrs"]*10,
        "Purpose":["Growth"]*10,
        "Allocation (%)":[50,15,10,7,5,5,3,3,1,1]
    })
}

# -------------------------
# Sidebar controls & import/export
# -------------------------
st.sidebar.header("Profile & Controls")
preset = st.sidebar.selectbox("Preset profile", list(TEMPLATES.keys()))
if st.sidebar.button("Load preset"):
    st.session_state['df'] = TEMPLATES[preset].copy()
    st.session_state['profile_name'] = preset
    st.success(f"Loaded preset: {preset}")

uploaded = st.sidebar.file_uploader("Upload CSV to replace workspace", type=["csv"])
if uploaded:
    try:
        updf = pd.read_csv(uploaded)
        required_cols = {"Asset Class","Allocation (%)","Returns (%)"}
        if not required_cols.issubset(set(updf.columns)):
            st.sidebar.error(f"CSV must contain: {', '.join(required_cols)}")
        else:
            st.session_state['df'] = updf.copy()
            st.session_state['df']["Allocation (%)"] = pd.to_numeric(st.session_state['df']["Allocation (%)"], errors='coerce').fillna(0.0)
            st.success("Uploaded CSV loaded")
    except Exception as e:
        st.sidebar.error(f"CSV read error: {e}")

st.sidebar.markdown("---")
enable_plotly3d = st.sidebar.checkbox("Enable Plotly interactive graphs (if available)", value=True)
enable_animations = st.sidebar.checkbox("Enable chart animations", value=True)

enable_excel = st.sidebar.checkbox("Enable Excel export", value=True)
enable_csv = st.sidebar.checkbox("Enable CSV export", value=True)

# init df in session
if 'df' not in st.session_state:
    st.session_state['df'] = TEMPLATES["Moderate Risk (30-45)"].copy()
    st.session_state['profile_name'] = "Moderate Risk (30-45)"

df = st.session_state['df']

# -------------------------
# Helper utility functions
# -------------------------
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
            if len(nums)>=2: return sum(nums)/len(nums)
        except: return None
    try: return float(s)
    except: return None

def weighted_avg_return(dframe):
    tmp = dframe.copy()
    tmp["_r"] = tmp["Returns (%)"].apply(parse_return)
    total = tmp["Allocation (%)"].sum()
    if total <= 0 or tmp["_r"].dropna().empty: return None
    return (tmp.loc[tmp["_r"].notna(), "_r"] * tmp.loc[tmp["_r"].notna(), "Allocation (%)"]).sum() / total

def to_excel_bytes(df_):
    # try multiple engines; if none available, raise
    buf = BytesIO()
    tried = False
    try:
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_.to_excel(writer, index=False, sheet_name="Portfolio")
        buf.seek(0); return buf.getvalue()
    except Exception:
        pass
    try:
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            df_.to_excel(writer, index=False, sheet_name="Portfolio")
        buf.seek(0); return buf.getvalue()
    except Exception as e:
        raise RuntimeError("No Excel writer available in environment: " + str(e))

# -------------------------
# Main UI: two columns (editor left, charts right)
# -------------------------
left, right = st.columns([1.2, 1.8])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Portfolio Editor**", unsafe_allow_html=True)

    # asset select (dropdown) instead of free-text
    asset_list = df["Asset Class"].tolist()
    chosen = st.selectbox("Select asset to edit", options=asset_list)

    idx = df.index[df["Asset Class"] == chosen].tolist()[0]
    row = df.loc[idx].copy()

    risk_options = ["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"]
    horizon_options = sorted(df["Horizon"].dropna().unique().tolist()) or ["1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"]
    purpose_options = sorted(df["Purpose"].dropna().unique().tolist()) or ["Growth","Income","Retirement","Tax Saving","Hedge"]

    new_risk = st.selectbox("Risk", options=risk_options, index=risk_options.index(row["Risk"]) if row["Risk"] in risk_options else 0)
    new_horizon = st.selectbox("Horizon", options=horizon_options, index=0)
    new_purpose = st.selectbox("Purpose", options=purpose_options, index=0)
    new_return = st.text_input("Returns (%)", value=str(row.get("Returns (%)","")))
    new_alloc = st.slider("Allocation (%)", 0.0, 100.0, float(row.get("Allocation (%)",0.0)), step=0.1)

    col_apply, col_del = st.columns([1,1])
    if col_apply.button("Apply changes"):
        st.session_state['df'].at[idx, "Risk"] = new_risk
        st.session_state['df'].at[idx, "Horizon"] = new_horizon
        st.session_state['df'].at[idx, "Purpose"] = new_purpose
        st.session_state['df'].at[idx, "Returns (%)"] = new_return
        st.session_state['df'].at[idx, "Allocation (%)"] = float(new_alloc)
        st.success(f"Updated {chosen}")
    if col_del.button("Remove asset"):
        st.session_state['df'] = st.session_state['df'].drop(index=idx).reset_index(drop=True)
        st.success(f"Removed {chosen}")

    st.markdown("---")
    st.markdown("**Add new asset**")
    new_name = st.text_input("Asset Class name")
    new_risk_in = st.selectbox("Risk (new)", options=risk_options, index=1, key="nrisk")
    new_horizon_in = st.selectbox("Horizon (new)", options=horizon_options, index=0, key="nhor")
    new_purpose_in = st.selectbox("Purpose (new)", options=purpose_options, index=0, key="npur")
    new_return_in = st.text_input("Returns (%) (new)", value="")
    new_alloc_in = st.number_input("Allocation (%) (new)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="nalloc")
    if st.button("Add asset"):
        if not new_name.strip():
            st.error("Asset name required.")
        else:
            row_new = {"Asset Class": new_name.strip(), "Risk": new_risk_in, "Returns (%)": new_return_in,
                       "Horizon": new_horizon_in, "Purpose": new_purpose_in, "Allocation (%)": float(new_alloc_in)}
            st.session_state['df'] = pd.concat([st.session_state['df'], pd.DataFrame([row_new])], ignore_index=True)
            st.success(f"Added {new_name.strip()}")

    st.markdown("---")
    if st.button("Normalize allocations to 100%"):
        total = st.session_state['df']["Allocation (%)"].sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state['df']["Allocation (%)"] = (st.session_state['df']["Allocation (%)"] / total * 100).round(2)
            st.success("Normalized allocations to 100%")

    # Downloads
    st.markdown("---")
    if enable_csv:
        csvb = st.session_state['df'].to_csv(index=False).encode()
        st.download_button("Download CSV", data=csvb, file_name=f"{st.session_state.get('profile_name','portfolio')}.csv", mime="text/csv")
    if enable_excel:
        try:
            excel_bytes = to_excel_bytes(st.session_state['df'])
            st.download_button("Download Excel (.xlsx)", data=excel_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error("Excel export unavailable in this environment. CSV is available. Error: " + str(e))

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("**Visual Dashboard**", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    total = st.session_state['df']["Allocation (%)"].sum()
    wavg = weighted_avg_return(st.session_state['df'])
    c1, c2 = st.columns([1,1])
    c1.metric("Total Allocation (%)", f"{total:.2f}")
    c2.metric("Weighted Avg Return (%)", f"{wavg:.2f}" if wavg is not None else "N/A")
    st.markdown("---")

    # Plotly branch
    if PLOTLY_OK and enable_plotly3d:
        # Donut / Pie
        fig = px.pie(st.session_state['df'], names="Asset Class", values="Allocation (%)", hole=0.45, title="Allocation (Donut)")
        fig.update_traces(textinfo='percent+label')
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, height=420)

        # 3D bar
        st.markdown("**3D Allocation Bar**")
        tmp = st.session_state['df'].reset_index().rename(columns={"index":"idx"})
        x = tmp.index.tolist()
        z = tmp["Allocation (%)"].tolist()
        names = tmp["Asset Class"].tolist()
        fig3d = go.Figure(data=[go.Bar3d(
            x=x, y=[0]*len(x), z=[0]*len(x), dx=0.6, dy=0.6, dz=z, text=names,
            hovertemplate="%{text}<br>Allocation: %{dz}%<extra></extra>"
        )])
        fig3d.update_layout(scene=dict(
            xaxis=dict(title="Asset (index)", tickmode='array', tickvals=x, ticktext=names, tickangle=45),
            yaxis=dict(title="Group"),
            zaxis=dict(title="Allocation (%)")
        ), margin=dict(l=0,r=0,b=0,t=30), height=520)
        st.plotly_chart(fig3d, use_container_width=True, height=520)

        # Line and Area (simulated trend)
        st.markdown("**Allocation Trend (simulated)**")
        months = pd.date_range(end=pd.Timestamp.today(), periods=6, freq='M').strftime("%b %Y").tolist()
        trend = pd.DataFrame({m: st.session_state['df']["Allocation (%)"].values for m in months})
        trend["Asset Class"] = st.session_state['df']["Asset Class"].values
        trend = trend.set_index("Asset Class").T
        fig_line = px.line(trend, x=trend.index, y=trend.columns, labels={'value':'Allocation (%)','variable':'Asset'})
        fig_line.update_layout(title="Allocation trend (simulated)")
        st.plotly_chart(fig_line, use_container_width=True, height=360)
        fig_area = px.area(trend, x=trend.index, y=trend.columns)
        fig_area.update_layout(title="Area view (simulated)")
        st.plotly_chart(fig_area, use_container_width=True, height=360)

    else:
        # Fallback visualizations (SVG donut + Streamlit bar)
        st.warning("Plotly not available — using fallback charts (SVG + Streamlit). Install plotly for interactive charts.")
        # SVG donut
        def svg_donut(labels, values, size=360, hole_ratio=0.6):
            total = sum(values) or 1
            cx = cy = size/2
            r = size*0.4
            inner_r = r*hole_ratio
            start = 0
            paths = []
            colors = ["#00f5d4","#00b4d8","#0077b6","#00b4ff","#00f6ff","#00c2b3","#00e6a8","#00a6ff","#00ffd6","#00ffaa"]
            for i, v in enumerate(values):
                angle = 360.0 * v / total
                end = start + angle
                sa = np.deg2rad(start); ea = np.deg2rad(end)
                x1 = cx + r * np.cos(sa); y1 = cy + r * np.sin(sa)
                x2 = cx + r * np.cos(ea); y2 = cy + r * np.sin(ea)
                large = 1 if angle > 180 else 0
                path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large} 1 {x2} {y2} Z"
                paths.append((path, colors[i % len(colors)], labels[i], f"{(v/total*100):.1f}%"))
                start = end
            svg = f"<svg width='{size}' height='{size}' viewBox='0 0 {size} {size}' xmlns='http://www.w3.org/2000/svg'>"
            for p,c,l,pt in paths:
                svg += f"<path d=\"{p}\" fill=\"{c}\" stroke='#00121b' stroke-width='0.5' />"
            svg += f"<circle cx='{cx}' cy='{cy}' r='{inner_r}' fill='#00121b' />"
            svg += "</svg>"
            legend = "<div style='margin-top:8px'>"
            for _,c,l,pt in paths:
                legend += f"<div style='display:flex;gap:8px;align-items:center'><div style='width:12px;height:12px;background:{c}'></div><div style='color:#dffaff'>{l} - {pt}</div></div>"
            legend += "</div>"
            return svg, legend
        labels = st.session_state['df']["Asset Class"].tolist()
        values = st.session_state['df']["Allocation (%)"].fillna(0).tolist()
        svg, legend = svg_donut(labels, values, size=360, hole_ratio=0.58)
        st.markdown(svg, unsafe_allow_html=True)
        st.markdown(legend, unsafe_allow_html=True)
        st.markdown("Allocation (bar chart fallback)")
        st.bar_chart(st.session_state['df'].set_index("Asset Class")["Allocation (%)"])
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Calculators & Rebalancer area (separate section below)
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("**Calculators & Quick Rebalancer**", unsafe_allow_html=True)

# Lumpsum & SIP calculators
st.markdown("### Lumpsum projection")
initial = st.number_input("Initial amount (₹)", min_value=100.0, value=100000.0, step=1000.0)
yrs = st.selectbox("Years", [1,3,5,7,10,15,20], index=2)
default_rate = weighted_avg_return(st.session_state['df']) or 7.0
rate = st.number_input("Expected annual return (%)", min_value=0.0, value=float(default_rate))
fv = initial * ((1 + rate/100.0) ** yrs)
st.metric(f"Future value after {yrs} yrs", f"₹{fv:,.0f}")

st.markdown("---")
st.markdown("### SIP projection (monthly)")
sip = st.number_input("Monthly SIP (₹)", min_value=100.0, value=5000.0, step=100.0)
sip_years = st.selectbox("SIP horizon (years)", [1,3,5,7,10,15,20], index=2, key="sip_h")
sip_rate = st.number_input("Expected annual return (%) for SIP", min_value=0.0, value=float(default_rate), key="sip_r")
months = sip_years * 12
r = sip_rate / 100.0 / 12.0
if r == 0:
    fv_sip = sip * months
else:
    fv_sip = sip * (( (1 + r) ** months - 1) / r) * (1 + r)
st.metric(f"SIP projected value in {sip_years} yrs", f"₹{fv_sip:,.0f}")

st.markdown("---")
# Rebalancer
st.markdown("### Quick Rebalancer")
target = st.selectbox("Target preset to rebalance to", list(TEMPLATES.keys()))
if st.button("Suggest rebalance"):
    target_df = TEMPLATES[target].copy()
    merged = pd.merge(st.session_state['df'][["Asset Class","Allocation (%)"]], target_df[["Asset Class","Allocation (%)"]], on="Asset Class", how="outer", suffixes=("_cur","_tgt")).fillna(0)
    merged["Delta"] = merged["Allocation (%)_tgt"] - merged["Allocation (%)_cur"]
    sells = merged[merged["Delta"] < 0]
    buys = merged[merged["Delta"] > 0]
    st.markdown("**Sell suggestions**")
    if sells.empty:
        st.write("No sells necessary.")
    else:
        for _, r in sells.iterrows():
            st.write(f"- {r['Asset Class']}: reduce by {abs(r['Delta']):.2f}%")
    st.markdown("**Buy suggestions**")
    if buys.empty:
        st.write("No buys necessary.")
    else:
        for _, r in buys.iterrows():
            st.write(f"- {r['Asset Class']}: increase by {r['Delta']:.2f}%")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Footer: HTML report + exporter fallback
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("**Export / Report**", unsafe_allow_html=True)

html = """<html><body><h3>Portfolio Report</h3></body></html>"""
# printable HTML (client-side)
report_html = "\n".join(["<tr><td>{}</td><td>{}</td></tr>".format(r["Asset Class"], r["Allocation (%)"]) for _, r in st.session_state['df'].iterrows()])
full_html = f"<html><body><h2>Asset Allocation Report</h2><table border='1'><thead><tr><th>Asset</th><th>Allocation (%)</th></tr></thead><tbody>{report_html}</tbody></table></body></html>"
b64 = base64.b64encode(full_html.encode()).decode()
st.markdown(f'<a href="data:text/html;base64,{b64}" download="portfolio_report.html">Download printable HTML report (open & Print→Save as PDF)</a>', unsafe_allow_html=True)

# CSV always available
if enable_csv:
    csv_bytes = st.session_state['df'].to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.csv", mime="text/csv")

# Excel try/catch
if enable_excel:
    try:
        excel_bytes_val = to_excel_bytes(st.session_state['df'])
        st.download_button("Download Excel (.xlsx)", data=excel_bytes_val, file_name=f"{st.session_state.get('profile_name','portfolio')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        st.error("Excel export unavailable in this environment. Install openpyxl or xlsxwriter. Error: " + str(e))

st.markdown("</div>", unsafe_allow_html=True)
st.caption("This app uses Plotly if available; otherwise falls back to SVG and Streamlit charts so it never crashes from missing plotting libraries.")
