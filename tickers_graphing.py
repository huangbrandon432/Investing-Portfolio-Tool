
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from IPython.display import Markdown
import numpy as np


def plot_and_get_info(ticker, start = None, end = None, ma = 'yes'):

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

    printmd('Given Timeframe:')
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
        avg10d_vol = str(round(ticker_info['averageDailyVolume10Day']/1000000,2)) + 'M'
        most_recent_vol = str(round(ticker_info['volume']/1000000,2)) + 'M'


        try:
            beta = round(ticker_info['beta'],2)
        except:
            beta = ticker_info['beta']

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

        stock_info = [market_cap, longname, sector, industry, country, beta, most_recent_vol, avg10d_vol, ps_trailing_12mo, forwardpe, pegratio, forwardeps, trailingeps,
                        shares_outstanding, shares_short, shares_short_perc_outstanding, floatshares, short_perc_float, perc_institutions, perc_insiders]

        stock_info_df = pd.DataFrame(stock_info, index = ['Market Cap', 'Name', 'Sector', 'Industry', 'Country', 'Beta', 'Day Volume (Most recent)',
                                                            'Avg 10D Volume', 'P/S Trailing 12mo', 'Forward P/E', 'PEG Ratio', 'Forward EPS',
                                                            'Trailing EPS', 'Shares Outstanding', 'Shares Short (Prev Mo)', 'Short % of Outstanding (Prev Mo)',
                                                             'Shares Float', 'Short % of Float (Prev Mo)', '% Institutions', '% Insiders'], columns = ['Info'])
        print()

        display(stock_info_df)

    except:
        pass



