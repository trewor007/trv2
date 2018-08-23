from threading import Thread
class x():
    #def __init__(self, raz=None, dwa=None, trzy=None):
    #    self.raz=raz
    #    self.dwa=dwa
    #    self.trzy=trzy
    def start(self):
        def _go():
            self.raz()
            self.dwa()
            self.trzy()
        self.thread=Thread(target=_go)
        self.thread.start()
    def raz(self):
        print("raz")
    def dwa(self):
        print("dwa")
    def trzy(self):
        print("trzy")
xx=x()
xx.start()