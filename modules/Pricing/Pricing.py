import pytz
import datetime
import json
import time
import numpy as np
import pandas as pd
from math import *
from modules.Db.Helper import *
from scipy.stats import norm
from modules.Chain import Chain


# import pandas as pd
# import numpy as np
from scipy.signal import savgol_filter
import time
import random
from functools import reduce
# from chart_studio.plotly import iplot as py
# import plotly.express as px
# import plotly.graph_objects as go
# import plotly.figure_factory as ff
import matplotlib.pyplot as plt
# import modules.Pricing

def rolling_window_calc(df_input, win_size= 6, min_periods=1, verbose= False, plotting=False):

    """
    win_size :: number of months to run the rolling average
    min_periods ::

    """
    start = time.time()
    print('running rolling_window_calc..')

    cols = df_input.columns.tolist()
    df = pd.DataFrame()
    df_output = pd.DataFrame()

    if verbose: print('processing ' + str(df_input.shape[1]) + ' columns.'); print('col number: '); count = 0;
    for col in cols:
        count += 1
        if verbose and count % 500 == 0: print('col ' + str(count) + ' col_name: ' + str(col))

        # Normalize the data
        A = np.nanmin(df_input[col], axis=0)
        B = np.nanmax(df_input[col], axis=0)-np.nanmin(df_input[col], axis=0)
        y = (df_input[col] - A) / B if B > 0 else df_input[col]
        df['data'] = y
        df['mean'] = y.rolling(win_size, min_periods).mean()
        # df['std'] = y.rolling(win_size, min_periods=1).std()
        # df['median'] = y.rolling(win_size, min_periods=1).median()

        # De-Normalize the data
        df_output[col] = A + (df['mean'] * B) if B > 0 else df['mean']

        if plotting:
            x = np.arange(len(y))
            plt.plot(x,df['data'], 'lightgray', label='data');
            plt.plot(x,df['mean'], 'green', label='rolling mean');
            #plt.plot(x,df['median'], 'red', label='rolling median');
            #plt.plot(x,df['std'], 'lightblue', label='rolling std');

    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())

    end = time.time()
    print('time: ', "{0:.2f}".format(end - start))

    return df_output

def visualize_rolling_win(df_before, df_after, n_samples= 8, random_state= 100):
    random.seed(random_state)
    n_samples = n_samples
    plt.figure(figsize = (20, n_samples*3))
    count = 1
    while count < 2 * n_samples:
        col = random.choice(df_before.columns)
        if df_before[col].isnull().sum() == 0:
            x = np.arange(len(df_before[col]))
            plt.subplot(n_samples,4,count)
            plt.plot(x,df_before[col], 'lightgray', label='imputed data')
            plt.plot(x,df_after[col], 'blue', label='despiked data')
            plt.legend()
            count += 1

def savgol_filter_smoothing(df_input, sg_window_length, sg_polyorder, sg_mode='nearest', verbose=False):
    """
    ip_method :: ‘linear’: Ignore the index and treat the values as equally spaced.
    ip_limit :: Maximum number of consecutive NaNs to fill. Must be greater than 0.
    """
    start = time.time()
    print('running savgol_filter_smoothing..')

    cols = df_input.columns.tolist()
    df_output = df_input.copy(deep=True)

    for col in cols:

        y_input = np.array(df_output[col])
        y_smooth = savgol_filter(y_input, window_length= sg_window_length, polyorder= sg_polyorder, mode= sg_mode)

        # Make sure smoothing process doesn't add more missing values: if it does, then overwrite the NaN from input data
        if np.count_nonzero(~np.isnan(y_input)) > np.count_nonzero(~np.isnan(y_smooth)):
            #print(np.count_nonzero(np.isnan(y_input)), np.count_nonzero(np.isnan(y_smooth)))
            not_null_y = pd.Series(list(map(int, ~np.isnan(y_input))))
            null_ysmooth = pd.Series(list(map(int, np.isnan(y_smooth))))
            mask_list = not_null_y * null_ysmooth
            y_add = mask_list * y_input
            y_smooth_filled = np.nan_to_num(y_smooth)
            #print(y_smooth)
            y_smooth = np.array(y_smooth_filled + y_add)
            #print(y_smooth)
            #break
            #print(np.count_nonzero(np.isnan(y_input)), np.count_nonzero(np.isnan(y_smooth)),'\n')

        df_output[col] = y_smooth
        #print(df_output[col].isnull().sum())

    # print results
    if verbose:
        print('Input DataFrame:')
        print('- shape: ', df_input.shape)
        print('- Null Counts: ', df_input.isnull().sum().sum())
        print('Output DataFrame:')
        print('- shape: ', df_output.shape)
        print('- Null Counts: ', df_output.isnull().sum().sum())

    end = time.time()
    print('time: ',"{0:.2f}".format(end - start))

    return df_output


