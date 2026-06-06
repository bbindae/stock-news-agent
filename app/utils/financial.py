import yfinance as yf

def get_company_info(ticker_symbol: str) -> dict:
    """
    By given ticker_symbol, return the company name.
    If the company name is not found, return Ticker itself
    """

    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        info = ticker.info

        company_name = info.get('longName') or info.get('shortName') or ticker_symbol.upper()
        sector = info.get('sector','')
        industry = info.get('industry','')

        return {"company_name": company_name, "sector": sector, "industry": industry}     
    
    except Exception as e:
        return {"company_name": ticker_symbol.upper(), "sector":None, "industry": None}
    