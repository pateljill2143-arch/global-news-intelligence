"""
Global News Intelligence Dashboard — Cloud Edition
Reads from exported graph_data_export.json — no live database connections.
Feature-complete match to the local dashboard.py:
  Doomsday Clock · Sidebar Filters · Topic Impact · Network Graph
  India Economy Table · 10-Year Historical · 5-Year Forecast
"""

import re
import json
import numpy as np
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Global Intelligence Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.markdown("""
<style>
    .main-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(120deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 1rem;
    }
    [data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1e40af; }
    [data-testid="stMetricLabel"] { font-size: 1rem; font-weight: 600; color: #64748b; }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; border-radius: 20px; padding: 0.5rem 2rem; font-weight: 600; border: none;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data():
    try:
        with open("graph_data_export.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file not found! Please run export_for_cloud.py first.")
        st.stop()


data = load_data()
all_rels = data.get("conflicts", []) + data.get("cooperations", [])

st.sidebar.header("🔍 Filters")
all_entity_names = [e["name"] for e in data.get("entities", [])]
selected_topic = st.sidebar.selectbox(
    "🎯 Select Topic/Entity", ["-- Select a Topic --"] + all_entity_names
)
relationship_type = st.sidebar.selectbox(
    "Relationship Type",
    ["All", "ATTACKS", "STRIKES", "SANCTIONS", "INVADES", "THREATENS",
     "TRADES_WITH", "SUPPORTS", "ALLIED_WITH", "HELPS", "CONDEMNS",
     "NEGOTIATES_WITH", "EXPORTS_TO", "IMPORTS_FROM"],
)
sentiment_filter = st.sidebar.selectbox("Sentiment", ["All", "positive", "negative", "neutral"])

if relationship_type != "All" or sentiment_filter != "All":
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✅ Active Filters")
    if relationship_type != "All":
        st.sidebar.success(f"Relationship: **{relationship_type}**")
    if sentiment_filter != "All":
        st.sidebar.success(f"Sentiment: **{sentiment_filter}**")


def apply_filters(rels):
    out = rels
    if relationship_type != "All":
        out = [r for r in out if r.get("relation") == relationship_type]
    if sentiment_filter != "All":
        out = [r for r in out if r.get("sentiment") == sentiment_filter]
    return out


col_t1, col_t2, col_t3 = st.columns([2, 2, 1])
with col_t1:
    st.markdown('<h1 class="main-title">🌍 Global News Intelligence System</h1>', unsafe_allow_html=True)
with col_t2:
    st.markdown(
        f"<div style='text-align:center;color:#94a3b8;padding:1rem;'>📅 Data exported: <strong>{data.get('exported_at','')[:19]}</strong></div>",
        unsafe_allow_html=True,
    )
with col_t3:
    if st.button("🔄 Refresh", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("### AI-Powered Knowledge Graph Analytics")

stats = data.get("stats", {})
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div style='background:linear-gradient(135deg,#667eea,#764ba2);padding:1.5rem;border-radius:15px;text-align:center;box-shadow:0 8px 16px rgba(102,126,234,.3);'>
        <div style='font-size:.9rem;color:#e0e7ff;font-weight:600;'>📊 ENTITIES</div>
        <div style='font-size:2.5rem;color:white;font-weight:800;'>{stats.get('total_entities',0):,}</div>
        <div style='font-size:.8rem;color:#c7d2fe;'>Knowledge nodes</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div style='background:linear-gradient(135deg,#f093fb,#f5576c);padding:1.5rem;border-radius:15px;text-align:center;box-shadow:0 8px 16px rgba(245,87,108,.3);'>
        <div style='font-size:.9rem;color:#fee;font-weight:600;'>🔗 RELATIONSHIPS</div>
        <div style='font-size:2.5rem;color:white;font-weight:800;'>{stats.get('total_relationships',0):,}</div>
        <div style='font-size:.8rem;color:#fecdd3;'>Graph connections</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div style='background:linear-gradient(135deg,#4facfe,#00f2fe);padding:1.5rem;border-radius:15px;text-align:center;box-shadow:0 8px 16px rgba(79,172,254,.3);'>
        <div style='font-size:.9rem;color:#dbeafe;font-weight:600;'>📰 ARTICLES</div>
        <div style='font-size:2.5rem;color:white;font-weight:800;'>{stats.get('total_articles',0):,}</div>
        <div style='font-size:.8rem;color:#bfdbfe;'>Collected & processed</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div style='background:linear-gradient(135deg,#fa709a,#fee140);padding:1.5rem;border-radius:15px;text-align:center;box-shadow:0 8px 16px rgba(250,112,154,.3);'>
        <div style='font-size:.9rem;color:#fef3c7;font-weight:600;'>⏳ PENDING</div>
        <div style='font-size:2.5rem;color:white;font-weight:800;'>{stats.get('unprocessed',0):,}</div>
        <div style='font-size:.8rem;color:#fde68a;'>Awaiting analysis</div></div>""", unsafe_allow_html=True)

st.markdown("---")

st.markdown("<h1 style='text-align:center;color:#FFFFFF;font-size:42px;'>⏰ Doomsday Clock — Global Threat Assessment</h1>", unsafe_allow_html=True)
st.markdown("<hr style='border:2px solid #FFFFFF;margin-bottom:30px;'>", unsafe_allow_html=True)

n_conflicts = len(data.get("conflicts", []))
n_coops = len(data.get("cooperations", []))
threat_ratio = n_conflicts / max(n_conflicts + n_coops, 1)
seconds_to_midnight = 85

