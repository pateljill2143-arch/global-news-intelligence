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

st.set_page_config(
    page_title="Global News Intelligence", 
    layout="wide", 
    page_icon="🌍",
    initial_sidebar_state="collapsed"
)

# Custom CSS for attractive styling
st.markdown("""
<style>
    /* Main title styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem;
        animation: fadeIn 1s ease-in;
    }
    
    /* Metric cards styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #64748b;
    }
    
    /* Card-like containers */
    .element-container {
        transition: transform 0.2s;
    }
    
    .element-container:hover {
        transform: translateY(-2px);
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Fade in animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    }
</style>
""", unsafe_allow_html=True)

# Load exported data with 5-minute cache TTL
@st.cache_data(ttl=300)  # Cache expires after 5 minutes
def load_data():
    try:
        with open("graph_data_export.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Data file not found! Please run export_for_cloud.py first.")
        st.stop()

data = load_data()

# Animated Header
st.markdown('<h1 class="main-title">🌍 Global News Intelligence Dashboard</h1>', unsafe_allow_html=True)

# Subtitle with refresh button
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.markdown(f"""
        <div style='text-align: center; color: #64748b; font-size: 1.1rem; padding: 0.5rem;'>
            <strong>Real-time AI-Powered News Analysis</strong>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
        <div style='text-align: center; color: #94a3b8; font-size: 0.95rem; padding: 0.5rem;'>
            📅 Last Updated: {data['exported_at'][:19]}
        </div>
    """, unsafe_allow_html=True)
with col3:
    if st.button("🔄 Refresh", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Enhanced Metrics Section with gradient background
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center; 
                    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);'>
            <div style='font-size: 0.9rem; color: #e0e7ff; font-weight: 600;'>📊 ENTITIES</div>
            <div style='font-size: 2.5rem; color: white; font-weight: 800;'>{:,}</div>
            <div style='font-size: 0.8rem; color: #c7d2fe;'>Knowledge nodes</div>
        </div>
    """.format(data['stats']['total_entities']), unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center;
                    box-shadow: 0 8px 16px rgba(245, 87, 108, 0.3);'>
            <div style='font-size: 0.9rem; color: #fee; font-weight: 600;'>🔗 RELATIONSHIPS</div>
            <div style='font-size: 2.5rem; color: white; font-weight: 800;'>{:,}</div>
            <div style='font-size: 0.8rem; color: #fecdd3;'>Graph connections</div>
        </div>
    """.format(data['stats']['total_relationships']), unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center;
                    box-shadow: 0 8px 16px rgba(79, 172, 254, 0.3);'>
            <div style='font-size: 0.9rem; color: #dbeafe; font-weight: 600;'>📰 ARTICLES</div>
            <div style='font-size: 2.5rem; color: white; font-weight: 800;'>{:,}</div>
            <div style='font-size: 0.8rem; color: #bfdbfe;'>Collected & processed</div>
        </div>
    """.format(data['stats']['total_articles']), unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                    padding: 1.5rem; border-radius: 15px; text-align: center;
                    box-shadow: 0 8px 16px rgba(250, 112, 154, 0.3);'>
            <div style='font-size: 0.9rem; color: #fef3c7; font-weight: 600;'>⏳ PENDING</div>
            <div style='font-size: 2.5rem; color: white; font-weight: 800;'>{:,}</div>
            <div style='font-size: 0.8rem; color: #fde68a;'>Awaiting analysis</div>
        </div>
    """.format(data['stats'].get('unprocessed', 0)), unsafe_allow_html=True)

st.divider()

# Tabbed interface for better organization
tab1, tab2, tab3, tab4 = st.tabs([
    "⚔️ Global Conflicts", 
    "🤝 Cooperations", 
    "📊 Entity Analytics", 
    "📰 Latest Articles"
])

