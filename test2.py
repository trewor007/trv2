pair='BTC-EUR'
wallet={'EUR':float(100),'BTC':float(0),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0)}
produkty=["BTC-EUR", "ETH-EUR", "ETC-EUR", "LTC-EUR", "BCH-EUR", "ZRX-EUR"]
smas_budget=[{"coin_amount":int(0), "kupiono": False, "BuyPrice":0, "Sentence":None} for _ in range(len(produkty))]
produkt_id=produkty.index(pair)
cena=[[] for _ in range(len(produkty))]
while True:
    print(wallet, smas_budget[produkt_id]['coin_amount'])
    a=int(input("1buy 2 sell"))
    
    if a==1:
        cena[produkt_id].append(float(input('cena kupna')))
        smas_budget[produkt_id]['coin_amount']=round(((0.1*wallet[pair[4:]])/cena[produkt_id][-1]),7)   #do zrobienia (uzaleznic od ilosci innych algorytmow kupujacych[y=((x/z)/v)])
        wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1]),7)
        print(wallet, smas_budget[produkt_id]['coin_amount'])
    if a==2:
        cena[produkt_id].append(float(input('cena sprzedazy')))
        wallet[pair[4:]]=round(wallet[pair[4:]]+(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1]),2)
        smas_budget[produkt_id]["coin_amount"]=float(0)
        print(wallet, smas_budget[produkt_id]['coin_amount'])




 #       ema_budget[produkt_id][j]['coin_amount']=round((10%wallet[pair[4:]]/cena[produkt_id][-1]),7)
 #       wallet[pair[4:]]=round(wallet[pair[4:]]-(wallet[pair[4:]]*(ema_budget[produkt_id][j]['coin_amount']/cena[produkt_id][-1])),7)
#
 #           wallet[pair[4:]]=round(wallet[pair[4:]]+(ema_budget[produkt_id][j]['coin_amount']*cena[produkt_id][-1]),2)
  #          ema_budget[produkt_id][j]["coin_amount"]=float(0)
#
#
 #               ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_SELL     {}{}@ Price: {}  Buyprice: {} ".format((j+1),ema_budget2[produkt_id][j]["coin_amount"],wallet[pair[:3]],cena[produkt_id][-1],smas_budget2[produkt_id][j]['BuyPrice']))
  #              ema_budget2[produkt_id][j]["coin_amount"]=float(0)
   #             ema_budget2[produkt_id][j]['BuyPrice']=float(0)
#
 #               ema_budget2[produkt_id][j]["Sentence"]=("EMA{}_BUY RSI  {}{}@ Price {}".format((j+1)ema_budget2[produkt_id][j]["coin_amount"],wallet[pair[:3]],cena[produkt_id][-1]))
  #              ema_budget[produkt_id][j]["Sentence"]=("EMA{}_BUY      {}{}@ Price {}".format((j+1)ema_budget[produkt_id][j]["coin_amount"],wallet[pair[:3]],cena[produkt_id][-1]))





#smas_budget[produkt_id]['coin_amount']=round((10%wallet[pair[4:]]/cena[produkt_id][-1]),7)
#wallet[pair[4:]]=round(wallet[pair[4:]]-(wallet[pair[4:]]*(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1])),7)

#smas_budget[produkt_id]['coin_amount']=round((10%wallet[pair[4:]]/cena[produkt_id][-1]),7)   
#wallet[pair[4:]]=round(wallet[pair[4:]]-(smas_budget[produkt_id]['coin_amount']*cena[produkt_id][-1]),7)
