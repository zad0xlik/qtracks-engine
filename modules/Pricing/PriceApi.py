import datetime
import time
import json
from math import *
from modules.Pricing import Pricing
from modules.Db import Redis
from modules.Chain import Chain

def is_float(input):
  try:
    num = float(input)
  except ValueError:
    return False
  return True

def checkSymbolType(symbol):
    try:
        if(symbol.split("_")[1][6]=="P" or symbol.split("_")[1][6]=="C"):
            return "symbol_id"
        else:
            return "not_valid"
    except IndexError:
        return "equity"
            
       

def price(accountId, symbols):
    prices = []

    for symbol in symbols:
        """
        Assign symbol_id, equity or not_valid
        """
        symbolType = checkSymbolType(symbol)

        """
        handle equity
        """
        if(symbolType == "equity"):
            """
            Check cache / download quote
            """
            chain = Redis.r.get('quote'+symbol)
            if(chain is None):
                chain = Chain.getQuote(accountId, symbol)
            else:
                chain = json.loads(chain)

            
            """
            calculate equity
            """
            if(chain is not None):
                price = round((float(chain[list(chain.keys())[0]]["askPrice"]) + float(chain[list(chain.keys())[0]]["bidPrice"]))/2,2)
                prices.append({symbol: {
                    "price": price,
                    "operation": "success"
                }})
            continue

        """
        handle symbol_id chain
        """
        start = time.time()
        chain = None
        if(symbolType == "symbol_id"):
            """
            check cache / download chain
            """
            symbolParts = symbol.split("_")
            symbolWithDate = symbolParts[0] + "_" + symbolParts[1][:6] + symbolParts[1][6]
            chain = Redis.r.get('chain' + symbolWithDate)
            if(chain is None):
                chain = Chain.getChainStrikes(accountId, symbol)
            else:
                chain = json.loads(chain)
        

        end = time.time()

        """
        calculate symbol_id price
        """
        if(chain is not None):
            lastunderlying = float(chain["underlying"])
            prices.append(Pricing.calculate(lastunderlying, chain, symbol, 0, 4).to_json())
            
    return prices