"""
Newton Method
"""
def find_vol(target_value, call_put, S, K, T, r):
    MAX_ITERATIONS = 10
    PRECISION = 1.0e-2

    sigma = 0.5
    for i in range(0, MAX_ITERATIONS):
        price = bs_price(call_put, S, K, T, r, sigma)
        vega = bs_vega(call_put, S, K, T, r, sigma)

        price = price
        diff = target_value - price  # our root
		
        if (abs(diff) < PRECISION):
            return sigma
        sigma = sigma + diff/vega 
	# value wasn't found, return best guess so far
    return sigma

"""
Black-Scholes FORMULA, Option Price
"""
def bs_price(cp_flag,S,K,T,r,v,q=0.0):
    N = norm.cdf

    d1 = (np.log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
    d2 = d1-v*sqrt(T)
    if cp_flag == 'c':
        price = S*exp(-q*T)*N(d1)-K*exp(-r*T)*N(d2)
    else:
        price = K*exp(-r*T)*N(-d2)-S*exp(-q*T)*N(-d1)
    return price

"""
VEGA
"""
def bs_vega(cp_flag,S,K,T,r,v,q=0.0):
    n = norm.pdf
    d1 = (log(S/K)+(r+v*v/2.)*T)/(v*sqrt(T))
    return S * sqrt(T)*n(d1)

def setPutcall(symbol):
    try:
        if(symbol.split("_")[1][6]=="P"):
            return "p"
        else:
            return "c"
    except IndexError:
        return None

"""
Calculate time to expiry
"""
def setTimeToExpiry(symbol):
    try:
        chainExpirationDate = Chain.convertSymbolDate(symbol.split("_")[1]).split("-")
        timetoexpiry = ((datetime.date(
                            int(chainExpirationDate[0]),
                            int(chainExpirationDate[1]),
                            int(chainExpirationDate[2])
                        )
                        - datetime.datetime.now(tz = pytz.timezone('US/Eastern')).date()
                    ).days + 1) / 365
        return timetoexpiry
    except IndexError:
        return None

"""
Calculate Polyfit
"""
#     in_window_length = 5
#     in_polyorder = 3
#     in_mode = 'nearest'
def calculate(lastunderlying, chain, symbol, ivAdjustment, polyValue, message, in_window_length=5, in_polyorder = 3, in_mode = 'nearest'):
    start = time.time()
    optionPriceBidList = []
    optionPriceAskList = []
    optionDelta = {}
    optionTheta = {}
    optionVolatility = {}
    marketBid = {}
    marketAsk = {}
    bidSize = {}
    askSize = {}
    strikeList = []
    filteredDeltas = []
    filteredTheta = []
    filteredVolatility = []
    filteredMarketBid = []
    filteredMarketAsk = []
    filteredBidSize = []
    filteredAskSize = []
    runtimes = []
    IVatBID = []
    IVatASK = []
    STRIKEFILTERED = []
    timestamps = []

    """
    normalize chain
    """
    if(chain.get("underlying", None)):
        del chain["underlying"]

    """
    handle putcall and time to expiry
    """
    cp = setPutcall(symbol)
    timeToExpiry = setTimeToExpiry(symbol)

    """
    extract price, delta, theta, volatility from chain strikes
    """
    for strike in chain.keys():
        optionPriceBidList.append(float(chain[strike][0]["bid"]))
        optionPriceAskList.append(float(chain[strike][0]["ask"]))
        optionDelta.update({strike: float(chain[strike][0]["delta"])})
        optionTheta.update({strike: float(chain[strike][0]["theta"])})
        optionVolatility.update({strike: float(chain[strike][0]["volatility"])})
        marketBid.update({strike: float(chain[strike][0]["bid"])})
        marketAsk.update({strike: float(chain[strike][0]["ask"])})
        bidSize.update({strike: float(chain[strike][0]["bidSize"])})
        askSize.update({strike: float(chain[strike][0]["askSize"])})
        strikeList.append(float(strike))

    optionprice_bid = np.array(optionPriceBidList)
    optionprice_ask = np.array(optionPriceAskList)
    strike = np.array(strikeList)
    riskfreerate = 0.01
    
    ## LOOP THRU ALL PRICES AND STRIKES
    try:
        for i in range(0, len(strike)):
            K = strike[i]
            T = timeToExpiry
            S = lastunderlying
            r = riskfreerate
            calcdIVatBID = round((find_vol(optionprice_bid[i], cp, S, K, T, r)),4)
            calcdIVatASK = round((find_vol(optionprice_ask[i], cp, S, K, T, r)),4)
            """
            filter outliers - negative IV is invalid, too high IV for DeepITM strikes doesn't make sense
            """
            if(calcdIVatBID > 0 
                    and calcdIVatBID < 3 
                    and calcdIVatASK > 0 
                    and calcdIVatASK < 3
                    and isnan(calcdIVatASK) is False
                    and isnan(calcdIVatBID) is False): 	 
                IVatBID = np.append(IVatBID, calcdIVatBID)
                IVatASK = np.append(IVatASK, calcdIVatASK)
                STRIKEFILTERED = np.append(STRIKEFILTERED, K)
        ##consider risk that bid and ask filtered outliers are diff, resulting in diff size arrays	
    except ZeroDivisionError:
        print('Trying to divide by zero at ', symbol)
        return None

    """
    OBTAIN VOLATILITY SMILE BY FITTING A CURVE THROUGH THE PRICES by STRIKE
    x-axis = list of strikes
    y-axis = list of values to be fit
    """
    BidIVFitRaw = np.polyfit(STRIKEFILTERED,IVatBID,polyValue)
    AskIVFitRaw = np.polyfit(STRIKEFILTERED,IVatASK,polyValue)
    """
    CREATE POLYNOMIAL OBJECT
    """
    BidIVFitPoly = np.poly1d(BidIVFitRaw)
    AskIVFitPoly = np.poly1d(AskIVFitRaw)
    """
    OUTPUT IV based on FIT
    """
    BidIVFit = np.around(BidIVFitPoly(STRIKEFILTERED), decimals=3)
    AskIVFit = np.around(AskIVFitPoly(STRIKEFILTERED), decimals=3)
    print("IVatBID", IVatBID)
    print('-------------------')
    print("STRIKEFILTERED", STRIKEFILTERED)
    print('-------------------')
    print("BidIVFitRaw: ", BidIVFitRaw)
    print('-------------------')
    print("BidIVFitPoly: ", BidIVFitPoly)
    print('-------------------')
    print("BidIVFit: ", BidIVFit)
    print('-------------------')

#     in_window_length = 5
#     in_polyorder = 3
#     in_mode = 'nearest'
    BidIVFitSavgol = savgol_filter_smoothing(pd.DataFrame(IVatBID), sg_window_length= in_window_length, sg_polyorder= in_polyorder)
    AskIVFitSavgol = savgol_filter_smoothing(pd.DataFrame(IVatASK), sg_window_length= in_window_length, sg_polyorder= in_polyorder)
#     print("BidIVFitSavgol: ", BidIVFitSavgol)
#     print('-------------------')
#     ts = pd.Series(df['Value'].values, index=df['Date'])
    BidIVFitSavgolSeries = pd.Series(BidIVFitSavgol[0].values, index=BidIVFitSavgol[0].index)
#     print("BidIVFitSavgolSeries: ", BidIVFitSavgolSeries)
#     print('-------------------')

    BidIVFitSavgolList = list(BidIVFitSavgol[0].values)
    print("BidIVFitSavgolList: ", BidIVFitSavgolList)
    print('-------------------')

    AskIVFitSavgolList = list(AskIVFitSavgol[0].values)
    print("AskIVFitSavgolList: ", AskIVFitSavgolList)
    print('-------------------')

    if message == "savgol":
#         , in_window_length=5, in_polyorder = 3, in_mode = 'nearest'
        message = message + '_' + str(in_window_length) + '_' + str(in_polyorder) + '_' + in_mode
        BidIVFit = np.array(BidIVFitSavgolList)
        print("BidIVFitArray: ", BidIVFit)
        print('-------------------')
        AskIVFit = np.array(AskIVFitSavgolList)
        print("message: ", message)
        print('-------------------')

    """   --- Add +ivAdjustment above -- 
    OUTPUT PRICES BASED ON FIT IV
    """
    OutputBids = np.around(bs_price(cp,lastunderlying,STRIKEFILTERED,timeToExpiry,riskfreerate,BidIVFit), decimals=3)
    OutputAsks = np.around(bs_price(cp,lastunderlying,STRIKEFILTERED,timeToExpiry,riskfreerate,AskIVFit), decimals=3)
    """
    extract filtered prices, deltas, theta, volatility
    """
    for finalStrike in STRIKEFILTERED.tolist():
        filteredDeltas.append(optionDelta[str(finalStrike)])
        filteredTheta.append(optionTheta[str(finalStrike)])
        filteredVolatility.append(optionVolatility[str(finalStrike)])
        filteredMarketBid.append(marketBid[str(finalStrike)])
        filteredMarketAsk.append(marketAsk[str(finalStrike)])
        filteredBidSize.append(bidSize[str(finalStrike)])
        filteredAskSize.append(askSize[str(finalStrike)])
        timestamps.append(str(datetime.datetime.now()))
        end = time. time()
        runtimes.append(end - start)
        
    pricing = pd.DataFrame(zip(STRIKEFILTERED
                                ,IVatBID
                                ,IVatASK
                                ,BidIVFit
                                ,AskIVFit
                                ,filteredDeltas
                                ,filteredTheta
                                ,filteredVolatility
                                ,filteredMarketBid
                                ,filteredMarketAsk
                                ,OutputBids
                                ,OutputAsks
                                ,filteredBidSize
                                ,filteredAskSize
                                ,timestamps
                                ,runtimes
        ),
        columns=["strike"
                    ,"ivAtBid"
                    ,"ivAtAsk"
                    ,"BidIVFit"
                    ,"AskIVFit"
                    ,"delta"
                    ,"theta"
                    ,"volatility"
                    ,"marketBid"
                    ,"marketAsk"
                    ,"CalculatedBid"
                    ,"CalculatedAsk"
                    ,"bidSize"
                    ,"askSize"
                    ,"timestamp"
                    ,"runtime"
    ])
    orderStrike = float(symbol.split("_")[1][7:])
    # print(orderStrike)

    try:
        # print(pricing)
        calculatedPricing = pricing[pricing.strike == orderStrike].iloc[0]
        pricing = Pricing(
            underlying = lastunderlying
            , symbolId = symbol
            , delta = calculatedPricing.delta
            , bidPrice = calculatedPricing.CalculatedBid
            , bidSize = calculatedPricing.bidSize
            , bidMarket = calculatedPricing.marketBid
            , askPrice = calculatedPricing.CalculatedAsk
            , askSize = calculatedPricing.askSize
            , askMarket = calculatedPricing.marketAsk
            , ivAtBid = calculatedPricing.ivAtBid
            , ivAtAsk = calculatedPricing.ivAtAsk
            , strikes = json.dumps(STRIKEFILTERED.tolist())
            , ivBidMarket = json.dumps(IVatBID.tolist())
            , ivAskMarket = json.dumps(IVatASK.tolist())
            , ivBidFit = json.dumps(BidIVFit.tolist())
            , ivAskFit = json.dumps(AskIVFit.tolist())
            , comment = message
            , timestamp = datetime.datetime.now()
            )
        Session.add(pricing)
        Session.commit()

        return calculatedPricing
    except IndexError:
        print("Strike not found")
        return None