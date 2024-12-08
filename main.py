import openai
from gather_yahoo_finance import gather_yahoo_finance
from get_graph import get_graph
from analysis import (
    calculate_roi,
    calculate_sharpe_ratio,
    calculate_volatility,
    track_profit_loss,
    calculate_sector_diversity
)
from risk_management import calculate_position_size
from market_sentiment import analyze_news_sentiment
from real_time_alerts import set_price_alert
from dotenv import load_dotenv
import os
import pandas as pd
from colorama import Fore, Style

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_stock(ticker, isHolding, include_sentiment=False):
    financial_data = gather_yahoo_finance(ticker)
    sentiment_data = ""
    if include_sentiment:
        sentiment_result = analyze_news_sentiment(ticker)
        sentiment_data = f"\nMarket Sentiment: {sentiment_result['interpretation']} (Score: {sentiment_result['sentiment_score']:.2f})"
    
    analysis_prompt = f"""
    Based on the following financial data for {ticker}:
    {financial_data}
    {sentiment_data}
    
    Is the user holding the stock? {isHolding}
    
    *y = yes, n = no*
    
    Use this information to provide a comprehensive financial analysis and investment recommendation.
    
    Not just the ticker, but also state the company name, and the industry it is in.
    
    Please provide a comprehensive financial analysis including:
    1. Investment recommendation (Buy, Sell, Hold, etc)
    2. Key financial metrics analysis
    3. Risk assessments
    4. Short-term and long-term outlook
    5. Important factors influencing the stock
    6. Potential price targets
    
    Present the analysis in a clear, structured format.
    
    The idea is to get to the point, but also provide a more detailed analysis than just a simple buy/sell/hold recommendation. Try to simplify the information so it isn't too long.
    """
    
    try:
        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional financial analyst with expertise in stock market analysis and investment strategies. Do NOT answer questions irrelevant to the topic AT ALL."
                },
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            temperature=0.7
        )
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred during analysis: {str(e)}"

