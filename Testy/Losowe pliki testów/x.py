zakres=[10, 20, 30]
produkty=["ETH-BTC", "ETC-BTC"]
cena=[[] for _ in range(len(produkty))]
smas=[[] for _ in range(len(produkty))]
rsi= [[] for _ in range(len(produkty))]
ema= [[] for _ in range(len(zakres))]
ema= [ema.copy() for _ in range(len(produkty))]#ema= [[] for _ in range(len(produkty))]
smas_budget=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0} for _ in range(len(produkty))]
smas_budget2=[{"1coin":int(0),"2coin":int(50), "kupiono": False, "BuyPrice":0} for _ in range(len(produkty))]
ema_budget=[smas_budget for _ in range(len(zakres))] #powinno być z zakresu
ema_budget2=[smas_budget for _ in range(len(zakres))]

#print(ema_budget)
#print(ema)

z=[10,20,30]
x=["alpha","betta"]
y=[[] for _ in range(len(z))]
y=[y.copy() for _ in range(len(x))]
y[1][1]=3
print(y)

