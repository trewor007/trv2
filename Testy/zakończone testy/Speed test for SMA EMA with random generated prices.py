import copy
import timeit
import time
import queue
import random
import numpy as np

q = queue.Queue()


class StockIndicators():
    def SI_sma(self, cena, zakres):
        self.cena=cena
        weights=np.ones((zakres,))/zakres
        smas=np.convolve(self.cena, weights, 'valid')
        return smas
        
    def SI_ema(self, cena, zakres):
        self.cena=cena
        weights_ema = np.exp(np.linspace(-1.,0.,zakres))
        weights_ema /= weights_ema.sum()
        ema=np.convolve(self.cena,weights_ema)[:len(self.cena)]
        ema[:zakres]=ema[zakres]
        return ema

    def SI_RSI (self, cena, zakres=14):
        deltas = np.diff(cena)
        seed = deltas[:zakres+1]
        up = seed[seed >= 0].sum()/zakres
        down = -seed[seed < 0].sum()/zakres
        rs = up/down
        rsi = np.zeros_like(cena)
        rsi[:zakres] = 100. - 100./(1. + rs)

        for i in range(zakres, len(cena)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
 
            up = (up*(zakres - 1) + upval)/zakres
            down = (down*(zakres - 1) + downval)/zakres
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)
        if len(cena) > zakres:
            return rsi[-1]
        else:
            return 50 

