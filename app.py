import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.get_news import fetch_news_by_query, save_news_to_file

# Page configuration
st.set_page_config(
    page_title="Patsnap Sales Trigger Dashboard",
    page_icon="🎯",
    layout="wide"
)

# Helper function to deduplicate articles
def deduplicate_articles(articles):
    """Remove duplicate articles based on URL"""
    seen_urls = set()
    unique = []
    for article in articles:
        url = article.get('url')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
    return unique

# Default trigger queries configuration
DEFAULT_TRIGGERS = {
    "Patent & IP": "patent granted OR IP OR intellectual property",
 #   "Funding": "funding round OR Series A OR Series B OR venture capital",
 #   "Acquisition": "acquisition OR merger OR partnership",
 #   "👔 Leadership": "CEO appointment OR CTO hire OR leadership change",
    "Product Launch": "product launch OR new product OR innovation announcement",
  #  "📜 Regulatory": "regulatory approval OR FDA approval OR certification",
   # "IPO": "IPO OR going public OR stock listing",
    "Expansion": "expansion OR opening office OR market entry"
}

st.title("🎯 Patsnap Sales Trigger Dashboard")
st.markdown("*Identify sales opportunities through news intelligence*")

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    
    # Mode selection
    mode = st.radio("Mode", ["Sales Triggers", "Custom Search"], index=0)
    
    st.markdown("---")
    st.markdown("### Search Criteria")
    
    # Common settings for both modes
    days_back = st.slider("Days to Look Back", min_value=1, max_value=30, value=7, 
                          help="How many days of historical news to search")
    
    sort_by = st.selectbox("Sort By", 
                          ["publishedAt", "relevancy", "popularity"],
                          help="publishedAt: newest first | relevancy: most relevant | popularity: most popular sources")
    
    region = st.selectbox(
        "Region Filter",
        ["None (Global)", "Singapore", "Asia", "United States", "Europe", "China", "India", "Japan"],
        index=1,  # Default to Singapore
        help="Filter news by region. 'None' searches globally."
    )
    
    st.markdown("---")
    
    if mode == "Sales Triggers":
        st.markdown("### 🎯 Sales Trigger Queries")
        st.markdown("*Customize search queries for each trigger type:*")
        
        # Dynamically create expanders and collect queries
        custom_queries = []
        for trigger_name, default_query in DEFAULT_TRIGGERS.items():
            with st.expander(trigger_name, expanded=False):
                query_text = st.text_area(
                    f"{trigger_name} Query",
                    value=default_query,
                    help=f"Search query for {trigger_name}",
                    key=trigger_name
                )
                if query_text.strip():
                    custom_queries.append((trigger_name, query_text.strip()))
        
    else:  # Custom Search mode
        st.markdown("### Custom Search Query")
        query = st.text_area(
            "Search Query",
            value="Apple OR Google OR Microsoft",
            help="Enter your custom search query. Use AND, OR, NOT for boolean search. Use quotes for exact phrases.",
            height=100
        )
        
        st.markdown("---")
        st.markdown("**Search Tips:**")
        st.markdown("""
        - Use `"exact phrase"` for exact match
        - Use `AND`, `OR`, `NOT` for boolean logic
        - Use `+must` for required words
        - Use `-exclude` to exclude words
        - Example: `crypto AND (ethereum OR bitcoin) NOT scam`
        """)
    
    fetch_button = st.button("🔄 Fetch Latest News", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### Quick Stats")

# Load or fetch news data
data_file = "data/sales_triggers.json" if mode == "Sales Triggers" else "data/news_data.json"
news_data = None

if fetch_button:
    with st.spinner("Fetching news articles..."):
        region_filter = None if region == "None (Global)" else region
        
        try:
            if mode == "Sales Triggers":
                # Fetch news for each custom query
                all_articles = []
                progress_bar = st.progress(0)
                
                for i, (trigger_type, query_text) in enumerate(custom_queries):
                    # Add region filter if specified
                    search_query = f"({query_text}) AND {region_filter}" if region_filter else query_text
                    
                    result = fetch_news_by_query(
                        query=search_query,
                        days_back=days_back,
                        sort_by=sort_by
                    )
                    
                    if result and result.get("status") == "ok":
                        articles = result.get("articles", [])
                        # Add trigger type to each article
                        for article in articles:
                            article['trigger_type'] = trigger_type
                        all_articles.extend(articles)
                    
                    progress_bar.progress((i + 1) / len(custom_queries))
                
                # Remove duplicates
                unique_articles = deduplicate_articles(all_articles)
                
                # Save results
                if unique_articles:
                    news_data = {
                        "status": "ok",
                        "totalResults": len(unique_articles),
                        "articles": unique_articles
                    }
                    save_news_to_file(news_data, filename="sales_triggers.json")
                    st.success(f"Fetched {len(unique_articles)} unique articles from {len(all_articles)} total!")
                else:
                    st.warning("No articles found. Try adjusting your queries or criteria.")
                    
            else:
                # Custom search mode
                search_query = f"({query}) AND {region_filter}" if region_filter else query
                news_data = fetch_news_by_query(query=search_query, days_back=days_back, sort_by=sort_by)
                
                if news_data and news_data.get("status") == "ok":
                    save_news_to_file(news_data)
                    st.success(f"Found {len(news_data.get('articles', []))} articles!")
                else:
                    st.warning("No articles found. Try different search terms.")
        
        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")
            st.info("Tip: You may have hit the API rate limit (100 requests/day). Try again later.")

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
    
    # Compact filter summary in an expander
    with st.expander("Active Filters & Queries", expanded=False):
        # Show filters in a compact single line
        region_display = region if region != "None (Global)" else "Global"
        st.markdown(f"**Mode:** {mode} | **Time Period:** Last {days_back} days | **Region:** {region_display} | **Sort By:** {sort_by}")
        
        # Show active queries summary if in Sales Triggers mode
        if mode == "Sales Triggers":
            st.markdown("**Active Triggers:**")
            trigger_names = [trigger_type for trigger_type, _ in custom_queries]
            st.markdown(", ".join([f"✓ {name}" for name in trigger_names]))
        else:
            st.markdown("**Search Query:**")
            display_query = f"({query}) AND {region}" if region != "None (Global)" else query
            st.code(display_query, language="text")
    
    
    # Main content
    if articles:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(articles)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df['date'] = df['publishedAt'].dt.date
        df['source_name'] = df['source'].apply(lambda x: x.get('name', 'Unknown'))
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Analytics", "Articles List", "Article Details"])
        
        with tab1:
            # Show trigger type distribution if in Sales Triggers mode
            if mode == "Sales Triggers" and 'trigger_type' in df.columns:
                st.subheader("Sales Trigger Distribution")
                
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
                st.subheader("Articles Over Time")
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
                st.subheader("Top Sources")
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
            st.subheader("Most Active Authors")
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
            st.subheader("All Articles")
            
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
                with st.expander(f"{article['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Source:** {article['source_name']}")
                        st.markdown(f"**Author:** {article.get('author', 'N/A')}")
                        st.markdown(f"**Published:** {article['publishedAt'].strftime('%Y-%m-%d %H:%M')}")
                        
                        # Show trigger type if in Sales Triggers mode
                        if article.get('trigger_type'):
                            st.markdown(f"**Trigger Type:** {article['trigger_type']}")
                        
                        if article.get('description'):
                            st.markdown(f"**Description:** {article['description']}")
                        
                        st.markdown(f"[Read Full Article]({article['url']})")
                    
                    with col2:
                        if article.get('urlToImage'):
                            st.image(article['urlToImage'], use_container_width=True)
        
        with tab3:
            st.subheader("Select an Article to View Details")
            
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
                    st.markdown(f"**Trigger Type:** {article['trigger_type']}")
                
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
    st.info("Click 'Fetch Latest News' in the sidebar to load news articles")
    st.markdown("""
    ### Welcome to Patsnap Sales Trigger Dashboard! 
    
    This application helps your sales team identify opportunities by tracking:
    
    **Sales Triggers Mode:**
    - **Funding Rounds** - Companies raising capital (Series A, B, venture funding)
    - **Acquisitions & Partnerships** - M&A activity and strategic partnerships
    - **Leadership Changes** - New CEO, CTO, and executive appointments
    - **Product Launches** - New product and innovation announcements
    - **Patents & Approvals** - Patent grants, regulatory, and FDA approvals
    - **IPOs & Public Listings** - Companies going public
    - **Expansions** - Office openings and market entry
    
    **Custom Search Mode:**
    - Search for any topic or company
    - Track specific industries or competitors
    - Monitor custom keywords
    
    **Features:**
    - Visualize trends and trigger distribution
    - Filter by trigger type, source, and keywords
    - Track publishing timeline
    - Export-ready data
    
    **Get started by selecting a mode and clicking 'Fetch Latest News' in the sidebar!**
    """)