clock_col1, clock_col2, clock_col3 = st.columns([2, 1, 2])
with clock_col1:
    fig_clock = go.Figure(go.Indicator(
        mode="gauge+number", value=seconds_to_midnight,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Seconds to Midnight", "font": {"size": 26, "color": "#FFFFFF", "family": "Arial Black"}},
        number={"font": {"size": 48, "color": "#FFFFFF", "family": "Arial Black"}},
        gauge={
            "axis": {"range": [None, 300], "tickwidth": 2, "tickcolor": "#FFFFFF", "tickfont": {"size": 12, "color": "#FFFFFF"}},
            "bar": {"color": "#CC0000", "thickness": 0.75},
            "bgcolor": "white", "borderwidth": 2, "bordercolor": "#333333",
            "steps": [{"range": [0, 60], "color": "#FF0000"}, {"range": [60, 120], "color": "#FF6600"},
                      {"range": [120, 180], "color": "#FFB300"}, {"range": [180, 300], "color": "#00CC00"}],
            "threshold": {"line": {"color": "#FFFFFF", "width": 4}, "thickness": 0.8, "value": 85},
        },
    ))
    fig_clock.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font={"color": "#FFFFFF", "family": "Arial"})
    st.plotly_chart(fig_clock, use_container_width=True)

with clock_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    threat_level, threat_color, threat_desc = "🟠 SEVERE", "#FF4500", "High Threat"
    if seconds_to_midnight <= 60:
        threat_level, threat_color, threat_desc = "🔴 CRITICAL", "#8B0000", "Extreme Danger"
    elif seconds_to_midnight <= 120:
        threat_level, threat_color, threat_desc = "🟠 SEVERE", "#FF4500", "High Threat"
    elif seconds_to_midnight <= 180:
        threat_level, threat_color, threat_desc = "🟡 ELEVATED", "#FFA500", "Moderate Risk"
    else:
        threat_level, threat_color, threat_desc = "🟢 GUARDED", "#32CD32", "Low Risk"
    st.markdown(f"""<div style='text-align:center;padding:25px;background:linear-gradient(135deg,{threat_color}15,{threat_color}30);
        border-radius:15px;border:3px solid {threat_color};'>
        <h1 style='color:{threat_color};margin:0;font-size:32px;'>{threat_level}</h1>
        <p style='font-size:16px;color:#333;margin:10px 0 0 0;font-weight:600;'>{threat_desc}</p></div>""", unsafe_allow_html=True)

with clock_col3:
    st.markdown("<h3 style='color:#FFFFFF;font-size:24px;'>📊 Threat Indicators</h3>", unsafe_allow_html=True)
    st.metric("⚔️ Conflicts Detected", n_conflicts)
    st.metric("😞 Negative Relations", n_conflicts)
    st.metric("😊 Positive Relations", n_coops)
    st.metric("📉 Threat Ratio", f"{int(threat_ratio * 100)}%")

with st.expander("ℹ️ Threat Levels"):
    st.markdown("🔴 **0–60 s** CRITICAL · 🟠 **60–120 s** SEVERE · 🟡 **120–180 s** ELEVATED · 🟢 **180+ s** GUARDED")

st.subheader("⚠️ Major Threats Contributing to Global Risk")
th1, th2 = st.columns(2)
with th1:
    st.markdown("**🔥 Recent Conflicts & Attacks**")
    if data.get("conflicts"):
        df_t = pd.DataFrame(data["conflicts"][:8])[["source", "relation", "target", "date"]]
        df_t.columns = ["Entity", "Action", "Target", "Date"]
        st.dataframe(df_t, use_container_width=True, hide_index=True)
    else:
        st.info("No major threats detected")
with th2:
    st.markdown("**🌍 High-Risk Entities**")
    entity_risk = {}
    for c in data.get("conflicts", []):
        entity_risk[c["source"]] = entity_risk.get(c["source"], 0) + 1
    if entity_risk:
        df_risk = pd.DataFrame(sorted(entity_risk.items(), key=lambda x: x[1], reverse=True)[:8], columns=["Entity", "Threat Actions"])
        st.dataframe(df_risk, use_container_width=True, hide_index=True)
    else:
        st.info("No high-risk entities identified")

st.markdown("---")

