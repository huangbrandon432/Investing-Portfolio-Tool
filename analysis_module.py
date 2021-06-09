

import robin_stocks as r
import pandas as pd
import numpy as np
from datetime import date, timedelta
import yfinance as yf
from collections import deque



###Stocks/Crypto#########################################################################################################################################

class StocksCrypto:

    def __init__(self, orders, crypto = 'no'):

        self.orders = orders
        self.crypto = crypto


    def examine_trades(self):

        self.total_gain = 0
        self.total_loss = 0
        self.trades = []

        trading_dict = {}
        net_gain_loss = 0

        for i in range(len(self.orders)):

            side = self.orders.loc[i, 'side']
            symbol = self.orders.loc[i, 'symbol']
            date = self.orders.loc[i, 'date'].strftime('%Y-%m-%d')
            quantity = self.orders.loc[i, 'quantity']
            avg_price = self.orders.loc[i, 'average_price']
            total = round(self.orders.loc[i, 'total'],2)


            if side == 'buy':

                if symbol+'_avgprice' in trading_dict:
                    cur_total = trading_dict[symbol+'_quantity']*trading_dict[symbol+'_avgprice']
                    new_total = cur_total + quantity * avg_price
                    trading_dict[symbol+'_quantity'] += quantity
                    trading_dict[symbol+'_avgprice'] = new_total/trading_dict[symbol+'_quantity']

                else:
                    trading_dict[symbol+'_avgprice'] = avg_price
                    trading_dict[symbol+'_quantity'] = quantity


                cur_avg_price = round(trading_dict[symbol+'_avgprice'],2)
                cur_quantity = round(trading_dict[symbol+'_quantity'],2)

                self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), cur_quantity, cur_avg_price, total, 0, str(0) + '%', net_gain_loss, ''])



            #if sell
            if side == 'sell':

                if symbol+'_avgprice' in trading_dict:


                    gain = round((avg_price - trading_dict[symbol+'_avgprice']) * quantity,2)
                    perc_gain = round((avg_price - trading_dict[symbol+'_avgprice'])/trading_dict[symbol+'_avgprice']*100,2)


                    if gain >= 0:
                        self.total_gain += gain

                    else:
                        self.total_loss += gain


                    trading_dict[symbol+'_quantity'] -= quantity

                    net_gain_loss = round(self.total_gain + self.total_loss,2)
                    cur_avg_price = round(trading_dict[symbol+'_avgprice'],2)
                    cur_quantity = round(trading_dict[symbol+'_quantity'],2)

                    self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), cur_quantity, cur_avg_price, total, gain, str(perc_gain) + '%', net_gain_loss, ''])



                    #if holding = 0, pop symbol avgprice and quantity
                    if trading_dict[symbol+'_quantity'] == 0:
                        trading_dict.pop(symbol+'_avgprice')
                        trading_dict.pop(symbol+'_quantity')

                else:

                    gain = round(avg_price * quantity,2)
                    self.total_gain += gain

                    net_gain_loss = round(self.total_gain + self.total_loss,2)

                    self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), None, None, total, gain, str(0) + '%', net_gain_loss, 'Yes'])


        self.trades_df = pd.DataFrame(self.trades, columns = ['Side', 'Symbol', 'Date', 'Quantity', 'Avg_Price', 'Cur Quantity', 'Cur_Avg_Cost', 'Total', 'Gain', '% Gain', 'Net Gain/Loss', 'Free/Acquired Stock'])

        self.gains_df = self.trades_df[(self.trades_df['Gain'] >= 0) & (self.trades_df['Side'] == 'sell')].sort_values('Gain', ascending = False).reset_index(drop=True)
        self.losses_df = self.trades_df[(self.trades_df['Gain'] < 0) & (self.trades_df['Side'] == 'sell')].sort_values('Gain').reset_index(drop=True)



    def add_price_diff(self):


        if self.crypto == 'no':

            stocks_sold = list(set(self.trades_df[self.trades_df['Side'] == 'sell']['Symbol']))

            ticker_cur_price = []

            for i in stocks_sold:
                try:
                    ticker = yf.Ticker(i)
                    close = round(ticker.history(period = "1d").reset_index(drop=True).loc[0, 'Close'],2)

                    ticker_cur_price.append((i, close, 'sell'))

                except:
                    pass

            ticker_cur_price = pd.DataFrame(ticker_cur_price, columns =['Symbol', 'Current Price', 'Side'])


            self.trades_df_with_price_diff = self.trades_df.merge(ticker_cur_price, how = 'left', on = ['Symbol', 'Side'])

            for i in range(len(self.trades_df_with_price_diff)):

                transac_date = pd.to_datetime(self.trades_df_with_price_diff.loc[i, 'Date'])
                symbol = self.trades_df_with_price_diff.loc[i, 'Symbol']

                if symbol == 'SOXL' and transac_date < pd.to_datetime('2021-03-02'):
                    self.trades_df_with_price_diff.loc[i, 'Current Price'] *= 15

                if symbol == 'TECL' and transac_date < pd.to_datetime('2021-03-02'):
                    self.trades_df_with_price_diff.loc[i, 'Current Price'] *= 10

                if symbol == 'AAPL' and transac_date < pd.to_datetime('2020-08-28'):
                    self.trades_df_with_price_diff.loc[i, 'Current Price'] *= 4

                if symbol == 'TSLA' and transac_date < pd.to_datetime('2020-08-31'):
                    self.trades_df_with_price_diff.loc[i, 'Current Price'] *= 5

        else:
            crypto_sold = list(set(self.trades_df[self.trades_df['Side'] == 'sell']['Symbol']))

            crypto_cur_price = []

            for i in crypto_sold:
                try:
                    crypto_market_price = float(r.crypto.get_crypto_quote(i, info='mark_price'))

                    crypto_cur_price.append((i, crypto_market_price, 'sell'))

                except:
                    pass

            crypto_cur_price = pd.DataFrame(crypto_cur_price, columns =['Symbol', 'Current Price', 'Side'])


            self.trades_df_with_price_diff = self.trades_df.merge(crypto_cur_price, how = 'left', on = ['Symbol', 'Side'])



        self.trades_df_with_price_diff['Price Sold & Curr Price % Diff'] = round((self.trades_df_with_price_diff['Current Price'] - self.trades_df_with_price_diff["Avg_Price"])/self.trades_df_with_price_diff["Avg_Price"] * 100, 2)
        self.trades_df_with_price_diff['Avg Cost & Curr Price % Diff'] = round((self.trades_df_with_price_diff['Current Price'] - self.trades_df_with_price_diff["Cur_Avg_Cost"])/self.trades_df_with_price_diff["Cur_Avg_Cost"] * 100, 2)

        self.trades_df_with_price_diff['Current Price'].fillna('', inplace=True)
        self.trades_df_with_price_diff['Price Sold & Curr Price % Diff'].fillna('', inplace=True)
        self.trades_df_with_price_diff['Avg Cost & Curr Price % Diff'].fillna('', inplace=True)

        self.trades_df_with_price_diff['Price Sold & Curr Price % Diff'] = self.trades_df_with_price_diff['Price Sold & Curr Price % Diff'].apply(lambda x: str(x) + '%' if x != '' else '')
        self.trades_df_with_price_diff['Avg Cost & Curr Price % Diff'] = self.trades_df_with_price_diff['Avg Cost & Curr Price % Diff'].apply(lambda x: str(x) + '%' if x != '' else '')



        self.gains_df_with_price_diff = self.trades_df_with_price_diff[(self.trades_df_with_price_diff['Gain'] >= 0) & (self.trades_df_with_price_diff['Side'] == 'sell')].sort_values('Gain', ascending = False).reset_index(drop=True)
        self.losses_df_with_price_diff = self.trades_df_with_price_diff[(self.trades_df_with_price_diff['Gain'] < 0) & (self.trades_df_with_price_diff['Side'] == 'sell')].sort_values('Gain').reset_index(drop=True)



    def add_hold_time(self):

        self.trades_df_with_price_diff['Days Held'] = None

        symbols = {}

        for i in range(len(self.trades_df_with_price_diff)):

            side = self.trades_df_with_price_diff.loc[i, 'Side']
            symbol = self.trades_df_with_price_diff.loc[i, 'Symbol']
            date = self.trades_df_with_price_diff.loc[i, 'Date']
            quantity = self.trades_df_with_price_diff.loc[i, 'Quantity']

            if side == 'buy':
                if symbol not in symbols:
                    symbols[symbol] = deque([])

                symbols[symbol].append([date, quantity])

            if side == 'sell':

                if symbol in symbols and len(symbols[symbol]) > 0:

                    first_in_queue_quantity = symbols[symbol][0][1]

                    symbols[symbol][0][1] -= quantity

                    hold_time = (pd.to_datetime(date) - pd.to_datetime(symbols[symbol][0][0])).days

                    if symbols[symbol][0][1] == 0:

                        self.trades_df_with_price_diff.loc[i, 'Days Held'] = hold_time
                        symbols[symbol].popleft()

                    elif symbols[symbol][0][1] > 0:

                        self.trades_df_with_price_diff.loc[i, 'Days Held'] = hold_time

                    else:
                        first_in_queue_weight_times_holdtime = 0

                        while symbols[symbol][0][1] < 0:

                            #neg value
                            quantity_excess = symbols[symbol][0][1]

                            hold_time = (pd.to_datetime(date) - pd.to_datetime(symbols[symbol][0][0])).days

                            first_in_que_weight = first_in_queue_quantity/quantity

                            first_in_queue_weight_times_holdtime += first_in_que_weight * hold_time

                            symbols[symbol].popleft()

                            first_in_queue_quantity = symbols[symbol][0][1]

                            symbols[symbol][0][1] += quantity_excess


                        hold_time = (pd.to_datetime(date) - pd.to_datetime(symbols[symbol][0][0])).days

                        if symbols[symbol][0][1] == 0:

                            self.trades_df_with_price_diff.loc[i, 'Days Held'] = round(first_in_queue_weight_times_holdtime + first_in_queue_quantity/quantity * hold_time,2)

                            symbols[symbol].popleft()

                        elif symbols[symbol][0][1] > 0:

                            self.trades_df_with_price_diff.loc[i, 'Days Held'] = round(first_in_queue_weight_times_holdtime + (first_in_queue_quantity - symbols[symbol][0][1])/quantity * hold_time,2)




