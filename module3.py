class Mywebsocket(object):
    def __init__(self, produkty=["RUB-USD", "RUB-EUR", "USD-EUR"]):
        self.produkty=produkty
    def start(self):
        print(self.produkty)
class Adria(Mywebsocket):
    def __init__(self, produkty="USD-EUR"):
        self.produkty=produkty   
    def start(self, produkty):  
        webs=Mywebsocket(produkty=produkty)
        webs.start()   


class Autotrader():
    produkty=["RUB-USD"]
    bot=Adria()
    bot.start(produkty)

Autotrader()