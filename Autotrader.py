        if len(cena)>zakres:
            
            smas=Si.SI_sma(cena=cena, zakres=zakres)                 
            rsi=Si.SI_RSI(cena=cena)
            print("===========================================================")
            print(rsi)
            if ((cena[-1]>smas[-1]) and (cena[-1]<cena[-2]) and smas_budget["kupiono"]==True):
                smas_budget["kupiono"]=False
                smas_budget["BuyPrice"]=cena[-1]
                smas_budget["2coin"]=round((smas_budget["1coin"]*cena[-1]),2)
                smas_budget["1coin"]=0
                print("SMAS_SELL @ Price {} current budget {} 1coin. {} 2coin".format(cena[-1],smas_budget["1coin"],smas_budget["2coin"]))
            elif ((cena[-1]<smas[-1]) and (cena[-1]>cena[-2]) and (smas_budget["kupiono"]==False) and (smas_budget["BuyPrice"]<cena[-1])):
                smas_budget["kupiono"]=True
                smas_budget["1coin"]=round((smas_budget["2coin"]/cena[-1]),7)
                smas_budget["2coin"]=0
                print("SMAS_BUY @ Price {} current budget {} 1coin. {} 2coin".format(cena[-1],smas_budget["1coin"],smas_budget["2coin"]))
            else:
                print("SMAS_PASS current budget {} 1coin. {} 2coin".format(smas_budget["1coin"],smas_budget["2coin"]))
            for i in zakres:
                j=zakres.index[i]
                if len(cena)>i:
                    e=Si.SI_ema(cena=cena, zakres=i)
                    k=e.tolist()
                    ema[j].append(k[-1])
                    if ((cena[-1]>ema[j][-1]) and (cena[-1]<cena[-2]) and ema_budget[j]["kupiono"]==True):
                        ema_budget[j]["kupiono"]=False
                        ema_budget[j]["BuyPrice"]=cena[-1]
                        ema_budget[j]["2coin"]=round((ema_budget[j]["1coin"]*cena[-1]),2)
                        ema_budget[j]["1coin"]=0
                        print("ema{}_SELL @ Price {} current budget {} 1coin. {} 2coin".format((j+1),cena[-1],ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                    elif ((cena[-1]<ema[j][-1]) and (cena[-1]>cena[-2]) and (ema_budget[j]["kupiono"]==False) and (ema_budget[j]["BuyPrice"]<cena[-1])):
                        ema_budget[j]["kupiono"]=True
                        ema_budget[j]["1coin"]=round((ema_budget[j]["2coin"]/cena[-1]),7)
                        ema_budget[j]["2coin"]=0
                        print("ema{}_BUY @ Price {} current budget {} 1coin. {} 2coin".format((j+1),cena[-1],ema_budget[j]["1coin"],ema_budget[j]["2coin"]))
                    else:
                        print("EMA{}_PASS current budget {} 1coin. {} 2coin".format(ema_budget[j]["1coin"],ema_budget[j]["2coin"]))

