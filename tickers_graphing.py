
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


def plot_history(ticker, start = None, end = None, ma = 'yes'):
    ticker_info = yf.Ticker(ticker)
    ticker_hist = ticker_info.history(period = 'max')

    if start and end:
        start_date, end_date = start, end
    else:
        start_date, end_date = ticker_hist.index[0], ticker_hist.index[-1]

    frame = ticker_hist.loc[start_date:end_date]
    closing_prices = frame['Close']


    fig = go.Figure()
    fig.add_trace(go.Scatter(x = closing_prices.index, y = closing_prices, mode = 'lines', name = 'Close'))

    if ma == 'yes':
        closing_prices_ma = frame['Close'].rolling(7).mean()
        fig.add_trace(go.Scatter(x = closing_prices_ma.index, y = closing_prices_ma, mode = 'lines', name = '7D Close Moving Average'))

    fig.update_layout(title = ticker, yaxis_title = 'Price')


    fig.show()

    start_price, end_price = frame.iloc[0]['Close'], frame.iloc[-1]['Close']
    print("Return: {:.2f}%".format((end_price - start_price)/start_price*100))
