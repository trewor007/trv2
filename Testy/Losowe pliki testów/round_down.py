import math

def round_down(number, n):
    return math.floor(number*10**n)/(10**n)


#k=7
#print(round_down((1.23456789), 7))

#n=2
#number=1.23456789
#a=math.floor(number)
#print(a)
#b=a*(10**n)
#print(b)

wallet={'EUR':float(200),'BTC':float(0.19),'ETH':float(0),'ETC':float(0),'LTC':float(0),'BCH':float(0), 'ZRX':float(0), 'USDC':float(0)}
produkty=['ETH-BTC']
pair='ETH-BTC'
produkt_id=produkty.index(pair)
smas_budget={'coin_amount':float(0)}
smas_budget2={'coin_amount':float(0)}
smas_budget3={'coin_amount':float(0)}
cena=1


for cena in [float(j) / 100 for j in range(1, 10000, 1)]:    
    smas_budget['coin_amount']=round(((0.1*wallet[pair[4:]])/cena),7)    # cena[-1] zamieniono na cena dla uproszczenia pętli
    smas_budget2['coin_amount']=round_down(((0.1*wallet[pair[4:]])/cena),7)
    smas_budget3['coin_amount']=((0.1*wallet[pair[4:]])/cena)
    if smas_budget['coin_amount'] != smas_budget2['coin_amount']:
        print('1: ', smas_budget['coin_amount'], ' 2: ',smas_budget2['coin_amount'], ' 3: ',smas_budget3['coin_amount'], ' Cena: ', cena)