if __name__ == "__main__":
    portfolio = pd.DataFrame(columns=['symbol', 'initial_investment', 'current_value', 'sector'])
    
    while True:
        print(f"\n{Fore.CYAN}Choose an option:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. View Portfolio Analytics{Style.RESET_ALL}")
        print(f"{Fore.GREEN}2. Analyze Stock{Style.RESET_ALL}")
        print(f"{Fore.GREEN}3. Manage Portfolio{Style.RESET_ALL}")
        print(f"{Fore.GREEN}4. Risk Management{Style.RESET_ALL}")
        print(f"{Fore.GREEN}5. Set Price Alerts{Style.RESET_ALL}")
        print(f"{Fore.RED}6. Exit{Style.RESET_ALL}")
        
        choice = input(f"{Fore.YELLOW}Enter your choice (1-6): {Style.RESET_ALL}")
        
        if choice == "1":
            clear_console()
            
            if portfolio.empty:
                print(f"{Fore.RED}Portfolio is empty. Please add positions first.{Style.RESET_ALL}")
                continue
                
            roi = calculate_roi(portfolio['initial_investment'].sum(), portfolio['current_value'].sum())
            pl = track_profit_loss(portfolio)
            sector_weights = calculate_sector_diversity(portfolio)

            print(f"\n{Fore.CYAN}Portfolio Analytics:{Style.RESET_ALL}")
            print("=" * 50)
            print(f"{Fore.YELLOW}Portfolio ROI: {roi}%{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Profit/Loss by Position:{Style.RESET_ALL}")
            print(pl)
            print(f"\n{Fore.YELLOW}Sector Weights:{Style.RESET_ALL}")
            print(sector_weights)
            print("=" * 50)
            
        elif choice == "2":
            clear_console()
            
            while True:
                ticker = input(f"{Fore.YELLOW}Enter stock ticker symbol (e.g. AAPL): {Style.RESET_ALL}").upper()
                if ticker.isalpha() and len(ticker) <= 5:
                    break
                print(f"{Fore.RED}Invalid ticker symbol. Please enter a valid stock symbol (1-5 letters).{Style.RESET_ALL}")

            while True:
                isHolding = input(f"{Fore.YELLOW}Are you holding this stock? (y/n): {Style.RESET_ALL}").lower()
                if isHolding in ['y', 'n']:
                    break
                print(f"{Fore.RED}Invalid input. Please enter 'y' for yes or 'n' for no.{Style.RESET_ALL}")

            while True:
                include_sentiment = input(f"{Fore.YELLOW}Include market sentiment analysis? (y/n): {Style.RESET_ALL}").lower()
                if include_sentiment in ['y', 'n']:
                    break
                print(f"{Fore.RED}Invalid input. Please enter 'y' for yes or 'n' for no.{Style.RESET_ALL}")

            valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y']
            while True:
                graph_term = input(f"{Fore.YELLOW}Enter the time period for the stock analysis (1d/5d/1mo/3mo/6mo/1y/2y/5y): {Style.RESET_ALL}").lower()
                if graph_term in valid_periods:
                    break
                print(f"{Fore.RED}Invalid time period. Please choose from: {', '.join(valid_periods)}{Style.RESET_ALL}")

            try:
                analysis = analyze_stock(ticker, isHolding, include_sentiment == 'y')
                graph = get_graph(ticker, graph_term)
                if "An error occurred" not in analysis:
                    print(f"\n{Fore.CYAN}Financial Analysis for {ticker}:{Style.RESET_ALL}")
                    print("=" * 50)
                    print(analysis)
                    print("=" * 50)
                    print(graph)
                else:
                    print(f"{Fore.RED}The ticker '{ticker}' does not exist. Please try again with a valid stock symbol.{Style.RESET_ALL}")
            except Exception:
                print(f"{Fore.RED}The ticker '{ticker}' does not exist. Please try again with a valid stock symbol.{Style.RESET_ALL}")
            
        elif choice == "3":
            clear_console()
            
            while True:
                print(f"\n{Fore.CYAN}Portfolio Management:{Style.RESET_ALL}")
                print(f"{Fore.GREEN}1. Add Position{Style.RESET_ALL}")
                print(f"{Fore.GREEN}2. Update Position{Style.RESET_ALL}")
                print(f"{Fore.GREEN}3. Remove Position{Style.RESET_ALL}")
                print(f"{Fore.GREEN}4. View Current Portfolio{Style.RESET_ALL}")
                print(f"{Fore.RED}5. Back to Main Menu{Style.RESET_ALL}")
                
                portfolio_choice = input(f"{Fore.YELLOW}Enter your choice (1-5): {Style.RESET_ALL}")
                
                if portfolio_choice == "1":
                    clear_console()
                    
                    symbol = input(f"{Fore.YELLOW}Enter stock symbol: {Style.RESET_ALL}").upper()
                    while True:
                        try:
                            initial_investment = float(input(f"{Fore.YELLOW}Enter initial investment amount: {Style.RESET_ALL}"))
                            current_value = float(input(f"{Fore.YELLOW}Enter current value: {Style.RESET_ALL}"))
                            break
                        except ValueError:
                            print(f"{Fore.RED}Please enter valid numerical values.{Style.RESET_ALL}")
                    
                    sector = input(f"{Fore.YELLOW}Enter sector (e.g., Technology, Healthcare): {Style.RESET_ALL}")
                    
                    new_position = pd.DataFrame({
                        'symbol': [symbol],
                        'initial_investment': [initial_investment],
                        'current_value': [current_value],
                        'sector': [sector]
                    })
                    portfolio = pd.concat([portfolio, new_position], ignore_index=True)
                    print(f"{Fore.GREEN}Position added successfully!{Style.RESET_ALL}")
                    
                elif portfolio_choice == "2":
                    clear_console()
                    
                    if portfolio.empty:
                        print(f"{Fore.RED}No positions to update.{Style.RESET_ALL}")
                        continue
                        
                    print(f"\n{Fore.YELLOW}Current positions:{Style.RESET_ALL}")
                    print(portfolio)
                    symbol = input(f"{Fore.YELLOW}Enter symbol to update: {Style.RESET_ALL}").upper()
                    
                    if symbol in portfolio['symbol'].values:
                        while True:
                            try:
                                current_value = float(input(f"{Fore.YELLOW}Enter new current value: {Style.RESET_ALL}"))
                                break
                            except ValueError:
                                print(f"{Fore.RED}Please enter a valid numerical value.{Style.RESET_ALL}")
                        portfolio.loc[portfolio['symbol'] == symbol, 'current_value'] = current_value
                        print(f"{Fore.GREEN}Position updated successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Symbol not found in portfolio.{Style.RESET_ALL}")
                        
                elif portfolio_choice == "3":
                    clear_console()
                    
                    if portfolio.empty:
                        print(f"{Fore.RED}No positions to remove.{Style.RESET_ALL}")
                        continue
                        
                    print(f"\n{Fore.YELLOW}Current positions:{Style.RESET_ALL}")
                    print(portfolio)
                    symbol = input(f"{Fore.YELLOW}Enter symbol to remove: {Style.RESET_ALL}").upper()
                    
                    if symbol in portfolio['symbol'].values:
                        portfolio = portfolio[portfolio['symbol'] != symbol]
                        print(f"{Fore.GREEN}Position removed successfully!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Symbol not found in portfolio.{Style.RESET_ALL}")
                        
                elif portfolio_choice == "4":
                    clear_console()
                    
                    if portfolio.empty:
                        print(f"{Fore.RED}Portfolio is empty.{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.YELLOW}Current Portfolio:{Style.RESET_ALL}")
                        print(portfolio)
                        
                elif portfolio_choice == "5":
                    clear_console()
                    break
                    
        elif choice == "4":
            clear_console()
            
            while True:
                ticker = input(f"{Fore.YELLOW}Enter stock ticker symbol (e.g. AAPL): {Style.RESET_ALL}").upper()
                if ticker.isalpha() and len(ticker) <= 5:
                    break
                print(f"{Fore.RED}Invalid ticker symbol. Please enter a valid stock symbol (1-5 letters).{Style.RESET_ALL}")
            
            while True:
                try:
                    account_size = float(input(f"{Fore.YELLOW}Enter your account size: {Style.RESET_ALL}"))
                    risk_percentage = float(input(f"{Fore.YELLOW}Enter risk percentage (1-100): {Style.RESET_ALL}"))
                    if 0 < risk_percentage <= 100:
                        break
                    print(f"{Fore.RED}Risk percentage must be between 1 and 100.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter valid numerical values.{Style.RESET_ALL}")
            
            try:
                position_info = calculate_position_size(ticker, account_size, risk_percentage)
                print(f"\n{Fore.CYAN}Position Size Analysis:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Suggested Position Size: ${position_info['suggested_position']}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Maximum Shares: {position_info['max_shares']}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error calculating position size: {str(e)}{Style.RESET_ALL}")

        elif choice == "5":
            clear_console()
            
            while True:
                ticker = input(f"{Fore.YELLOW}Enter stock ticker symbol (e.g. AAPL): {Style.RESET_ALL}").upper()
                if ticker.isalpha() and len(ticker) <= 5:
                    break
                print(f"{Fore.RED}Invalid ticker symbol. Please enter a valid stock symbol (1-5 letters).{Style.RESET_ALL}")
            
            while True:
                try:
                    target_price = float(input(f"{Fore.YELLOW}Enter target price: {Style.RESET_ALL}"))
                    break
                except ValueError:
                    print(f"{Fore.RED}Please enter a valid numerical value.{Style.RESET_ALL}")
            
            set_price_alert(ticker, target_price)
            print(f"{Fore.GREEN}Price alert set for {ticker} at ${target_price:.2f}{Style.RESET_ALL}")
            
        elif choice == "6":
            clear_console()
            print(f"{Fore.RED}Exiting the program...{Style.RESET_ALL}")
            break
        
        else:
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 6.{Style.RESET_ALL}")
