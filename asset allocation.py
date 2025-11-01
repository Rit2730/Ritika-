# asset_allocation_svg_safe.py
import streamlit as st
import pandas as pd
import math
from io import StringIO

st.set_page_config(page_title="Premium Asset Allocation (SVG-safe)", layout="wide", page_icon="💠")

# -------------------------
# Minimal requirements only: streamlit + pandas (no matplotlib/plotly)
# -------------------------

# --- Styles (dark premium)
st.markdown(
    """
    <style>
    body { background: linear-gradient(180deg,#061026 0%, #031226 100%); color: #e6f7ff; font-family: Inter, Roboto, Arial; }
    .stButton>button { background-color:#06b6b4; color:#021226; border-radius:8px; padding:6px 10px; }
    .sidebar .stMarkdown { color:#cfeef0; }
    .title-border { border-bottom: 1px solid rgba(191,239,255,0.06); padding-bottom:8px; margin-bottom:12px; }
    .small-muted { color:#bfefff; opacity:0.8; font-size:0.9em; }
    .svg-card { background:#071028; padding:12px; border-radius:10px; box-shadow: 0 6px 18px rgba(0,0,0,0.6); }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Typing animation for title & insights (silent)
# -------------------------
title_html = """
<div id="typed_title" style="font-family:Inter, Roboto, Arial; font-size:30px; color:#bfefff; font-weight:700;"></div>
<script>
const titleText = "💠 Premium Asset Allocation Dashboard";
let p = 0;
function typeTitle() {
  if (p < titleText.length) {
    document.getElementById('typed_title').innerHTML += titleText.charAt(p);
    p++;
    setTimeout(typeTitle, 20);
  } else {
    const el = document.getElementById('typed_title');
    el.style.borderRight = "2px solid rgba(191,239,255,0.7)";
    setInterval(()=>{ el.style.borderRight = el.style.borderRight ? '' : '2px solid rgba(191,239,255,0.7)'; }, 700);
  }
}
typeTitle();
</script>
"""
st.components.v1.html(title_html, height=60)

st.markdown(" ")
st.markdown("<div class='title-border'></div>", unsafe_allow_html=True)

# -------------------------
# Predefined portfolio data (your data)
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
    "Purpose": ["Secure income", "Higher income low risk", "Tax-efficient retirement corpus", "Capital protection", "Stable returns", "Monthly/quarterly income", "Inflation hedge", "Predictable maturity returns", "Guaranteed income", "Stability + diversification"],
    "Allocation (%)": [30, 20, 10, 10, 10, 7, 5, 3, 3, 2]
}

MODERATE_DATA = {
    "Asset Class": ["Large-Cap Equity Funds", "Mid/Small-Cap Funds", "Global Equity ETFs/Funds", "Hybrid/Balanced Funds",
                    "Corporate Bond Funds", "REITs", "Gold", "Private Credit / Debt AIF", "Farmland / Agro Real Assets", "Digital Asset Basket (tiny)"],
    "Risk": ["High", "High", "High", "Moderate", "Moderate", "Moderate", "Moderate", "Mod–High", "Moderate", "High"],
    "Returns (%)": ["8–12", "10–15", "7–12", "7–10", "6–9", "6–10", "3–8", "8–12", "4–8", "Varies"],
    "Horizon": ["7–10 yrs", "7–12 yrs", "7–10 yrs", "5–8 yrs", "3–7 yrs", "5–10 yrs", "3–7 yrs", "3–7 yrs", "5–15 yrs", "5–10 yrs"],
    "Purpose": ["Core growth", "Higher alpha", "Geographic diversification", "Smoother volatility", "Income stability", "Property income", "Risk hedge", "Enhanced yield", "Real asset diversification", "Asymmetric payoff"],
    "Allocation (%)": [25, 15, 10, 10, 10, 7, 5, 5, 5, 3]
}

HIGH_DATA = {
    "Asset Class": ["Domestic Equity (Large/Mid/Small)", "International Equities", "Venture Capital / Startup Investments",
                    "Private Equity Funds", "Crypto / Blockchain Assets", "Commodities (Energy/Metals ETFs)", "Real Assets (Timber/Renewables)",
                    "Structured Products / Hedge Funds", "IP / Music Royalties", "Active Derivatives (Hedged)"],
    "Risk": ["Very High"] * 10,
    "Returns (%)": ["10–15", "8–15", "20+", "15+", "Highly variable", "Varies", "6–12", "Varies", "Variable", "Variable"],
    "Horizon": ["10–20 yrs"] * 10,
    "Purpose": ["Primary growth source", "Global growth exposure", "High innovation upside", "Superior alpha potential", "Speculative moonshot", "Cycle & inflation hedge", "Alternative diversifier", "Non-correlated returns", "Uncorrelated cash-flows", "Tactical"],
    "Allocation (%)": [50, 15, 10, 7, 5, 5, 3, 3, 1, 1]
}

profiles = {
    "Low Risk Profile": pd.DataFrame(LOW_DATA),
    "Moderate Risk Profile": pd.DataFrame(MODERATE_DATA),
    "High Risk Profile": pd.DataFrame(HIGH_DATA),
}

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Profile & Controls")
selected_profile = st.sidebar.selectbox("Choose portfolio profile", list(profiles.keys()))

uploaded = st.sidebar.file_uploader("Upload CSV to replace this profile (optional)", type=["csv"])
if uploaded is not None:
    try:
        df_upload = pd.read_csv(uploaded)
        required_cols = {"Asset Class", "Allocation (%)", "Returns (%)"}
        if not required_cols.issubset(set(df_upload.columns)):
            st.sidebar.error(f"CSV must contain: {', '.join(required_cols)}")
        else:
            profiles[selected_profile] = df_upload.copy()
            st.sidebar.success("CSV loaded for selected profile.")
    except Exception as e:
        st.sidebar.error(f"CSV read error: {e}")

# store current df in session
if "profile_name" not in st.session_state or st.session_state.profile_name != selected_profile:
    st.session_state.profile_name = selected_profile
    st.session_state.current_df = profiles[selected_profile].copy()

st.sidebar.markdown("---")
if st.sidebar.button("Reset to default for profile"):
    st.session_state.current_df = profiles[selected_profile].copy()
    st.sidebar.success("Reset completed.")

st.sidebar.markdown("---")
show_icons = st.sidebar.checkbox("Show icons legend", value=True)

# -------------------------
# Editor with fallback (safe)
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
    with st.form("manual_edit_form"):
        rows = []
        for i, row in manual_df.iterrows():
            st.markdown(f"**Row {i+1} — {row.get('Asset Class','')}**")
            ac = st.text_input(f"Asset Class [{i}]", value=str(row.get("Asset Class", "")))
            rsk = st.text_input(f"Risk [{i}]", value=str(row.get("Risk", "")))
            ret = st.text_input(f"Returns (%) [{i}]", value=str(row.get("Returns (%)", "")))
            hor = st.text_input(f"Horizon [{i}]", value=str(row.get("Horizon", "")))
            purp = st.text_input(f"Purpose [{i}]", value=str(row.get("Purpose", "")))
            alloc = st.number_input(f"Allocation (%) [{i}]", value=float(row.get("Allocation (%)", 0.0)), step=0.1, key=f"alloc_{i}")
            rows.append({"Asset Class": ac, "Risk": rsk, "Returns (%)": ret, "Horizon": hor, "Purpose": purp, "Allocation (%)": alloc})
            st.markdown("---")
        submitted_manual = st.form_submit_button("Submit manual edits")
    if submitted_manual:
        edited_df = pd.DataFrame(rows)

if edited_df is not None:
    if st.button("Apply changes"):
        if "Allocation (%)" in edited_df.columns:
            edited_df["Allocation (%)"] = pd.to_numeric(edited_df["Allocation (%)"], errors="coerce").fillna(0.0)
        st.session_state.current_df = edited_df.copy()
        st.success("Changes applied.")
    else:
        st.info(f"Editor mode: {editor_mode}. After editing, click 'Apply changes'.")

# Normalize & download
col_norm, col_dl = st.columns([1, 1])
with col_norm:
    if st.button("Normalize allocations to 100%"):
        total = st.session_state.current_df.get("Allocation (%)", pd.Series(dtype=float)).sum()
        if total == 0:
            st.error("Total allocation is 0 — cannot normalize.")
        else:
            st.session_state.current_df["Allocation (%)"] = (st.session_state.current_df["Allocation (%)"] / total * 100.0).round(2)
            st.success("Allocations normalized to 100%")
with col_dl:
    csv_buf = st.session_state.current_df.to_csv(index=False)
    st.download_button("Download current table (CSV)", data=csv_buf, file_name=f"{selected_profile.replace(' ','_')}.csv", mime="text/csv")

# Show current table
st.subheader("Current Portfolio Table")
if show_icons:
    st.markdown("""
    <div style="display:flex;gap:12px;align-items:center;margin-bottom:8px;">
      <div style="display:flex;flex-direction:column;align-items:center;"><div style="font-size:18px">💵</div><small class="small-muted">Debt</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;"><div style="font-size:18px">📈</div><small class="small-muted">Equity</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;"><div style="font-size:18px">🏠</div><small class="small-muted">Real Assets</small></div>
      <div style="display:flex;flex-direction:column;align-items:center;"><div style="font-size:18px">🟨</div><small class="small-muted">Alternatives</small></div>
    </div>
    """, unsafe_allow_html=True)

st.dataframe(st.session_state.current_df.reset_index(drop=True), use_container_width=True)

# -------------------------
# Helpers: parse returns string -> numeric average
# -------------------------
def parse_return_value(val):
    if pd.isna(val):
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("%", "").replace("–", "-").replace("—", "-")
    if "+" in s:
        try:
            return float(s.replace("+", ""))
        except:
            return None
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
# Filters (view-only)
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
# Summary metrics and typing-insight (silent)
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

insight_text = ""
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insight_text = "Conservative portfolio — lower expected returns."
    elif weighted_avg_return < 10:
        insight_text = "Balanced portfolio — blend of safety and growth."
    else:
        insight_text = "Aggressive portfolio — higher expected returns with higher volatility."
else:
    insight_text = "Weighted return not available — check numeric Returns (%) values."

insight_html = f"""
<div id="typed_ins" style="font-family:Inter, Roboto, Arial; font-size:16px; color:#dffaff; font-weight:600;"></div>
<script>
const txt = {insight_text!r};
let j = 0;
function typeIns() {{
  if (j < txt.length) {{
    document.getElementById('typed_ins').innerHTML += txt.charAt(j);
    j++;
    setTimeout(typeIns, 25);
  }}
}}
typeIns();
</script>
"""
st.components.v1.html(insight_html, height=50)

# -------------------------
# Visuals: SVG Donut and SVG faux 3D bar
# -------------------------

def make_svg_donut(labels, values, size=360, hole_ratio=0.6, colors=None):
    total = sum(values) if sum(values) > 0 else 1
    cx = cy = size / 2
    r = size * 0.4
    inner_r = r * hole_ratio
    start_angle = 0
    paths = []
    if colors is None:
        # generate palette
        base_colors = ["#06b6b4","#0891b2","#0ea5a4","#06b6b4","#a3e635","#60a5fa","#f59e0b","#fb7185","#a78bfa","#34d399"]
    else:
        base_colors = colors
    for i, v in enumerate(values):
        angle = 360.0 * v / total
        end_angle = start_angle + angle
        # convert to radians
        sa = math.radians(start_angle)
        ea = math.radians(end_angle)
        x1 = cx + r * math.cos(sa)
        y1 = cy + r * math.sin(sa)
        x2 = cx + r * math.cos(ea)
        y2 = cy + r * math.sin(ea)
        large = 1 if angle > 180 else 0
        path = f"M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large} 1 {x2} {y2} Z"
        # text position (mid angle)
        mid = math.radians(start_angle + angle / 2.0)
        tx = cx + (r + 20) * math.cos(mid)
        ty = cy + (r + 20) * math.sin(mid)
        paths.append({
            "path": path,
            "color": base_colors[i % len(base_colors)],
            "label": labels[i],
            "pct": f"{(v/total*100):.1f}%",
            "tx": tx,
            "ty": ty
        })
        start_angle = end_angle
    # create SVG string
    svg_parts = [f"<svg width='{size}' height='{size}' viewBox='0 0 {size} {size}' xmlns='http://www.w3.org/2000/svg'>"]
    # slices
    for p in paths:
        svg_parts.append(f"<path d=\"{p['path']}\" fill=\"{p['color']}\" stroke='#031226' stroke-width='0.5'/>")
    # inner circle
    svg_parts.append(f"<circle cx='{cx}' cy='{cy}' r='{inner_r}' fill='#031226'/>")
    # labels as simple legend under svg (we will not overlay many labels to avoid clutter)
    svg_parts.append("</svg>")
    # create an HTML legend
    legend_html = "<div style='display:flex;flex-direction:column;gap:6px;margin-top:8px;'>"
    for p in paths:
        legend_html += f"<div style='display:flex;align-items:center;gap:8px;'><div style='width:12px;height:12px;border-radius:3px;background:{p['color']}'></div><div style='font-size:13px;color:#dffaff'>{p['label']} - {p['pct']}</div></div>"
    legend_html += "</div>"
    return "".join(svg_parts), legend_html

def make_svg_3d_bars(labels, values, width=600, height=340):
    # simple faux-3d using skew and gradient rectangles; values normalized
    maxv = max(values) if max(values) > 0 else 1
    bar_w = max(26, int((width - 160) / len(labels)))
    gap = 10
    svg = [f"<svg width='{width}' height='{height}' viewBox='0 0 {width} {height}' xmlns='http://www.w3.org/2000/svg'>"]
    # background
    svg.append(f"<rect width='100%' height='100%' fill='transparent' />")
    base_x = 60
    base_y = height - 40
    for i, (lab, val) in enumerate(zip(labels, values)):
        h = (val / maxv) * (height - 120)
        x = base_x + i * (bar_w + gap)
        y = base_y - h
        # shadow/back face
        svg.append(f"<rect x='{x+8}' y='{y+8}' width='{bar_w}' height='{h}' fill='rgba(0,0,0,0.12)' rx='4' />")
        # main bar
        svg.append(f"<rect x='{x}' y='{y}' width='{bar_w}' height='{h}' fill='#06b6b4' rx='4' />")
        # top highlight
        svg.append(f"<rect x='{x}' y='{y}' width='{bar_w}' height='{6}' fill='rgba(255,255,255,0.15)' />")
        # label (rotated)
        svg.append(f"<text x='{x + bar_w/2}' y='{base_y + 14}' font-size='11' fill='#dffaff' text-anchor='middle' transform='rotate(0 {x + bar_w/2} {base_y + 14})'>{lab}</text>")
        svg.append(f"<text x='{x + bar_w/2}' y='{y - 6}' font-size='12' fill='#e6fffa' text-anchor='middle'>{val:.1f}%</text>")
    svg.append("</svg>")
    return "".join(svg)

# Render donut + legend
labels = st.session_state.current_df["Asset Class"].tolist()
values = st.session_state.current_df["Allocation (%)"].fillna(0).tolist()

col_a, col_b = st.columns([1, 1])
with col_a:
    st.markdown("**Allocation — Donut (SVG)**")
    svg_str, legend_html = make_svg_donut(labels, values, size=360, hole_ratio=0.58)
    st.markdown(f"<div class='svg-card'>{svg_str}{legend_html}</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("**3D Style Allocation Bars (SVG)**")
    svg3 = make_svg_3d_bars(labels, values, width=680, height=340)
    st.markdown(f"<div class='svg-card'>{svg3}</div>", unsafe_allow_html=True)

# -------------------------
# Projection calculator
# -------------------------
st.markdown("---")
st.subheader("Projection Calculator (1 / 3 / 5 / 10 yrs)")
initial = st.number_input("Initial investment (₹)", min_value=1000.0, value=100000.0, step=1000.0)
yrs = st.selectbox("Projection horizon (years)", [1, 3, 5, 10], index=1)

proj_df = df_calc.copy()
total_alloc_now = proj_df["Allocation (%)"].sum()
if total_alloc_now <= 0:
    st.warning("Allocations sum to 0 — set allocations before projecting returns.")
else:
    proj_df["Weight"] = proj_df["Allocation (%)"] / total_alloc_now
    fallback = proj_df["_ParsedReturn"].median() if proj_df["_ParsedReturn"].notna().any() else 6.0
    proj_df["_UseReturn"] = proj_df["_ParsedReturn"].fillna(fallback)
    portfolio_return_decimal = (proj_df["_UseReturn"] * proj_df["Weight"]).sum() / 100.0
    future_val = initial * ((1 + portfolio_return_decimal) ** yrs)
    st.metric(f"Projected value after {yrs} years", f"₹{future_val:,.0f}")
    st.caption(f"Portfolio avg annual return used: {portfolio_return_decimal*100:.2f}% (fallback {fallback:.2f}% where needed)")

# -------------------------
# Automatic insights
# -------------------------
st.markdown("---")
st.subheader("Automatic Insights")
insights = []
if total_alloc < 90:
    insights.append("Total allocation < 90% — consider deploying idle cash or adjust allocations.")
if total_alloc > 110:
    insights.append("Total allocation > 110% — allocations not normalized.")
if weighted_avg_return is not None:
    if weighted_avg_return < 6:
        insights.append("Conservative expected returns (<6%).")
    elif weighted_avg_return < 10:
        insights.append("Balanced expected returns (6–10%).")
    else:
        insights.append("Aggressive expected returns (>10%).")
if not st.session_state.current_df.empty:
    top_idx = st.session_state.current_df["Allocation (%)"].idxmax()
    top_asset = st.session_state.current_df.loc[top_idx, "Asset Class"]
    top_alloc = st.session_state.current_df.loc[top_idx, "Allocation (%)"]
    if top_alloc >= 35:
        insights.append(f"High concentration: {top_asset} at {top_alloc:.1f}% allocation.")

if insights:
    for it in insights:
        st.info(it)
else:
    st.write("No immediate insights — portfolio looks balanced.")

st.markdown("---")
st.caption("SVG-safe professional app — uses only Streamlit + Pandas so it runs without Plotly/Matplotlib.")

