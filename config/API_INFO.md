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

**How Search Works:**
- By default, searches **all fields**: title, description, AND content
- Can be restricted using `searchIn` parameter to specific fields
- Supports advanced search operators:
  - Exact phrases: `"funding round"`
  - Must include: `+bitcoin`
  - Must exclude: `-bitcoin`
  - Boolean logic: `crypto AND (ethereum OR litecoin) NOT bitcoin`

**What Gets Searched:**
- **Title** - Article headline
- **Description** - Article snippet/summary
- **Content** - Full article body (truncated to 200 chars in response)

**Sort Options:**
- `relevancy` - Most closely related to query first
- `popularity` - Articles from popular sources first
- `publishedAt` - Newest articles first (default)

### 2. `/v2/top-headlines`
Get top headlines by country or category.
- Used in: `fetch_top_headlines()`
- Filters: country code, category
- Does NOT use query-based search


## Rate Limiting

With 100 requests per day, be mindful when using `fetch_sales_triggers()` as it makes **7 API calls** (one per trigger type).

**Daily request budget:**
- 7 requests = 1 full sales trigger fetch
- ~14 sales trigger fetches per day maximum
- Mix with custom searches as needed

### Pros:
- ✅ Large database of 80,000+ global news sources
- ✅ Simple REST API, easy to integrate
- ✅ Good documentation and Python client library
- ✅ Free tier available (100 requests/day)
- ✅ Boolean search operators (AND, OR, NOT)
- ✅ Filter by date, source, language, country

### Cons:
- ❌ **24-hour delay on articles** (free tier)
- ❌ Only 1 month of historical data
- ❌ **100 requests/day limit** (very restrictive)
- ❌ Headlines and descriptions only (no full content on free tier)
- ❌ No sentiment analysis
- ❌ No entity recognition
- ❌ Basic search only (title, description, content)
