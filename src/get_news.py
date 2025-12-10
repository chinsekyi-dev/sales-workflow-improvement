import json
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from newsapi import NewsApiClient

# Load environment variables from config/.env
config_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', '.env')
load_dotenv(dotenv_path=config_env_path)
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))


def fetch_news_by_query(query="Apple", days_back=30, sort_by="popularity"):
    """
    Fetch news articles from NewsAPI by search query
    Search for news articles that mention a specific topic or keyword
    
    Args:
        query: Search query string
        days_back: Number of days to look back
        sort_by: Sort order (popularity, publishedAt, relevancy)
    """
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        response = newsapi.get_everything(
            q=query,
            from_param=from_date,
            to=to_date,
            sort_by=sort_by,
            language='en'
        )
        return response
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None


def fetch_top_headlines(country="sg", category=None):
    """
    Fetch top headlines from NewsAPI
    Get the current top headlines for a country or category
    
    Args:
        country: Country code (e.g., 'sg', 'us', 'gb', 'cn', 'au', 'in', etc.)
        category: Category (business, technology, science, health, sports, entertainment, etc.)
    """
    try:
        response = newsapi.get_top_headlines(
            country=country,
            category=category
        )
        return response
    except Exception as e:
        print(f"Error fetching news: {e}")
        return None


def fetch_sales_triggers(days_back=7, sort_by="publishedAt", region=None):
    """
    Fetch sales trigger news for Patsnap's sales team
    Searches for funding, acquisitions, leadership changes, product launches, etc.
    
    Args:
        days_back: Number of days to look back
        sort_by: Sort order (publishedAt recommended for timely triggers)
        region: Optional region filter (e.g., 'Singapore', 'Asia', 'United States')
    
    Returns:
        dict: Combined news data with articles from all sales trigger queries
    """
    # Sales trigger queries
    # TODO: Need to be improved by Sales team feedback
    queries = [
        "patent OR IP OR intellectual property",
        "funding round OR Series A OR Series B OR venture capital",
        "acquisition OR merger OR partnership",
        "CEO appointment OR CTO hire OR leadership change",
        "product launch OR new product OR innovation announcement",
        "patent granted OR regulatory approval OR FDA approval",
        "IPO OR going public OR stock listing",
        "expansion OR opening office OR market entry"
    ]
    
    # Add region filter if specified
    if region:
        queries = [f"({query}) AND {region}" for query in queries]
    
    all_articles = []
    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")
    
    for query in queries:
        try:
            response = newsapi.get_everything(
                q=query,
                from_param=from_date,
                to=to_date,
                sort_by=sort_by,
                language='en'
            )
            
            if response.get('status') == 'ok' and response.get('articles'):
                # Add source query tag to each article
                for article in response['articles']:
                    article['trigger_type'] = query
                all_articles.extend(response['articles'])
                print(f"Found {len(response['articles'])} articles for: {query}")
        except Exception as e:
            print(f"Error fetching news for '{query}': {e}")
            continue
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article.get('url') not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    return {
        'status': 'ok',
        'totalResults': len(unique_articles),
        'articles': unique_articles
    }
    

def save_news_to_file(news_data, filename="news_data.json"):
    """Save news data to a JSON file in the data directory"""
    if news_data:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "w") as f:
            json.dump(news_data, f, indent=2)
        print(f"News data saved to {filepath}")
        return filepath
    return None


if __name__ == "__main__":
    print("Fetching sales trigger news for Patsnap (Singapore focus)...")
    print("=" * 50)
    
    # Fetch sales triggers for Singapore
    news = fetch_sales_triggers(days_back=7, sort_by="publishedAt", region="Singapore")
    
    if news:
        print(f"\nStatus: {news.get('status')}")
        print(f"Total Unique Articles: {news.get('totalResults')}")
        print(f"Articles Retrieved: {len(news.get('articles', []))}")
        
        # Save to file
        save_news_to_file(news, filename="sales_triggers.json")
        
        # Print first 3 articles as examples
        if news.get('articles'):
            print("\n" + "=" * 50)
            print("Sample Sales Trigger Articles:")
            print("=" * 50)
            for i, article in enumerate(news['articles'][:3], 1):
                print(f"\n{i}. {article.get('title')}")
                print(f"   Source: {article.get('source', {}).get('name')}")
                print(f"   Published: {article.get('publishedAt')}")
                print(f"   Trigger Type: {article.get('trigger_type')}")
                print(f"   URL: {article.get('url')}")
