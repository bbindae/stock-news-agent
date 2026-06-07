from agent.state import StockNewsState

def route_messages(state: StockNewsState):
    """if there are news items in the state go to END; otherwise, go grab news!"""
    if(state.news_items):
        return 'end'
    return 'search_news'