# NewsAPI Information

## About NewsAPI

**Website:** https://newsapi.org

NewsAPI is a simple REST API for searching and retrieving live news articles from around the web.

## Free Tier Limitations

- **Free for development** (not for production)
- **100 requests per day** - No extra requests available
- **Articles have a 24-hour delay** - Live headlines not available on free tier
- **Search articles up to a month old** - Historical data limited to 1 month
- **CORS enabled for localhost** - Works for local development
- **No uptime SLA** - Service availability not guaranteed
- **Basic support** - Limited support for free accounts

## API Endpoints Used

### 1. `/v2/everything`
Search through millions of articles from various sources.
- Used in: `fetch_news_by_query()` and `fetch_sales_triggers()`
- Filters: query, date range, language, sort order

### 2. `/v2/top-headlines`
Get top headlines by country or category.
- Used in: `fetch_top_headlines()`
- Filters: country code, category

## Configuration

API key is stored in `config/.env`:
```
NEWS_API_KEY=your_api_key_here
```

Get your free API key at: https://newsapi.org/register

## Rate Limiting

With 100 requests per day, be mindful when using `fetch_sales_triggers()` as it makes **7 API calls** (one per trigger type).

**Daily request budget:**
- 7 requests = 1 full sales trigger fetch
- ~14 sales trigger fetches per day maximum
- Mix with custom searches as needed