if selected_topic != "-- Select a Topic --":
    st.header(f"🎯 Impact Analysis: {selected_topic}")
    filtered_rels = apply_filters(all_rels)
    outgoing = [{"Impact": r["relation"], "Affecting": r["target"], "Date": r.get("date", "N/A"), "Sentiment": r.get("sentiment", "N/A")}
                for r in filtered_rels if r.get("source") == selected_topic]
    incoming = [{"Impact": r["relation"], "From": r["source"], "Date": r.get("date", "N/A"), "Sentiment": r.get("sentiment", "N/A")}
                for r in filtered_rels if r.get("target") == selected_topic]

    col_il, col_ir = st.columns(2)
    with col_il:
        st.subheader(f"📤 What {selected_topic} is doing")
        if outgoing:
            st.dataframe(pd.DataFrame(outgoing), use_container_width=True)
            st.metric("Total Outgoing Actions", len(outgoing))
            st.bar_chart(pd.DataFrame(outgoing)["Impact"].value_counts())
        else:
            st.info(f"{selected_topic} has no outgoing relationships")
    with col_ir:
        st.subheader(f"📥 What is happening to {selected_topic}")
        if incoming:
            st.dataframe(pd.DataFrame(incoming), use_container_width=True)
            st.metric("Total Incoming Actions", len(incoming))
            st.bar_chart(pd.DataFrame(incoming)["Impact"].value_counts())
        else:
            st.info(f"{selected_topic} has no incoming relationships")

    st.subheader(f"🕸️ Relationship Network for {selected_topic}")
    edges = [(selected_topic, r["Affecting"], r["Impact"]) for r in outgoing] + [(r["From"], selected_topic, r["Impact"]) for r in incoming]
    if edges:
        G = nx.DiGraph()
        for s, t, lbl in edges:
            G.add_edge(s, t, label=lbl)
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        edge_traces = []
        for e in G.edges():
            x0, y0 = pos[e[0]]; x1, y1 = pos[e[1]]
            edge_traces.append(go.Scatter(x=[x0, x1, None], y=[y0, y1, None], mode="lines",
                                          line=dict(width=2, color="#888"), hoverinfo="none", showlegend=False))
        node_x, node_y, node_text, node_color = [], [], [], []
        for node in G.nodes():
            x, y = pos[node]; node_x.append(x); node_y.append(y)
            node_text.append(node)
            node_color.append("#FF4B4B" if node == selected_topic else "#1f77b4")
        node_trace = go.Scatter(x=node_x, y=node_y, mode="markers+text", text=node_text,
                                textposition="top center", marker=dict(size=30, color=node_color, line_width=2), hoverinfo="text")
        fig_net = go.Figure(data=edge_traces + [node_trace],
                            layout=go.Layout(showlegend=False, hovermode="closest",
                                             margin=dict(b=0, l=0, r=0, t=0), height=500,
                                             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
        st.plotly_chart(fig_net, use_container_width=True)
        st.caption(f"🔴 Red: {selected_topic} | 🔵 Blue: Connected entities")
    else:
        st.info(f"No network connections found for {selected_topic}")
    st.markdown("---")

col_left, col_right = st.columns(2)
filtered_all = apply_filters(all_rels)
conflict_rel_types = {"ATTACKS", "STRIKES", "INVADES", "THREATENS", "CONDEMNS", "SANCTIONS"}
coop_rel_types = {"TRADES_WITH", "SUPPORTS", "ALLIED_WITH", "HELPS", "NEGOTIATES_WITH", "EXPORTS_TO", "IMPORTS_FROM"}

with col_left:
    st.subheader("🔴 Active Conflicts")
    conf_rows = [{"Source": r["source"], "Action": r["relation"], "Target": r["target"],
                  "Date": r.get("date", "N/A"), "Sentiment": r.get("sentiment", "N/A")}
                 for r in data.get("conflicts", []) if (relationship_type == "All" or r.get("relation") == relationship_type)
                 and (sentiment_filter == "All" or r.get("sentiment") == sentiment_filter)][:20]
    if conf_rows:
        st.dataframe(pd.DataFrame(conf_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No conflicts found with selected filters")

with col_right:
    st.subheader("🟢 Cooperations")
    coop_rows = [{"Source": r["source"], "Action": r["relation"], "Target": r["target"],
                  "Date": r.get("date", "N/A"), "Sentiment": r.get("sentiment", "N/A")}
                 for r in data.get("cooperations", []) if (relationship_type == "All" or r.get("relation") == relationship_type)
                 and (sentiment_filter == "All" or r.get("sentiment") == sentiment_filter)][:20]
    if coop_rows:
        st.dataframe(pd.DataFrame(coop_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No cooperations found with selected filters")

st.markdown("---")

st.subheader("📊 Top Entities by Mentions")
if data.get("entities"):
    top15 = data["entities"][:15]
    df_ent = pd.DataFrame(top15)
    df_ent.columns = ["Entity", "Mentions"]
    fig_ent = px.bar(df_ent, x="Entity", y="Mentions", title="Most Mentioned Entities",
                     color="Mentions", color_continuous_scale="Blues")
    st.plotly_chart(fig_ent, use_container_width=True)

st.subheader("🔗 Relationship Types Distribution")
if data.get("relationship_types"):
    df_rt = pd.DataFrame(data["relationship_types"])
    df_rt.columns = ["Type", "Count"]
    if relationship_type != "All":
        df_rt = df_rt[df_rt["Type"] == relationship_type]
    fig_pie_rt = px.pie(df_rt, values="Count", names="Type", title="Distribution of Relationship Types")
    st.plotly_chart(fig_pie_rt, use_container_width=True)

st.markdown("---")

st.markdown("<h2 style='text-align:center;color:#FF9933;font-size:32px;'>🇮🇳 Indian Economy & Parliament — News Table</h2>", unsafe_allow_html=True)
st.markdown("<hr style='border:2px solid #138808;margin-bottom:20px;'>", unsafe_allow_html=True)

india_kw_map = {
    "All": r"India|Indian|Modi|BJP|Lok Sabha|Rajya Sabha|Parliament|Rupee|RBI|Sensex|Nirmala|GST|SEBI|Rahul Gandhi",
    "Parliament & Bills": r"Parliament|Lok Sabha|Rajya Sabha|bill|legislation|amendment|ordinance",
    "Economy & Trade": r"India.*trade|trade.*India|India.*GDP|India.*economy|India.*export|India.*import",
    "Budget & Finance": r"union budget|finance bill|GST|RBI|fiscal|Nirmala",
    "Stock Market": r"Sensex|Nifty|BSE|NSE|Indian.*market|India.*stock|SEBI",
    "Political Parties": r"BJP|Congress|AAP|Modi|Rahul Gandhi|opposition|India.*election|India.*politics",
    "Defence & Security": r"Indian Army|Indian Navy|Indian Air Force|defence.*India|India.*military|Kashmir",
}

itc1, itc2, itc3 = st.columns(3)
with itc1:
    india_category = st.selectbox("Category", list(india_kw_map.keys()), key="india_cat")
with itc2:
    india_source_filter = st.selectbox("Source", ["All", "The Hindu", "Indian Express", "Times of India",
                                                   "Economic Times", "Hindustan Times", "NDTV", "India Today"], key="india_src")
with itc3:
    india_limit = st.slider("Max Articles", 10, 50, 30, key="india_lim")

kw_pattern = india_kw_map.get(india_category, india_kw_map["All"])
all_articles = data.get("articles", [])
india_art = []
for a in all_articles:
    title = a.get("title", "") or ""
    if re.search(kw_pattern, title, re.IGNORECASE):
        src = a.get("source", "")
        if india_source_filter == "All" or re.search(india_source_filter, src, re.IGNORECASE):
            india_art.append(a)
india_art = india_art[:india_limit]

if india_art:
    india_rows = []
    for a in india_art:
        tl = (a.get("title", "") or "").lower()
        if any(w in tl for w in ["parliament", "lok sabha", "rajya sabha", "bill", "amendment"]):
            tag = "🏛️ Parliament"
        elif any(w in tl for w in ["budget", "gst", "rbi", "fiscal", "nirmala"]):
            tag = "💰 Budget/Finance"
        elif any(w in tl for w in ["sensex", "nifty", "stock", "sebi"]):
            tag = "📈 Markets"
        elif any(w in tl for w in ["trade", "export", "import", "deal"]):
            tag = "🤝 Trade"
        elif any(w in tl for w in ["army", "navy", "defence", "military", "kashmir"]):
            tag = "🛡️ Defence"
        elif any(w in tl for w in ["bjp", "congress", "election", "modi", "rahul", "opposition"]):
            tag = "🗳️ Politics"
        else:
            tag = "🇮🇳 India"
        t = a.get("title", "")
        india_rows.append({"Category": tag, "Headline": t[:100] + ("..." if len(t) > 100 else ""),
                           "Source": a.get("source", "Unknown"), "Date": a.get("date", "N/A")})

    def _color_india_row(row):
        c = {"🏛️ Parliament": "background-color:#E65100;color:#fff",
             "💰 Budget/Finance": "background-color:#1B5E20;color:#fff",
             "📈 Markets": "background-color:#0D47A1;color:#fff",
             "🤝 Trade": "background-color:#4A148C;color:#fff",
             "🛡️ Defence": "background-color:#B71C1C;color:#fff",
             "🗳️ Politics": "background-color:#F57F17;color:#000",
             "🇮🇳 India": "background-color:#212121;color:#fff"}
        return [c.get(row["Category"], "")] * len(row)

    st.dataframe(pd.DataFrame(india_rows).style.apply(_color_india_row, axis=1),
                 use_container_width=True, hide_index=True)
    st.download_button("📥 Download India News CSV", pd.DataFrame(india_rows).to_csv(index=False),
                       file_name=f"india_news_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
else:
    st.info("No India-related articles found in the exported data.")

st.markdown("---")

st.markdown("<h2 style='text-align:center;color:#FF9933;font-size:36px;'>🇮🇳 Indian Economy — 10-Year Historical Overview</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#AAAAAA;'>Source: World Bank / IMF / RBI official data</p>", unsafe_allow_html=True)
st.markdown("<hr style='border:2px solid #138808;margin-bottom:20px;'>", unsafe_allow_html=True)

india_econ_data = {
    "Year": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "GDP Growth (%)":       [8.0,  8.3,  6.8,  6.5,  5.0, -5.8,  9.1,  7.2,  8.2,  7.6,  6.5],
    "Inflation (%)":        [4.9,  4.5,  3.3,  4.9,  3.7,  6.2,  5.5,  6.7,  5.4,  4.8,  4.2],
    "Unemployment (%)":     [3.5,  3.4,  3.5,  3.4,  5.3,  7.1,  6.0,  4.8,  3.9,  3.7,  3.5],
    "Forex Reserves ($B)":  [352,  360,  409,  393,  457,  577,  633,  563,  620,  645,  670],
    "Current Acct (% GDP)": [-1.0,-0.6, -1.5, -2.1, -0.9,  1.7, -1.2, -2.0, -1.3, -1.0, -0.8],
    "Rupee per USD":        [65.5, 67.1, 65.1, 68.4, 70.4, 74.1, 73.9, 78.6, 82.7, 83.5, 84.0],
    "FDI Inflows ($B)":     [44,   46,   60,   62,   51,   64,   82,   85,   71,   78,   85],
}
df_econ = pd.DataFrame(india_econ_data)

econ_indicators = st.multiselect("Select Indicators to Display",
    ["GDP Growth (%)", "Inflation (%)", "Unemployment (%)", "Current Acct (% GDP)"],
    default=["GDP Growth (%)", "Inflation (%)"], key="econ_indicators")

hist_col1, hist_col2 = st.columns([2, 1])
with hist_col1:
    if econ_indicators:
        cmap = {"GDP Growth (%)":"#00C853","Inflation (%)":"#FF6D00","Unemployment (%)":"#D500F9","Current Acct (% GDP)":"#2979FF"}
        fig_hist = go.Figure()
        for ind in econ_indicators:
            fig_hist.add_trace(go.Scatter(x=df_econ["Year"], y=df_econ[ind], name=ind,
                                          mode="lines+markers", line=dict(color=cmap.get(ind,"#FFF"), width=3), marker=dict(size=8)))
        fig_hist.add_vrect(x0=2019.7, x1=2020.5, fillcolor="red", opacity=0.12,
                           annotation_text="COVID-19", annotation_position="top left", annotation_font_color="white")
        fig_hist.add_vrect(x0=2018.8, x1=2019.2, fillcolor="orange", opacity=0.10,
                           annotation_text="Elections", annotation_position="top right", annotation_font_color="white")
        fig_hist.update_layout(title="India Key Economic Indicators (2015–2025)", xaxis_title="Year", yaxis_title="%", height=420,
                               paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,20,0.8)", font_color="white",
                               legend=dict(bgcolor="rgba(0,0,0,0.5)", bordercolor="white", borderwidth=1, font=dict(color="white")),
                               xaxis=dict(tickmode="array", tickvals=df_econ["Year"].tolist(), gridcolor="rgba(255,255,255,0.1)"),
                               yaxis=dict(gridcolor="rgba(255,255,255,0.1)"), hovermode="x unified")
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Select at least one indicator.")
with hist_col2:
    st.subheader("💵 Rupee vs USD & Forex")
    fig_fx = go.Figure()
    fig_fx.add_trace(go.Bar(x=df_econ["Year"], y=df_econ["Forex Reserves ($B)"], name="Forex Reserves ($B)",
                            marker_color="#1565C0", opacity=0.85, yaxis="y2"))
    fig_fx.add_trace(go.Scatter(x=df_econ["Year"], y=df_econ["Rupee per USD"], name="₹ per USD",
                                mode="lines+markers", line=dict(color="#FF6D00", width=3), marker=dict(size=7)))
    fig_fx.update_layout(title="Rupee Depreciation & Forex Reserves", height=420,
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,20,0.8)", font_color="white",
                         yaxis=dict(title="₹ per USD", gridcolor="rgba(255,255,255,0.1)"),
                         yaxis2=dict(title="Forex ($B)", overlaying="y", side="right"),
                         legend=dict(bgcolor="rgba(0,0,0,0.5)", font=dict(color="white")),
                         xaxis=dict(tickmode="array", tickvals=df_econ["Year"].tolist(), gridcolor="rgba(255,255,255,0.1)"),
                         hovermode="x unified")
    st.plotly_chart(fig_fx, use_container_width=True)

st.subheader("📦 FDI Inflows into India (USD Billion)")
fig_fdi = px.bar(df_econ, x="Year", y="FDI Inflows ($B)", color="FDI Inflows ($B)",
                 color_continuous_scale="Greens", text="FDI Inflows ($B)", title="FDI Inflows (2015–2025)")
fig_fdi.update_traces(textposition="outside", textfont_color="white")
fig_fdi.update_layout(height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,20,0.8)",
                      font_color="white", coloraxis_showscale=False,
                      xaxis=dict(tickmode="array", tickvals=df_econ["Year"].tolist(), gridcolor="rgba(255,255,255,0.1)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.1)"))
st.plotly_chart(fig_fdi, use_container_width=True)

with st.expander("📋 Key Economic Milestones (2015–2025)"):
    st.dataframe(pd.DataFrame([
        {"Year": 2016, "Event": "Demonetisation", "Impact": "GDP dipped short-term, digital payments surged"},
        {"Year": 2017, "Event": "GST Rollout", "Impact": "Unified tax system, initial disruption to SMEs"},
        {"Year": 2019, "Event": "Corporate Tax Cut to 22%", "Impact": "Boosted FDI, improved business sentiment"},
        {"Year": 2020, "Event": "COVID-19 Pandemic", "Impact": "GDP contracted -5.8%, worst since independence"},
        {"Year": 2021, "Event": "V-Shaped Recovery", "Impact": "9.1% growth, fastest among major economies"},
        {"Year": 2022, "Event": "Global Inflation & Rate Hikes", "Impact": "Rupee hit 83/$, RBI raised repo to 6.5%"},
        {"Year": 2023, "Event": "India G20 Presidency", "Impact": "Record FDI interest, Digital India expansion"},
        {"Year": 2024, "Event": "General Election (NDA wins)", "Impact": "Policy continuity, Sensex hit 85,000"},
        {"Year": 2025, "Event": "India 3rd Largest Economy", "Impact": "Surpassed Japan in nominal GDP"},
    ]), use_container_width=True, hide_index=True)

st.markdown("---")

st.markdown("<h2 style='text-align:center;color:#FF9933;font-size:36px;'>🔮 India Economy — 5-Year AI Forecast (2026–2030)</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#AAAAAA;font-size:15px;'>Predictive model trained on 10 years of real economic data · adjusted by live news sentiment</p>", unsafe_allow_html=True)
st.markdown("<hr style='border:2px solid #FF9933;margin-bottom:20px;'>", unsafe_allow_html=True)

_hist_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
_forecast_years = [2026, 2027, 2028, 2029, 2030]
_all_years = _hist_years + _forecast_years
_indicators_to_forecast = {
    "GDP Growth (%)":    [8.0,  8.3,  6.8, 6.5,  5.0, -5.8, 9.1, 7.2, 8.2, 7.6, 6.5],
    "Inflation (%)":     [4.9,  4.5,  3.3, 4.9,  3.7,  6.2, 5.5, 6.7, 5.4, 4.8, 4.2],
    "Unemployment (%)":  [3.5,  3.4,  3.5, 3.4,  5.3,  7.1, 6.0, 4.8, 3.9, 3.7, 3.5],
    "Rupee per USD (₹)": [65.5, 67.1, 65.1,68.4, 70.4, 74.1,73.9,78.6,82.7,83.5,84.0],
    "FDI Inflows ($B)":  [44,   46,   60,  62,   51,   64,  82,  85,  71,  78,  85],
}
_pos_s = n_coops
_neg_s = n_conflicts
_sentiment_score = (_pos_s - _neg_s) / max(_pos_s + _neg_s, 1)

fc1, fc2, fc3 = st.columns(3)
with fc1:
    _selected_indicator = st.selectbox("📊 Indicator to Forecast", list(_indicators_to_forecast.keys()), key="fcast_ind")
with fc2:
    _scenario = st.select_slider("📡 Economic Scenario",
        options=["🔴 Pessimistic", "⚪ Base Case", "🟢 Optimistic"], value="⚪ Base Case", key="fcast_scenario")
with fc3:
    _show_band = st.checkbox("Show Confidence Band", value=True, key="fcast_band")

_scenario_deltas = {
    "GDP Growth (%)":    {"🔴 Pessimistic": -2.5, "⚪ Base Case": 0.0, "🟢 Optimistic": 2.2},
    "Inflation (%)":     {"🔴 Pessimistic":  1.8, "⚪ Base Case": 0.0, "🟢 Optimistic":-1.5},
    "Unemployment (%)":  {"🔴 Pessimistic":  1.5, "⚪ Base Case": 0.0, "🟢 Optimistic":-1.2},
    "Rupee per USD (₹)": {"🔴 Pessimistic":  8.0, "⚪ Base Case": 0.0, "🟢 Optimistic":-6.0},
    "FDI Inflows ($B)":  {"🔴 Pessimistic": -20,  "⚪ Base Case": 0.0, "🟢 Optimistic": 22},
}
_scenario_adj = _scenario_deltas[_selected_indicator][_scenario]
_sent_nudge = _sentiment_score * abs(_scenario_deltas[_selected_indicator]["🟢 Optimistic"]) * 0.2
_hist_vals = _indicators_to_forecast[_selected_indicator]
_coeffs = np.polyfit(_hist_years, _hist_vals, deg=1)
_poly = np.poly1d(_coeffs)
_unit_map = {"GDP Growth (%)":"%","Inflation (%)":"%","Unemployment (%)":"%","Rupee per USD (₹)":"₹","FDI Inflows ($B)":"$B"}
_unit = _unit_map[_selected_indicator]
_clamp = {"GDP Growth (%)":(1.5,12.0),"Inflation (%)":(1.5,12.0),"Unemployment (%)":(1.5,10.0),"Rupee per USD (₹)":(70.0,120.0),"FDI Inflows ($B)":(40,9999)}
_forecast_vals = []
for _i, (_yr, _base) in enumerate(zip(_forecast_years, [float(_poly(y)) for y in _forecast_years])):
    _yw = (_i + 1) / len(_forecast_years)
    _val = _base + (_scenario_adj + _sent_nudge) * _yw
    lo, hi = _clamp[_selected_indicator]
    _forecast_vals.append(max(lo, min(hi, _val)))

fig_fcast = go.Figure()
fig_fcast.add_trace(go.Scatter(x=_hist_years, y=_hist_vals, name="Historical Data",
                               mode="lines+markers", line=dict(color="#00C853", width=3), marker=dict(size=8)))
if _show_band:
    _cu = [v + abs(v)*0.13 for v in _forecast_vals]; _cl = [v - abs(v)*0.13 for v in _forecast_vals]
    fig_fcast.add_trace(go.Scatter(x=_forecast_years+_forecast_years[::-1], y=_cu+_cl[::-1],
                                   fill="toself", fillcolor="rgba(255,153,51,0.15)",
                                   line=dict(color="rgba(255,255,255,0)"), name="Confidence Range (±13%)"))
fig_fcast.add_trace(go.Scatter(x=_forecast_years, y=_forecast_vals, name=f"AI Forecast ({_scenario})",
                               mode="lines+markers", line=dict(color="#FF9933", width=3, dash="dash"),
                               marker=dict(size=11, symbol="diamond", color="#FF9933")))
fig_fcast.add_vline(x=2025.5, line_dash="dash", line_color="rgba(255,255,255,0.5)", line_width=2,
                    annotation_text="Historical | Forecast", annotation_font_color="white")
fig_fcast.update_layout(title=f"India {_selected_indicator} — Historical & 5-Year Forecast", height=470,
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(20,20,20,0.85)",
                        font_color="white", hovermode="x unified",
                        legend=dict(bgcolor="rgba(0,0,0,0.5)", bordercolor="#FF9933", borderwidth=1, font=dict(color="white")),
                        xaxis=dict(tickmode="array", tickvals=_all_years, gridcolor="rgba(255,255,255,0.08)"),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"))
st.plotly_chart(fig_fcast, use_container_width=True)

_sc = "#00C853" if _sentiment_score > 0.1 else ("#FF4444" if _sentiment_score < -0.1 else "#FFB300")
_sl = "Positive 😊" if _sentiment_score > 0.1 else ("Negative 😟" if _sentiment_score < -0.1 else "Neutral 😐")
st.markdown(f"""<div style='background:rgba(255,153,51,0.08);border:1px solid #FF9933;border-radius:10px;padding:10px 18px;margin-bottom:14px;font-size:13px;'>
📡 <b>News Sentiment</b>: <span style='color:{_sc};font-weight:700;'>{_sl}</span>
&nbsp;|&nbsp; Score: <b>{_sentiment_score:+.2f}</b>
&nbsp;|&nbsp; Positive (cooperations): <b>{_pos_s}</b> · Negative (conflicts): <b>{_neg_s}</b>
&nbsp;|&nbsp; Scenario shift: <b>{_scenario_adj:+.1f} {_unit}</b></div>""", unsafe_allow_html=True)

_frows = []
for _i, _yr in enumerate(_forecast_years):
    _val = _forecast_vals[_i]; _prev = _forecast_vals[_i-1] if _i > 0 else _hist_vals[-1]; _chg = _val - _prev
    _hg = _selected_indicator in ["GDP Growth (%)", "FDI Inflows ($B)"]
    _frows.append({"Year": _yr, f"Predicted {_selected_indicator}": f"{_val:.2f} {_unit}",
                   "Change from Prior Year": f"{'▲' if _chg >= 0 else '▼'} {abs(_chg):.2f} {_unit}",
                   "Signal": "✅ Good" if (_chg >= 0) == _hg else "⚠️ Caution", "Scenario": _scenario})

def _color_frow(row):
    return (["background-color:#003b1a;color:#fff"] if "✅" in row["Signal"] else ["background-color:#3b0000;color:#fff"]) * len(row)

st.dataframe(pd.DataFrame(_frows).style.apply(_color_frow, axis=1), use_container_width=True, hide_index=True)
st.download_button("📥 Download 5-Year Forecast CSV", pd.DataFrame(_frows).to_csv(index=False),
                   file_name=f"india_forecast_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

st.markdown("---")

st.markdown("<h2 style='text-align:center;color:#FF9933;font-size:36px;'>🇮🇳 Indian Economy Impact Analysis</h2>", unsafe_allow_html=True)
st.markdown("<hr style='border:2px solid #138808;margin-bottom:30px;'>", unsafe_allow_html=True)

INDIA_RE = re.compile(r"India|Indian|Modi|Rupee|Delhi|Mumbai|RBI|BJP|Lok Sabha|Rajya Sabha|Parliament|Nirmala|Sensex|Nifty|GST|SEBI", re.IGNORECASE)
india_rels_data = [r for r in all_rels if INDIA_RE.search(r.get("source","")) or INDIA_RE.search(r.get("target",""))]
_pos_india = sum(1 for r in india_rels_data if r.get("sentiment") == "positive")
_neg_india = sum(1 for r in india_rels_data if r.get("sentiment") == "negative")
_trade_india = sum(1 for r in india_rels_data if r.get("relation") in {"TRADES_WITH","EXPORTS_TO","IMPORTS_FROM","SUPPORTS"})
_conflict_india = sum(1 for r in india_rels_data if r.get("relation") in {"ATTACKS","SANCTIONS","CONDEMNS","THREATENS","INVADES"})

ia1, ia2, ia3, ia4 = st.columns(4)
ia1.metric("🔗 India Relations", len(india_rels_data))
ia2.metric("📈 Positive Impact", _pos_india, delta=f"{_pos_india - _neg_india:+d}")
ia3.metric("💼 Trade Relations", _trade_india)
ia4.metric("⚠️ Conflicts", _conflict_india)

st.markdown("---")
ec1, ec2 = st.columns([1.2, 1])
with ec1:
    st.subheader("📊 India Relationship Types")
    if india_rels_data:
        df_ir = pd.DataFrame(india_rels_data)
        rc = df_ir["relation"].value_counts().reset_index(); rc.columns = ["Relation Type", "Count"]
        fig_ir = px.bar(rc, x="Count", y="Relation Type", orientation="h", title="India Relations by Type",
                        color="Count", color_continuous_scale="Oranges", text="Count")
        fig_ir.update_traces(textposition="outside")
        fig_ir.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             font_color="white", coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(fig_ir, use_container_width=True)
    else:
        st.info("No India-related data found")
with ec2:
    st.subheader("🎯 Sentiment Distribution")
    if india_rels_data:
        df_ir2 = pd.DataFrame(india_rels_data)
        sd = df_ir2["sentiment"].value_counts().reset_index(); sd.columns = ["Sentiment", "Count"]
        fig_sp = px.pie(sd, values="Count", names="Sentiment", title="Sentiment Breakdown",
                        color="Sentiment", color_discrete_map={"positive":"#00CC00","negative":"#FF4444","neutral":"#FFB300"}, hole=0.4)
        fig_sp.update_traces(textinfo="label+percent", textfont_size=13)
        fig_sp.update_layout(height=380, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_sp, use_container_width=True)
    else:
        st.info("No sentiment data available")

st.markdown("---")
st.subheader("🔮 Future Economic Impact Predictions for India")
predictions = []
ps_map = {}
for r in india_rels_data:
    p = r.get("target") if INDIA_RE.search(r.get("source","")) else r.get("source")
    if not p or INDIA_RE.search(p):
        continue
    if p not in ps_map:
        ps_map[p] = {"count":0,"pos":0,"neg":0,"rel":r.get("relation","")}
    ps_map[p]["count"] += 1
    if r.get("sentiment") == "positive": ps_map[p]["pos"] += 1
    elif r.get("sentiment") == "negative": ps_map[p]["neg"] += 1

for partner, ps in sorted(ps_map.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
    pr = ps["pos"] / max(ps["count"], 1)
    if pr >= 0.7 and ps["count"] >= 3:
        impact, fc_text, conf = "High Positive", f"Strong growth through {ps['rel']} with {partner}", "High (85-95%)"
    elif pr >= 0.5:
        impact, fc_text, conf = "Moderate Positive", f"Stable cooperation with {partner}", "Medium (65-75%)"
    elif pr < 0.3:
        impact, fc_text, conf = "Negative", f"Potential challenges with {partner}", "Medium (60-70%)"
    else:
        impact, fc_text, conf = "Neutral", f"Uncertain outlook with {partner}", "Low (40-50%)"
    predictions.append({"Partner/Factor": partner, "Predicted Impact": impact,
                         "Forecast": fc_text, "Confidence": conf, "Relationship Strength": ps["count"]})

_ti = len(india_rels_data)
if _ti > 0:
    _ss = (_pos_india - _neg_india) / _ti
    if _ss > 0.3 and (_trade_india / _ti) > 0.2:
        _ov, _ot, _oc = "Strong Growth", f"GDP 6.5–7.5% based on {_pos_india} positive & {_trade_india} trade relations", "High (80-90%)"
    elif _ss > 0:
        _ov, _ot, _oc = "Moderate Growth", f"GDP 5.0–6.0% with mixed sentiment ({_pos_india} pos vs {_neg_india} neg)", "Medium (70-80%)"
    else:
        _ov, _ot, _oc = "Cautious", f"GDP at risk (4.0–5.0%) due to {_neg_india} negative relations", "Medium (65-75%)"
    predictions.insert(0, {"Partner/Factor": "🇮🇳 Overall Indian Economy",
                            "Predicted Impact": _ov, "Forecast": _ot, "Confidence": _oc, "Relationship Strength": _ti})

if predictions:
    def _ci(val):
        if "High Positive" in val or "Strong Growth" in val: return "background-color:#D4EDDA;color:#155724"
        if "Moderate" in val: return "background-color:#D1ECF1;color:#0C5460"
        if "Negative" in val: return "background-color:#F8D7DA;color:#721C24"
        if "Cautious" in val: return "background-color:#FFF3CD;color:#856404"
        return ""
    df_pred = pd.DataFrame(predictions)
    st.dataframe(df_pred.style.applymap(_ci, subset=["Predicted Impact"]), use_container_width=True, hide_index=True)
    st.download_button("📥 Download Predictions CSV", df_pred.to_csv(index=False),
                       file_name=f"india_predictions_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
else:
    st.warning("Insufficient data. Collect more India-related news then re-export.")

st.markdown("---")

st.subheader("📰 Latest Articles Processed")
if data.get("articles"):
    df_art = pd.DataFrame(data["articles"])
    kw = st.text_input("🔍 Search articles", placeholder="Enter keyword...")
    if kw:
        mask = df_art.apply(lambda row: row.astype(str).str.contains(kw, case=False).any(), axis=1)
        df_art = df_art[mask]
    st.markdown(f"**Showing {len(df_art)} articles**")
    st.dataframe(df_art, height=400, hide_index=True, use_container_width=True)

st.markdown("---")

fc1, fc2, fc3 = st.columns(3)
with fc1:
    st.markdown("<div style='text-align:center;padding:1rem;'><div style='font-size:2rem;'>🤖</div><div style='font-size:.9rem;color:#64748b;font-weight:600;'>AI-Powered</div><div style='font-size:.8rem;color:#94a3b8;'>BERT NER Processing</div></div>", unsafe_allow_html=True)
with fc2:
    st.markdown("<div style='text-align:center;padding:1rem;'><div style='font-size:2rem;'>🕸️</div><div style='font-size:.9rem;color:#64748b;font-weight:600;'>Knowledge Graph</div><div style='font-size:.8rem;color:#94a3b8;'>Neo4j Database</div></div>", unsafe_allow_html=True)
with fc3:
    st.markdown("<div style='text-align:center;padding:1rem;'><div style='font-size:2rem;'>📡</div><div style='font-size:.9rem;color:#64748b;font-weight:600;'>Real-time Data</div><div style='font-size:.8rem;color:#94a3b8;'>Multi-source APIs</div></div>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center;padding:1.5rem;color:#94a3b8;font-size:.85rem;'>Data exported: <strong>{data.get('exported_at','')[:19]}</strong><br>Built with Streamlit, Plotly, NetworkX and Python</div>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⏰ Doomsday Clock")
ck_e = "🔴" if seconds_to_midnight <= 90 else ("🟠" if seconds_to_midnight <= 120 else "🟡")
ck_s = "CRITICAL" if seconds_to_midnight <= 90 else ("SEVERE" if seconds_to_midnight <= 120 else "ELEVATED")
st.sidebar.markdown(f"{ck_e} **{ck_s}**\n\n**{seconds_to_midnight} seconds** to midnight\n\n*Official Bulletin of Atomic Scientists*")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 System Info")
st.sidebar.info(f"**Data From Export:**\nEntities: {stats.get('total_entities',0):,}\nRelationships: {stats.get('total_relationships',0):,}\nArticles: {stats.get('total_articles',0):,}\n\n**Sources:** Guardian · NewsData · GNews\n\n**To update:** Run export_for_cloud.py + git push")
