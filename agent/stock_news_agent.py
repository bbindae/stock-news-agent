from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from agent.state import StockNewsState

from agent.nodes import (
    load_news,
    search_news,
    summarize_news,
    save_to_db,
    route_messages
)

def create_stock_news_agent() -> CompiledStateGraph:
    """Constructs the Langgraph state machine, connects nodes with edges,
    and returns the compiled executable graph object
    """

    builder = StateGraph(StockNewsState)
    builder.add_node("load_news", load_news)    
    builder.add_node("search_news", search_news)
    builder.add_node("summarize_news", summarize_news)
    builder.add_node("save_to_db", save_to_db)

    builder.add_edge(START, "load_news")
    builder.add_conditional_edges("load_news",route_messages,{"search_news": "search_news", "end":END})
    builder.add_edge("search_news","summarize_news")
    builder.add_edge("summarize_news", "save_to_db")
    builder.add_edge("save_to_db", END)

    return builder.compile()

