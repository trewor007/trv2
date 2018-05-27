import time
import json
from websocket import create_connection

ws=create_connection("wss://ws-feed.gdax.com")
ws.send(json.dumps({"type": "subscribe", "channels": [{"name": "heartbeat", "product_ids": ["BTC-EUR"],}]}))
newdict={}  
  
def KonektorWebsocketTicker():                                
    dane=json.loads(ws.recv())                               
    print(json.dumps(dane, indent=4, sort_keys=True))             
    b=['type', 'sequence', 'product_id', 'price', 'open_24h', 'volume_24h', 'low_24h', 'high_24h', 'volume_30d', 'best_bid', 'best_ask', 'side', 'time', 'trade_id', 'last_size']
    i=0
    while i<len(b):
        a = eval("dane.get('" + b[i] + "', None)")
        print(" A:    ", a)
        print(" B[i]: ", b[i])
        newdict[b[i]]=a
        i=i+1
    c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (newdict['type'], newdict['sequence'], newdict['product_id'], newdict['price'], newdict['open_24h'], newdict['volume_24h'], newdict['low_24h'], newdict['high_24h'], newdict['volume_30d'], newdict['best_bid'], newdict['best_ask'], newdict['side'], newdict['time'], newdict['trade_id'], newdict['last_size']))
    conn.commit()
while True:
     KonektorWebsocketHeartbeat()
     print(newdict)
     time.sleep(0.5)  
    



 #c.execute("INSERT INTO Subskribe (type, side, price, time, order_id, product_id, order_type, size, reason, remaining_size, client_oid, sequence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (newdict["type"], newdict["side"], newdict["price"], newdict["time"],  newdict["order_id"], newdict["product_id"], newdict["order_type"], newdict["size"], [newdict["reason"], [newdict["remaining_size"], [newdict["client_oid"], [newdict["sequence"]))
        #x=x+1

#'type', 'side', 'price', 'time', 'order_id', 'product_id', 'order_type', 'size', 'reason', 'remaining_size', 'client_oid', 'sequence'

c.execute("INSERT INTO Ticker(type, sequence, product_id, price, open_24h, volume_24h, low_24h, high_24h, volume_30d, best_bid, best_ask, side, time, trade_id, last_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (newdict['type'], newdict['sequence'], newdict['product_id'], newdict['price'], newdict['open_24h'], newdict['volume_24h'], newdict['low_24h'], newdict['high_24h'], newdict['volume_30d'], newdict['best_bid'], newdict['best_ask'], newdict['side'], newdict['time'], newdict['trade_id'], newdict['last_size']))

'type', 'sequence', 'product_id', 'price', 'open_24h', 'volume_24h', 'low_24h', 'high_24h', 'volume_30d', 'best_bid', 'best_ask', 'side', 'time', 'trade_id', 'last_size'
newdict['type'], newdict['sequence'], newdict['product_id'], newdict['price'], newdict['open_24h'], newdict['volume_24h'], newdict['low_24h'], newdict['high_24h'], newdict['volume_30d'], newdict['best_bid'], newdict['best_ask'], newdict['side'], newdict['time'], newdict['trade_id'], newdict['last_size']

c.execute("INSERT INTO l2update(type, product_id, time, bids, asks, change) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (newdict['type'], newdict['product_id'], newdict['time'], newdict['bids'], newdict['asks'], newdict['change']))