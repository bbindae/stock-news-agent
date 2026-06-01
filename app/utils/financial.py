import yfinance as yf

def get_company_name(ticker_symbol: str) -> str:
    """
    By given ticker_symbol, return the company name.
    If the company name is not found, return Ticker itself
    """

    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        info = ticker.info

        company_name = info.get('longName') or info.get('shortName')

        if company_name:
            return company_name
        else:
            return ticker_symbol.upper()
    
    except Exception as e:
        return ticker_symbol.upper()
    