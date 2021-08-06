import time
import json
import asyncio
import subprocess
from pathlib import Path
from modules.Db import Redis
from modules.Streamer import Multistream
from modules.Order.OrderHandler import getAllFullOrders


def symbolParse(symbol):
    symbolParts = symbol.split("_")
    if(len(symbolParts) > 1):
        symbolWithDate = symbolParts[0]+"_" + \
            symbolParts[1][:6]+symbolParts[1][6]
        return symbolWithDate
    return symbol


def stream():
    print("Listening for orders to download chain...")
    while(True):
        orders = []
        symbols = []
        streaming = Redis.r.get("streaming")
        if(streaming is None):
            streaming = []
        if(len(streaming) != 0):
            streaming = json.loads(streaming)
            Redis.r.expire("streaming", 10)

        orders = getAllFullOrders()
        print(json.dumps(orders))
        for order in orders:
            for leg in order["legs"]:
                symbol = leg["symbol"]
                symbolWithDate = symbolParse(symbol)
                print(symbolWithDate)
                if(symbolWithDate not in symbols):
                    symbols.append(symbolWithDate)
        if(len(symbols) != 0):
            print(symbols)
            print(streaming)
            if(symbols != streaming):
                Redis.r.set("streaming", json.dumps(symbols))
                print(",".join(symbols))
                subprocess.call(
                    ["python", "qtracks.py", "daemon", "-s", ",".join(symbols)])
                print("OK")
        else:
            if(len(streaming) != 0):
                Redis.r.delete("streaming")
                print("DELETED, OK")
        time.sleep(2)