def compare_charts(tickers = [], start = None, end = None, ma = 'yes'):

    if len(tickers) <= 1:
        raise Exception("Please enter at least two tickers to compare")

    def normalize_data(column):

        min = column.min()
        max = column.max()

        # time series normalization part
        # y will be a column in a dataframe
        y = (column - min) / (max - min)

        return y

    def printmd(string):
        display(Markdown(string))


    start_end_prices = {}
    closing_90_days = []


    fig = go.Figure()

    #
    for ticker in tickers:

        ticker_obj = yf.Ticker(ticker)
        ticker_hist = ticker_obj.history(period = 'max')

        if start and end:
            start_date, end_date = start, end
        else:
            start_date, end_date = ticker_hist.index[0], ticker_hist.index[-1]


        frame = ticker_hist.loc[start_date:end_date].copy()
        frame['Norm Close'] = normalize_data(frame['Close'])
        closing_prices = frame['Norm Close']

        start_end_prices[ticker] = {'start_price': frame.iloc[0]['Close'], 'end_price': frame.iloc[-1]['Close']}
        closing_90_days.append(closing_prices.iloc[-90:].to_frame().rename(columns = {'Norm Close': ticker}))


        fig.add_trace(go.Scatter(x = closing_prices.index, y = closing_prices, mode = 'lines', name = ticker + ' Norm Close'))

        if ma == 'yes':
            closing_prices_ma = frame['Norm Close'].rolling(7).mean()
            fig.add_trace(go.Scatter(x = closing_prices_ma.index, y = closing_prices_ma, mode = 'lines', name = i + '7D Close Moving Average'))


    fig.update_layout(title = ', '.join(tickers) + ' Comparison', yaxis_title = 'Norm Price')
    fig.show()



    printmd('Given Timeframe:')

    for ticker in tickers:

        start_price, end_price = start_end_prices[ticker]['start_price'], start_end_prices[ticker]['end_price']

        printmd(ticker + " Return: {:.2f}%".format((end_price - start_price)/start_price*100))



    if len(tickers) > 2:
        concat_closing_90_days = pd.concat(closing_90_days, axis = 1)

        print('\n')
        printmd("Last 90 Days Close Pearson Correlation Matrix: ")
        display(concat_closing_90_days.corr())

        fig2 = px.imshow(concat_closing_90_days.corr(), color_continuous_scale = 'blues', title = 'Last 90 Days Close Pearson Correlation Heatmap',
                            width = 500, height = 400)
        fig2.show()


    else:

        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(x = closing_90_days[0].loc[:, tickers[0]], y = closing_90_days[1].loc[:, tickers[1]], mode = 'markers', name = 'Norm Close'))

        fig2.update_layout(title = ', '.join(tickers) + ' Last 90 Days Correlation', xaxis_title = tickers[0], yaxis_title = tickers[1], width = 1500, height = 500)

        fig2.show()

        printmd("Pearson Correlation: " + str(round(closing_90_days[0].loc[:, tickers[0]].corr(closing_90_days[1].loc[:, tickers[1]]),3)))
        print()






    #
    # ticker_obj1 = yf.Ticker(tickers[0])
    # ticker_hist1 = ticker_obj1.history(period = 'max')
    #
    # ticker_obj2 = yf.Ticker(tickers[1])
    # ticker_hist2 = ticker_obj2.history(period = 'max')
    #
    # if start and end:
    #     start_date, end_date = start, end
    # else:
    #     start_date, end_date = ticker_hist1.index[0], ticker_hist1.index[-1]
    #
    #
    # def normalize_data(column):
    #
    #     min = column.min()
    #     max = column.max()
    #
    #     # time series normalization part
    #     # y will be a column in a dataframe
    #     y = (column - min) / (max - min)
    #
    #     return y
    #
    #
    # frame1 = ticker_hist1.loc[start_date:end_date].copy()
    # frame1['Norm Close'] = normalize_data(frame1['Close'])
    # closing_prices1 = frame1['Norm Close']
    #
    # frame2 = ticker_hist2.loc[start_date:end_date].copy()
    # frame2['Norm Close'] = normalize_data(frame2['Close'])
    # closing_prices2 = frame2['Norm Close']
    #
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x = closing_prices1.index, y = closing_prices1, mode = 'lines', name = str(tickers[0]) + ' Norm Close'))
    # fig.add_trace(go.Scatter(x = closing_prices2.index, y = closing_prices2, mode = 'lines', name = str(tickers[1]) + ' Norm Close'))
    #
    # if ma == 'yes':
    #     closing_prices_ma1 = frame1['Norm Close'].rolling(7).mean()
    #     fig.add_trace(go.Scatter(x = closing_prices_ma1.index, y = closing_prices_ma1, mode = 'lines', name = str(tickers[0]) + '7D Close Moving Average'))
    #
    #     closing_prices_ma2 = frame2['Norm Close'].rolling(7).mean()
    #     fig.add_trace(go.Scatter(x = closing_prices_ma2.index, y = closing_prices_ma2, mode = 'lines', name = str(tickers[1]) + '7D Close Moving Average'))
    #
    # fig.update_layout(title = ', '.join(tickers) + ' Comparison', yaxis_title = 'Norm Price')
    #
    #
    # fig.show()
    #
    #
    # start_price1, end_price1 = frame1.iloc[0]['Close'], frame1.iloc[-1]['Close']
    #
    # start_price2, end_price2 = frame2.iloc[0]['Close'], frame2.iloc[-1]['Close']
    #
    #
    # def printmd(string):
    #     display(Markdown(string))
    #
    # printmd('Given Timeframe:')
    # printmd(str(tickers[0]) + " Return: {:.2f}%".format((end_price1 - start_price1)/start_price1*100))
    # printmd(str(tickers[1]) + " Return: {:.2f}%".format((end_price2 - start_price2)/start_price2*100))
    #
    #
    # fig2 = go.Figure()
    # fig2.add_trace(go.Scatter(x = closing_prices1.iloc[-90:], y = closing_prices2.iloc[-90:], mode = 'markers', name = 'Norm Close'))
    #
    # fig2.update_layout(title = ', '.join(tickers) + ' Last 90 Days Correlation', xaxis_title = str(tickers[0]), yaxis_title = str(tickers[1]))
    #
    #
    # fig2.show()
    #
    # print("Pearson Correlation:", round(closing_prices1.iloc[-90:].corr(closing_prices2.iloc[-90:]),3))
