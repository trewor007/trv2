#price=[[T, O, H, L, C],[T, O, H, L, C],[T, O, H, L, C]]
import time
import random

cena=[]
skala=30
while True:
    price=round((random.uniform(1, 20)),2)
    print(len(cena))
    if len(cena)==0:
        cena.append([0,0,0,0,0])
        cena[0][0]=time.time()  #Open Time
        cena[0][1]=price        #Open Price
        cena[0][2]=price        #High Price
        cena[0][3]=price        #Low Price
        cena[0][4]=price        #Close Price
    elif len(cena)>0:
        if price>cena[-1][2]:
            cena[-1][2]=price
            cena[-1][4]=price
        elif price<cena[-1][3]:
            cena[-1][3]=price
            cena[-1][4]=price
        elif (time.time()-cena[-1][0])>skala:
            cena.append([0,0,0,0,0])
            cena[-1][0]=time.time()  #Open Time
            cena[-1][1]=price        #Open Price
            cena[-1][2]=price        #High Price
            cena[-1][3]=price        #Low Price
            cena[-1][4]=price        #Close Price
        else:
            cena[-1][4]=price
        
    print(cena)
    time.sleep(5)

