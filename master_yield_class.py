import pandas as pd
import mongo
from datetime import datetime, timedelta
import db
import math
import sys
import scipy
from scipy import stats
import statistics
import cython
import numpy as np
import CONSTANTS
import pytz
import time
from optionprice import Option
from pathlib import Path
import threading
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import download
import random
import optuna

np.seterr(divide='ignore', invalid='ignore')

global_yield_and_pf_objects = []

#download.download_full_crypto_data('BTC')
TOTAL_KEY = CONSTANTS.TOTAL_KEY
coin_network_dict = CONSTANTS.coin_network_dict

class master_yield_class:
    def __init__(self):
        self.pools_df = pd.DataFrame({})
        self.time_last_updated = datetime.min

        self.optimal_df = pd.DataFrame({})
        self.starting_portfolio = pd.DataFrame(columns=['ticker','amount','$ value'],index=[])
        self.fitness_to_use = CONSTANTS.fitness_BALANCED
        self.rebalance_frequency = 30
        self.recalculate_total_starting_pf_val()

        self.add_asset_to_pf('ETH',100)
        self.add_asset_to_pf('USDT',10000)
        return

    def retrieve_pool_addresses(self):
        #pull from each blockchain?
        return list(CONSTANTS.pool_address_dict.keys())

    def get_asset_ratios_from_blockchain(self,address):
        print("looking up ratios by address")
        assets = CONSTANTS.pool_address_dict[address][2]
        if len(assets) > 0: return [1/len(assets)] * len(assets)
        return [1.0]

    def get_assets_by_pool_address(self, address):
        if address in list(CONSTANTS.pool_address_dict.keys()):
            assets = CONSTANTS.pool_address_dict[address][2]
            ratios = self.get_asset_ratios_from_blockchain(address)
            if len(assets) != len(ratios):
                print("ERROR: RATIOS IS NOT EQUAL TO ASSETS")
                sys.exit()
            return assets,ratios
        return [CONSTANTS.tkr_WBTC,CONSTANTS.ETH], [0.0,0.0]

    def get_TVL_for_pool_address(self,pool_address):
        return random.randrange(100, 600, 25)

    def get_total_estimated_return_by_pool_address(self, pool_address):
        sum_of_yields = self.get_interest_rate_by_pool_address(pool_address)
        sum_of_yields += self.get_trading_rewards_by_pool_address(pool_address)
        sum_of_yields += self.get_token_rewards_yield_by_pool_address(pool_address)
        sum_of_yields += self.get_impermanent_loss_by_pool_address(pool_address)

        return float(random.randrange(2, 25, 1)) / 100

    def get_interest_rate_by_pool_address(self,pool_address):
        return 0.0

    def get_trading_rewards_by_pool_address(self,pool_address):
        #get volume
        return 0.0

    def get_impermanent_loss_by_pool_address(self,pool_address):
        return 0.0

    def get_token_rewards_yield_by_pool_address(self,pool_address):
        return 0.0

    def get_volatility_of_USD_value_of_pool(self,pool_address):
        return float(random.randrange(15, 55, 6)) / 100

    def get_amplitude_of_USD_value_of_pool(self,pool_address,days):
        return 0.0

    def get_historical_return_by_pool_address(self,pool_address,days):
        return float(random.randrange(5,20,5))/100

    def get_normalised_score_by_pool_address(self,pool_address):
        return random.randrange(4, 16, 1)

    def get_security_score_by_pool_address(self,pool_address):
        return 0.0

    def get_estimated_return_adjusted_for_fitness_by_pool_address(self,pool_address):
        ret = self.get_total_estimated_return_by_pool_address(pool_address)
        adj = 0.0

        if self.fitness_to_use == CONSTANTS.fitness_STABLECOINS: adj = 0.0
        if self.fitness_to_use == CONSTANTS.fitness_LOW_VOLATILITY: adj = 0.0
        if self.fitness_to_use == CONSTANTS.fitness_BALANCED: adj = 0.0
        if self.fitness_to_use == CONSTANTS.fitness_BULLISH: adj = 0.0

        #get drawdown / amplitude
        #different weights to different scenarios
        return ret + adj

    def update_pools_data(self):
        yield_df_columns = ['Provider', 'Chain', 'Address',
                            'Assets', 'Ratios', #5
                            'TVL', 'stable', 'lending / trading', #4
                            'ESTIMATED TOTAL RETURN',
                            'ESTIMATED TOTAL RETURN - ADJUSTED',
                            'volatility',  #2
                            'SCORE',
                            'security rating',
                            'HISTORICAL RETURN - 3M', #3

                            'hidden - estimated return from INTEREST',
                            'hidden - estimated return from TRADES',
                            'hidden - estimated return from TOKEN REWARDS',
                            'hidden - estimated return from IMPERMANENT LOSS',
                            'hidden - historical AMPLITUDE in asset values',
                            
                            #'hidden - L3m return',
                            'hidden - assets list', #original list
                            'hidden - ratios list', #original list
                            ]
        addresses = self.retrieve_pool_addresses()
        print(f"Addresses: {addresses}")
        data = []
        for el in addresses:
            provider = CONSTANTS.pool_address_dict[el][0]
            chain = CONSTANTS.pool_address_dict[el][1]
            assets, ratios = self.get_assets_by_pool_address(el)

            assets_str = ''
            for i in range(len(assets)):
                if i < len(assets) -1:
                    assets_str += assets[i] + '/'
                else:
                    assets_str += assets[i]

            ratios_str = ''
            for i in range(len(ratios)):
                if i < len(ratios) -1:
                    ratios_str += "{:.0%}".format(ratios[i]) + ':'
                else:
                    ratios_str += "{:.0%}".format(ratios[i])

            stable = all([elll in CONSTANTS.STABLECOINS for elll in assets]) #all_stablecoins
            print(f"el: {el}")
            lend_or_trade = CONSTANTS.pool_address_dict[el][3]

            TVL = self.get_TVL_for_pool_address(el)

            calced = [provider] + [chain] + [el] + [assets_str] + [ratios_str]
            calced += [TVL]
            calced += [stable] + [lend_or_trade]
            calced += [self.get_total_estimated_return_by_pool_address(el)] #ESTIMATED TOTAL RETURN

            calced += [self.get_estimated_return_adjusted_for_fitness_by_pool_address(el)]  #ADJUSTMENT FOR FITNESS

            calced += [self.get_volatility_of_USD_value_of_pool(el)] #VOLATILITY
            calced += [self.get_normalised_score_by_pool_address(el)] #[14.2] #score
            calced += [self.get_security_score_by_pool_address(el)] #security rating
            calced += [self.get_historical_return_by_pool_address(el,90)] #hist return

            calced += [self.get_interest_rate_by_pool_address(el)] #hist return
            calced += [self.get_trading_rewards_by_pool_address(el)] #hist return
            calced += [self.get_token_rewards_yield_by_pool_address(el)] #hist return
            calced += [self.get_impermanent_loss_by_pool_address(el)] #hist return
            calced += [self.get_amplitude_of_USD_value_of_pool(el,30)] #hist return

            calced += [assets] + [ratios]
            data.append(calced)

        self.pools_df = pd.DataFrame(index=addresses, columns=yield_df_columns, data=np.array(data))  # here populate df
        return

    def get_pools_data_fig(self):
        fig_pools_dataframe = make_subplots(
            rows=1, cols=1,
            vertical_spacing=0.025,
            specs=[
                [{"type": "table"}],
            ]
        )

        self.update_pools_data()

        df = self.pools_df.copy()
        #print("Df: ", df)

        if len(df) > 0:
            for el in list(df.columns):
                #print("el: ", el)
                if 'hidden' in el: df = df.drop(el, axis=1)
                #print(df)
                #print("------------")

        headers = list(df.columns)
        vals = df.transpose().values.tolist()

        fig_pools_dataframe.add_trace(go.Table(
            columnwidth=[0.3, 0.25, 0.7, 0.3, 0.25, 0.25, 0.25, 0.25],
            header=dict(values=headers,
                        fill_color='cadetblue', #'lightsteelblue', 'darkcyan',
                        font=dict(color=['rgb(45,45,45)'], size=12.5),
                        align='left'),
            cells=dict(values=vals,
                       fill_color='lavenderblush',
                       align='left',
                       font=dict(color=['rgb(45,45,45)'], size=12.5),
                       format=[None, None, None, None, None,",.1f", None, None, ",.1%"],
                       height=17.75,
                       ),
        )
            , row=1, col=1
        )

        fig_pools_dataframe.update_layout(margin=dict(l=0, r=0, t=0, b=0), )
        return fig_pools_dataframe

    def get_exch_rate(self,ticker):
        if ticker in CONSTANTS.STABLECOINS: return 1.00
        if ticker == CONSTANTS.tkr_WETH: ticker = CONSTANTS.tkr_ETH
        if ticker == CONSTANTS.tkr_WBTC: ticker = CONSTANTS.tkr_BTC

        if CONSTANTS.USE_IN_MEMORY_DB_OR_NO:
            if ticker not in db.data_db.keys():
                print("DATA NOT FOUND")
                return 0.999
            print("777 - PULLING FROM IN MEMORY DB: ")
            lenpx = len(db.data_db[ticker][db.in_memory_db_date_key]) - 1
            print(db.data_db[ticker][db.in_memory_db_date_key][0],db.data_db[ticker][db.in_memory_db_date_key][lenpx])
            return db.data_db[ticker][db.price_key][lenpx - 1]

        dt = datetime.now() - timedelta(days=CONSTANTS.historical_days_to_pull)
        px = mongo.retrieve_record_series_attribute_recent(ticker,CONSTANTS.price_record_key,dt)
        if len(px[0]) == 0:
            dt = datetime.now() - timedelta(days=CONSTANTS.historical_days_to_pull)
            px = mongo.retrieve_record_series_attribute_recent(ticker, CONSTANTS.price_record_key, dt)
        if len(px[0]) == 0:
            print("DATA NOT FOUND")
            return 0.999
        #print(dt,px)
        #print(len(px))
        #print("time / price of ", ticker, ":",px[0][len(px[0])-1], px[1][len(px[1])-1])

        #print("TICKERS LOADED IN INMEMORY DB: ")
        #print(db.data_db.keys())

        return px[1][len(px[1])-1]

    #OPTIMISATION
    def recalculate_total_starting_pf_val(self):
        total = 0.0

        for el in list(self.starting_portfolio.index):
            if el is not TOTAL_KEY: total +=  self.starting_portfolio.loc[el]['$ value']

        self.starting_portfolio.loc[TOTAL_KEY] = ['TOTAL',0,total]

        self.starting_portfolio = self.starting_portfolio.sort_index()

        return


    def add_asset_to_pf(self,ticker,value):
        print("in class func - adding asset to pf")
        exch_rate = self.get_exch_rate(ticker)
        if ticker in list(self.starting_portfolio.index):
            old_val = self.starting_portfolio.loc[ticker]['amount']
            self.starting_portfolio.loc[ticker] = [ticker,old_val+value,(old_val+value)*exch_rate]
        else:
            self.starting_portfolio.loc[ticker] = [ticker,value,value*exch_rate]
        self.recalculate_total_starting_pf_val()
        return

    def delete_asset_from_pf(self,ticker):
        if ticker in list(self.starting_portfolio.index):
            self.starting_portfolio = self.starting_portfolio.drop(ticker)
        self.recalculate_total_starting_pf_val()
        return

    def get_starting_portfolio_fig(self):
        headers1 = list(self.starting_portfolio.columns)
        vals1 = self.starting_portfolio.transpose().values.tolist()

        fig_starting_portfolio = make_subplots(
            rows=1, cols=1,
            vertical_spacing=0.025,
            specs=[
                [{"type": "table"}],
            ]
        )

        fig_starting_portfolio.add_trace(go.Table(
            columnwidth=[0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.25],
            header=dict(values=headers1,
                        fill_color='cadetblue', #'lightsteelblue',
                        font=dict(color=['rgb(45,45,45)'], size=12.5),
                        align='left'),
            cells=dict(values=vals1,
                       fill_color='lavenderblush',
                       align='left',
                       font=dict(color=['rgb(45,45,45)'], size=12.5),
                       format=[None, ",.2f", ",.2f"],  # , ",.0%", ",.1%"
                       height=17.75,
                       ),
        )
            , row=1, col=1
        )

        fig_starting_portfolio.update_layout(margin=dict(l=0, r=0, t=0, b=0), )

        return fig_starting_portfolio

    def get_gas_fees_from_pf_weights(self,settings_dict):
        if self.fitness_to_use == CONSTANTS.fitness_BALANCED: pools_df = self.pools_df.copy()
        if self.fitness_to_use == CONSTANTS.fitness_STABLECOINS: pools_df = self.pools_df.copy()

        #1 - calculate minimum number of transfers - assume NO SWAPS REQUIRED
        gas_fees_from_transfers_only = 0.0 #BY NUMBER OF TRANSFERS

        assets_in_resultant_pf_USD = {}
        assets_in_resultant_pf_units = {}

        print("weights: ", settings_dict, sum(settings_dict.values()))
        print("228 - pools df: ", pools_df)
        print("134: ", self.starting_portfolio)
        print("133 - starting PF val: ", self.starting_portfolio.loc[TOTAL_KEY]['$ value'])

        for el in list(settings_dict.keys()):
            print("el: ", el)
            a = pools_df.loc[el]['hidden - assets list']
            w = pools_df.loc[el]['hidden - ratios list']
            print(a,w)

            est_amt = settings_dict[el] * self.starting_portfolio.loc[TOTAL_KEY]['$ value']
            print("135: ", est_amt)

            for el in zip(a, w):
                print(el[0],el[1])
                if el[0] in assets_in_resultant_pf_USD.keys(): assets_in_resultant_pf_USD[el[0]] += el[1] * est_amt
                if el[0] not in assets_in_resultant_pf_USD.keys(): assets_in_resultant_pf_USD[el[0]] = el[1] * est_amt

                if el[0] in assets_in_resultant_pf_units.keys(): assets_in_resultant_pf_units[el[0]] += el[1] * est_amt / self.get_exch_rate(el[0])
                if el[0] not in assets_in_resultant_pf_units.keys(): assets_in_resultant_pf_units[el[0]] = el[1] * est_amt / self.get_exch_rate(el[0])

                print(assets_in_resultant_pf_USD)

        print("assets_in_resultant_pf USD: ", assets_in_resultant_pf_USD)
        print("assets_in_resultant_pf units: ", assets_in_resultant_pf_units)

        #number_of_unique_assets
        for el in assets_in_resultant_pf_USD:
            gas_fees_from_transfers_only += self.get_gas_fee(el,assets_in_resultant_pf_USD[el])

        print("137 - MIN EST GAS FEES: ", gas_fees_from_transfers_only)
        print("138 - ASSETS NOW: ", self.starting_portfolio)
        print("139 - ASSETS AFTER SWAP: ", assets_in_resultant_pf_units)

        starting_pf_dict = {}
        for el in list(self.starting_portfolio.index):
            if el == TOTAL_KEY: continue
            starting_pf_dict[el] = self.starting_portfolio.loc[el]['amount']

        dict_of_swaps_to_get_to_target_pf = {}
        for item in starting_pf_dict.keys():
            if item in assets_in_resultant_pf_units.keys():
                dict_of_swaps_to_get_to_target_pf[item] = assets_in_resultant_pf_units[item] - starting_pf_dict[item]
            if item not in assets_in_resultant_pf_units.keys():  # means it was sold
                dict_of_swaps_to_get_to_target_pf[item] = -starting_pf_dict[item]

        for item in assets_in_resultant_pf_units.keys():
            if item not in starting_pf_dict.keys(): dict_of_swaps_to_get_to_target_pf[item] = assets_in_resultant_pf_units[item]

        print("Intersects:", dict_of_swaps_to_get_to_target_pf)
        print("trades: ", len(dict_of_swaps_to_get_to_target_pf.keys()))

        fees_from_transfers = gas_fees_from_transfers_only  # 2x - stake + unstake - #sum of fees for transfers
        fees_from_swaps = len(dict_of_swaps_to_get_to_target_pf.keys())  # sum of fees for swaps

        return fees_from_transfers,fees_from_swaps

    #####OBJECTIVE FUNCTION
    def optuna_objective_func_new(self,trial, pf_weights):
        settings_dict = dict(pf_weights)

        self.unallocated_starting_pf = self.starting_portfolio.copy()
        sum_of_weights_so_far = 0.0
        print("----")

        #choose random assets
        for el in list(settings_dict.keys()):
            start = 0.0
            step = 0.01
            end = 1.0 - sum_of_weights_so_far - step

            if el == list(settings_dict.keys())[-1]:
                step = 0.01
                start = max(1.00 - sum_of_weights_so_far - step * 1.0,0.0)
                end = max(1.00 - sum_of_weights_so_far,step)
                print("last: ", start,end,step)
                settings_dict[el] = trial.suggest_discrete_uniform(el, start, end, step)
            else:
                if start != 0.0:
                    if end % start == 0.0: end = end - step

                settings_dict[el] = trial.suggest_discrete_uniform(el, start, end, step)

            sum_of_weights_so_far += settings_dict[el]
            print("uniform trials: ", settings_dict[el],type(settings_dict[el]),' sum: ', sum_of_weights_so_far)


        if sum_of_weights_so_far > 1.00:
            print(sum_of_weights_so_far)
            sys.exit("SUM NOT ADDING UP TO 1")
        # apply the weights to get the return
        if self.fitness_to_use == CONSTANTS.fitness_BALANCED: pools_df = self.pools_df.copy()
        if self.fitness_to_use == CONSTANTS.fitness_STABLECOINS: pools_df = self.pools_df.copy()

        ######XXXX
        ######XXXX
        fees_from_transfers,fees_from_swaps = self.get_gas_fees_from_pf_weights(settings_dict)

        #print('337 - TRUTH: ', fees_from_transfers == fees_from_transfers2,fees_from_swaps == fees_from_swaps2)
        #sys.exit()

        portfolio_after_fixed_costs = self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - (fees_from_transfers + fees_from_swaps)
        interest_earned_during_rebal_period = 0.0

        for el in settings_dict:
            raw_return = pools_df.loc[el]['ESTIMATED TOTAL RETURN - ADJUSTED']
            weight_USD_amount = settings_dict[el] * portfolio_after_fixed_costs
            interest_earned_during_rebal_period += weight_USD_amount * (raw_return*self.rebalance_frequency/365)
            print('XXX: ', raw_return, weight_USD_amount, interest_earned_during_rebal_period, portfolio_after_fixed_costs,self.starting_portfolio.loc[TOTAL_KEY]['$ value'])

        blended_return_net_of_fees = (portfolio_after_fixed_costs + interest_earned_during_rebal_period - fees_from_transfers) / self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - 1.00
        blended_return_net_of_fees = blended_return_net_of_fees * 365 / self.rebalance_frequency

        print("scaled weights: ", settings_dict,' sum: ', sum(settings_dict.values()))
        print("blended tgt return: ", blended_return_net_of_fees)
        print("-------------------")

        return -blended_return_net_of_fees #ADJUSTED VERSION

    def optimise_portfolio(self):
        start_time = time.time()

        #rebalance_frequency = self.rebalance_frequency
        number_of_trials = CONSTANTS.number_of_trials

        weights = {}
        optimal_setts = {}
        pools_df = self.pools_df.copy()

        ##################OPTIMISER CODE
        for el in list(self.pools_df.index): weights[el] = 0.0
        study = optuna.create_study() #, fitness_to_use,rebalance_frequency
        study.optimize(lambda trial: self.optuna_objective_func_new(trial, weights), n_trials=number_of_trials)
        for el in list(study.best_params.keys()): optimal_setts[el] = study.best_params[el]

        factor = 1.0 / sum(optimal_setts.values())
        for k in optimal_setts: optimal_setts[k] = optimal_setts[k] * factor

        ######RECONSTRUCT PF NET OF FEES
        settings_dict = dict(optimal_setts)
        fees_from_transfers, fees_from_swaps = self.get_gas_fees_from_pf_weights(settings_dict)

        portfolio_after_fixed_costs = self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - (fees_from_transfers + fees_from_swaps)
        interest_earned_during_rebal_period = 0.0
        interest_earned_during_rebal_period_ADJ = 0.0

        for el in settings_dict:
            raw_return = pools_df.loc[el]['ESTIMATED TOTAL RETURN']
            weight_USD_amount = settings_dict[el] * portfolio_after_fixed_costs
            interest_earned_during_rebal_period += weight_USD_amount * (raw_return*self.rebalance_frequency/365)

            raw_return_ADJ = pools_df.loc[el]['ESTIMATED TOTAL RETURN - ADJUSTED']
            #weight_USD_amount = settings_dict[el] * portfolio_after_fixed_costs
            interest_earned_during_rebal_period_ADJ += weight_USD_amount * (raw_return_ADJ*self.rebalance_frequency/365)

        blended_return_net_of_fees = (portfolio_after_fixed_costs + interest_earned_during_rebal_period - fees_from_transfers) / self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - 1.00
        blended_return_net_of_fees = blended_return_net_of_fees * 365 / self.rebalance_frequency

        blended_return_net_of_fees_ADJ = (portfolio_after_fixed_costs + interest_earned_during_rebal_period_ADJ - fees_from_transfers) / self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - 1.00
        blended_return_net_of_fees_ADJ = blended_return_net_of_fees_ADJ * 365 / self.rebalance_frequency
        ######


        #RECONSTRUCT WEIGHTS INTO A GAS-ADJUSTED RETURN
        print("--------------------------------------------------------")
        print("-------OPTIMAL SETTINGS ARE: ", optimal_setts)
        checksum = 0.0
        for el in optimal_setts: checksum += optimal_setts[el]
        print("sum of weights of optimal: ", checksum)
        print("OPTIMAL RETURN: ", blended_return_net_of_fees)

        ##################OPTIMISER CODE

        idx = list(pools_df.index)
        opt_pf = []

        for el in idx:
            print("populating optimised df: ", el)
            gas = (fees_from_transfers + fees_from_swaps) / len(list(optimal_setts.keys()))
            if el not in optimal_setts.keys():
                x = [CONSTANTS.pool_address_dict[el][0]] + [el] + [0.0] + [0.0] + [pools_df.loc[el]['ESTIMATED TOTAL RETURN']]
                x += [pools_df.loc[el]['ESTIMATED TOTAL RETURN - ADJUSTED']] + [0.0]
            else:
                x = [CONSTANTS.pool_address_dict[el][0]] + [el] + [portfolio_after_fixed_costs*optimal_setts[el]] + [optimal_setts[el]]
                x += [pools_df.loc[el]['ESTIMATED TOTAL RETURN']] + [pools_df.loc[el]['ESTIMATED TOTAL RETURN - ADJUSTED']] + [gas]
            opt_pf.append(x)

        self.optimal_df = pd.DataFrame(index=idx, columns=['provider','pool','amount','%','est return - 1m net of gas','est return - adj','gas cost'],data=opt_pf)
        #print("sum of amts: ", self.optimal_df['amount'].sum())
        totals = ['Total:'] + [0,self.optimal_df['amount'].sum(),self.optimal_df['%'].sum(),blended_return_net_of_fees,blended_return_net_of_fees_ADJ,self.optimal_df['gas cost'].sum()]
        self.optimal_df.loc['Total'] = totals

        #print("STARTING PF VALUE: ", self.optimal_df['amount'].sum(),self.optimal_df['gas cost'].sum(), 'starting: ', self.starting_portfolio.loc[TOTAL_KEY]['$ value'])
        print("DIFF: ",self.starting_portfolio.loc[TOTAL_KEY]['$ value'] - self.optimal_df.loc['Total']['gas cost'] - self.optimal_df.loc['Total']['amount'] , 'starting: ')
        print("---RUNNING OPTIMISATION TOOK: %s seconds ---" % (time.time() - start_time))
        return

    def get_gas_fee(self,ticker,amount):
        network = coin_network_dict[ticker]
        gas = 50.0
        if network == 'Ethereum':   gas = 50.0
        if network == 'Polygon':    gas = 0.01
        return gas

    def get_gas_fee_for_swap(self,from_coin,to_coin):
        gas_fee = 0.01
        from_network = coin_network_dict[from_coin]
        to_network = coin_network_dict[to_coin]
        #if both on ETH:
        if from_network == to_network and to_network == c.chain_ETHEREUM: return self.get_gas_fee(from_coin)
        #if both on Polygon
        return gas_fee


    def get_optimised_portfolio_fig(self):
        self.optimise_portfolio()
        headers2 = list(self.optimal_df)
        vals2 = self.optimal_df.transpose().values.tolist()

        fig_2_optimised_pf = make_subplots(
            rows=1, cols=1,
            vertical_spacing=0.025,
            specs=[
                [{"type": "table"}],
            ]
        )

        fig_2_optimised_pf.update_layout(margin=dict(l=0, r=0, t=0, b=0), )

        fig_2_optimised_pf.add_trace(go.Table(
            columnwidth=[0.25, 0.7, 0.2, 0.2, 0.35, 0.3, 0.4],
            header=dict(values=headers2,
                        fill_color='cadetblue',
                        font=dict(color=['rgb(45,45,45)'], size=12.5),
                        align='left'),
            cells=dict(values=vals2,
                       fill_color='lavenderblush',
                       align='left',
                       font=dict(color=['rgb(45,45,45)'], size=12.5),
                       format=[None, None, ",.0f", ",.1%", ",.1%", ",.1%", ",.1f"],  # , ",.0%", ",.1%"
                       height=17.75,
                       ),
        )
            , row=1, col=1
        )

        return fig_2_optimised_pf

print("setting up master yield class")
global_yield_and_pf_objects.append(master_yield_class())