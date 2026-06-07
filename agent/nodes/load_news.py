from datetime import datetime
from zoneinfo import ZoneInfo
from agent.state import StockNewsState, NewsItems
from agent.utils import supabase
from agent.utils import get_company_info

def load_news(state: StockNewsState):
    """Load news from data base if news exist; fill the state"""   

    pacific = ZoneInfo("America/Los_Angeles")

    now_pacific = datetime.now(pacific)
    start_of_day = now_pacific.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now_pacific.replace(hour=23, minute=59, second=59, microsecond=999999)

    start_utc = start_of_day.astimezone(ZoneInfo("UTC")).isoformat()
    end_utc = end_of_day.astimezone(ZoneInfo("UTC")).isoformat()

    result = (
        supabase.table("stock_news")
        .select("*, tickers!inner(symbol, is_active)")
        .eq("tickers.symbol", state.ticker.upper())
        .eq("tickers.is_active", True)
        .gte("created_at", start_utc)
        .lte("created_at", end_utc)        
        .order("published_at", desc=True)
        .execute()
    )
    
    if not result or not result.data:
        return state
    

    company_info = get_company_info(state.ticker)

    news_items = [
        NewsItems(
            id= idx+1,
            title= row["title"],
            content= row["content"],
            content_kr = row["content_kr"],
            raw_content= row["raw_content"],
            published_date= datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
            summary=        row["summary"],
            summary_kr=     row["summary_kr"],
            sentiment_label=row["sentiment"],
            url=            row["source_url"],
            sentiment_score=row["sentiment_score"]
        )
        for idx, row in enumerate(result.data)
    ]

    return {"company_name": company_info["company_name"], 
                "industry": company_info["industry"],
                "sector": company_info["sector"],
                "news_items": news_items}