# asset_allocation_safe_plotly.py
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import base64
import datetime

# --- Try import Plotly gracefully ---
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    PLOTLY_OK = False

st.set_page_config(page_title="Asset Allocation", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# CSS - cyber theme (single)
# -------------------------
st.markdown(
    """
    <style>
      .stApp { background: linear-gradient(180deg,#000814 0%, #00121b 50%, #001a26 100%); color: #e6fbff; font-family: Inter, Roboto, Arial; }
      .card { background: rgba(255,255,255,0.03); border-radius:12px; padding:14px; border:1px solid rgba(0,255,230,0.04); }
      h1 { color:#bff7ff; font-weight:800; margin:6px 0 2px 0; }
      .muted { color:#cfefff; opacity:0.9; }
      .sidebar .sidebar-content { background: linear-gradient(180deg,#001117,#001825); border-radius:10px; padding:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Typing heading (single unique id)
# -------------------------
st.components.v1.html(
    """
    <div id="asset_alloc_heading" style="font-size:34px;font-weight:800;color:#bff7ff;"></div>
    <script>
      const txt = "Asset Allocation";
      const el = document.getElementById("asset_alloc_heading");
      let i=0;
      function typeNext() {
        if (i < txt.length) { el.innerText += txt.charAt(i); i++; setTimeout(typeNext, 20); }
        else { el.style.borderRight = "2px solid rgba(0,255,230,0.12)"; }
      }
      typeNext();
    </script>
    """,
    height=48
)
st.markdown("<div class='muted'>Cyber-tech theme — safe Plotly fallback, calculators & exports</div>", unsafe_allow_html=True)
st.markdown("---", unsafe_allow_html=True)

# -------------------------
# Preset templates (user chose preset A earlier)
# -------------------------
TEMPLATES = {
    "Low Risk (45-65)": pd.DataFrame({
        "Asset Class": ["Government Bonds (G-sec)", "AAA Corporate Bonds", "PPF / NSC", "Fixed Deposits",
                        "Short/Mid-Term Debt Funds", "REITs", "Gold (SGB/ETF)", "Target Maturity ETFs",
                        "Annuity / Pension", "Infra Debt / InvIT Debt"],
        "Risk": ["Very Low","Low","Very Low","Very Low","Low","Low–Mod","Moderate","Low","Very Low","Low–Mod"],
        "Returns (%)":["4–7","5–8","6–7","5–7","4–7","6–9","3–8","4–7","3–6","6–9"],
        "Horizon": ["3–10 yrs","2–7 yrs","5–15 yrs","1–5 yrs","1–5 yrs","5–10 yrs","3–10 yrs","3–10 yrs","Lifetime","5–10 yrs"],
        "Purpose": ["Income","Income","Retirement","Capital protection","Stable returns","Property income","Inflation hedge","Predictable returns","Guaranteed income","Diversify"],
        "Allocation (%)":[30,20,10,10,10,7,5,3,3,2]
    }),
    "Moderate Risk (30-45)": pd.DataFrame({
        "Asset Class": ["Large-Cap Equity Funds","Mid/Small-Cap Funds","Global Equity ETFs","Hybrid/Balanced Funds","Corporate Bond Funds","REITs","Gold","Private Credit","Farmland","Digital Asset Basket"],
        "Risk": ["High","High","High","Moderate","Moderate","Moderate","Moderate","Mod–High","Moderate","High"],
        "Returns (%)":["8–12","10–15","7–12","7–10","6–9","6–10","3–8","8–12","4–8","Varies"],
        "Horizon":["7–10 yrs","7–12 yrs","7–10 yrs","5–8 yrs","3–7 yrs","5–10 yrs","3–7 yrs","3–7 yrs","5–15 yrs","5–10 yrs"],
        "Purpose":["Growth","Alpha","Diversify","Smoother volatility","Income stability","Property income","Hedge","Enhanced yield","Real assets","Asymmetric payoff"],
        "Allocation (%)":[25,15,10,10,10,7,5,5,5,3]
    }),
    "High Risk (25-30)": pd.DataFrame({
        "Asset Class": ["Domestic Equity","International Equities","Venture Capital","Private Equity","Crypto","Commodities","Real Assets","Hedge Funds","IP Royalties","Derivatives"],
        "Risk": ["Very High"]*10,
        "Returns (%)":["10–15","8–15","20+","15+","Highly variable","Varies","6–12","Varies","Variable","Variable"],
        "Horizon":["10–20 yrs"]*10,
        "Purpose":["Growth"]*10,
        "Allocation (%)":[50,15,10,7,5,5,3,3,1,1]
    })
}

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Controls")
preset = st.sidebar.selectbox("Load preset", list(TEMPLATES.keys()))
if st.sidebar.button("Load preset to workspace", key="load_preset"):
    st.session_state["df"] = TEMPLATES[preset].copy()
    st.session_state["profile_name"] = preset
    st.success(f"Loaded preset: {preset}")

uploaded = st.sidebar.file_uploader("Upload CSV to workspace", type=["csv"])
if uploaded is not None:
    try:
        uploaded_df = pd.read_csv(uploaded)
        req = {"Asset Class","Allocation (%)","Returns (%)"}
        if not req.issubset(set(uploaded_df.columns)):
            st.sidebar.error(f"CSV must contain columns: {', '.join(req)}")
        else:
            st.session_state["df"] = uploaded_df.copy()
            st.session_state["df"]["Allocation (%)"] = pd.to_numeric(st.session_state["df"]["Allocation (%)"], errors="coerce").fillna(0.0)
            st.success("CSV uploaded into workspace")
    except Exception as e:
        st.sidebar.error(f"CSV read error: {e}")

enable_plotly = st.sidebar.checkbox("Prefer Plotly visuals (if available)", value=True)
enable_excel_export = st.sidebar.checkbox("Enable Excel export", value=True)
enable_csv_export = st.sidebar.checkbox("Enable CSV export", value=True)

# initialize workspace df
if "df" not in st.session_state:
    st.session_state["df"] = TEMPLATES["Moderate Risk (30-45)"].copy()
    st.session_state["df"]["Allocation (%)"] = pd.to_numeric(st.session_state["df"]["Allocation (%)"], errors="coerce").fillna(0.0)
    st.session_state["profile_name"] = "Moderate Risk (30-45)"

df = st.session_state["df"]

# -------------------------
# Helpers
# -------------------------
def parse_return(v):
    if pd.isna(v): return None
    if isinstance(v,(int,float)): return float(v)
    s = str(v).replace("%","").replace("–","-").strip()
    if "+" in s:
        s = s.replace("+","")
        try: return float(s)
        except: return None
    if "-" in s:
        parts = s.split("-")
        try:
            nums = [float(x) for x in parts if x!=""]
            if len(nums)>=2: return sum(nums)/len(nums)
        except: return None
    try: return float(s)
    except: return None

def weighted_avg_return(df_):
    tmp = df_.copy()
    tmp["_p"] = tmp["Returns (%)"].apply(parse_return)
    total = tmp["Allocation (%)"].sum()
    if total<=0 or tmp["_p"].dropna().empty:
        return None
    return (tmp.loc[tmp["_p"].notna(), "_p"] * tmp.loc[tmp["_p"].notna(), "Allocation (%)"]).sum() / total

def to_excel_bytes(df_):
    buf = BytesIO()
    # try openpyxl first, then xlsxwriter
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
        raise RuntimeError("Excel writer not available: " + str(e))

# -------------------------
# Left: Editor / Add / Normalize / Downloads
# -------------------------
left, right = st.columns([1.2, 1.8])

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Portfolio Editor", unsafe_allow_html=True)

    # Inline editor when available, otherwise provide fallback form
    try:
        if hasattr(st, "data_editor"):
            edited = st.data_editor(df, num_rows="dynamic", key="editor_data")
            if st.button("Apply table edits", key="apply_table"):
                edited["Allocation (%)"] = pd.to_numeric(edited["Allocation (%)"], errors="coerce").fillna(0.0)
                st.session_state["df"] = edited.copy()
                st.success("Applied table edits")
        else:
            raise AttributeError
    except Exception:
        st.warning("Inline editor not available — using controlled editor")
        asset = st.selectbox("Select asset", df["Asset Class"].tolist(), key="asset_select")
        idx = df.index[df["Asset Class"] == asset].tolist()[0]
        row = df.loc[idx]
        risk_opt = ["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"]
        new_risk = st.selectbox("Risk", options=risk_opt, index=risk_opt.index(row["Risk"]) if row["Risk"] in risk_opt else 0)
        horizons = sorted(df["Horizon"].dropna().unique().tolist()) or ["1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"]
        new_hor = st.selectbox("Horizon", options=horizons, index=0)
        purposes = sorted(df["Purpose"].dropna().unique().tolist()) or ["Growth","Income","Retirement","Tax Saving"]
        new_purp = st.selectbox("Purpose", options=purposes, index=0)
        new_ret = st.text_input("Returns (%)", value=str(row.get("Returns (%)","")))
        new_alloc = st.slider("Allocation (%)", 0.0, 100.0, float(row.get("Allocation (%)",0.0)), step=0.1)
        if st.button("Apply changes to selected asset", key="apply_controlled"):
            st.session_state["df"].at[idx, "Risk"] = new_risk
            st.session_state["df"].at[idx, "Horizon"] = new_hor
            st.session_state["df"].at[idx, "Purpose"] = new_purp
            st.session_state["df"].at[idx, "Returns (%)"] = new_ret
            st.session_state["df"].at[idx, "Allocation (%)"] = float(new_alloc)
            st.success(f"Updated {asset}")

    st.markdown("---", unsafe_allow_html=True)
    st.markdown("### Add New Asset", unsafe_allow_html=True)
    name = st.text_input("Asset Class name", key="add_name")
    rsk = st.selectbox("Risk (new)", options=["Very Low","Low","Low–Mod","Moderate","Mod–High","High","Very High"], key="add_risk")
    hor = st.selectbox("Horizon (new)", options=["1-3 yrs","3-5 yrs","5-10 yrs","10+ yrs"], key="add_hor")
    purp = st.selectbox("Purpose (new)", options=["Growth","Income","Retirement","Tax Saving","Hedge"], key="add_purp")
    ret_new = st.text_input("Returns (%) (new)", key="add_ret")
    alloc_new = st.number_input("Allocation (%) (new)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="add_alloc")
    if st.button("Add asset to portfolio", key="add_asset"):
        if not name.strip():
            st.error("Asset name is required.")
        else:
            newrow = {"Asset Class": name.strip(), "Risk": rsk, "Returns (%)": ret_new, "Horizon": hor, "Purpose": purp, "Allocation (%)": float(alloc_new)}
            st.session_state["df"] = pd.concat([st.session_state["df"], pd.DataFrame([newrow])], ignore_index=True)
            st.success(f"Added {name.strip()}")

    st.markdown("---", unsafe_allow_html=True)
    if st.button("Normalize allocations to 100%", key="normalize"):
        total = st.session_state["df"]["Allocation (%)"].sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state["df"]["Allocation (%)"] = (st.session_state["df"]["Allocation (%)"] / total * 100.0).round(2)
            st.success("Normalized allocations to 100%")

    st.markdown("---", unsafe_allow_html=True)
    # Downloads (unique keys)
    if enable_csv_export:
        csv_bytes = st.session_state["df"].to_csv(index=False).encode()
        st.download_button("Download CSV", data=csv_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.csv", mime="text/csv", key="download_csv_unique")
    if enable_excel_export:
        try:
            excel_bytes = to_excel_bytes(st.session_state["df"])
            st.download_button("Download Excel (.xlsx)", data=excel_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="download_excel_unique")
        except Exception as e:
            st.error("Excel export not available in this environment. Install openpyxl/xlsxwriter. Error: " + str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Right: Charts & Metrics
# -------------------------
with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Visual Dashboard", unsafe_allow_html=True)

    total_alloc = st.session_state["df"]["Allocation (%)"].sum()
    wavg = weighted_avg_return(st.session_state["df"])
    col1, col2 = st.columns(2)
    col1.metric("Total Allocation (%)", f"{total_alloc:.2f}")
    col2.metric("Weighted Avg Return (%)", f"{wavg:.2f}" if wavg is not None else "N/A")

    st.markdown("---", unsafe_allow_html=True)

    # Use Plotly when available & enabled, otherwise fallback
    if PLOTLY_OK and enable_plotly:
        # Donut (Plotly)
        fig = px.pie(st.session_state["df"], names="Asset Class", values="Allocation (%)", hole=0.45, title="Allocation (Donut)")
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True, height=420)

        # 3D bar
        st.markdown("#### 3D Allocation Bar")
        tmp = st.session_state["df"].reset_index().rename(columns={"index":"idx"})
        x = tmp.index.tolist()
        z = tmp["Allocation (%)"].tolist()
        names = tmp["Asset Class"].tolist()
        fig3d = go.Figure(data=[go.Bar3d(
            x=x, y=[0]*len(x), z=[0]*len(x), dx=0.6, dy=0.6, dz=z, text=names,
            hovertemplate="%{text}<br>Allocation: %{dz}%<extra></extra>"
        )])
        fig3d.update_layout(scene=dict(
            xaxis=dict(title="Asset index", tickmode='array', tickvals=x, ticktext=names, tickangle=45),
            yaxis=dict(title="Group"), zaxis=dict(title="Allocation (%)")
        ), margin=dict(l=0,r=0,b=0,t=30), height=520)
        st.plotly_chart(fig3d, use_container_width=True, height=520)

        # Line + Area (simulated)
        st.markdown("#### Allocation Trend (simulated)")
        months = pd.date_range(end=pd.Timestamp.today(), periods=6, freq='M').strftime("%b %Y").tolist()
        trend = pd.DataFrame({m: st.session_state["df"]["Allocation (%)"].values for m in months})
        trend["Asset Class"] = st.session_state["df"]["Asset Class"].values
        trend = trend.set_index("Asset Class").T
        fig_line = px.line(trend, x=trend.index, y=trend.columns, labels={'value':'Allocation (%)','variable':'Asset'})
        fig_line.update_layout(title="Allocation trend (simulated)")
        st.plotly_chart(fig_line, use_container_width=True, height=360)
        fig_area = px.area(trend, x=trend.index, y=trend.columns)
        fig_area.update_layout(title="Area view (simulated)")
        st.plotly_chart(fig_area, use_container_width=True, height=360)

    else:
        st.warning("Plotly not available or disabled — showing fallback visuals.")
        # simple pie fallback (SVG)
        def simple_svg_pie(labels, values, size=360, hole=0.5):
            total = float(sum(values)) if sum(values) else 1.0
            cx = cy = size/2
            r = size*0.4
            inner = r*hole
            start = 0
            parts = []
            cols = ["#00f5d4","#00b4d8","#0077b6","#00b4ff","#00f6ff","#00c2b3","#00e6a8","#00a6ff","#00ffd6","#00ffaa"]
            for i, v in enumerate(values):
                angle = 360.0 * v / total
                end = start + angle
                sa = np.deg2rad(start); ea = np.deg2rad(end)
                x1 = cx + r*np.cos(sa); y1 = cy + r*np.sin(sa)
                x2 = cx + r*np.cos(ea); y2 = cy + r*np.sin(ea)
                large = 1 if angle > 180 else 0
                d = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large} 1 {x2} {y2} Z"
                parts.append((d, cols[i%len(cols)], labels[i], f"{(v/total*100):.1f}%"))
                start = end
            svg = f"<svg width='{size}' height='{size}' viewBox='0 0 {size} {size}' xmlns='http://www.w3.org/2000/svg'>"
            for p,c,lab,pct in parts:
                svg += f"<path d=\"{p}\" fill=\"{c}\" stroke='#00121b' stroke-width='0.5'/>"
            svg += f"<circle cx='{cx}' cy='{cy}' r='{inner}' fill='#00121b'/>"
            svg += "</svg>"
            legend = "<div>"
            for _,c,lab,pct in parts:
                legend += f"<div style='display:flex;gap:8px;align-items:center'><div style='width:12px;height:12px;background:"+c+"'></div><div style='color:#dffaff'>" + lab + " - " + pct + "</div></div>"
            legend += "</div>"
            return svg, legend
        labels = st.session_state["df"]["Asset Class"].tolist()
        vals = st.session_state["df"]["Allocation (%)"].fillna(0).tolist()
        svg, legend = simple_svg_pie(labels, vals)
        st.markdown(svg, unsafe_allow_html=True)
        st.markdown(legend, unsafe_allow_html=True)
        st.markdown("Allocation (bar chart fallback)")
        st.bar_chart(st.session_state["df"].set_index("Asset Class")["Allocation (%)"])
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Calculators & Rebalancer (bottom)
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### Calculators & Quick Rebalancer", unsafe_allow_html=True)

# Lumpsum
initial = st.number_input("Initial lumpsum (₹)", min_value=100.0, value=100000.0)
proj_years = st.selectbox("Projection years", [1,3,5,7,10,15,20], index=2)
default_r = weighted_avg_return(st.session_state["df"]) or 7.0
exp_rate = st.number_input("Expected annual return (%)", value=float(default_r))
fv = initial * ((1 + exp_rate/100.0) ** proj_years)
st.metric(f"Future value ({proj_years} yrs)", f"₹{fv:,.0f}")

st.markdown("---", unsafe_allow_html=True)
# SIP
sip = st.number_input("Monthly SIP amount (₹)", min_value=100.0, value=5000.0, key="sip_amt")
sip_years = st.selectbox("SIP horizon (years)", [1,3,5,7,10,15,20], index=2, key="sip_h")
r_month = exp_rate / 100.0 / 12.0
months = sip_years * 12
if r_month == 0:
    fv_sip = sip * months
else:
    fv_sip = sip * (( (1 + r_month) ** months - 1) / r_month) * (1 + r_month)
st.metric(f"SIP projected value ({sip_years} yrs)", f"₹{fv_sip:,.0f}")

st.markdown("---", unsafe_allow_html=True)
# Rebalancer
st.markdown("Quick Rebalance Suggestion", unsafe_allow_html=True)
target_preset = st.selectbox("Target preset", list(TEMPLATES.keys()), key="target_preset")
if st.button("Get Rebalance Steps", key="rebalance_btn"):
    target_df = TEMPLATES[target_preset].copy()
    merged = pd.merge(st.session_state["df"][["Asset Class","Allocation (%)"]], target_df[["Asset Class","Allocation (%)"]], on="Asset Class", how="outer", suffixes=("_cur","_tgt")).fillna(0)
    merged["Delta"] = merged["Allocation (%)_tgt"] - merged["Allocation (%)_cur"]
    sells = merged[merged["Delta"]<0]
    buys = merged[merged["Delta"]>0]
    st.markdown("#### Sell (reduce)")
    if sells.empty:
        st.write("No sell suggestions")
    else:
        for _,r in sells.iterrows():
            st.write(f"- {r['Asset Class']}: reduce by {abs(r['Delta']):.2f}%")
    st.markdown("#### Buy (increase)")
    if buys.empty:
        st.write("No buy suggestions")
    else:
        for _,r in buys.iterrows():
            st.write(f"- {r['Asset Class']}: increase by {r['Delta']:.2f}%")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Export section (bottom) — ensure unique keys
# -------------------------
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### Export & Report", unsafe_allow_html=True)

# HTML report (downloadable via data URI)
report_html = "<html><body><h2>Asset Allocation Report</h2><table border='1'><thead><tr><th>Asset</th><th>Allocation (%)</th></tr></thead><tbody>"
for _, r in st.session_state["df"].iterrows():
    report_html += f"<tr><td>{r['Asset Class']}</td><td style='text-align:right'>{r['Allocation (%)']}</td></tr>"
report_html += "</tbody></table></body></html>"
b64 = base64.b64encode(report_html.encode()).decode()
st.markdown(f'<a href="data:text/html;base64,{b64}" download="portfolio_report.html">Download printable HTML report (open → Print → Save as PDF)</a>', unsafe_allow_html=True)

if enable_csv_export:
    csv_bytes = st.session_state["df"].to_csv(index=False).encode()
    st.download_button("Download CSV", data=csv_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.csv", mime="text/csv", key="export_csv_unique")

if enable_excel_export:
    try:
        excel_bytes = to_excel_bytes(st.session_state["df"])
        st.download_button("Download Excel (.xlsx)", data=excel_bytes, file_name=f"{st.session_state.get('profile_name','portfolio')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="export_xlsx_unique")
    except Exception as e:
        st.error("Excel export not available in this environment. Add openpyxl/xlsxwriter to requirements. Error: " + str(e))

st.markdown("</div>", unsafe_allow_html=True)

# footer
st.caption("Asset Allocation — safe Plotly fallback. Add 'plotly' to requirements.txt for interactive charts.")
