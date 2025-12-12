# Sales workflow improvement initiative


### Patsnap Sales Trigger Dashboard
Track sales opportunities by monitoring news for companies with patent activity, product launches, and expansions.

## Setup

1. Install dependencies:
   ```bash
   make install
   ```

2. Add your NewsAPI key to `config/.env`:
    Get API key from https://newsapi.org
   ```
   NEWS_API_KEY=your_api_key_here
   ```

3. Run the dashboard:
   ```bash
   make run-app
   ```

## Usage

- Open `http://localhost:8501` in your browser
- Click **"Fetch Latest News"** to load articles
- View analytics and browse relevant companies