class Rules():
    def SMA_EMA(self, produkt_id, zakres, cena, smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet):
        smas[produkt_id]=Si.SI_sma(cena=cena[produkt_id], zakres=zakres[0])            
        rsi[produkt_id]=Si.SI_RSI(cena=cena[produkt_id])
        print("===========================================================")
        print("Pair: {} Rsi: {}. Cena Size: {}".format(pair, rsi[produkt_id], len(cena[produkt_id])))
        if ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==True) and (smas_budget[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie
            smas_budget[produkt_id]["kupiono"]=False       
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1]),2)
            smas_budget[produkt_id]["Sentence"]=("SMAS_SELL {} {}@ Price: {}  Buyprice: {} ".format(smas_budget[produkt_id]["coin_amount"],pair[:3],cena[produkt_id][-1],smas_budget[produkt_id]['BuyPrice']))
            smas_budget[produkt_id]["coin_amount"]=float(0)
            smas_budget[produkt_id]['BuyPrice']=float(0)
        elif ((cena[produkt_id][-1]>smas[produkt_id][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (smas_budget2[produkt_id]["kupiono"]==True) and (smas_budget2[produkt_id]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
            smas_budget2[produkt_id]["kupiono"]=False
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget2[produkt_id]['coin_amount']*cena[produkt_id][-1]),2)
            smas_budget2[produkt_id]["Sentence"]=("SMAS_SELL RSI {} {}@ Price: {} Buyprice: {}".format(smas_budget2[produkt_id]["coin_amount"],pair[:3],cena[produkt_id][-1],smas_budget2[produkt_id]['BuyPrice']))
            smas_budget2[produkt_id]["coin_amount"]=float(0)
            smas_budget2[produkt_id]['BuyPrice']=float(0)
        elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (smas_budget[produkt_id]["kupiono"]==False) ): #kupowanie
            smas_budget[produkt_id]["kupiono"]=True
            smas_budget[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
            smas_budget[produkt_id]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[produkt_id][-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1]),7)
            smas_budget[produkt_id]["Sentence"]=("SMAS_BUY  {} {}@ Price {}".format(smas_budget[produkt_id]["coin_amount"],pair[:3],cena[produkt_id][-1]))
        elif ((cena[produkt_id][-1]<smas[produkt_id][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (smas_budget2[produkt_id]["kupiono"]==False) ): #kupowanie rsi
            smas_budget2[produkt_id]["kupiono"]=True
            smas_budget2[produkt_id]["BuyPrice"]=cena[produkt_id][-1]
            smas_budget2[produkt_id]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[produkt_id][-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget2[produkt_id]['coin_amount']*cena[produkt_id][-1]),7)
            smas_budget2[produkt_id]["Sentence"]=("SMAS_BUY RSI  {} {}@ Price {}".format(smas_budget2[produkt_id]["coin_amount"],pair[:3],cena[produkt_id][-1]))
        else:
            pass
        for i in zakres:
            if len(cena[produkt_id])>i:
                j=zakres.index(i)
                e=Si.SI_ema(cena=cena[produkt_id], zakres=i)
                k=e.tolist()
                ema[produkt_id][j].append(k[-1])
                if ((cena[produkt_id][-1]>ema[produkt_id][j][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (ema_budget[produkt_id][j]["kupiono"]==True) and (ema_budget[produkt_id][j]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie
                    ema_budget[produkt_id][j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget[produkt_id][j]['coin_amount']*cena[produkt_id][-1]),2)
                    ema_budget[produkt_id][j]["Sentence"]=("EMA{}_SELL {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget[produkt_id][j]["coin_amount"],pair[:3],cena[produkt_id][-1],ema_budget[produkt_id][j]['BuyPrice']))
                    ema_budget[produkt_id][j]["coin_amount"]=float(0)
                    ema_budget[produkt_id][j]['BuyPrice']=float(0)
                elif ((cena[produkt_id][-1]>ema[produkt_id][j][-1]) and (cena[produkt_id][-1]<cena[produkt_id][-2]) and (rsi[produkt_id]<30) and (ema_budget2[produkt_id][j]["kupiono"]==True) and (ema_budget2[produkt_id][j]["BuyPrice"]<cena[produkt_id][-1])): #sprzedawanie rsi
                    ema_budget2[produkt_id][j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget2[produkt_id][j]['coin_amount']*cena[produkt_id][-1]),2)
                    ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_SELL RSI {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget2[produkt_id][j]["coin_amount"],pair[:3],cena[produkt_id][-1],ema_budget2[produkt_id][j]['BuyPrice']))
                    ema_budget2[produkt_id][j]["coin_amount"]=float(0)
                    ema_budget2[produkt_id][j]['BuyPrice']=float(0)
                elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (ema_budget[produkt_id][j]["kupiono"]==False) ): #kupowanie
                    ema_budget[produkt_id][j]["kupiono"]=True
                    ema_budget[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                    ema_budget[produkt_id][j]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[produkt_id][-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget[produkt_id][j]['coin_amount']*cena[produkt_id][-1]),7)
                    ema_budget[produkt_id][j]["Sentence"]=("EMA{}_BUY  {} {}@ Price {}".format((j+1),ema_budget[produkt_id][j]["coin_amount"],pair[:3],cena[produkt_id][-1]))
                elif ((cena[produkt_id][-1]<ema[produkt_id][j][-1]) and (cena[produkt_id][-1]>cena[produkt_id][-2]) and (rsi[produkt_id]>70) and (ema_budget2[produkt_id][j]["kupiono"]==False) ): #kupowanie rsi
                    ema_budget2[produkt_id][j]["kupiono"]=True
                    ema_budget2[produkt_id][j]["BuyPrice"]=cena[produkt_id][-1]
                    ema_budget2[produkt_id][j]['coin_amount']=round(((0.15*wallet[pair[4:]])/cena[produkt_id][-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget2[produkt_id][j]['coin_amount']*cena[produkt_id][-1]),7)
                    ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_BUY RSI  {} {}@ Price {}".format((j+1),ema_budget2[produkt_id][j]["coin_amount"],pair[:3],cena[produkt_id][-1]))
                else:
                    pass 
        for x in range(len(produkty)):
            print(smas_budget[x]["Sentence"],smas_budget2[x]["Sentence"])               
            for y in range(len(zakres)):
                print(ema_budget[x][y]["Sentence"],ema_budget2[x][y]["Sentence"])
        return smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet    
    def SMA_EMA2(self, produkt_id, zakres, cena, smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet):
        smas=Si.SI_sma(cena=cena, zakres=zakres[0])            
        rsi=Si.SI_RSI(cena=cena)
        print("===========================================================")
        print("Pair: {} Rsi: {}. Cena Size: {}".format(pair, rsi, len(cena)))
        if ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (smas_budget["kupiono"]==True) and (smas_budget["BuyPrice"]<cena[-1])): #sprzedawanie
            smas_budget["kupiono"]=False       
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget['coin_amount']*cena[-1]),2)
            smas_budget["Sentence"]=("SMAS_SELL {} {}@ Price: {}  Buyprice: {} ".format(smas_budget["coin_amount"],pair[:3],cena[-1],smas_budget['BuyPrice']))
            smas_budget["coin_amount"]=float(0)
            smas_budget['BuyPrice']=float(0)
        elif ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (smas_budget2["kupiono"]==True) and (smas_budget2["BuyPrice"]<cena[-1])): #sprzedawanie rsi
            smas_budget2["kupiono"]=False
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget2['coin_amount']*cena[-1]),2)
            smas_budget2["Sentence"]=("SMAS_SELL RSI {} {}@ Price: {} Buyprice: {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1],smas_budget2['BuyPrice']))
            smas_budget2["coin_amount"]=float(0)
            smas_budget2['BuyPrice']=float(0)
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (smas_budget["kupiono"]==False) ): #kupowanie
            smas_budget["kupiono"]=True
            smas_budget["BuyPrice"]=cena[-1]
            smas_budget['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget['coin_amount']*cena[-1]),7)
            smas_budget["Sentence"]=("SMAS_BUY  {} {}@ Price {}".format(smas_budget["coin_amount"],pair[:3],cena[-1]))
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (smas_budget2["kupiono"]==False) ): #kupowanie rsi
            smas_budget2["kupiono"]=True
            smas_budget2["BuyPrice"]=cena[-1]
            smas_budget2['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget2['coin_amount']*cena[-1]),7)
            smas_budget2["Sentence"]=("SMAS_BUY RSI  {} {}@ Price {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1]))
        else:
            pass
        for i in zakres:
            if len(cena)>i:
                j=zakres.index(i)
                e=Si.SI_ema(cena=cena, zakres=i)
                k=e.tolist()
                ema[j].append(k[-1])
                if ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (ema_budget[j]["kupiono"]==True) and (ema_budget[j]["BuyPrice"]<cena[-1])): #sprzedawanie
                    ema_budget[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget[j]['coin_amount']*cena[-1]),2)
                    ema_budget[j]["Sentence"]=("EMA{}_SELL {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1],ema_budget[j]['BuyPrice']))
                    ema_budget[j]["coin_amount"]=float(0)
                    ema_budget[j]['BuyPrice']=float(0)
                elif ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (ema_budget2[j]["kupiono"]==True) and (ema_budget2[j]["BuyPrice"]<cena[-1])): #sprzedawanie rsi
                    ema_budget2[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget2[j]['coin_amount']*cena[-1]),2)
                    ema_budget2[j]["Sentence"]=("EMA{}_SELL RSI {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1],ema_budget2[j]['BuyPrice']))
                    ema_budget2[j]["coin_amount"]=float(0)
                    ema_budget2[j]['BuyPrice']=float(0)
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (ema_budget[j]["kupiono"]==False) ): #kupowanie
                    ema_budget[j]["kupiono"]=True
                    ema_budget[j]["BuyPrice"]=cena[-1]
                    ema_budget[j]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget[j]['coin_amount']*cena[-1]),7)
                    ema_budget[j]["Sentence"]=("EMA{}_BUY  {} {}@ Price {}".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1]))
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (ema_budget2[j]["kupiono"]==False) ): #kupowanie rsi
                    ema_budget2[j]["kupiono"]=True
                    ema_budget2[j]["BuyPrice"]=cena[-1]
                    ema_budget2[j]['coin_amount']=round(((0.15*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget2[j]['coin_amount']*cena[-1]),7)
                    ema_budget2[j]["Sentence"]=("EMA{}_BUY RSI  {} {}@ Price {}".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1]))
                else:
                    pass 

        return smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet     
    def SMA_EMA3(self, produkt_id, zakres, cena, smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet):
        smas=Si.SI_sma(cena=cena, zakres=zakres[0])            
        rsi=Si.SI_RSI(cena=cena)
        print("===========================================================")
        print("Pair: {} Rsi: {}. Cena Size: {}".format(pair, rsi, len(cena)))
        if ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (smas_budget["kupiono"]==True) and (smas_budget["BuyPrice"]<cena[-1])): #sprzedawanie
            smas_budget["kupiono"]=False       
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget['coin_amount']*cena[-1]),2)
            smas_budget["Sentence"]=("SMAS_SELL {} {}@ Price: {}  Buyprice: {} ".format(smas_budget["coin_amount"],pair[:3],cena[-1],smas_budget['BuyPrice']))
            smas_budget["coin_amount"]=float(0)
            smas_budget['BuyPrice']=float(0)
        elif ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (smas_budget2["kupiono"]==True) and (smas_budget2["BuyPrice"]<cena[-1])): #sprzedawanie rsi
            smas_budget2["kupiono"]=False
            wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget2['coin_amount']*cena[-1]),2)
            smas_budget2["Sentence"]=("SMAS_SELL RSI {} {}@ Price: {} Buyprice: {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1],smas_budget2['BuyPrice']))
            smas_budget2["coin_amount"]=float(0)
            smas_budget2['BuyPrice']=float(0)
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (smas_budget["kupiono"]==False) ): #kupowanie
            smas_budget["kupiono"]=True
            smas_budget["BuyPrice"]=cena[-1]
            smas_budget['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget['coin_amount']*cena[-1]),7)
            smas_budget["Sentence"]=("SMAS_BUY  {} {}@ Price {}".format(smas_budget["coin_amount"],pair[:3],cena[-1]))
        elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (smas_budget2["kupiono"]==False) ): #kupowanie rsi
            smas_budget2["kupiono"]=True
            smas_budget2["BuyPrice"]=cena[-1]
            smas_budget2['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
            wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget2['coin_amount']*cena[-1]),7)
            smas_budget2["Sentence"]=("SMAS_BUY RSI  {} {}@ Price {}".format(smas_budget2["coin_amount"],pair[:3],cena[-1]))
        else:
            pass
        for i in zakres:
            if len(cena)>i:
                j=zakres.index(i)
                ema[j]=Si.SI_ema(cena=cena, zakres=i)
                if ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (ema_budget[j]["kupiono"]==True) and (ema_budget[j]["BuyPrice"]<cena[-1])): #sprzedawanie
                    ema_budget[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget[j]['coin_amount']*cena[-1]),2)
                    ema_budget[j]["Sentence"]=("EMA{}_SELL {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1],ema_budget[j]['BuyPrice']))
                    ema_budget[j]["coin_amount"]=float(0)
                    ema_budget[j]['BuyPrice']=float(0)
                elif ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and (rsi<30) and (ema_budget2[j]["kupiono"]==True) and (ema_budget2[j]["BuyPrice"]<cena[-1])): #sprzedawanie rsi
                    ema_budget2[j]["kupiono"]=False
                    wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget2[j]['coin_amount']*cena[-1]),2)
                    ema_budget2[j]["Sentence"]=("EMA{}_SELL RSI {} {}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1],ema_budget2[j]['BuyPrice']))
                    ema_budget2[j]["coin_amount"]=float(0)
                    ema_budget2[j]['BuyPrice']=float(0)
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (ema_budget[j]["kupiono"]==False) ): #kupowanie
                    ema_budget[j]["kupiono"]=True
                    ema_budget[j]["BuyPrice"]=cena[-1]
                    ema_budget[j]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget[j]['coin_amount']*cena[-1]),7)
                    ema_budget[j]["Sentence"]=("EMA{}_BUY  {} {}@ Price {}".format((j+1),ema_budget[j]["coin_amount"],pair[:3],cena[-1]))
                elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (rsi>70) and (ema_budget2[j]["kupiono"]==False) ): #kupowanie rsi
                    ema_budget2[j]["kupiono"]=True
                    ema_budget2[j]["BuyPrice"]=cena[-1]
                    ema_budget2[j]['coin_amount']=round(((0.15*wallet[pair[4:]])/cena[-1]),7)
                    wallet[pair[4:]]=round(wallet[pair[4:]]-(ema_budget2[j]['coin_amount']*cena[-1]),7)
                    ema_budget2[j]["Sentence"]=("EMA{}_BUY RSI  {} {}@ Price {}".format((j+1),ema_budget2[j]["coin_amount"],pair[:3],cena[-1]))
                else:
                    pass 

        return smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet     
