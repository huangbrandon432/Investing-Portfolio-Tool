
###Stocks/Crypto#########################################################################################################################################

class StocksCrypto:

    def __init__(self, orders, crypto = 'no'):

        self.orders = orders
        self.crypto = crypto
        self.total_gain = 0
        self.total_loss = 0
        self.trades = []
        self.losses = []
        self.gains = []

    def examine_trades(self, printbuy = 'no'):

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

                self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), cur_avg_price, total, 0, str(0) + '%', net_gain_loss, ''])


                if printbuy == 'yes':


                    print(f'Buy {symbol} on {date}, Quantity: {quantity}, Avg Price: ${avg_price}, Current Avg Cost: {cur_avg_price}, Total: ${total}')
                    print('\n')

            #if sell
            if side == 'sell':

                if symbol+'_avgprice' in trading_dict:

                    cur_avg_price = round(trading_dict[symbol+'_avgprice'],2)

                    print(f'Sell {symbol} on {date}, Quantity: {quantity}, Avg Price: ${avg_price}, Current Avg Cost: {cur_avg_price}, Total: ${total}')

                    gain = round((avg_price - trading_dict[symbol+'_avgprice']) * quantity,2)
                    perc_gain = round((avg_price - trading_dict[symbol+'_avgprice'])/trading_dict[symbol+'_avgprice']*100,2)


                    if gain >= 0:
                        self.total_gain += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%')

                        self.gains.append([symbol, date, quantity, avg_price, gain, str(perc_gain) + '%'])

                    else:
                        self.total_loss += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%, LOSS')

                        self.losses.append([symbol, date, quantity, avg_price, gain, str(perc_gain) + '%'])

                    trading_dict[symbol+'_quantity'] -= quantity

                    net_gain_loss = round(self.total_gain + self.total_loss,2)

                    self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), cur_avg_price, total, gain, str(perc_gain) + '%', net_gain_loss, ''])

                    print(f'Net Gain/Loss: ${net_gain_loss}')
                    print('\n')


                    #if holding = 0, pop symbol avgprice and quantity
                    if trading_dict[symbol+'_quantity'] == 0:
                        trading_dict.pop(symbol+'_avgprice')
                        trading_dict.pop(symbol+'_quantity')

                else:

                    print(f'Sell {symbol} on {date}, Quantity: {quantity}, Avg Price: ${avg_price}, Total: ${total}')

                    gain = round(avg_price * quantity,2)
                    self.total_gain += gain

                    self.gains.append([symbol, date, quantity, avg_price, gain, 'Free/Acquired Stock'])

                    net_gain_loss = round(self.total_gain + self.total_loss,2)

                    self.trades.append([side, symbol, date, round(quantity, 2), round(avg_price, 2), cur_avg_price, total, gain, str(0) + '%', net_gain_loss, 'Yes'])

                    print(f'Free/Acquired Stock Gain: ${gain}')
                    print('\n')


        if self.crypto == 'no':

            print()
            print(f'Total Stock Gain: ${self.total_gain}')
            print(f'Total Stock Loss: ${self.total_loss}')

        elif self.crypto == 'yes':

            print()
            print(f'Total Crypto Gain: ${self.total_gain}')
            print(f'Total Crypto Loss: ${self.total_loss}')



    def get_gainers_losers(self):

        self.gains_df = pd.DataFrame(self.gains, columns = ['Symbol', 'Date', 'Quantity', 'Avg_Price', 'Gain', '% Gain']).sort_values('Gain', ascending = False).reset_index(drop=True)
        self.losses_df = pd.DataFrame(self.losses, columns = ['Symbol', 'Date', 'Quantity', 'Avg_Price', 'Gain', '% Gain']).sort_values('Gain').reset_index(drop=True)


    def get_examined_trades_df(self):

        self.trades_df = pd.DataFrame(self.trades, columns = ['Side', 'Symbol', 'Date', 'Quantity', 'Avg_Price', 'Cur_Avg_Cost', 'Total', 'Gain', '% Gain', 'Net Gain/Loss', 'Free/Acquired Stock'])



###Options#########################################################################################################################################

