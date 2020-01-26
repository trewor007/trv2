aktualizacja=[  [["buy", "166.10", "22.11000000"]], [["sell", "166.90", "10.00000000"]],
                [["buy", "166.12", "13.80000000"]], [["sell", "166.87", "0.93805987"]],
                [["buy", "166.10", "13.80000000"]], [["sell", "167.38", "0"]],
                [["buy", "166.42", "0"]],[['buy','93.1', '1']]]

#Asks=[['166.87','12'], ['166.91','38'], ['167.38','90']] #ma rosnąć
#Bids=[['166.42','90'], ['166.12','12'], ['166.11','38']] #ma maleć

Asks=[[166.87,12], [166.91,38], [167.38,90]] #ma rosnąć
Bids=[[166.42,90], [166.12,12], [166.11,38]] #ma maleć

for Zmiana in aktualizacja:
    JuzJest=False
    if Zmiana[0][0]=='sell':                                           #jeżeli zmiana dotyczy sprzedaży
        zListy=Asks
    else:        zListy=Bids
    for num, data in enumerate(zListy):                                       #przejżyj tabele 
        if data[0]==Zmiana[0][1] and Zmiana[0][2]!='0':                                 #jeżeli cena z aktualizacji znajduje się już w tabeli
            data[1]=Zmiana[0][2]                                   #zamień ilość waluty po tej cenie na tą z aktualizacji
            JuzJest=True
        if data[0]==Zmiana[0][1] and Zmiana[0][2]=='0':   #jeżeli ilość waluty z aktualizacji wynosi zero
            zListy.pop(num)                                                   #usuń daną pozycje z tabeli
            JuzJest=True
    if JuzJest==False and Zmiana[0][0]=='sell':
        for num, data in enumerate(zListy):
            if Zmiana[0][1]<data[0] :     #Ask
                zListy.insert(num, Zmiana[0][1:])
                break
            elif num==(len(zListy)-1):
                zListy.append(Zmiana[0][1:])
                break
            else:
                pass
    if JuzJest==False and Zmiana[0][0]=='buy':
        for num, data in enumerate(zListy):
            if Zmiana[0][1]>data[0] :      #Bid
                zListy.insert(num, Zmiana[0][1:])
                break
            elif num==(len(zListy)-1):
                zListy.append(Zmiana[0][1:])
                break
            else:
                pass
    print(Zmiana)
    print(Asks)
    print(Bids)
    print("=============================")