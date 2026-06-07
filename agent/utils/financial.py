from typing import Optional 
from pydantic import BaseModel
from datetime import datetime, timezone
import yfinance as yf
import re
import pytz
from tavily import TavilyClient

def get_company_info(ticker_symbol: str) -> dict:
    """
    By given ticker_symbol, return the company name.
    If the company name is not found, return Ticker itself
    """

    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        info = ticker.info

        company_name = info.get('longName') or info.get('shortName') or ticker_symbol.upper()
        sector = info.get('sector','')
        industry = info.get('industry','')

        return {"company_name": company_name, "sector": sector, "industry": industry}     
    
    except Exception as e:
        return {"company_name": ticker_symbol.upper(), "sector":None, "industry": None}
    

def is_relavant_news(ticker: str, company_name: str, title: str, content: str) -> bool:
    """determine wether the given news is relavant or not"""

    text = f"{title} {content}".lower()
    ticker_lower = ticker.lower()
    company_name_lower = company_name.lower()
    
    # ticker matching
    ticker_pattern = r'\b' + re.escape(ticker_lower) + r'\b'
    has_ticker = bool(re.search(ticker_pattern, text))

    if has_ticker:
        return True
    
    # comany_name matching
    has_company = company_name_lower in text

    if has_company:
        return True
    
    # company alias matching
    index = company_name_lower.replace('.','').replace(',','').find(' ')
    if index != -1:
        company_alias = company_name_lower[:index]
    else:
        company_alias = company_name_lower
    
    has_company_alias = company_alias in text
    if has_company_alias:
        return True
    
    return False

def parse_published_date(date_str: Optional[str]) -> Optional[datetime]:
    """Convert string datatime to datetime"""

    if not date_str:
        return None
    
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",       # 2025-01-15T10:30:00Z
        "%Y-%m-%dT%H:%M:%S%z",      # 2025-01-15T10:30:00+00:00
        "%Y-%m-%d %H:%M:%S",        # 2025-01-15 10:30:00
        "%Y-%m-%d",                 # 2025-01-15
        "%a, %d %b %Y %H:%M:%S %z", # Mon, 15 Jan 2025 10:30:00 +0000
        "%a, %d %b %Y %H:%M:%S %Z"  # Tue, 02 Jun 2026 20:07:00 GMT
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    
    #None of format is succeded
    return None

def to_pst(date_to_convert:Optional[datetime]) -> str:
    if not date_to_convert:
        return None
        
    PST = pytz.timezone("America/Los_Angeles")
    return date_to_convert.astimezone(PST).strftime("%a, %d %b %Y %H:%M:%S %Z")


class StockNewsItem(BaseModel):
    """a model class returned by search_stock_news function"""
    id: int
    ticker: str
    company_name: str
    title: str
    content: str
    raw_content: str
    url: str
    published_date: Optional[datetime] = None

# Domain preset
DOMAIN_PRESETS = {
    "general": [
        "reuters.com",
        "cnbc.com",
        "finance.yahoo.com",
        "marketwatch.com",
        "bloomberg.com",
    ],
    "deep_analysis": [
        "seekingalpha.com",
        "barrons.com",
        "wsj.com",
        "morningstar.com",
        "ft.com",
    ],
    "realtime": [
        "cnbc.com",
        "benzinga.com",
        "finance.yahoo.com",
        "marketwatch.com",
        "thestreet.com",
    ],
    "mix_and_match":[
        "bloomberg.com",
        "reuters.com",
        "wsj.com",
        "ft.com",
        "cnbc.com",
        "finance.yahoo.com"
    ],
    "best_free_domains" :[
    "finance.yahoo.com",   
    "reuters.com",         
    "cnbc.com",            
    "marketwatch.com",     
    "benzinga.com",        
    ]
}

def search_stock_news(ticker: str, company_name: str, max_results: int) -> list[StockNewsItem]:
    """return the most recent news limited by given ticker and company name.
    Also, it filters most relavant news. 
    """ 
    tavily_client = TavilyClient();
    domains = DOMAIN_PRESETS["best_free_domains"]
    query = f'{company_name} ({ticker}) latest stock news'
    max_news_from_tavily = 10

    response = tavily_client.search(query=query, 
                                    topic="news", 
                                    max_results=max_news_from_tavily,
                                    search_depth="basic",
                                    include_raw_content="markdown",
                                    days = 3,
                                    include_domains=domains)
    
    #-- Filter most relavant top 3 news 
    sorted_results = sorted(
        response.get("results", []),
        key=lambda x: x.get("score", 0),
        reverse=True)
    
    filtered_news = []
    filtered_set = set()

    for idx, r in enumerate(sorted_results):
        if len(filtered_news) >= max_results:
                break
        
        if is_relavant_news(ticker, company_name, r['title'], r['content']):
            filtered_news.append(
                StockNewsItem(
                id = idx,
                ticker=ticker,
                company_name=company_name,
                title=r['title'],
                content=r['content'],
                raw_content=r['raw_content'],
                url=r['url'],
                published_date=parse_published_date(r['published_date'])              
                )
            )
            filtered_set.add(idx)
    
    if len(filtered_news) < max_results:
        sorted_results = [r for i, r in enumerate(sorted_results) if i not in filtered_set]
        id = len(filtered_news)
        for idx, r in enumerate(sorted_results):
            if len(filtered_news) >= max_results:
                break

            filtered_news.append(
                StockNewsItem(
                id = idx + id,
                ticker=ticker,
                company_name=company_name,
                title=r['title'],
                content=r['content'],
                raw_content=r['raw_content'],
                url=r['url'],
                published_date=parse_published_date(r['published_date'])              
                )
            )   
   
    return filtered_news