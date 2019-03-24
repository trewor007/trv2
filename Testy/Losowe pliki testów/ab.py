produkty=["BTC-EUR", "ETH-EUR"]
cena=[[] for _ in range(len(produkty))]
czas=[[] for _ in range(len(produkty))]
cena[0]=[1, 2, 3, 4, 5]
czas[0]=[-1, -2, -3, -4 ,-5]
cena[1]=['aa','bb','cc']
czas[1]=['-a','-b','-c']

for x in range(len(produkty)):
    cena[x]=cena[x][::-1]
    czas[x]=czas[x][::-1]
