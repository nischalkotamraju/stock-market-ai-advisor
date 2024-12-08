from yahoo_fin import stock_info
import time
import yfinance as yf
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_prediction(ticker, target_price, alert_type='above'):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="5m")
    recent_volatility = hist['Close'].pct_change().std()

    analysis_prompt = f"""
    The stock {ticker} has had the following price changes today (in 5-minute intervals):
    {hist['Close'].tail(10).to_list()}

    The target price for this stock is ${target_price}.
    
    The stock's current price is {hist['Close'].iloc[-1]}.

    Please analyze the recent price movements and predict:
    1. Will the stock price reach the target price of ${target_price} today?
    2. Should the user be alerted if the price is likely to exceed or drop below the target by the end of the day?
    3. Does the price movement suggest that the stock is unlikely to change significantly today?

    Provide a clear and concise recommendation and talk like you are talking to the user.
    """

    try:
        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a stock market analyst with expertise in predicting short-term stock movements."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.7
        )

        ai_response = chat_completion.choices[0].message['content']
        return ai_response

    except Exception as e:
        print(f"Error generating AI prediction: {str(e)}")
        return f"Error generating AI prediction: {str(e)}"


def set_price_alert(ticker, target_price, alert_type='above'):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1d", interval="5m")
    current_price = stock_info.get_live_price(ticker)
    
    ai_analysis = get_ai_prediction(ticker, target_price, alert_type)

    if "unlikely to change significantly today" in ai_analysis:
        return f"AI analysis suggests that {ticker} is unlikely to reach the target price of {target_price} today. No alert needed."

    print(f"Monitoring {ticker} for target price {target_price}...")

    while True:
        current_price = stock_info.get_live_price(ticker)
        print(f"Current price of {ticker}: {current_price}")

        if alert_type == 'above' and current_price >= target_price:
            return f"Alert: {ticker} has reached {current_price}, above target {target_price}"
        elif alert_type == 'below' and current_price <= target_price:
            return f"Alert: {ticker} has dropped to {current_price}, below target {target_price}"

        time.sleep(60)
