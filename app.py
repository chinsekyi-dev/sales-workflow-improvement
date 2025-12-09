import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.get_news import fetch_news_by_query, fetch_sales_triggers, save_news_to_file

# Page configuration
st.set_page_config(
    page_title="Patsnap Sales Trigger Dashboard",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Patsnap Sales Trigger Dashboard")
st.markdown("*Identify sales opportunities through news intelligence*")
st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Mode selection
    mode = st.radio("Mode", ["Sales Triggers", "Custom Search"], index=0)
    
    if mode == "Custom Search":
        query = st.text_input("Search Query", value="Apple")
        days_back = st.slider("Days to Look Back", min_value=1, max_value=30, value=7)
        sort_by = st.selectbox("Sort By", ["popularity", "publishedAt", "relevancy"])
    else:
        region = st.selectbox(
            "Region Filter",
            ["Global (All)", "Singapore", "Asia", "United States", "Europe", "China"],
            index=1  # Default to Singapore
        )
        days_back = st.slider("Days to Look Back", min_value=1, max_value=30, value=7)
        sort_by = "publishedAt"
        st.info("Sales Triggers mode searches for: funding, acquisitions, leadership changes, product launches, patents, IPOs, and expansions")
    
    fetch_button = st.button("🔄 Fetch Latest News", type="primary")
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")

# Load or fetch news data
data_file = "data/sales_triggers.json" if mode == "Sales Triggers" else "data/news_data.json"
news_data = None

if fetch_button:
    with st.spinner("Fetching news articles..."):
        if mode == "Sales Triggers":
            # Pass region filter, None if "Global (All)" selected
            region_filter = None if region == "Global (All)" else region
            news_data = fetch_sales_triggers(days_back=days_back, sort_by=sort_by, region=region_filter)
            if news_data:
                save_news_to_file(news_data, filename="sales_triggers.json")
        else:
            news_data = fetch_news_by_query(query=query, days_back=days_back, sort_by=sort_by)
            if news_data:
                save_news_to_file(news_data)
        
        if news_data:
            st.success("✅ News data fetched successfully!")
        else:
            st.error("❌ Failed to fetch news data")

# Try to load existing data
if news_data is None and os.path.exists(data_file):
    try:
        with open(data_file, "r") as f:
            news_data = json.load(f)
    except Exception as e:
        st.error(f"Error loading data file: {e}")

# Display the data
if news_data and news_data.get("status") == "ok":
    articles = news_data.get("articles", [])
    
    # Display stats in sidebar
    with st.sidebar:
        st.metric("Total Results", news_data.get("totalResults", 0))
        st.metric("Articles Loaded", len(articles))
    
    # Show active filters at the top
    st.markdown("### 🔍 Active Filters")
    filter_cols = st.columns(4)
    with filter_cols[0]:
        st.info(f"**Mode:** {mode}")
    with filter_cols[1]:
        st.info(f"**Time Period:** Last {days_back} days")
    with filter_cols[2]:
        if mode == "Sales Triggers":
            region_display = region if region != "Global (All)" else "Global"
            st.info(f"**Region:** {region_display}")
        else:
            st.info(f"**Query:** {query}")
    with filter_cols[3]:
        st.info(f"**Sort By:** {sort_by}")
    
    st.markdown("---")
    
    # Main content
    if articles:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(articles)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df['date'] = df['publishedAt'].dt.date
        df['source_name'] = df['source'].apply(lambda x: x.get('name', 'Unknown'))
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📋 Articles List", "🔍 Article Details"])
        
        with tab1:
            # Show trigger type distribution if in Sales Triggers mode
            if mode == "Sales Triggers" and 'trigger_type' in df.columns:
                col_header1, col_header2 = st.columns([3, 1])
                with col_header1:
                    st.subheader("🎯 Sales Trigger Distribution")
                with col_header2:
                    if region and region != "Global (All)":
                        st.markdown(f"<div style='text-align: right; padding: 10px; background-color: #e3f2fd; border-radius: 5px; margin-top: 10px;'><strong>🌍 Region:</strong> {region}</div>", unsafe_allow_html=True)
                
                trigger_counts = df['trigger_type'].value_counts()
                fig_triggers = px.pie(
                    values=trigger_counts.values,
                    names=trigger_counts.index,
                    title="Distribution of Sales Triggers",
                    hole=0.3
                )
                st.plotly_chart(fig_triggers, use_container_width=True)
                st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📅 Articles Over Time")
                articles_per_day = df.groupby('date').size().reset_index(name='count')
                fig_timeline = px.line(
                    articles_per_day, 
                    x='date', 
                    y='count',
                    markers=True,
                    title="Number of Articles Published per Day"
                )
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            with col2:
                st.subheader("📰 Top Sources")
                source_counts = df['source_name'].value_counts().head(10)
                fig_sources = px.bar(
                    x=source_counts.values,
                    y=source_counts.index,
                    orientation='h',
                    title="Top 10 News Sources",
                    labels={'x': 'Number of Articles', 'y': 'Source'}
                )
                st.plotly_chart(fig_sources, use_container_width=True)
            
            # Word cloud-style visualization of authors
            st.subheader("✍️ Most Active Authors")
            authors = df[df['author'].notna()]['author'].value_counts().head(10)
            if not authors.empty:
                fig_authors = go.Figure(data=[go.Bar(
                    x=authors.values,
                    y=authors.index,
                    orientation='h',
                    marker_color='lightblue'
                )])
                fig_authors.update_layout(
                    title="Top 10 Authors by Article Count",
                    xaxis_title="Number of Articles",
                    yaxis_title="Author"
                )
                st.plotly_chart(fig_authors, use_container_width=True)
            else:
                st.info("No author information available")
        
        with tab2:
            # Show header with region indicator
            col_header1, col_header2 = st.columns([2, 1])
            with col_header1:
                st.subheader("📋 All Articles")
            with col_header2:
                if mode == "Sales Triggers" and region and region != "Global (All)":
                    st.markdown(f"<div style='text-align: right; padding: 8px; background-color: #e3f2fd; border-radius: 5px; margin-top: 5px;'><strong>🌍 {region}</strong></div>", unsafe_allow_html=True)
            
            # Add filters
            if mode == "Sales Triggers" and 'trigger_type' in df.columns:
                col1, col2, col3 = st.columns(3)
                with col1:
                    selected_triggers = st.multiselect(
                        "Filter by Trigger Type",
                        options=df['trigger_type'].unique(),
                        default=None
                    )
                with col2:
                    selected_sources = st.multiselect(
                        "Filter by Source",
                        options=df['source_name'].unique(),
                        default=None
                    )
                with col3:
                    search_term = st.text_input("Search in titles", "")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    selected_sources = st.multiselect(
                        "Filter by Source",
                        options=df['source_name'].unique(),
                        default=None
                    )
                with col2:
                    search_term = st.text_input("Search in titles", "")
            
            # Apply filters
            filtered_df = df.copy()
            if mode == "Sales Triggers" and 'trigger_type' in df.columns and selected_triggers:
                filtered_df = filtered_df[filtered_df['trigger_type'].isin(selected_triggers)]
            if selected_sources:
                filtered_df = filtered_df[filtered_df['source_name'].isin(selected_sources)]
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['title'].str.contains(search_term, case=False, na=False)
                ]
            
            # Display articles
            st.write(f"Showing {len(filtered_df)} articles")
            
            for idx, article in filtered_df.iterrows():
                with st.expander(f"📄 {article['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Source:** {article['source_name']}")
                        st.markdown(f"**Author:** {article.get('author', 'N/A')}")
                        st.markdown(f"**Published:** {article['publishedAt'].strftime('%Y-%m-%d %H:%M')}")
                        
                        # Show trigger type if in Sales Triggers mode
                        if article.get('trigger_type'):
                            st.markdown(f"**🎯 Trigger Type:** {article['trigger_type']}")
                        
                        if article.get('description'):
                            st.markdown(f"**Description:** {article['description']}")
                        
                        st.markdown(f"[🔗 Read Full Article]({article['url']})")
                    
                    with col2:
                        if article.get('urlToImage'):
                            st.image(article['urlToImage'], use_container_width=True)
        
        with tab3:
            # Show header with region indicator
            col_header1, col_header2 = st.columns([2, 1])
            with col_header1:
                st.subheader("🔍 Select an Article to View Details")
            with col_header2:
                if mode == "Sales Triggers" and region and region != "Global (All)":
                    st.markdown(f"<div style='text-align: right; padding: 8px; background-color: #e3f2fd; border-radius: 5px; margin-top: 5px;'><strong>🌍 {region}</strong></div>", unsafe_allow_html=True)
            
            article_titles = [f"{i+1}. {a['title']}" for i, a in enumerate(articles)]
            selected_article_idx = st.selectbox(
                "Choose an article",
                range(len(article_titles)),
                format_func=lambda x: article_titles[x]
            )
            
            if selected_article_idx is not None:
                article = articles[selected_article_idx]
                
                # Display article image if available
                if article.get('urlToImage'):
                    st.image(article['urlToImage'], use_container_width=True)
                
                st.markdown(f"## {article['title']}")
                st.markdown(f"*By {article.get('author', 'Unknown')} | {article['source']['name']} | {article['publishedAt']}*")
                
                # Show trigger type if available
                if article.get('trigger_type'):
                    st.markdown(f"**🎯 Trigger Type:** {article['trigger_type']}")
                
                st.markdown("---")
                
                if article.get('description'):
                    st.markdown(f"### Description")
                    st.markdown(article['description'])
                
                if article.get('content'):
                    st.markdown(f"### Content")
                    st.markdown(article['content'])
                
                st.markdown(f"### [Read Full Article →]({article['url']})")
    else:
        st.info("No articles found. Try adjusting your search parameters.")
else:
    st.info("👈 Click 'Fetch Latest News' in the sidebar to load news articles")
    st.markdown("""
    ### Welcome to Patsnap Sales Trigger Dashboard! 
    
    This application helps your sales team identify opportunities by tracking:
    
    **� Sales Triggers Mode:**
    - 📈 **Funding Rounds** - Companies raising capital (Series A, B, venture funding)
    - 🤝 **Acquisitions & Partnerships** - M&A activity and strategic partnerships
    - � **Leadership Changes** - New CEO, CTO, and executive appointments
    - 🚀 **Product Launches** - New product and innovation announcements
    - � **Patents & Approvals** - Patent grants, regulatory, and FDA approvals
    - 💰 **IPOs & Public Listings** - Companies going public
    - 🌍 **Expansions** - Office openings and market entry
    
    **🔍 Custom Search Mode:**
    - Search for any topic or company
    - Track specific industries or competitors
    - Monitor custom keywords
    
    **� Features:**
    - Visualize trends and trigger distribution
    - Filter by trigger type, source, and keywords
    - Track publishing timeline
    - Export-ready data
    
    **Get started by selecting a mode and clicking 'Fetch Latest News' in the sidebar!**
    """)

