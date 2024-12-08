import numpy as np
import yfinance as yf
import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_analysis(ticker, account_size, risk_percentage, suggested_position, daily_volatility):
    analysis_prompt = f"""
    Given the following information for the stock {ticker}:
    - Account Size: ${account_size}
    - Risk Percentage: {risk_percentage}%
    - Suggested Position Size: ${suggested_position}
    - Daily Volatility (standard deviation of daily returns): {daily_volatility * 100:.2f}%

    Please provide an analysis on the following:
    1. Is the suggested position size reasonable given the account size and risk percentage?
    2. What impact does the daily volatility have on the recommended position size?
    3. What could be the risks associated with taking such a position in terms of volatility?
    4. Any general recommendations for adjusting position size to better manage risk based on this stock's volatility?

    Please provide a clear and concise response.
    
    Also, provide some news of the stock that relate to the risk management below the bullet points.
    """
    
    try:
        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a financial advisor with expertise in portfolio management and risk assessment."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7
        )
        ai_response = chat_completion.choices[0].message['content']
        print("\n\n", ai_response)
        return ai_response

    except Exception as e:
        print(f"Error generating AI analysis: {str(e)}")
        return f"Error generating AI analysis: {str(e)}"


def calculate_position_size(ticker, account_size, risk_percentage):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    
    daily_volatility = hist['Close'].pct_change().std()
    
    max_position = account_size * (risk_percentage / 100)
    
    suggested_position = max_position * (1 - daily_volatility)
    
    ai_analysis = get_ai_analysis(ticker, account_size, risk_percentage, suggested_position, daily_volatility)

    return {
        'suggested_position': round(suggested_position, 2),
        'max_shares': round(suggested_position / stock.info['currentPrice'], 0),
        'ai_analysis': ai_analysis
    }