class Options:

    def __init__(self, option_orders):
        self.option_orders = option_orders
        self.total_optionsgain = 0
        self.total_optionsloss = 0
        self.losses = []
        self.gains = []

    def examine_trades(self, printopening = 'yes'):

        long_trading_dict = {}
        long_symbol_strike_exp_type_list = []
        short_trading_dict = {}
        short_symbol_strike_exp_type_list = []

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



                if printopening == 'yes':

                    cur_long_avg_price = round(long_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    print(f'Buy {symbol} {option_type}, {opening_strategy}, Expiration: {exp}, Strike: {strike} on {order_date}, Quantity: {quantity} contracts, Avg Price: ${avg_price}, Current Avg Cost: ${cur_long_avg_price}, Total: ${total}')
                    print()


            elif side == 'sell' and closing_strategy in ['long_call', 'long_put']:

                if symb_exp_strike_type+'_avgprice' in long_trading_dict:


                    cur_long_avg_price = round(long_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    print(f'Sell {symbol} {option_type}, {closing_strategy}, Expiration: {exp}, Strike: {strike} on {order_date}, Quantity: {quantity} contracts, Avg Price: ${avg_price}, Current Avg Cost: ${cur_long_avg_price}, Total: ${total}')


                    gain = round((avg_price - cur_long_avg_price) * quantity*100,2)
                    perc_gain = round((avg_price - cur_long_avg_price)/cur_long_avg_price*100,2)

                    if gain >= 0:
                        self.total_optionsgain += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%')
                        print()
                        self.gains.append([symbol, option_type, closing_strategy, exp, strike, gain, str(perc_gain) + '%'])

                    else:
                        self.total_optionsloss += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%, LOSS')
                        print()
                        self.losses.append([symbol, option_type, closing_strategy, exp, strike, gain, str(perc_gain) + '%'])

                    long_trading_dict[symb_exp_strike_type+'_quantity'] -= quantity

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




                if printopening == 'yes':

                    cur_short_avg_price = round(short_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    print(f'Sell {symbol} {option_type}, {opening_strategy}, Expiration: {exp}, Strike: {strike} on {order_date}, Quantity: {quantity} contracts, Avg Price: ${avg_price}, Current Avg Cost: ${cur_short_avg_price}, Total: ${total}')
                    print()


            elif side == 'buy' and closing_strategy in ['short_call', 'short_put']:

                if symb_exp_strike_type+'_avgprice' in short_trading_dict:

                    cur_short_avg_price = round(short_trading_dict[symb_exp_strike_type+'_avgprice'],2)

                    print(f'Buy {symbol} {option_type}, {closing_strategy}, Expiration: {exp}, Strike: {strike} on {order_date}, Quantity: {quantity} contracts, Avg Price: ${avg_price}, Current Avg Cost: ${cur_short_avg_price}, Total: ${total}')

                    gain = round((cur_short_avg_price - avg_price) * quantity * 100, 2)
                    perc_gain = round( (cur_short_avg_price - avg_price) / cur_short_avg_price * 100, 2)

                    if gain >= 0:
                        self.total_optionsgain += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%')
                        print()
                        self.gains.append([symbol, option_type, closing_strategy, exp, strike, gain, str(perc_gain) + '%'])

                    else:
                        self.total_optionsloss += gain

                        print(f'Gain: ${gain}, % Gain: {perc_gain}%, LOSS')
                        print()
                        self.losses.append([symbol, option_type, closing_strategy, exp, strike, gain, str(perc_gain) + '%'])

                    short_trading_dict[symb_exp_strike_type+'_quantity'] -= quantity

                    #if holding position = 0, then pop chain_symbol avgprice and chain_symbol quantity

                    if short_trading_dict[symb_exp_strike_type+'_quantity'] == 0:

                        short_trading_dict.pop(symb_exp_strike_type+'_avgprice')
                        short_trading_dict.pop(symb_exp_strike_type+'_quantity')
                        short_symbol_strike_exp_type_list.remove(symb_exp_strike_type)


        print()



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

            total = round(avg_price * quantity * 100,2)


            symb_exp_strike_type = f'{symbol} {exp} {strike} {option_type}'

            if symb_exp_strike_type in long_symbol_strike_exp_type_list and opening_strategy in ['long_call', 'long_put'] and exp < date.today():

                print(f'Expired: {symbol} {option_type}, {opening_strategy}, Expiration: {exp}, Strike: {strike}, Quantity: {quantity}, Avg Price: ${avg_price} Total: ${total}')

                self.losses.append([symbol, option_type, opening_strategy, exp, strike, total*-1, '-100%'])
                self.total_optionsloss -= total


            if symb_exp_strike_type in short_symbol_strike_exp_type_list and opening_strategy in ['short_call', 'short_put'] and exp < date.today():

                print(f'Expired: {symbol} {option_type}, {opening_strategy}, Expiration: {exp}, Strike: {strike}, Quantity: {quantity}, Avg Price: ${avg_price} Total: ${total}')

                self.gains.append([symbol, option_type, opening_strategy, exp, strike, total, '100%'])
                self.total_optionsgain += total


        print('\n')


    def get_gains_losses(self):

        print()

        print(f'Total Options Gain: ${self.total_optionsgain}')
        print(f'Total Options Loss: ${self.total_optionsloss}')


        self.gains_df = pd.DataFrame(self.gains, columns = ['Symbol', 'Option Type', 'Strategy', 'Expiration', 'Strike', 'Gain', '% Gain'])
        self.losses_df = pd.DataFrame(self.losses, columns = ['Symbol', 'Option Type', 'Strategy', 'Expiration', 'Strike', 'Gain', '% Gain'])


        self.gains_df['Expiration'] = self.gains_df['Expiration'].astype(str).str.replace(' 00:00:00', '')
        self.losses_df['Expiration'] = self.losses_df['Expiration'].astype(str).str.replace(' 00:00:00', '')
        self.gains_df['Gain'] = self.gains_df['Gain'].astype('float64')
        self.losses_df['Gain'] = self.losses_df['Gain'].astype('float64')


        print('\n')
        print('Top Option Gainers:')
        display(self.gains_df.sort_values('Gain', ascending=False).reset_index(drop=True))

        print()
        print('Top Option Losers:')
        display(self.losses_df.sort_values('Gain').reset_index(drop=True))
