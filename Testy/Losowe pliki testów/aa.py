smas_budget={"2coin":float(50),"1coin":float(0)}
while True:
    cena=float(input("cena kupna"))
    print(cena)
    smas_budget["1coin"]=float(round((smas_budget["2coin"]/cena),7))
    smas_budget["2coin"]=float(0)
    print("{}/{}".format(smas_budget["1coin"], smas_budget["2coin"]))
    cena=float(input("cena sprzedazy"))
    print(cena)
    smas_budget["2coin"]=float(round((smas_budget["1coin"]*cena),2))
    smas_budget["1coin"]=float(0)
    print("{}/{}".format(smas_budget["1coin"], smas_budget["2coin"]))
