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
    def __init__(self, load_training_data=True, save_training_data=True, load_training_model=True, multi_stage_test=True, produkty=['ETH-BTC'], Epochs=100):
        self.produkty=produkty
        self.cena=[[] for _ in range(len(self.produkty))]
        self.produkt_id=0
        self.seq_len=160#80
        self.future_period_predict=3
        self.ratio_to_predict=self.produkty[0]
        self.Epochs=Epochs
        self.BATCH_SIZE=19422#12800#6400#1600#70#90
        self.NAME='tenserflow_model'
        self.load_training_data=load_training_data
        self.load_training_model=load_training_model
        self.save_training_data=save_training_data
        self.multi_stage_test=multi_stage_test

        
    def classify(self,current, future):
        if float(future)>float(current):
            return 1
        else:
            return 0
    def preprocess_Main_data_frame(self, Main_data_frame):
        Main_data_frame=Main_data_frame.drop('future', 1)

        for col in Main_data_frame.columns:
            if col !='target':
                Main_data_frame[col]=Main_data_frame[col].pct_change()
                Main_data_frame.dropna(inplace=True)
                Main_data_frame[col]=preprocessing.scale(Main_data_frame[col].values)
        Main_data_frame.dropna(inplace=True)
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
            Main_data_frame=pd.read_csv('training_data.csv',sep=',')
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
                    Main_data_frame.to_csv("training_data.csv", index=False)
                else:
                    pass
       
        Main_data_frame['future']=Main_data_frame[f'{produkty[self.produkt_id]}_close_price'].shift(-self.future_period_predict)
        Main_data_frame['target']=list(map(self.classify, Main_data_frame[f'{produkty[self.produkt_id]}_close_price'], Main_data_frame['future']))
        print(Main_data_frame.head())
 
        times=sorted(Main_data_frame.index.values)
        last_5pct=sorted(Main_data_frame.index.values)[-int(0.15*len(times))]
        validation_Main_data_frame=Main_data_frame[(Main_data_frame.index>= last_5pct)]
        Main_data_frame=Main_data_frame[(Main_data_frame.index< last_5pct)]

        self.train_x, self.train_y = self.preprocess_Main_data_frame(Main_data_frame)
        self.validation_x, self.validation_y= self.preprocess_Main_data_frame(validation_Main_data_frame)

        print("train data: {} validation {}".format(len(self.train_x), len(self.validation_x)))
        print("dont buy: {} Buys: {}".format(self.train_y.count(0), self.train_y.count(1)))
        print("VALIDATION dont buy: {} buy {}".format(self.validation_y.count(0), self.validation_y.count(1)))
    def model(self, First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod, Load_From_Checkpoint):
        if self.load_training_model==True:   #Odczyt z zapisanego pliku modelu treningowego
            if self.multi_stage_test==True:
                if self.Load_From_Checkpoint==True:
                    model=load_model("models/checkpoint/1L{}_2L{}_3L{}_4L{}.model".format(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod))
                else:
                    model=load_model("models/1L{}_2L{}_3L{}_4L{}.model".format(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod))
            else:
                model=load_model("model4")
        else:
            model=Sequential()
            model.add(LSTM(First_Layer_Nod,input_shape=(self.train_x.shape[1:]), return_sequences=True))
            model.add(Dropout(0.1))
            model.add(BatchNormalization())

            model.add(LSTM(Second_Layer_Nod, return_sequences=True))
            model.add(Dropout(0.1))
            model.add(BatchNormalization())

            model.add(LSTM(Third_Layer_Nod))
            model.add(Dropout(0.2))
            model.add(BatchNormalization())

            model.add(Dense(Forth_Layer_Nod, activation='relu'))
            model.add(Dropout(0.2))

            model.add(Dense(2,activation='softmax'))    
                        
        opt=tf.keras.optimizers.Adam(lr=0.005, decay=1e-6)

        #Compile Model
        model.compile(
            loss='sparse_categorical_crossentropy', 
            optimizer=opt, 
            metrics=['accuracy']
        )

        model.summary()

        tensorboard=TensorBoard(log_dir="models/logs/1L{}_2L{}_3L{}_4L{}".format(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod))
        checkpoint= ModelCheckpoint("models/checkpoint/1L{}_2L{}_3L{}_4L{}.model".format(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod, monitor='val_acc', verbose=1, save_best_only=True, model='max'))
        #train model
        model.fit(
            self.train_x, self.train_y,
            batch_size=self.BATCH_SIZE,
            epochs=self.Epochs,
            validation_data=(self.validation_x, self.validation_y),
            callbacks=[tensorboard, checkpoint]#csv_logger]#, reduce_lr]#, ]
        ) 
         #score_model
        score=model.evaluate(self.validation_x, self.validation_y, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy: ', score[1])

        if self.multi_stage_test==True:
            model.save("models/1L{}_2L{}_3L{}_4L{}.model".format(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod))
        else:
            model.save("models/{}.model".format(score[1]))
def Preignitor():

    end=(time.time())
    start=1551453562
    #start=end-8000000#880000
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])

First_Layer_Nods=   [15]
Second_Layer_Nods=  [8,15,32,64,128]
Third_Layer_Nods=   [8,15,32,64,128]
Forth_Layer_Nods=   [4,8,16,32]
Current_Layer_Nods= [0,0,0,0]



try:
    f= open("progress.txt", 'x')    #tworze plik zapisu postepu jezeli nie istnieje
except:
    with open('progress.txt') as fd:    #odczytuje zawartosc pliku jezli istnieje
        Current_Layer_Nods=json.load(fd)
#TFM=Tensorflow_Model(load_training_data=False, save_training_data=True, load_training_model=False,  multi_stage_test=True, Epochs=10)
#TFM.data_procesing()
print("Aktualne: {}".format(Current_Layer_Nods))
for First_Layer_Nod in First_Layer_Nods:
    if Current_Layer_Nods[0]<=First_Layer_Nod:
        for Second_Layer_Nod in Second_Layer_Nods:
            if Current_Layer_Nods[1]<=Second_Layer_Nod:
                if Second_Layer_Nod >= First_Layer_Nod:
                    for Third_Layer_Nod in Third_Layer_Nods:
                        if Current_Layer_Nods[2]<=Third_Layer_Nod:
                            if Third_Layer_Nod <= Second_Layer_Nod:
                                for Forth_Layer_Nod in Forth_Layer_Nods:
                                    if Current_Layer_Nods[3]<Forth_Layer_Nod:
                                        if Forth_Layer_Nod <Third_Layer_Nod:
                                            TFM=Tensorflow_Model(load_training_data=True, save_training_data=False, load_training_model=False,  multi_stage_test=True, Epochs=1000)
                                            TFM.data_procesing()
                                            sf=[First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod]
                                            with open('progress.txt','w') as outfile:
                                                json.dump(sf, outfile)
                                            TFM.model(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod, Load_From_Checkpoint=False)
                                            clear_session()

                                    if Current_Layer_Nods[3]==Forth_Layer_Nod and Current_Layer_Nods[2]==Third_Layer_Nod and Current_Layer_Nods[1]==Second_Layer_Nod and Current_Layer_Nods[0]==First_Layer_Nod and Current_Layer_Nods!=[0,0,0,0]:
                                        TFM=Tensorflow_Model(load_training_data=True, save_training_data=False, load_training_model=False,  multi_stage_test=True, Epochs=1000)
                                        TFM.data_procesing() 
                                        TFM.model(First_Layer_Nod, Second_Layer_Nod, Third_Layer_Nod, Forth_Layer_Nod, Load_From_Checkpoint=True)
                                        clear_session()