def Ignitor():
    global n, produkty, zakres, wallet, cena, smas, rsi, ema, smas_budget, smas_budget2, ema_budget, ema_budget2, xxx
    n=200
    produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
    zakres=[10, 20, 40, 80]
    wallet={'EUR':float(200),'BTC':float(0),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0)}
    cena=[[] for _ in range(len(produkty))]
    smas=[[] for _ in range(len(produkty))]
    rsi= [[] for _ in range(len(produkty))]
    ema= [[] for _ in range(len(zakres))]
    ema= [copy.deepcopy(ema) for _ in range(len(produkty))]
    smas_budget=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
    smas_budget2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
    ema_zakres=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
    ema_zakres2=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(zakres))]
    ema_budget=[copy.deepcopy(ema_zakres) for _ in range(len(produkty))]
    ema_budget2=[copy.deepcopy(ema_zakres2) for _ in range(len(produkty))]
    xxx=0
    b=False    
    return n, produkty, zakres, wallet, cena, smas, rsi, ema, smas_budget, smas_budget2, ema_budget, ema_budget2, xxx
Si=StockIndicators()
beta=[]
beta1=[]
beta2=[]

Ignitor()

while xxx<n:
    price=random.uniform(0,100)
    pair=random.choice(produkty)
    b=True
    if b==True:
        alfa=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        if len(cena[produkt_id])>zakres[0]:
            Ru=Rules()
            alfa=time.time()
            Ru.SMA_EMA(produkt_id, zakres, cena, smas_budget, smas_budget2, ema_budget, ema_budget2, smas, rsi, ema, wallet)
            beta.append(time.time()-alfa)
            print(beta[-1], xxx)
        else:
            pass
    xxx=xxx+1
