from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Literal
from agent.utils import get_ollama_llm
from agent.state import StockNewsState

class NewAnalysis(BaseModel):
    """Structured NewsOutput model schema utilized by summarize_news node"""
    id: int = Field(description="the article id")
    title: str = Field(description="A title of the article")
    content_kr: str = Field(description="A concise Korean translation of the content")
    summary: str = Field(description="A concise summary of the article in 2-3 sentences (English)")
    summary_kr: str = Field(description="Korean translation of the summary")    
    sentiment_label: Literal["Positive", "Negative", "Neutral"] = Field(description="Sentiment analysis result - must of one of: 'Positive', 'Negative', 'Neutral'")
    sentiment_score: float = Field(description="Sentiment confidence score between -1.0 (most negative) and 1.0 (most positive)")

class NewsAnalysisList(BaseModel):
    """Structured NewsOutput mode schema utilized by summarize_news node"""
    articles: List[NewAnalysis]


def summarize_news(state: StockNewsState):
    """Summarize 3 news and add sentiment and embedding"""


    news_content = "\n\n".join([f"Article {n.id}: \nTitle: {n.title}\nContent: {n.raw_content}\nURL:{n.url}\nDate: {n.published_date}"
                                for n in state.news_items
                                ]).replace("{","{{").replace("}","}}")  
    
    prompt = f"""
    You are a financial news analyst. Analyze the following news articles about {state.ticker} ({state.company_name})

    For each article, provide:

    1. **id**: the article id
    2. **title**: A title of the article
    3. **content_kr**: A concise Korean translation of the content
    4. **summary**: A concise summary of the article in 4-5 sentences (English)
    5. **summary_kr**: Korean translation of the summary    
    6. **sentiment_label**: Sentiment analysis result - must of one of: 'Positive', 'Negative', 'Neutral'
    7. **sentiment_score**: Sentiment confidence score between -1.0 (most negative) and 1.0 (most positive)

    News Articles:
    {news_content}   

    Return a JSON object with an "articles" key containing the list of results.
    """

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a financial news analyst specializing in stock market analysis."),
        ("user", prompt)
    ])

      
    llm = get_ollama_llm()
    llm_with_structure = llm.with_structured_output(NewsAnalysisList)

    chain = prompt_template | llm_with_structure

    response = chain.invoke({
        "ticker": state.ticker,
        "company_name": state.company_name,
        "news_content": news_content
    })
   
    return {"news_items": response.articles}
