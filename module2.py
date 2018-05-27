import time
import datetime
import timeit
#d={'typtranzakcji':"type",'kupsprzedaj':"side",'orderid':"order_id",'cena':"price",'czas':"time",'parawalut':"product_id",'typzamowienia':"order_type",'rozmiar':"size",'powod':"reason",'rozmiar2':"remaining_size",'klientoid':"client_oid",'sekwencja':"sequence"}
#d[0]
#for key in d:
#    print("KEY:", end="")
#    print(key, "  ", end="")
#    print("VALUE:", end="")
#    print(d[key]) 

#start=input("podaj poczatek   [dd-mm-rrrr hh:mm]")
#start_b=input("podaj koniec     [dd-mm-rrrr hh:mm]")
#class ACDC():
#    def foo(self, alfa="01-01-2018 00:00", beta="20-05-2018 00:00", x=300, skala=60):
#        self.start=time.mktime(time.strptime(alfa, '%d-%m-%Y %H:%M')) 
#        self.end=time.mktime(time.strptime(beta, '%d-%m-%Y %H:%M')) 
#        if self.end-self.start > x*skala:
#            self.end_tmp=self.end
#            self.end=self.start+(x*skala)
#            self.bar()
#            while self.end < self.end_tmp:
#                self.start=self.end
#                self.end=self.start+(x*skala)
#                self.bar()
#            else:
#                self.end=self.end_tmp
#                self.bar()             
#        else:
#                self.bar()
#    def bar(self):
#            start=datetime.datetime.fromtimestamp(self.start)
#            print(start)
#            end=datetime.datetime.fromtimestamp(self.end)
#            print(end)
#w=ACDC()
#a=time.time()
#w.foo()
#b=time.time()
#print(b-a)


import talib as ta
import numpy as np
import pandas as pd
import scipy
from scipy import signal
import time as t

PAIR = info.primary_pair
PERIOD = 30

def initialize():
    storage.reset()
    storage.elapsed = storage.get('elapsed', [0,0,0,0,0,0])

def cumsum_sma(array, period):
    ret = np.cumsum(array, dtype=float)
    ret[period:] = ret[period:] - ret[:-period]
    return ret[period - 1:] / period

def pandas_sma(array, period):
    return pd.rolling_mean(array, period)

def api_sma(array, period):
    # this method is native to Tradewave and does NOT return an array
    return (data[PAIR].ma(PERIOD))

def talib_sma(array, period):
    return ta.MA(array, period)

def convolve_sma(array, period):
    return np.convolve(array, np.ones((period,))/period, mode='valid')

def fftconvolve_sma(array, period):    
    return scipy.signal.fftconvolve(
        array, np.ones((period,))/period, mode='valid')    

def tick():

    close = data[PAIR].warmup_period('close')

    t1 = t.time()
    sma_api = api_sma(close, PERIOD)
    t2 = t.time()
    sma_cumsum = cumsum_sma(close, PERIOD)
    t3 = t.time()
    sma_pandas = pandas_sma(close, PERIOD)
    t4 = t.time()
    sma_talib = talib_sma(close, PERIOD)
    t5 = t.time()
    sma_convolve = convolve_sma(close, PERIOD)
    t6 = t.time()
    sma_fftconvolve = fftconvolve_sma(close, PERIOD)
    t7 = t.time()

    storage.elapsed[-1] = storage.elapsed[-1] + t2-t1
    storage.elapsed[-2] = storage.elapsed[-2] + t3-t2
    storage.elapsed[-3] = storage.elapsed[-3] + t4-t3
    storage.elapsed[-4] = storage.elapsed[-4] + t5-t4
    storage.elapsed[-5] = storage.elapsed[-5] + t6-t5    
    storage.elapsed[-6] = storage.elapsed[-6] + t7-t6        

    plot('sma_api', sma_api)  
    plot('sma_cumsum', sma_cumsum[-5])
    plot('sma_pandas', sma_pandas[-10])
    plot('sma_talib', sma_talib[-15])
    plot('sma_convolve', sma_convolve[-20])    
    plot('sma_fftconvolve', sma_fftconvolve[-25])

def stop():

    log('ticks....: %s' % info.max_ticks)

    log('api......: %.5f' % storage.elapsed[-1])
    log('cumsum...: %.5f' % storage.elapsed[-2])
    log('pandas...: %.5f' % storage.elapsed[-3])
    log('talib....: %.5f' % storage.elapsed[-4])
    log('convolve.: %.5f' % storage.elapsed[-5])    
    log('fft......: %.5f' % storage.elapsed[-6])