k=(sum(beta)/len(beta))
#================================================================================================================================================================


Ignitor()

while xxx<n:
    price=random.uniform(0,20)
    pair=random.choice(produkty)
    b=True
    if b==True:
        alfa1=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        if len(cena[produkt_id])>zakres[0]:
            Ru=Rules()
            alfa1=time.time()
            Ru.SMA_EMA2(produkt_id=produkt_id, zakres=zakres, cena=cena[produkt_id], smas_budget=smas_budget[produkt_id], smas_budget2=smas_budget2[produkt_id], ema_budget=ema_budget[produkt_id], ema_budget2=ema_budget2[produkt_id], smas=smas[produkt_id], rsi=rsi[produkt_id], ema=ema[produkt_id], wallet=wallet)
            for x in range(len(produkty)):
                print(smas_budget[x]["Sentence"],smas_budget2[x]["Sentence"])               
                for y in range(len(zakres)):
                    print(ema_budget[x][y]["Sentence"],ema_budget2[x][y]["Sentence"])
            beta1.append(time.time()-alfa1)
            print(beta1[-1], xxx)
        else:
            pass
    xxx=xxx+1
k1=(sum(beta1)/len(beta1))
#================================================================================================================================================================

Ignitor()

while xxx<n:
    price=random.uniform(0,20)
    pair=random.choice(produkty)
    b=True
    if b==True:
        alfa2=time.time()
        b=False
        produkt_id=produkty.index(pair)
        cena[produkt_id].append(float(price))
        if len(cena[produkt_id])>zakres[0]:
            Ru=Rules()
            alfa2=time.time()
            Ru.SMA_EMA2(produkt_id=produkt_id, zakres=zakres, cena=cena[produkt_id], smas_budget=smas_budget[produkt_id], smas_budget2=smas_budget2[produkt_id], ema_budget=ema_budget[produkt_id], ema_budget2=ema_budget2[produkt_id], smas=smas[produkt_id], rsi=rsi[produkt_id], ema=ema[produkt_id], wallet=wallet)
            for x in range(len(produkty)):
                print(smas_budget[x]["Sentence"],smas_budget2[x]["Sentence"])               
                for y in range(len(zakres)):
                    print(ema_budget[x][y]["Sentence"],ema_budget2[x][y]["Sentence"])
            beta2.append(time.time()-alfa2)
            print(beta2[-1], xxx)
        else:
            pass
    xxx=xxx+1
k2=(sum(beta2)/len(beta2))


print("srednia: first: {} second: {} third {}".format(k, k1, k2))
print("suma: first: {} second: {} third {}".format(sum(beta), sum(beta1), sum(beta2)))
            
            
