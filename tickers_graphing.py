
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from IPython.display import Markdown


def plot_history(ticker, start = None, end = None, ma = 'yes'):

    ticker_obj = yf.Ticker(ticker)
    ticker_hist = ticker_obj.history(period = 'max')


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


    def printmd(string):
        display(Markdown(string))

    printmd("Return: {:.2f}%".format((end_price - start_price)/start_price*100))



    try:
        ticker_info = ticker_obj.info

        print()
        printmd('Business Summary: ' + ticker_info['longBusinessSummary'])

        market_cap = str(round(ticker_info['marketCap']/1000000000,2)) + 'B'
        longname = ticker_info['longName']
        sector = ticker_info['sector']
        industry = ticker_info['industry']
        country = ticker_info['country']

        try:
            beta = round(ticker_info['beta'],2)
        except:
            beta = ticker_info['beta']

        avg10d_vol = str(round(ticker_info['averageDailyVolume10Day']/1000000,2)) + 'M'

        try:
            ps_trailing_12mo = round(ticker_info['priceToSalesTrailing12Months'],2)
        except:
            ps_trailing_12mo = ticker_info['priceToSalesTrailing12Months']

        try:
            forwardpe = round(ticker_info['forwardPE'],2)
        except:
            forwardpe = ticker_info['forwardPE']

        pegratio = ticker_info['pegRatio']
        forwardeps = ticker_info['forwardEps']
        trailingeps = ticker_info['trailingEps']
        shares_outstanding = str(round(ticker_info['sharesOutstanding']/1000000,2)) + 'M'
        shares_short = str(round(ticker_info['sharesShort']/1000000,2)) + 'M'
        shares_short_perc_outstanding = str(round(ticker_info['sharesPercentSharesOut']*100,2)) + '%'
        floatshares = str(round(ticker_info['floatShares']/1000000,2)) + 'M'

        try:
            short_perc_float = str(round(ticker_info['shortPercentOfFloat']*100,2)) + '%'
        except:
            short_perc_float = ticker_info['shortPercentOfFloat']

        perc_institutions = str(round(ticker_info['heldPercentInstitutions']*100,2)) + '%'
        perc_insiders = str(round(ticker_info['heldPercentInsiders']*100,2)) + '%'

        stock_info = [market_cap, longname, sector, industry, country, beta, avg10d_vol, ps_trailing_12mo, forwardpe, pegratio, forwardeps, trailingeps,
                        shares_outstanding, shares_short, shares_short_perc_outstanding, floatshares, short_perc_float, perc_institutions, perc_insiders]

        stock_info_df = pd.DataFrame(stock_info, index = ['Market Cap', 'Name', 'Sector', 'Industry', 'Country', 'Beta',
                                                            'Avg 10D Volume', 'P/S Trailing 12mo', 'Forward P/E', 'PEG Ratio', 'Forward EPS',
                                                            'Trailing EPS', 'Shares Outstanding', 'Shares Short', 'Short % of Outstanding',
                                                             'Shares Float', 'Short % of Float', '% Institutions', '% Insiders'], columns = ['Info'])
        print()

        display(stock_info_df)

    except:
        pass
