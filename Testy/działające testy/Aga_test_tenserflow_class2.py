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

produkty=['ETH-BTC']
produkt_id=0
cena=[[] for _ in range(len(produkty))]

class Tensorflow_Model():
    def __init__(self, load_training_data=True, save_training_data=True, load_training_model=True, multi_stage_test=True, training_model_type=4, produkty=['ETH-BTC'], Epochs=100):
        self.produkty=produkty
        self.cena=[[] for _ in range(len(self.produkty))]
        self.produkt_id=0
        self.seq_len=80
        self.future_period_predict=3
        self.ratio_to_predict=self.produkty[0]
        self.Epochs=Epochs
        self.BATCH_SIZE=90
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
    def preprocess_data_frame(self, data_frame):
        data_frame=data_frame.drop('future', 1)

        for col in data_frame.columns:
            if col !='target':
                data_frame[col]=data_frame[col].pct_change()
                data_frame.dropna(inplace=True)
                data_frame[col]=preprocessing.scale(data_frame[col].values)
        data_frame.dropna(inplace=True)
        sequential_data=[]
        prev_days=deque(maxlen=self.seq_len)
        for i in data_frame.values:
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
        data_frame=pd.DataFrame()

        if self.load_training_data==True:   #Odczyt z zapisanego pliku z danymi treningowymi
            data_frame=pd.read_csv('training_data.csv',sep=',')
            print("training data loaded from csv file")
        else:
            data_frame=pd.DataFrame(columns=['time', 'low_price', 'high_price', 'open_price','close_price', 'volume'])#zmiana
            Preignitor()
            for i in range(len(cena[produkt_id])):
                 data_frame.loc[i] = [cena[produkt_id][i][0],cena[produkt_id][i][1],cena[produkt_id][i][2],cena[produkt_id][i][3],cena[produkt_id][i][4],cena[produkt_id][i][5]]#zmiana
            if self.save_training_data==True:
                data_frame.to_csv("training_data.csv", index=False)
            else:
                pass
       
        data_frame.set_index("time", inplace=True)
        data_frame['future']=data_frame['close_price'].shift(-self.future_period_predict)
        data_frame['target']=list(map(self.classify, data_frame['close_price'], data_frame['future']))
        print(data_frame.head())
 
        times=sorted(data_frame.index.values)
        last_5pct=sorted(data_frame.index.values)[-int(0.05*len(times))]
        validation_data_frame=data_frame[(data_frame.index>= last_5pct)]
        data_frame=data_frame[(data_frame.index< last_5pct)]

        self.train_x, self.train_y = self.preprocess_data_frame(data_frame)
        self.validation_x, self.validation_y= self.preprocess_data_frame(validation_data_frame)

        print("train data: {} validation {}".format(len(self.train_x), len(self.validation_x)))
        print("dont buy: {} Buys: {}".format(self.train_y.count(0), self.train_y.count(1)))
        print("VALIDATION dont buy: {} buy {}".format(self.validation_y.count(0), self.validation_y.count(1)))
    def model(self):
        if self.load_training_model==True:   #Odczyt z zapisanego pliku modelu treningowego
            if self.multi_stage_test==True:
                model=load_model("models/Multi_stage_test-{}.model".format(training_model_type))
            else:
                model=load_model("model4")
        else:
            if self.training_model_type==4: #1 layer dependant on the number of columns 
                model=Sequential()
                model.add(LSTM(5,input_shape=(self.train_x.shape[1:]), return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(64, return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(64))
                model.add(Dropout(0.2))
                model.add(BatchNormalization())

                model.add(Dense(32, activation='relu'))
                model.add(Dropout(0.2))

                model.add(Dense(2,activation='softmax'))  
            if self.training_model_type==3: #1 layer dependant on the number of columns half
                model=Sequential()
                model.add(LSTM(5,input_shape=(self.train_x.shape[1:]), return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32, return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32))
                model.add(Dropout(0.2))
                model.add(BatchNormalization())

                model.add(Dense(16, activation='relu'))
                model.add(Dropout(0.2))

                model.add(Dense(2,activation='softmax'))    
            if self.training_model_type==2: #quarter of the bigest training model:
                model=Sequential()
                model.add(LSTM(32,input_shape=(self.train_x.shape[1:]), return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32, return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32))
                model.add(Dropout(0.2))
                model.add(BatchNormalization())

                model.add(Dense(16, activation='relu'))
                model.add(Dropout(0.2))

                model.add(Dense(2,activation='softmax'))

            if self.training_model_type==1: #1 layer dependant of column number +1:
                model=Sequential()
                model.add(LSTM(6,input_shape=(self.train_x.shape[1:]), return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(64, return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(64))
                model.add(Dropout(0.2))
                model.add(BatchNormalization())

                model.add(Dense(32, activation='relu'))
                model.add(Dropout(0.2))

                model.add(Dense(2,activation='softmax'))

            if self.training_model_type==0: #1 layer dependant of column number +1:
                model=Sequential()
                model.add(LSTM(6,input_shape=(self.train_x.shape[1:]), return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32, return_sequences=True))
                model.add(Dropout(0.1))
                model.add(BatchNormalization())

                model.add(LSTM(32))
                model.add(Dropout(0.2))
                model.add(BatchNormalization())

                model.add(Dense(16, activation='relu'))
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

        tensorboard=TensorBoard(log_dir="logs/{}{}".format(training_model_type,self.NAME))

        filepath="RNN_FINAL-{epoch:02d}-{val_acc:.3f}"
        csv_logger= CSVLogger('logs/training{}.log'.format(training_model_type), append=True)
        checkpoint= ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, model='max'))
        reduce_lr=  ReduceLROnPlateau(monitor='val_loss', factor=0.0005, patience=3, min_lr=0.001, verbose=1)


        #train model
        model.fit(
            self.train_x, self.train_y,
            batch_size=self.BATCH_SIZE,
            epochs=self.Epochs,
            validation_data=(self.validation_x, self.validation_y),
            callbacks=[tensorboard]#csv_logger]#, reduce_lr]#, checkpoint]
        ) 
         #score_model
        score=model.evaluate(self.validation_x, self.validation_y, verbose=0)
        print('Test loss:', score[0])
        print('Test accuracy: ', score[1])

        if self.multi_stage_test==True:
            model.save("models/Multi_stage_test-{}.model".format(training_model_type))
        else:
            model.save("models/{}.model".format(score[1]))
def Preignitor():
    end=(time.time())
    start=end-5000000#880000
    for product_id in produkty:
        PR=Public_Requester()
        un_filtered=PR.Historic_rates_divider(start=start, end=end, skala=300, produkt=product_id)
        for v in range(len(un_filtered)):
            cena[produkty.index(product_id)].append(un_filtered[v])
for training_model_type in range(0,5):
    TFM=Tensorflow_Model(load_training_data=True, save_training_data=False, load_training_model=False, training_model_type=training_model_type, multi_stage_test=True, Epochs=10)
    TFM.data_procesing() 
    TFM.model()
    clear_session()
while True:
    for training_model_type in range(0,5):
        TFM=Tensorflow_Model(load_training_data=True, save_training_data=False, load_training_model=True, training_model_type=training_model_type, multi_stage_test=True, Epochs=30)
        TFM.data_procesing() 
        TFM.model()
        clear_session()