###Options#########################################################################################################################################

class Options:

    def __init__(self, option_orders):
        self.option_orders = option_orders


    def examine_trades(self):

        self.total_optionsgain = 0
        self.total_optionsloss = 0
        self.trades = []

        long_trading_dict = {}
        long_symbol_strike_exp_type_list = []
        short_trading_dict = {}
        short_symbol_strike_exp_type_list = []

        net_gain_loss = 0

        for i in range(len(self.option_orders)):

            side = self.option_orders.loc[i, 'side']
            symbol = self.option_orders.loc[i, 'chain_symbol']
            exp = self.option_orders.loc[i, 'expiration_date']
            strike = self.option_orders.loc[i, 'strike_price']
            option_type = self.option_orders.loc[i, 'option_type']
            order_date = self.option_orders.loc[i, 'order_created_at'].strftime('%Y-%m-%d')
            quantity = self.option_orders.loc[i, 'processed_quantity']
            opening_strategy = self.option_orders.loc[i, 'opening_strategy']
            closing_strategy = self.option_orders.loc[i, 'closing_strategy']
            avg_price = self.option_orders.loc[i, 'price']

            total = round(avg_price * quantity * 100,2)

            symb_exp_strike_type = f'{symbol} {exp} {strike} {option_type}'


            if side == 'buy' and opening_strategy in ['long_call', 'long_put']:

                if symb_exp_strike_type not in long_symbol_strike_exp_type_list:
                    long_symbol_strike_exp_type_list.append(symb_exp_strike_type)


                if symb_exp_strike_type+'_avgprice' in long_trading_dict:
                    cur_total = long_trading_dict[symb_exp_strike_type+'_quantity']*long_trading_dict[symb_exp_strike_type+'_avgprice']
                    new_total = cur_total + quantity * avg_price
                    long_trading_dict[symb_exp_strike_type+'_quantity'] += quantity
                    long_trading_dict[symb_exp_strike_type+'_avgprice'] = new_total/long_trading_dict[symb_exp_strike_type+'_quantity']

                else:
                    long_trading_dict[symb_exp_strike_type+'_avgprice'] = avg_price
                    long_trading_dict[symb_exp_strike_type+'_quantity'] = quantity



                cur_long_avg_price = round(long_trading_dict[symb_exp_strike_type+'_avgprice'],2)
                cur_long_quantity = round(long_trading_dict[symb_exp_strike_type+'_quantity'],2)

                self.trades.append([side, symbol, option_type, opening_strategy, exp, strike, order_date, quantity, avg_price, cur_long_avg_price, cur_long_quantity, total, 0, str(0), '', net_gain_loss])


            elif side == 'sell' and closing_strategy in ['long_call', 'long_put']:

                if symb_exp_strike_type+'_avgprice' in long_trading_dict:

                    cur_long_avg_price = round(long_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    gain = round((avg_price - cur_long_avg_price) * quantity*100,2)
                    perc_gain = round((avg_price - cur_long_avg_price)/cur_long_avg_price*100,2)

                    if gain >= 0:
                        self.total_optionsgain += gain

                    else:
                        self.total_optionsloss += gain

                    long_trading_dict[symb_exp_strike_type+'_quantity'] -= quantity

                    net_gain_loss = round(self.total_optionsgain + self.total_optionsloss, 2)
                    cur_long_quantity = round(long_trading_dict[symb_exp_strike_type+'_quantity'], 2)

                    self.trades.append([side, symbol, option_type, closing_strategy, exp, strike, order_date, quantity, avg_price, cur_long_avg_price, cur_long_quantity, total, gain, str(perc_gain) + '%', '', net_gain_loss])


                    #if holding = 0, pop chain_symbol avgprice and quantity
                    if long_trading_dict[symb_exp_strike_type+'_quantity'] == 0:
                        long_trading_dict.pop(symb_exp_strike_type+'_avgprice')
                        long_trading_dict.pop(symb_exp_strike_type+'_quantity')
                        long_symbol_strike_exp_type_list.remove(symb_exp_strike_type)


            elif side == 'sell' and opening_strategy in ['short_call', 'short_put']:

                if symb_exp_strike_type not in short_symbol_strike_exp_type_list:
                    short_symbol_strike_exp_type_list.append(symb_exp_strike_type)

                if symb_exp_strike_type+'_avgprice' in short_trading_dict:
                    cur_total = short_trading_dict[symb_exp_strike_type+'_quantity']*short_trading_dict[symb_exp_strike_type+'_avgprice']
                    new_total = cur_total + quantity * avg_price
                    short_trading_dict[symb_exp_strike_type+'_quantity'] += quantity
                    short_trading_dict[symb_exp_strike_type+'_avgprice'] = new_total/short_trading_dict[symb_exp_strike_type+'_quantity']

                #else add chain_symbol_avgprice = buy price in df and chain_symbol_quantity = bought quantity
                else:
                    short_trading_dict[symb_exp_strike_type+'_avgprice'] = avg_price
                    short_trading_dict[symb_exp_strike_type+'_quantity'] = quantity



                cur_short_avg_price = round(short_trading_dict[symb_exp_strike_type+'_avgprice'], 2)
                cur_short_quantity = round(short_trading_dict[symb_exp_strike_type+'_quantity'], 2)

                self.trades.append([side, symbol, option_type, opening_strategy, exp, strike, order_date, quantity, avg_price, cur_short_avg_price, cur_short_quantity, total, 0, str(0), '', net_gain_loss])



            elif side == 'buy' and closing_strategy in ['short_call', 'short_put']:

                if symb_exp_strike_type+'_avgprice' in short_trading_dict:

                    cur_short_avg_price = round(short_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    gain = round((cur_short_avg_price - avg_price) * quantity * 100, 2)
                    perc_gain = round( (cur_short_avg_price - avg_price) / cur_short_avg_price * 100, 2)

                    if gain >= 0:
                        self.total_optionsgain += gain
                    else:
                        self.total_optionsloss += gain


                    short_trading_dict[symb_exp_strike_type+'_quantity'] -= quantity

                    net_gain_loss = round(self.total_optionsgain + self.total_optionsloss, 2)
                    cur_short_quantity = round(short_trading_dict[symb_exp_strike_type+'_quantity'], 2)

                    self.trades.append([side, symbol, option_type, closing_strategy, exp, strike, order_date, quantity, avg_price, cur_short_avg_price, cur_short_quantity, total, gain, str(perc_gain) + '%', '', net_gain_loss])

                    #if holding position = 0, then pop chain_symbol avgprice and chain_symbol quantity
                    if short_trading_dict[symb_exp_strike_type+'_quantity'] == 0:
                        short_trading_dict.pop(symb_exp_strike_type+'_avgprice')
                        short_trading_dict.pop(symb_exp_strike_type+'_quantity')
                        short_symbol_strike_exp_type_list.remove(symb_exp_strike_type)


    #expired orders
        for i in range(len(self.option_orders)):

            symbol = self.option_orders.loc[i, 'chain_symbol']
            exp = self.option_orders.loc[i, 'expiration_date']
            strike = self.option_orders.loc[i, 'strike_price']
            option_type = self.option_orders.loc[i, 'option_type']
            quantity = self.option_orders.loc[i, 'processed_quantity']
            order_date = self.option_orders.loc[i, 'order_created_at'].strftime('%Y-%m-%d')
            opening_strategy = self.option_orders.loc[i, 'opening_strategy']
            closing_strategy = self.option_orders.loc[i, 'closing_strategy']
            avg_price = self.option_orders.loc[i, 'price']

            symb_exp_strike_type = f'{symbol} {exp} {strike} {option_type}'

            if symb_exp_strike_type in long_symbol_strike_exp_type_list and opening_strategy in ['long_call', 'long_put'] and exp < date.today():

                total = long_trading_dict[symb_exp_strike_type+'_avgprice'] * long_trading_dict[symb_exp_strike_type+'_quantity'] * 100

                long_trading_dict.pop(symb_exp_strike_type+'_avgprice')
                long_trading_dict.pop(symb_exp_strike_type+'_quantity')
                long_symbol_strike_exp_type_list.remove(symb_exp_strike_type)

                self.total_optionsloss -= total
                net_gain_loss = round(self.total_optionsgain + self.total_optionsloss, 2)

                self.trades.append([side, symbol, option_type, opening_strategy, exp, strike, order_date, quantity, avg_price, 0, 0, total, -total, '-100%', 'Yes', net_gain_loss])

            if symb_exp_strike_type in short_symbol_strike_exp_type_list and opening_strategy in ['short_call', 'short_put'] and exp < date.today():

                total = short_trading_dict[symb_exp_strike_type+'_avgprice'] * short_trading_dict[symb_exp_strike_type+'_quantity'] * 100

                short_trading_dict.pop(symb_exp_strike_type+'_avgprice')
                short_trading_dict.pop(symb_exp_strike_type+'_quantity')
                short_symbol_strike_exp_type_list.remove(symb_exp_strike_type)

                self.total_optionsgain += total
                net_gain_loss = round(self.total_optionsgain + self.total_optionsloss, 2)

                self.trades.append([side, symbol, option_type, opening_strategy, exp, strike, order_date, quantity, avg_price, 0, 0, total, total, '', 'Yes', net_gain_loss])


        self.trades_df = pd.DataFrame(self.trades, columns = ['Side', 'Symbol', 'Option Type', 'Strategy', 'Expiration', 'Strike', 'Date', 'Quantity', 'Avg_Price', 'Cur_Avg_Cost', 'Cur Quantity', 'Total', 'Gain', '% Gain', 'Expired', 'Net Gain/Loss'])
        self.trades_df['Expiration'] = self.trades_df['Expiration'].astype(str).str.replace(' 00:00:00', '')
        self.trades_df['Gain'] = self.trades_df['Gain'].astype('float64')

        self.gains_df = self.trades_df[(self.trades_df['Gain'] > 0)].sort_values('Gain', ascending = False).reset_index(drop=True)
        self.losses_df = self.trades_df[(self.trades_df['Gain'] < 0)].sort_values('Gain').reset_index(drop=True)
