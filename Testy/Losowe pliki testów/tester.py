import random
import numpy as np
zakres=[5,10,15,20]
produkty=['alfa',"beta","gamma","delta"]
data=[[],[],[],[]]
ema=[[[0],[0],[0],[0]],[[0],[0],[0],[0]],[[0],[0],[0],[0]],[[0],[0],[0],[0]]]
smas=[[0],[0],[0],[0]]
def SI_sma(data, zakres):
    weights=np.ones((zakres,))/zakres
    smas=np.convolve(data, weights, 'valid')
    return smas
        
def SI_ema(data, zakres):

    weights_ema = np.exp(np.linspace(-1.,0.,zakres))
    weights_ema /= weights_ema.sum()
    ema=np.convolve(data,weights_ema)[:len(data)]
    ema[:zakres]=ema[zakres]
    return ema

while True:
    produkt=random.choice(produkty)
    produkt_id=produkty.index(produkt)
    
    data[produkt_id].append(random.uniform(0,100))    
    if len(data[produkt_id])>zakres[0]:
        smas[produkt_id]=SI_sma(data=data[produkt_id], zakres=zakres[0])
        #print(produkt)        
        #print(produkt_id)
        #print(smas[produkt_id][-1]) #calc using smas
        for i in zakres:
            if len(data[produkt_id])>i:
                j=zakres.index(i)
                e=SI_ema(data=data[produkt_id], zakres=i)
                k=e.tolist()                              
                ema[produkt_id][j].append(k[-1])
                #print(ema[produkt_id][j][-1]) #calc using ema
        for produkt_id in range(len(produkty)):
            print("smas calculation for {} is {}".format((produkty[produkt_id]),(smas[produkt_id][-1])))
            for i in range(len(zakres)):
                print("ema{} calculation for {} is {}".format(i,(produkty[produkt_id]),(ema[produkt_id][i][-1])))
    input("press enter")

