import copy
zakres=[5, 10, 15]
produkty=["BTC-EUR", "ETH-EUR"]
ema0= [[].copy() for _ in range(len(zakres))]
ema= [ema0.copy() for _ in range(len(produkty))]
print(ema)
ema[0][0].append("1")
ema[0][1].append("2")
ema[0][0].append("1")
print(ema)

ema0= [[].copy() for _ in range(len(zakres))]
ema= [copy.deepcopy(ema0) for _ in range(len(produkty))]
print(ema)
ema[0][0].append("1")
ema[0][1].append("2")
ema[0][0].append("1")
print(ema)

ema0= [[] for _ in range(len(zakres))]
ema= [copy.deepcopy(ema0) for _ in range(len(produkty))]
print(ema)
ema[0][0].append("1")
ema[0][1].append("2")
ema[0][0].append("1")
print(ema)

ema= [[] for _ in range(len(zakres))]
ema= [copy.deepcopy(ema) for _ in range(len(produkty))]
print(ema)
ema[0][0].append("1")
ema[0][1].append("2")
ema[0][0].append("1")
print(ema)
