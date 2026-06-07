from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
import uvicorn

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

if __name__ == "__main__":
    print("🚀 [System] Launching LangServe API Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)

    