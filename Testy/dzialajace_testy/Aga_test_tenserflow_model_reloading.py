# This Python file uses the following encoding: utf-8
import datetime
import copy
import hmac
import h5py
#import hashlib
import json
import platform
import time
import timeit
import random

import pandas as pd
import numpy as np
import tensorflow as tf

from collections import deque
from sklearn import preprocessing
from tensorflow.python.keras.models import Sequential, load_model
from tensorflow.python.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from tensorflow.python.keras.callbacks import  ModelCheckpoint, ReduceLROnPlateau, CSVLogger
class Tensorflow_Model():
    def classify(current, future):
        if float(future)>float(current):
            return 1
        else:
            return 0
    def preprocess_data_frame(data_frame):
        data_frame=data_frame.drop('future', 1)

        for col in data_frame.columns:
            if col !='target':
                data_frame[col]=data_frame[col].pct_change()
                data_frame.dropna(inplace=True)
                data_frame[col]=preprocessing.scale(data_frame[col].values)
        data_frame.dropna(inplace=True)
        sequential_data=[]
        prev_days=deque(maxlen=seq_len)
        for i in data_frame.values:
            prev_days.append([n for n in i[:-1]])
            if len(prev_days)==seq_len:
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

produkty=['ETH-BTC']
cena=[[] for _ in range(len(produkty))]

produkt_id=0
seq_len=80
future_period_predict=3
ratio_to_predict=produkty[0]
Epochs=20
BATCH_SIZE=80
NAME='tenserflow_model_{}'.format(time.time())

pd.set_option('display.max_rows',100)
data_frame=pd.DataFrame()
data_frame=pd.read_csv('Training_data.csv',sep=',')
print("training data loaded")
data_frame.set_index("time", inplace=True)
print(data_frame.head())

times=sorted(data_frame.index.values)
last_5pct=sorted(data_frame.index.values)[-int(0.05*len(times))]
validation_data_frame=data_frame[(data_frame.index>= last_5pct)]
data_frame=data_frame[(data_frame.index< last_5pct)]

train_x, train_y = preprocess_data_frame(data_frame)
validation_x, validation_y= preprocess_data_frame(validation_data_frame)

print("train data: {} validation {}".format(len(train_x), len(validation_x)))
print("dont buy: {} Buys: {}".format(train_y.count(0), train_y.count(1)))
print("VALIDATION dont buy: {} buy {}".format(validation_y.count(0), validation_y.count(1)))

model=load_model("model1")
opt=tf.keras.optimizers.Adam(lr=0.01, decay=1e-6)


#Compile Model
model.compile(
    loss='sparse_categorical_crossentropy', 
    optimizer=opt, 
    metrics=['accuracy']
)

filepath="RNN_FINAL-{epoch:02d}-{val_acc:.3f}"
csv_logger= CSVLogger('logs/training.log')
checkpoint= ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, model='max'))
reduce_lr=  ReduceLROnPlateau(monitor='val_loss', factor=0.005, patience=3, min_lr=0.001, verbose=1)


#train model
history=model.fit(
    train_x, train_y,
    batch_size=BATCH_SIZE,
    epochs=Epochs,
    validation_data=(validation_x, validation_y),
    callbacks=[csv_logger, reduce_lr, checkpoint]
) 
 #score_model
score=model.evaluate(validation_x, validation_y, verbose=0)
print('Test loss:', score[0])
print('Test accuracy: ', score[1])

model.save("models/{}".format(score[1]))





