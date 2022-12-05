import datetime

date_str = '%d-%m-%Y'
print_or_no = 0
title_font_sz = 14
font_style = 'Lucida Console, monospace' #Inconsolata, monospace; Spartan, sans-serif;' #"Roboto, monospace"  # "Courier New, monospace"

historical_days_to_pull = 10

#KEYS
ticker_key = "ticker"
price_record_key = 'prices'

#EMAIL
EMAIL = ""
FROM_EMAIL = EMAIL #''
MAILJET_API_KEY = ''
MAILJET_API_SECRET = ''

WEBSITE_NAME = 'fondue.finance'
password = "yieldmustbehigh1" #mongo login

#DOWNLOAD
cryptocompare_API_key = ""
ARCHIVE_NODE_API_KEY = ''
#polygon_API_key = ""

MONGO_URL = ""

USE_IN_MEMORY_DB_OR_NO = True
number_of_trials = 50

tkr_BTC = 'BTC'
tkr_ETH = 'ETH'
tkr_WBTC = 'WBTC'
tkr_WETH = 'WETH'

tkr_USDC = 'USDC'
tkr_USDT = 'USDT'
tkr_DAI = 'DAI'
tkr_FRAX = 'FRAX'
tkr_MIM = 'MIM'

tkr_AVAX = 'AVAX'
tkr_MATIC = 'MATIC'
tkr_SUSHI = 'SUSHI'
tkr_UNISWAP = 'UNI'
tkr_SOLANA = 'SOL'

STABLECOINS = [tkr_USDC,tkr_USDT,tkr_DAI,tkr_MIM]

fitness_STABLECOINS =       'stablecoins'
fitness_LOW_VOLATILITY =    'low volatility'
fitness_BALANCED =          'balanced'
fitness_BULLISH =           'bullish'
#low impermanent loss?
#high interest rate

FITNESS_DD = [
    {'label': fitness_STABLECOINS, 'value': fitness_STABLECOINS},
    {'label': fitness_LOW_VOLATILITY, 'value': fitness_LOW_VOLATILITY},
    {'label': fitness_BALANCED, 'value': fitness_BALANCED},
    {'label': fitness_BULLISH, 'value': fitness_BULLISH},
           ]

chain_ETHEREUM = 'Ethereum'
chain_POLYGON = 'Polygon'
chain_AVALANCHE = 'Avalanche'
chain_BNB = 'Binance Smart Chain'
chain_BITCOIN = 'Bitcoin'

coin_network_dict = {
    tkr_ETH:        chain_ETHEREUM,
    tkr_WBTC:       chain_ETHEREUM,
    tkr_MATIC:      chain_POLYGON,
    tkr_AVAX:       chain_AVALANCHE,
    tkr_WETH:       chain_ETHEREUM,
    tkr_USDT:       chain_ETHEREUM,
    tkr_USDC:       chain_ETHEREUM,
    tkr_BTC:        chain_BITCOIN,
    tkr_FRAX:       chain_ETHEREUM,
    tkr_MIM:        chain_ETHEREUM,
}



pool_BALANCER = 'Balancer'
pool_AAVE = 'Aave'
pool_UNISWAP = 'Uniswap'
pool_CURVE = 'Curve'

type_TRADING = 'trading'
type_LENDING = 'lending'

#pool_address_dict_cols = []

pool_address_dict = {
    #address: (pool provider, list of coins, trading or lending, trading fee, interest rate)
    '0x5c6ee304399dbdb9c8ef030ab642b10820db8f56': (pool_BALANCER, chain_ETHEREUM, [tkr_USDC,tkr_ETH],type_TRADING,0.003),
    '0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5': (pool_AAVE,chain_ETHEREUM,[tkr_USDT],type_LENDING,0),
    '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8': (pool_UNISWAP, chain_ETHEREUM, [tkr_USDC,tkr_ETH],type_TRADING,0.003),
    '0xc63b0708e2f7e69cb8a1df0e1389a98c35a76d52': (pool_UNISWAP, chain_ETHEREUM, [tkr_FRAX,tkr_USDC],type_TRADING, 0.003),
    '0xD51a44d3FaE010294C616388b506AcdA1bfAAE46': (pool_CURVE,chain_ETHEREUM,[tkr_USDT,tkr_WBTC,tkr_WETH],0.0012),
}

TOTAL_KEY = 'zzTOTAL'
