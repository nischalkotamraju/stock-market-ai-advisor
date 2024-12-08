def get_graph(ticker_symbol, period='1y'):
    import yfinance as yf
    from asciichartpy import plot
    from colorama import Fore, Style
    
    stock = yf.Ticker(ticker_symbol)
    hist = stock.history(period=period)
    
    prices = hist['Close'].tolist()
    sampled_prices = prices[::5]
    
    config = {
        'height': 12,
        'format': '{:6.2f}'
    }
    
    print(f"\n{Fore.CYAN}{ticker_symbol} Price History ({period}){Style.RESET_ALL}")
    print("-" * 50)
    
    print(plot(sampled_prices, config))
    
    print(f"\n{Fore.YELLOW}Start: ${prices[0]:.2f} | End: ${prices[-1]:.2f}{Style.RESET_ALL}\n")
    
    return hist
