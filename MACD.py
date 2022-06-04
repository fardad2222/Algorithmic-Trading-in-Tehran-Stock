# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 16:16:27 2021

@author: parsian rayane
"""

# Importing Packages
import requests
import pandas as pd
import numpy as np
from math import floor
from termcolor import colored as cl
import matplotlib.pyplot as plt
import pytse_client as tse
import datetime as dt
import pathlib


plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')
#dt.datetime(2021, 1, 1)
startDate = dt.datetime(2020,8,1)
endDate = dt.datetime(2021,7,29)
daterange = pd.date_range(startDate,endDate)
# Extracting Data from Tehran Stock
#tickers=tse.download(symbols='all', write_to_csv=True, include_jdate=True)
#ticker=tse.download(symbols='کچاد', write_to_csv=True, include_jdate= True)
#kachadd = pd.read_csv("C:/Users/parsian rayane/Desktop/tickers_data")
#kachadd = pd.read_csv("C:/Users/parsian rayane/Desktop/tickers_data/كچاد.csv")


import glob
import os
import pandas as pd   
path = r'C:/Users/parsian rayane/Desktop/AlgoTrading Strategy/tickers_data'                     # use your path
all_files = glob.glob(os.path.join(path, "*.csv"))     # advisable to use os.path.join as this makes concatenation OS independent
df_from_each_file = (pd.read_csv(f) for f in all_files)
kachadd  = pd.concat(df_from_each_file, ignore_index=True)
kachadd = kachadd.iloc[::-1]
kachadd = kachadd.head(35)
#kachadd = pd.Index(kachad[10:60])
#kachad = kachad.set_index("jdate")
#kachadd = kachadd.set_index("jdate")
#kachadd = kachadd.loc["1400-04-04":"1400-05-11"]
#print(kachad.loc[5:30])
print(kachadd)


#kachadd = pd.Index(kachad[0:60])

# MACD Calculation
def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
    hist = pd.DataFrame(macd['macd'] - signal['signal']).rename(columns = {0:'hist'})
    frames =  [macd, signal, hist]
    df = pd.concat(frames, join = 'inner', axis = 1)
    return df

kachadd_macd = get_macd(kachadd['close'], 26, 12, 9)
kachadd_macd.tail()

# MACD Plot
def plot_macd(prices, macd, signal, hist):
    ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
    ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

    ax1.plot(prices)
    ax2.plot(macd, color = 'grey', linewidth = 1.5, label = 'MACD')
    ax2.plot(signal, color = 'red', linewidth = 1.5, label = 'SIGNAL')

    for i in range(len(prices)):
        if str(hist[i])[0] == '-':
            ax2.bar(prices.index[i], hist[i], color = '#ef5350')
        else:
            ax2.bar(prices.index[i], hist[i], color = '#26a69a')

    plt.legend(loc = 'lower right')

plot_macd(kachadd['close'], kachadd_macd['macd'], kachadd_macd['signal'], kachadd_macd['hist'])


#exponential moving average (10 and 50 days)
time_period10 = 10
k = (2/(time_period10+1))
ema_p10 = 0
ema10_values=[]
for i in range(len(kachadd['adjClose'])):
    if (ema_p10 == 0):
        ema_p10 = kachadd['adjClose'][i]
    else:
        ema_p10 = ema_p10 + k*(kachadd['adjClose'][i] - ema_p10)
    ema10_values.append(ema_p10)
ema10_values=pd.Series(ema10_values,index=kachadd.index)
   

time_period50 = 50
k = (2/(time_period50+1))
ema_p50 = 0
ema_values50=[]
for i in range(len(kachadd['adjClose'])):
    if (ema_p50 == 0):
        ema_p50 = kachadd['adjClose'][i]
    else:
        ema_p50 = ema_p50 + k*(kachadd['adjClose'][i] - ema_p50)
    ema_values50.append(ema_p50)
ema_values50 = pd.Series(ema_values50,index=kachadd.index)
       
 
# Creating the trading stratagy
def implement_macd_strategy(prices, data):    
    buy_price = []
    sell_price = []
    macd_signal = []
    signal = 0

    for i in range(len(data)):
        if data['macd'][i] > data['signal'][i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        elif data['macd'][i] < data['signal'][i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            macd_signal.append(0)
            
    return buy_price, sell_price, macd_signal
            
buy_price, sell_price, macd_signal = implement_macd_strategy(kachadd['close'], kachadd_macd)

# Plotting the trading Lists
ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

ax1.plot(kachadd['close'], color = 'skyblue', linewidth = 2, label = 'GOOGL')
ax1.plot(kachadd.index, buy_price, marker = '^', color = 'green', markersize = 10, label = 'BUY SIGNAL', linewidth = 0)
ax1.plot(kachadd.index, sell_price, marker = 'v', color = 'r', markersize = 10, label = 'SELL SIGNAL', linewidth = 0)
ax1.legend()
ax1.set_title('KACHAD MACD SIGNALS')
ax2.plot(kachadd_macd['macd'], color = 'grey', linewidth = 1.5, label = 'MACD')
ax2.plot(kachadd_macd['signal'], color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')

for i in range(len(kachadd_macd)):
    if str(kachadd_macd['hist'][i])[0] == '-':
        ax2.bar(kachadd_macd.index[i], kachadd_macd['hist'][i], color = '#ef5350')
    else:
        ax2.bar(kachadd_macd.index[i], kachadd_macd['hist'][i], color = '#26a69a')
        
plt.legend(loc = 'lower right')
plt.show()

# Creating our position
position = []
for i in range(len(macd_signal)):
    if macd_signal[i] > 1:
        position.append(0)
    else:
        position.append(1)
        
for i in range(len(kachadd['close'])):
    if macd_signal[i] == 1:
        position[i] = 1
    elif macd_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]
        
 
    
macd = kachadd_macd['macd']
signal = kachadd_macd['signal']
close_price = kachadd['close']
macd_signal = pd.DataFrame(macd_signal).rename(columns = {0:'macd_signal'}).set_index(kachadd.index)
position = pd.DataFrame(position).rename(columns = {0:'macd_position'}).set_index(kachadd.index)

frames = [close_price, macd, signal, macd_signal, position]
strategy = pd.concat(frames, join = 'inner', axis = 1)

#print(name)
#print(macd_signal)
#print(position)
print(strategy)

# BackTesting strategy
kachadd_ret = pd.DataFrame(np.diff(kachadd['close'])).rename(columns = {0:'returns'})
macd_strategy_ret = []

for i in range(len(kachadd_ret)):
    try:
        returns = kachadd_ret['returns'][i]*strategy['macd_position'][i]
        macd_strategy_ret.append(returns)
    except:
        pass
    
macd_strategy_ret_df = pd.DataFrame(macd_strategy_ret).rename(columns = {0:'macd_returns'})

investment_value = 100000
number_of_stocks = floor(investment_value/kachadd['close'][1])
macd_investment_ret = []

for i in range(len(macd_strategy_ret_df['macd_returns'])):
    returns = number_of_stocks*macd_strategy_ret_df['macd_returns'][i]
    macd_investment_ret.append(returns)

macd_investment_ret_df = pd.DataFrame(macd_investment_ret).rename(columns = {0:'investment_returns'})
total_investment_ret = round(sum(macd_investment_ret_df['investment_returns']), 2)
profit_percentage = floor((total_investment_ret/investment_value)*100)
print(cl('Profit gained from the MACD strategy by investing $100k in kachad : {}'.format(total_investment_ret), attrs = ['bold']))
print(cl('Profit percentage of the MACD strategy : {}%'.format(profit_percentage), attrs = ['bold']))


