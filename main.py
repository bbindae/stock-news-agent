from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from dotenv import load_dotenv
from pathlib import Path
import uvicorn
import sys


if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"[System] .evn successfully loaded")
else:
    print(f"[Warning] .env file not fould")


from agent.stock_news_agent import create_stock_news_agent

app = FastAPI(
    title="Stock News Agent API",
    version="0.3",
    description="REST API for the Stock News Agent"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

stock_news_agent = create_stock_news_agent()

add_routes(
    app,
    stock_news_agent,
    path="/agent",
)


#===========================================================
# Custom POST endpoint
#===========================================================
class Payload(BaseModel):
    ticker: str

class StockNews(BaseModel):
    id: int
    title: str
    content: str
    content_kr: str
    summary: str
    summary_kr: str
    published_date: datetime
    url: str
    sentiment_label: str
    sentiment_score: float

class StockNewsList(BaseModel):
    ticker: str
    news_list: list[StockNews]

@app.post("/api/v1/stock-news/news", response_model=StockNewsList)
async def get_stock_news(payload: Payload):
    initial_input = {
        "ticker": payload.ticker
    }

    result = await stock_news_agent.ainvoke(initial_input)

    response = StockNewsList(
        ticker=payload.ticker,
        news_list=[
            StockNews(
                id=r.id,
                title=r.title,
                content=r.content,
                content_kr=r.content_kr,
                summary=r.summary,
                summary_kr=r.summary_kr,
                published_date=r.published_date,
                url=r.url,
                sentiment_label=r.sentiment_label,
                sentiment_score=r.sentiment_score
            ) for r in result['news_items'] 
        ]        
    )

    return response    


if __name__ == "__main__":
    print("🚀 [System] Launching LangServe API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8008)

    