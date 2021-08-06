import time
import json
import requests
from datetime import datetime
from modules.Auth import Auth
from modules.Db import Redis


def convertSymbolDate(symbolParts):
    month = symbolParts[:2]
    day = symbolParts[2:4]
    year = "20"+symbolParts[4:6]
    return f'{year}-{month}-{day}'

# Get chain data for a given symbol and expiration date


def getChainStrikes(accountId, symbol):
    symbolParts = symbol.split("_")
    symbolWithDate = symbolParts[0]+"_" + symbolParts[1][:6]+symbolParts[1][6]

    # check if anything exists in redis db
    key_check = Redis.r.exists("name")
    print("key_check: ", key_check)
    keys_check = Redis.r.keys()
    print("keys_check: ", keys_check)

    chain = Redis.r.get('chain'+symbolWithDate)
    print("-----", symbolParts[0])

    if(chain is None):
        # Sets the access token as a header param
        start = time.time()
        header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
#         header = {"Authorization": f'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODc4NzU1NTEsIm5iZiI6MTU4Nzg3NTU1MSwianRpIjoiMGE5ZjQ2MWMtMTBkZi00ZGNiLTljOTAtNmU5M2Q2NTlmMmU1IiwiZXhwIjoxNTg4NDgwMzUxLCJpZGVudGl0eSI6InRlc3RhY2NvdW50IiwiZnJlc2giOmZhbHNlLCJ0eXBlIjoiYWNjZXNzIn0.V0LgDc40jxBffFib60SyCSiUAPhNEr8IFukjvB9WnkU'}

        putcallSymbol = ""
        putcall = ""
        symbolDate = convertSymbolDate(symbolParts[1])

        if(symbolParts[1][6] == "P"):
            putcallSymbol = "putExpDateMap"
            putcall = "PUT"
        else:
            putcallSymbol = "callExpDateMap"
            putcall = "CALL"
        body = {
            "symbol": symbolParts[0],
            "includeQuotes": "TRUE",
            "contractType": putcall,
            "fromDate": symbolDate,
            "toDate": symbolDate,
            "optionType": "s"
        }
        # requests.get.headers = header params
        print("header supplied: ", header)
        print("body supplied: ", body)
        response = requests.get(
            f'https://api.tdameritrade.com/v1/marketdata/chains',
            headers=header,
            params=body
        )
        print("get chain info content: ", response.content)
        if(response.content):
            chain = json.loads(response.content)
            print("this is the response we are getting: ", chain)
            if(response.status_code == 200):
                if(chain["status"] == "SUCCESS"):
                    exactSymbolDate = ""
                    for chainDate in chain[putcallSymbol].keys():
                        if(symbolDate in chainDate):
                            exactSymbolDate = chainDate
                        else:
                            return None
                    chainToSend = {}
                    chainToSend.update(
                        {"underlying": chain["underlyingPrice"]})
                    chainToSend.update(chain[putcallSymbol][exactSymbolDate])
                    end = time.time()
                    print("Snapshot Download Time: " + str(end-start))
                    now = datetime.now()
                    date = now.strftime("%y-%m-%d")
                    timeNow = now.strftime("%H:%M:%S")
                    """
                    Save chain in DB
                    """
                    # Redis.r.set('chain'+' '+symbolWithDate+' '+date+' '+timeNow,
                    #             json.dumps(chainToSend))
                    # Replace for postgres db
                    # fields: chain, symbolwithdate, date and time
                    Redis.r.set('chain'+symbolWithDate,
                                json.dumps(chainToSend))
                    Redis.r.expire('chain'+symbolWithDate, 3)
                    return chainToSend
    else:
        return json.loads(chain)
    return None


def getQuote(accountId, symbol):
    chain = Redis.r.get('quote'+symbol)
    if(chain is None):
        header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
        response = requests.get(
            f'https://api.tdameritrade.com/v1/marketdata/{symbol}/quotes',
            headers=header
        )
        if(response.content):
            chain = json.loads(response.content)
            if(response.status_code == 200):
                Redis.r.set('quote'+symbol, response.content)
                Redis.r.expire('quote'+symbol, 3)
                return chain
        return None
    else:
        chain = json.loads(chain)
    return chain
