from agent.state import StockNewsState, NewsItems
from agent.utils import get_company_info, search_stock_news

def search_news(state: StockNewsState):
    """Search Top 3 news by stock symbo e.g. SNDK"""

    company_info = get_company_info(state.ticker)
    stock_news = search_stock_news(state.ticker, company_info['company_name'], 3)

    news_items = [NewsItems(
            id=idx,
            title=n.title,
            content=n.content,
            content_kr='',
            raw_content=n.raw_content,
            summary='',
            summary_kr='',
            published_date=n.published_date,
            url=n.url,
            sentiment_label='',
            sentiment_score=0.0
            ) for idx, n in enumerate(stock_news)]                  
    
    return {"company_name": company_info['company_name'], 
            "sector": company_info['sector'], 
            "industry": company_info['industry'], 
            "news_items":news_items}
