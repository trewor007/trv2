# This Python file uses the following encoding: utf-8
import base64
import datetime
import copy
import hmac
import h5py
import hashlib
import json
import platform
import urllib3
import urllib.request
import time
import timeit
import random
import requests
import queue
import os
import pandas as pd
import numpy as np
import tensorflow as tf
import threading as Thread

from collections import deque

from sklearn import preprocessing
from tensorflow.python.keras.backend import clear_session
from tensorflow.python.keras.models import Sequential, load_model
from tensorflow.python.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from tensorflow.python.keras.callbacks import  TensorBoard, ModelCheckpoint, ReduceLROnPlateau, CSVLogger



from Public_Requester import Public_Requester

produkty=['ETH-BTC', "BTC-EUR", "ETH-EUR"]
produkt_id=0
cena=[[] for _ in range(len(produkty))]

class Tensorflow_Model():
    def __init__(self, load_training_data=True, save_training_data=True, load_training_model=True, multi_stage_test=True, training_model_type=4, produkty=['ETH-BTC'], Epochs=100):
        self.produkty=produkty
        self.cena=[[] for _ in range(len(self.produkty))]
        self.produkt_id=0
        self.seq_len=288#80
        self.future_period_predict=3
        self.ratio_to_predict=self.produkty[0]
        self.Epochs=Epochs
        self.BATCH_SIZE=12800#6400#1600#70#90
        self.NAME='tenserflow_model'
        self.load_training_data=load_training_data
        self.load_training_model=load_training_model
        self.save_training_data=save_training_data
        self.multi_stage_test=multi_stage_test
        self.training_model_type=training_model_type
        
    def classify(self,current, future):
        if float(future)>float(current):
            return 1
        else:
            return 0
    def preprocess_Main_data_frame(self, Main_data_frame):
        Main_data_frame=Main_data_frame.drop('future', 1)    #odrzucenie danych z "przyszlosci"

        for col in Main_data_frame.columns:                  #iteracja przez kazda kolumne
            if col !='target':                               # jeśli kolumna nie nazywa sie "target"
                Main_data_frame[col]=Main_data_frame[col].pct_change()  #.ptc_change zamienia dane na procentowa roznice pomiedzy col[n] a con[n+1] col zero staje sie NAN
                Main_data_frame.dropna(inplace=True)                    #oczyszcza NAN z pierwszej pozycji po wykorzystaniu ptc_change
                Main_data_frame[col]=preprocessing.scale(Main_data_frame[col].values)   #skaluje wartośći pomiędzy 0 a 1
        Main_data_frame.dropna(inplace=True)    #oczyszczanie z NAN
        sequential_data=[]
        prev_days=deque(maxlen=self.seq_len)
        for i in Main_data_frame.values:
            prev_days.append([n for n in i[:-1]])
            if len(prev_days)==self.seq_len:
                sequential_data.append([np.array(prev_days), i [-1]])

        random.shuffle(sequential_data)
        buys=[]
        sells=[]
        for seq, target in sequential_data:
            if target==0:
                sells.append([seq, target])
            elif target==1:
                buys.append([seq, target])
    
        random.shuffle(buys)
        random.shuffle(sells)
    
        lower=min(len(buys), len(sells))
        buys=buys[:lower]
        sells=sells[:lower]
        sequential_data=buys+sells
        random.shuffle(sequential_data)
    
        x=[]
        y=[]
    
        for seq, target in sequential_data:
            x.append(seq)
            y.append(target)
        return np.array(x), y
        
    def data_procesing(self):
        pd.set_option('display.max_rows',100)
        Main_data_frame=pd.DataFrame()                              #Tworzenie glownej bazy danych 

        if self.load_training_data==True:   #Odczyt z zapisanego pliku z danymi treningowymi
            Main_data_frame=pd.read_csv('training_data_multi.csv',sep=',')
            print("training data loaded from csv file")
        else:
            Preignitor()
            """
            dla kazdego indeksu stworz tymczasowa baze danych i pobierz dane z listy.
            następnie zmien nazwy kolumn tak by kazda z nich byla poprzedzona nazwa pary walutowej
            ustaw czas jako indeks tabeli,    """
            
            for produkt_id in range(len(produkty)): 
                #print(cena[produkt_id])
                data_frame=pd.DataFrame.from_records(cena[produkt_id], columns=['time', 'low_price', 'high_price', 'open_price','close_price', 'volume'])
                print(data_frame.head())
                data_frame.rename(columns={'low_price': f'{produkty[produkt_id]}_low_price',
                                            'high_price': f'{produkty[produkt_id]}_high_price',
                                            'open_price': f'{produkty[produkt_id]}_open_price',
                                            'close_price': f'{produkty[produkt_id]}_close_price',
                                            'volume': f'{produkty[produkt_id]}_volume'}, inplace=True) 
                print(data_frame.head())
                data_frame.set_index('time', inplace=True)
                print(data_frame.head())
                if len(Main_data_frame)==0:                             #pierwsza iteracja
                    Main_data_frame=data_frame                          #glowna baza danych z tymczasowej bazy
                else:                                                   #kazda kolejna iteracja
                    Main_data_frame=Main_data_frame.join(data_frame)    #tymczasowa baza danych doklejona z prawej strony glownej bazy danych
                print(Main_data_frame.head())
                if self.save_training_data==True:
                    Main_data_frame.to_csv("training_data_multi.csv", index=False)
                else:
                    pass
       
        #Main_data_frame.set_index("time", inplace=True)
        Main_data_frame['future']=Main_data_frame[f'{produkty[self.produkt_id]}_close_price'].shift(-self.future_period_predict)
        Main_data_frame['target']=list(map(self.classify, Main_data_frame[f'{produkty[self.produkt_id]}_close_price'], Main_data_frame['future']))
        print(Main_data_frame.head())
 
        times=sorted(Main_data_frame.index.values)
        last_5pct=sorted(Main_data_frame.index.values)[-int(0.05*len(times))]
        validation_Main_data_frame=Main_data_frame[(Main_data_frame.index>= last_5pct)]
        Main_data_frame=Main_data_frame[(Main_data_frame.index< last_5pct)]

        self.train_x, self.train_y = self.preprocess_Main_data_frame(Main_data_frame)
        self.validation_x, self.validation_y= self.preprocess_Main_data_frame(validation_Main_data_frame)

        print("train data: {} validation {}".format(len(self.train_x), len(self.validation_x)))
        print("dont buy: {} Buys: {}".format(self.train_y.count(0), self.train_y.count(1)))
        print("VALIDATION dont buy: {} buy {}".format(self.validation_y.count(0), self.validation_y.count(1)))

def Preignitor():
    end=1554069600
    start=1546297200
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])
TFM=Tensorflow_Model(load_training_data=False, save_training_data=True, load_training_model=False,  multi_stage_test=True, Epochs=10)
TFM.data_procesing()

