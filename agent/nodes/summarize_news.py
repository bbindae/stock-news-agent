from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Literal
from agent.utils import get_ollama_llm
from agent.state import StockNewsState

class NewAnalysis(BaseModel):
    """Structured NewsOutput model schema utilized by summarize_news node"""
    id: int = Field(description="the article id")
    title: str = Field(description="A title of the article")
    content_kr: str = Field(description="A concise Korean translation of the 'Content' field")
    summary: str = Field(description="A concise summary of the article in 4-5 sentences (English) based strictly on the 'Content' field")
    summary_kr: str = Field(description="A concise Korean translation of the 'summary' generated above. It MUST be based entirely and exclusively on the actual facts provided in the 'Content' field. Do not invent any facts or mention that information is missing.")    
    sentiment_label: Literal["Positive", "Negative", "Neutral"] = Field(description="Sentiment analysis result - must of one of: 'Positive', 'Negative', 'Neutral'")
    sentiment_score: float = Field(description="Sentiment confidence score between -1.0 (most negative) and 1.0 (most positive)")

class NewsAnalysisList(BaseModel):
    """Structured NewsOutput mode schema utilized by summarize_news node"""
    articles: List[NewAnalysis]


def summarize_news(state: StockNewsState):
    """Summarize 3 news and add sentiment and embedding"""
    
    processed_items = []
    for n in state.news_items:
        clean_content = str(n.raw_content).replace("\\", " ")
        clean_title = str(n.title).replace("\\", " ")
               
        item_text = (
            f"Article ID: {n.id}\n"
            f"Title: {clean_title}\n"            
            f"Content: {clean_content}\n"
            f"URL: {n.url}\n"
            f"Date: {n.published_date}"
        )
        processed_items.append(item_text)

    news_content = "\n\n".join(processed_items)
    
    prompt = f"""
    You are a financial news analyst. Analyze the following news articles about {state.ticker} ({state.company_name}).

    For each article, provide:
    - id: the article id
    - title: The title of the article
    - content_kr: A concise Korean translation of the 'Content' field.
    - summary: A concise summary of the article in 4-5 sentences (English) based strictly on the 'Content' field.
    - summary_kr: A concise Korean translation of the 'summary' generated above. It MUST be based entirely and exclusively on the actual facts provided in the 'Content' field. Do not invent any facts or mention that information is missing.
    - sentiment_label: Sentiment analysis result - must be one of: 'Positive', 'Negative', 'Neutral'
    - sentiment_score: Sentiment confidence score between -1.0 (most negative) and 1.0 (most positive)

    News Articles:
    {news_content}   
    
    Return a JSON object with an "articles" key containing the list of results.

    [Crucial Guidelines]:
    - Even if {state.ticker} or {state.company_name} is not explicitly mentioned in the text, analyze how the overall market trends, macroeconomics, or industry competitors (e.g., cruising/travel sector) mentioned in the news might indirectly affect {state.ticker}.
    - **CRITICAL**: 'summary_kr' and 'content_kr' must be generated using ONLY the text provided inside the 'Content' field of each article. Always extract value and fill the structure.
    """
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a financial news analyst specializing in stock market analysis."),
        ("user", prompt)
    ])

      
    llm = get_ollama_llm()
    llm_with_structure = llm.with_structured_output(NewsAnalysisList, method="json_mode")

    chain = prompt_template | llm_with_structure

    response = chain.invoke({
        "ticker": state.ticker,
        "company_name": state.company_name,
        "news_content": news_content
    })
   
    return {"news_items": response.articles}
