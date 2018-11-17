import time
import datetime

import timeit

import queue
import os
import random
import copy

import matplotlib.pyplot as plt
import matplotlib.animation as animation


q = queue.Queue()

beta=[0,]
b=False
czas=[]
produkty=["primo"]
cena=[[] for _ in range(len(produkty))]


fig,ax1, ax2=plt.subplots(1,1,1)

def animate(i):
        
        ax1.clear()
        ax2.clear()
        ax1.plot(czas,cena[0])
        ax2.plot(czas,beta)
    
    
while True:
    time.sleep(1)
    alpfa=time.time()
    #input('press enter')
    rand_produkt=random.choice(produkty) 
    rand_price=random.randint(1,10)
    rand_czas=time.ctime()
    alfa={'type':'ticker', 'price':rand_price, 'product_id':rand_produkt, 'time':rand_czas}
    q.put(alfa)
    if q.not_empty:            
        dane=q.get()        
        typ=dane.get('type',None)
        if typ=='ticker':
            price=dane.get('price', None)
            pair=dane.get('product_id',None)
            t=dane.get('time', None)
            b=True
    if b==True:
        b=False
        
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        czas.append(t)


    plt.ion()
    ani=animation.FuncAnimation(fig,animate,interval=1000)#, blit=True)repeat=True)
    plt.show()
    plt.pause(0.001)
    #fig.clf()
    beta.append(time.time()-alpfa)
    print(beta[-1])
