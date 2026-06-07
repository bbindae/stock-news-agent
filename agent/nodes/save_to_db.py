import logging
from agent.utils import supabase
from agent.state import StockNewsState

logger = logging.getLogger(__name__)

def save_to_db(state: StockNewsState):
    """
    persists ticker info and news items to Supabase.
    
    Steps:
        1. Upsert ticker into `tickers` (insert if not exists, skip if already there).
        2. Insert each NewsItem into `stock_news`.
    
    Returns:
        Unchanged state (pass-through node).
    """
    symbol = state.ticker.upper()

    existing = (
        supabase.table("tickers")
        .select("id, company_name, sector, industry")
        .eq("symbol", symbol)
        .maybe_single()
        .execute()
    )

    ticker_id = None

    # Insert
    if existing is None:
        result = (
            supabase.table("tickers")
            .insert({
                "symbol":   symbol,
                "company_name": state.company_name,
                "sector":   state.sector,
                "industry": state.industry    
            })
            .select("id")
            .execute()
        )

        print("result:", result)

        ticker_id = result.data[0]["id"]
        logger.info(f"Inserted new ticker '{symbol}' -> id={ticker_id}")
    else: #Update
        ticker_id = existing.data["id"]
        changes = {}

        if state.company_name != existing.data["company_name"]:
            changes["company_name"] = state.company_name
        if state.sector != existing.data["sector"]:
            changes["sector"] = state.sector
        if state.industry != existing.data["industry"]:
            changes["industry"] = state.industry
        
        if changes:
            supabase.table("tickers").update(changes).eq("id", ticker_id).execute()
            logger.info(f"Updated ticker '{symbol}' -> {changes}")


    # Insert News
    if not state.news_items:
        return state
    
    rows = []
    for item in state.news_items:
        rows.append({
            "ticker_id":    ticker_id,
            "title":        item.title,
            "content":      item.content,
            "content_kr":   item.content_kr,
            "raw_content":  item.raw_content,
            "source_url":          item.url,
            "published_at": item.published_date.isoformat() if item.published_date else None,
            "summary":      item.summary,
            "summary_kr":   item.summary_kr,
            "sentiment":    item.sentiment_label.lower(),
            "sentiment_score": item.sentiment_score
        })
    
    if not rows:
        return state
    
    news_result = (
        supabase.table("stock_news")
        .insert(rows)
        .select("id")
        .execute()
    )

    logger.info(f"Inserted {len(news_result.data)} news item(s) for ticker '{state.ticker}'")
    
    return state