with tab1:
    st.markdown("### ⚔️ Global Conflicts & Tensions")
    if data['conflicts']:
        conflicts_df = pd.DataFrame(data['conflicts'])
        
        # Create two columns for count and table
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Total Conflicts", len(conflicts_df), delta=None)
            
            # Conflict types breakdown
            if 'relation' in conflicts_df.columns:
                conflict_types = conflicts_df['relation'].value_counts()
                st.markdown("**Conflict Types:**")
                for ctype, count in conflict_types.items():
                    st.markdown(f"- {ctype}: **{count}**")
        
        with col2:
            # Enhanced conflicts table with color coding
            st.dataframe(
                conflicts_df[['source', 'relation', 'target', 'date']],
                height=400,
                hide_index=True,
                use_container_width=True
            )
        
        # Conflict network visualization
        st.markdown("### 🗺️ Conflict Network")
        if len(conflicts_df) > 0:
            # Create network graph
            fig = go.Figure()
            
            # Get unique entities
            sources = conflicts_df['source'].unique()
            targets = conflicts_df['target'].unique()
            all_entities = list(set(list(sources) + list(targets)))[:20]  # Limit to top 20
            
            # Create sankey diagram
            source_indices = [all_entities.index(s) for s in conflicts_df['source'][:20] if s in all_entities]
            target_indices = [all_entities.index(t) for t in conflicts_df['target'][:20] if t in all_entities]
            
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_entities,
                    color="#e63946"
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=[1]*len(source_indices),
                    color="rgba(230, 57, 70, 0.3)"
                )
            )])
            
            fig.update_layout(
                title="Conflict Flow Diagram",
                font=dict(size=12),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🕊️ No conflicts detected in the current dataset")

with tab2:
    st.markdown("### 🤝 Global Cooperations & Alliances")
    if data['cooperations']:
        coop_df = pd.DataFrame(data['cooperations'])
        
        # Create two columns
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Total Cooperations", len(coop_df), delta=None)
            
            # Cooperation types breakdown
            if 'relation' in coop_df.columns:
                coop_types = coop_df['relation'].value_counts()
                st.markdown("**Cooperation Types:**")
                for ctype, count in coop_types.items():
                    st.markdown(f"- {ctype}: **{count}**")
        
        with col2:
            st.dataframe(
                coop_df[['source', 'relation', 'target', 'date']],
                height=400,
                hide_index=True,
                use_container_width=True
            )
        
        # Cooperation network
        st.markdown("### 🌐 Cooperation Network")
        if len(coop_df) > 0:
            sources = coop_df['source'].unique()
            targets = coop_df['target'].unique()
            all_entities = list(set(list(sources) + list(targets)))[:20]
            
            source_indices = [all_entities.index(s) for s in coop_df['source'][:20] if s in all_entities]
            target_indices = [all_entities.index(t) for t in coop_df['target'][:20] if t in all_entities]
            
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=all_entities,
                    color="#06d6a0"
                ),
                link=dict(
                    source=source_indices,
                    target=target_indices,
                    value=[1]*len(source_indices),
                    color="rgba(6, 214, 160, 0.3)"
                )
            )])
            
            fig.update_layout(
                title="Cooperation Flow Diagram",
                font=dict(size=12),
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🤝 No cooperations detected in the current dataset")

with tab3:
    st.markdown("### 📊 Entity Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top Entities Bar Chart with gradient
        if data['entities']:
            top_entities = data['entities'][:15]
            fig = go.Figure(data=[
                go.Bar(
                    x=[e['mentions'] for e in top_entities],
                    y=[e['name'] for e in top_entities],
                    orientation='h',
                    marker=dict(
                        color=[e['mentions'] for e in top_entities],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Mentions")
                    ),
                    text=[e['mentions'] for e in top_entities],
                    textposition='auto',
                )
            ])
            
            fig.update_layout(
                title="🏆 Top 15 Most Mentioned Entities",
                xaxis_title="Number of Mentions",
                yaxis_title="Entity",
                yaxis={'categoryorder':'total ascending'},
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Relationship Types Pie Chart with custom colors
        if data.get('relationship_types'):
            fig = go.Figure(data=[
                go.Pie(
                    labels=[r['type'] for r in data['relationship_types']],
                    values=[r['count'] for r in data['relationship_types']],
                    hole=0.4,
                    marker=dict(
                        colors=px.colors.qualitative.Set3,
                        line=dict(color='white', width=2)
                    ),
                    textinfo='label+percent',
                    textfont=dict(size=12)
                )
            ])
            
            fig.update_layout(
                title="🔗 Relationship Types Distribution",
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Entity mentions timeline (if available)
    st.markdown("### 📈 Entity Trends")
    top_10 = data['entities'][:10]
    names = [e['name'] for e in top_10]
    mentions = [e['mentions'] for e in top_10]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=names,
        y=mentions,
        mode='lines+markers',
        marker=dict(
            size=12,
            color=mentions,
            colorscale='Plasma',
            showscale=True,
            line=dict(width=2, color='white')
        ),
        line=dict(width=3, color='rgba(99, 110, 250, 0.8)'),
        fill='tozeroy',
        fillcolor='rgba(99, 110, 250, 0.2)'
    ))
    
    fig.update_layout(
        title="Top 10 Entity Mention Distribution",
        xaxis_title="Entity",
        yaxis_title="Mentions",
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### 📰 Latest Processed Articles")
    if data['articles']:
        articles_df = pd.DataFrame(data['articles'])
        
        # Add a search filter
        search = st.text_input("🔍 Search articles", placeholder="Enter keyword...")
        
        if search:
            mask = articles_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
            filtered_df = articles_df[mask]
        else:
            filtered_df = articles_df
        
        st.markdown(f"**Showing {len(filtered_df)} of {len(articles_df)} articles**")
        
        # Display with better formatting
        st.dataframe(
            filtered_df,
            height=500,
            hide_index=True,
            use_container_width=True,
            column_config={
                "title": st.column_config.TextColumn("Article Title", width="large"),
                "source": st.column_config.TextColumn("Source", width="small"),
                "category": st.column_config.TextColumn("Category", width="small"),
                "date": st.column_config.TextColumn("Published", width="small")
            }
        )
    else:
        st.info("📭 No articles available yet")

# Enhanced Footer
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2rem;'>🤖</div>
            <div style='font-size: 0.9rem; color: #64748b; font-weight: 600;'>AI-Powered</div>
            <div style='font-size: 0.8rem; color: #94a3b8;'>BERT NER Processing</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2rem;'>🕸️</div>
            <div style='font-size: 0.9rem; color: #64748b; font-weight: 600;'>Knowledge Graph</div>
            <div style='font-size: 0.8rem; color: #94a3b8;'>Neo4j Database</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='font-size: 2rem;'>📡</div>
            <div style='font-size: 0.9rem; color: #64748b; font-weight: 600;'>Real-time Data</div>
            <div style='font-size: 0.8rem; color: #94a3b8;'>Multi-source APIs</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem; color: #94a3b8; font-size: 0.85rem;'>
        Last data export: <strong>{data['exported_at'][:19]}</strong><br>
        Built with ❤️ using Streamlit, Plotly, and Python
    </div>
""", unsafe_allow_html=True)
