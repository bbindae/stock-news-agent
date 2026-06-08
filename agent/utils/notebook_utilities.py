from IPython.display import Image, display, Markdown
from langgraph.graph.state import CompiledStateGraph

from agent.utils.financial import to_pst
from agent.state import StockNewsState

def draw_graph(graph: CompiledStateGraph):
    """draw a complied graph as mermaid png"""

    display(Image(graph.get_graph(xray=1).draw_mermaid_png()))

def render_stock_news(state: StockNewsState):
    """render stock news in markdown"""

    md = f"# 📈 {state['ticker']} - {state['company_name']} News\n"
    md += f"**Sector**: {state['sector']}  \n"
    md += f"**Industry**:{state['industry']}\n\n"
    
    for i, item in enumerate(state['news_items'], 1):
        
        emoji = {"Positive": "🟢", "Negative": "🔴", "Neutral": "🟡"}.get(item.sentiment_label, "⚪")
        
        md += f"## {i}. {item.title}\n\n"
        md += f"**Published date**: {to_pst(item.published_date)}  \n"
        md += f"**Sentiment**: {emoji} {item.sentiment_label} (score: {item.sentiment_score:.2f})  \n"
        md += f"**URL**: [{item.url}]({item.url})\n\n"
        md += f"### Summary\n{item.summary}\n\n"
        md += f"### 요약\n{item.summary_kr}\n\n"        
        md += f"### content\n{item.content.replace('#',r'\#')}\n\n"
        md += f"### 내용\n{item.content_kr.replace('#',r'\#')}\n\n"
        md += "-------------------------------------------------------------\n\n"
    
    display(Markdown(md))