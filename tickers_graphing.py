
import yfinance as yf
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from IPython.display import Markdown
import numpy as np
from datetime import date, timedelta


def plot_and_get_info(ticker, start = None, end = None, ma = 'yes'):

    ticker_obj = yf.Ticker(ticker)
    ticker_hist = ticker_obj.history(period = 'max')


    if start and end:
        start_date, end_date = start, end
    else:
        start_date, end_date = ticker_hist.index[0], ticker_hist.index[-1]


    frame = ticker_hist.loc[start_date:end_date]
    closing_prices = frame['Close']
    volume = frame['Volume']


    fig = make_subplots(rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03, row_heights = [0.8, 0.2])


    fig.add_trace(go.Scatter(x = closing_prices.index, y = closing_prices, mode = 'lines', name = 'Close'), row = 1, col = 1)


    if ma == 'yes':
        closing_prices_ma = frame['Close'].rolling(7).mean()
        fig.add_trace(go.Scatter(x = closing_prices_ma.index, y = closing_prices_ma, mode = 'lines', name = '7D Close Moving Average'), row = 1, col = 1)

    fig.add_trace(go.Bar(x = closing_prices.index, y = volume, name = 'Volume'), row=2, col=1)

    fig.update_xaxes(rangeslider_visible = True, rangeslider_thickness = 0.1, row=2, col=1)
    fig.update_yaxes(title_text="Price", row=1, col=1)

    fig.update_layout(title=ticker, height = 600,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label="1w",
                             step="day",
                             stepmode="backward"),
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="YTD",
                             step="year",
                             stepmode="todate"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                type="date"
            )
        )


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
                        shares_outstanding, perc_institutions, perc_insiders, shares_short, shares_short_perc_outstanding, floatshares, short_perc_float]

        stock_info_df = pd.DataFrame(stock_info, index = ['Market Cap', 'Name', 'Sector', 'Industry', 'Country', 'Beta', 'Day Volume (Most recent)',
                                                            'Avg 10D Volume', 'P/S Trailing 12mo', 'Forward P/E', 'PEG Ratio', 'Forward EPS',
                                                            'Trailing EPS', 'Shares Outstanding', 'Institutions % of Oustanding',
                                                            'Insiders % of Oustanding', 'Shares Short (Prev Mo)', 'Short % of Outstanding (Prev Mo)',
                                                             'Shares Float', 'Short % of Float (Prev Mo)'], columns = ['Info'])
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

        # time series normalization
        # y will be a column in a dataframe
        y = (column - min) / (max - min)

        return y

    def printmd(string):
        display(Markdown(string))


    start_end_prices = {}
    closing_90_days = []


    fig = go.Figure()


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
            fig.add_trace(go.Scatter(x = closing_prices_ma.index, y = closing_prices_ma, mode = 'lines', name = ticker + '7D Close Moving Average'))


    fig.update_layout(title = ', '.join(tickers) + ' Comparison', yaxis_title = 'Norm Price')

    fig.update_layout(height = 600,
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=7,
                             label="1w",
                             step="day",
                             stepmode="backward"),
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=3,
                             label="3m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="YTD",
                             step="year",
                             stepmode="todate"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True, thickness = 0.1
                ),
                type="date"
            )
        )

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

        fig2.update_layout(title = ', '.join(tickers) + ' Last 90 Days Correlation', xaxis_title = tickers[0], yaxis_title = tickers[1], width = 1000, height = 500)

        fig2.show()

        printmd("Pearson Correlation: " + str(round(closing_90_days[0].loc[:, tickers[0]].corr(closing_90_days[1].loc[:, tickers[1]]),3)))
        print()



def plot_buysell_points(ticker, tradesdf, crypto = 'no'):

    trade_history = tradesdf[tradesdf['Symbol'] == ticker].reset_index(drop=True)

    if crypto == 'yes':
        ticker += '-USD'

    ticker_obj = yf.Ticker(ticker)
    ticker_hist = ticker_obj.history(period = 'max')

    if len(ticker_hist) == 0:
        return

    start_date = (pd.to_datetime(trade_history.loc[0, 'Date']) - timedelta(150)).strftime("%Y-%m-%d")
    today_date = date.today().strftime("%Y-%m-%d")

    frame = ticker_hist.loc[start_date:today_date]
    closing_prices = frame['Close']


    fig = go.Figure()

    fig.add_trace(go.Scatter(x = closing_prices.index, y = closing_prices, mode = 'lines', name = 'Close'))

    for i in range(len(trade_history)):
        trade_date = trade_history.loc[i, 'Date']
        price = trade_history.loc[i, 'Avg_Price']
        quantity = trade_history.loc[i, 'Quantity']
        total = trade_history.loc[i, 'Total']
        side = trade_history.loc[i, 'Side']
        gain = trade_history.loc[i, 'Gain']
        perc_gain = trade_history.loc[i, '% Gain']

        if side == 'buy':

            fig.add_annotation(x = trade_date, y = price, text = f'BB', showarrow = True, arrowhead = 1,
                               ax = -0.5, ay = -30, arrowsize = 1.5, align = 'left',
                               hovertext = f'B, P: {price}, Q: {quantity}, T: {total}, D: {trade_date}')

        if side == 'sell':

            fig.add_annotation(x = trade_date, y = price, text = f'SS', showarrow = True, arrowhead = 1,
                               ax = 20, ay = -30, arrowsize = 1.5, align = 'right',
                               hovertext = f'S, P: {price}, Q: {quantity}, T: {total}, D: {trade_date}, G: {gain}, %G: {perc_gain}')



    fig.update_layout(title = ticker, yaxis_title = 'Price')


    fig.show()
