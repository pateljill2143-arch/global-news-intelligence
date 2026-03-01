"""
Cloud-friendly Streamlit Dashboard - reads from exported JSON data
No database connections needed - perfect for Streamlit Cloud deployment!
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="Global News Intelligence", layout="wide", page_icon="🌍")

# Load exported data
@st.cache_data
def load_data():
    try:
        with open("graph_data_export.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Data file not found! Please run export_for_cloud.py first.")
        st.stop()

data = load_data()

# Header
st.title("🌍 Global News Intelligence Dashboard")
st.markdown(f"**Last Updated:** {data['exported_at'][:19]}")

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Total Entities", f"{data['stats']['total_entities']:,}")
with col2:
    st.metric("🔗 Total Relationships", f"{data['stats']['total_relationships']:,}")
with col3:
    st.metric("📰 Articles Collected", f"{data['stats']['total_articles']:,}")
with col4:
    st.metric("⏳ Unprocessed", f"{data['stats'].get('unprocessed', 0):,}")

st.divider()

# Two column layout
col_left, col_right = st.columns(2)

with col_left:
    # Conflicts
    st.subheader("⚔️ Global Conflicts")
    if data['conflicts']:
        conflicts_df = pd.DataFrame(data['conflicts'])
        st.dataframe(
            conflicts_df[['source', 'relation', 'target', 'date']],
            height=300,
            hide_index=True
        )
    else:
        st.info("No conflicts detected yet")
    
    # Top Entities Chart
    st.subheader("📊 Top Entities by Mentions")
    if data['entities']:
        top_entities = data['entities'][:15]
        fig = px.bar(
            top_entities,
            x='mentions',
            y='name',
            orientation='h',
            title="Most Mentioned Entities",
            labels={'mentions': 'Number of Mentions', 'name': 'Entity'}
        )
        fig.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True, key="entities_chart")

with col_right:
    # Cooperations
    st.subheader("🤝 Global Cooperations")
    if data['cooperations']:
        coop_df = pd.DataFrame(data['cooperations'])
        st.dataframe(
            coop_df[['source', 'relation', 'target', 'date']],
            height=300,
            hide_index=True
        )
    else:
        st.info("No cooperations detected yet")
    
    # Relationship Types Distribution
    st.subheader("🔗 Relationship Distribution")
    if data.get('relationship_types'):
        fig = px.pie(
            data['relationship_types'],
            values='count',
            names='type',
            title="Relationship Types"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True, key="relationships_chart")

st.divider()

# Latest Articles
st.subheader("📰 Latest Processed Articles")
if data['articles']:
    articles_df = pd.DataFrame(data['articles'])
    st.dataframe(
        articles_df,
        height=300,
        hide_index=True
    )
else:
    st.info("No articles available")

# Footer
st.divider()
st.caption(f"🔄 Data snapshot from {data['exported_at'][:10]} | 🌐 Powered by BERT NER + Neo4j Knowledge Graph")
