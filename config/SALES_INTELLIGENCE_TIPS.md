# Sales Intelligence Improvement Tips

## Current Issues Solved
✅ Added business context words (company, startup, firm, corporation)
✅ Added action verbs (granted, filed, launches, secures, announces)
✅ Improved query structure to filter out academic/government content

## Additional Improvements to Consider

### 1. **Filter Out Irrelevant Sources** (Post-Processing)
Add source filtering in your dashboard to exclude:
- Academic journals (.edu domains, journal sites)
- Government sites (.gov, .gov.uk)
- Wikipedia, generic news aggregators
- Personal blogs

**Implementation:** Add a source blacklist in `app.py`:
```python
EXCLUDED_SOURCES = [
    'plos.org', 'arxiv.org', 'ieee.org', 'springer.com',
    '.gov', '.gov.uk', '.edu',
    'wikipedia.org', 'reddit.com'
]

# Filter articles
filtered_articles = [
    article for article in articles 
    if not any(excluded in article.get('url', '').lower() 
              for excluded in EXCLUDED_SOURCES)
]
```

### 2. **Prioritize Business News Sources**
Focus on sources that cover business/tech news:
- TechCrunch, VentureBeat, The Information
- Business Insider, Bloomberg, Reuters
- Industry-specific publications (BioSpace for pharma, TechNode for Asia tech)

**Implementation:** Add source scoring or preferred sources filter

### 3. **Add Company Name Extraction**
Extract and highlight company names from articles:
```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp(article['description'])
companies = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
```

### 4. **Enrich with Additional Context**
- Check if company has a website (filter out non-companies)
- Add company size/industry classification
- Show company LinkedIn or Crunchbase profile link
- Display funding history if available

### 5. **Add Negative Keywords** (Exclude Noise)
```python
# Example for Patent query
'(company OR startup) AND (patent granted) AND Singapore NOT (journal OR research OR academic OR university)'
```

### 6. **Industry-Specific Triggers**
Since you're Patsnap (IP/innovation focus), consider:
- R&D investment announcements
- Technology partnerships
- Innovation lab openings
- Patent litigation news (shows active IP portfolio)

### 7. **Quality Scoring System**
Score articles based on:
- Source credibility (business news = high, academic = low)
- Recency (fresher = better for sales)
- Company mentions (named companies = higher relevance)
- Region relevance (exact match > nearby region)

### 8. **Upgrade NewsAPI** ⚠️
**Current Limitation:** NewsAPI free tier only searches last 30 days with 24hr delay

**Options:**
- **NewsAPI.ai** ($49/mo) - Better business news coverage, 3 years history
- **Aylien News API** - Better entity extraction, industry classification
- **Finlight** - Specialized in business/financial news
- **Custom web scraping** - TechCrunch, Crunchbase, PitchBook RSS feeds

### 9. **Add Confidence/Relevance Indicators**
Show in dashboard:
- 🟢 High confidence (company name + action + location all present)
- 🟡 Medium confidence (2 of 3 present)
- 🔴 Low confidence (generic match)

### 10. **Sales Team Feedback Loop**
Add UI elements:
- ⭐ "Mark as relevant" button
- 👎 "Not useful" button
- Collect feedback to refine queries over time

## Query Best Practices

### Good Query Structure:
```
(entity type) AND (trigger event) AND (action verb) [AND region]
```

### Examples:
**Good:** `(startup OR company) AND patent AND (granted OR filed) AND Singapore`
- Focuses on companies taking action

**Bad:** `patent AND Singapore`
- Too broad, matches academic/government content

### Action Verbs Library:
- **Funding:** raises, secures, closes, announces, receives
- **Expansion:** opens, launches, expands, enters, establishes
- **Partnership:** partners, collaborates, teams up, joins forces
- **Product:** launches, unveils, introduces, releases, announces
- **Leadership:** appoints, hires, names, promotes, welcomes

## Monitoring & Maintenance

### Weekly Tasks:
1. Review false positives (irrelevant articles)
2. Check for missed opportunities (manual search comparison)
3. Update excluded sources list
4. Refine queries based on team feedback

### Monthly Tasks:
1. Analyze which triggers generate most leads
2. Review conversion rates per trigger type
3. Update industry-specific keywords
4. Consider upgrading API if hitting rate limits

## Quick Wins for Next Sprint:

1. ✅ **Done:** Add business context to queries
2. **Next:** Add source blacklist filtering
3. **Next:** Create company name extraction
4. **Next:** Add relevance confidence score
5. **Next:** Set up feedback collection system

---

**Remember:** The goal is **qualified leads**, not just article count. 
Better to have 10 highly relevant articles than 100 noisy ones! 🎯
