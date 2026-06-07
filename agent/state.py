from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Annotated


class NewsItems(BaseModel):
    """Structured data model for an individual news item processed within the agent."""
    id: int
    title: str
    content: str
    content_kr: str    
    raw_content: str
    summary: str
    summary_kr: str
    published_date: Optional[datetime]
    url: str
    sentiment_label: str
    sentiment_score: float

def merge_news_items(existing: list[NewsItems], new: list) -> list[NewsItems]:
    """(reducer) Merge new news items into existing list, updating fields if item id already exists."""
    existing_map = {item.id: item for item in existing}
    
    for new_item in new:
        new_dict = new_item.model_dump()

        if new_dict.get('id') in existing_map:            
            existing_map[new_dict['id']] = existing_map[new_dict['id']].model_copy(
                update={k: v for k, v in new_dict.items() if v is not None}
            )
        else:
            existing_map[new_dict['id']] = NewsItems(**new_dict)
    
    return list(existing_map.values())

class StockNewsState(BaseModel):
    """The global state object maintained throughout the LangGraph workflow
    for processing stock-specific news and analytic data.
    """
    ticker: str = Field(description="Ticker symbol. e.g. SNDK, APPL")
    company_name: Optional[str] = Field(default=None, description="The company name from the ticker symbol. e.g. Apple, inc.")
    sector: Optional[str] = Field(default=None, description="The broad economic sector the company belongs to. e.g. Technology, Healthcare, Financials, Energy")
    industry: Optional[str] = Field(default=None, description="The specific industry within the sector. e.g. Semiconductors, Software, Biotechnology, Oil & Gas")
    news_items: Annotated[Optional[list[NewsItems]], merge_news_items] = Field(default_factory=list)


