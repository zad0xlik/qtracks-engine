import time
import json
import urllib
import xmltodict
import asyncio
import websockets
from pathlib import Path
from datetime import datetime
from modules.Chain import Chain
from modules.Auth import Auth
from modules.Db import Redis


def optionField(key):
    fields = {
        "2": "bid",
        "3": "ask",
        "4": "last"
    }
    if(key in fields.keys()):
        return fields[key]
    return None


def symbolParse(symbol):
    symbolParts = symbol.split("_")
    symbolWithDate = symbolParts[0]+"_" + \
        symbolParts[1][:6]+symbolParts[1][6]
    return symbolWithDate


async def getCredentials(user):
    date_time_obj = datetime.strptime(
        user["streamerInfo"]["tokenTimestamp"], "%Y-%m-%dT%H:%M:%S%z")
    timestamp = str(date_time_obj.timestamp()*1000)
    credentials = {
        "userid": user["accounts"][0]["accountId"],
        "token": user["streamerInfo"]["token"],
        "company": user["accounts"][0]["company"],
        "segment": user["accounts"][0]["segment"],
        "cddomain": user["accounts"][0]["accountCdDomainId"],
        "usergroup": user["streamerInfo"]["userGroup"],
        "accesslevel": user["streamerInfo"]["accessLevel"],
        "authorized": "Y",
        "timestamp": timestamp[:-2],
        "appid": user["streamerInfo"]["appId"],
        "acl": user["streamerInfo"]["acl"]
    }

    # Format the credentials to url format
    return(urllib.parse.urlencode(credentials))


async def stream(accountId, symbols):
    user = Auth.getUserPrincipals(accountId)
    credentials = await getCredentials(user)
    request = {
        "requests": [
            {
                "service": "ADMIN",
                "command": "LOGIN",
                "requestid": 0,
                "account": user["accounts"][0]["accountId"],
                "source": user["streamerInfo"]["appId"],
                "parameters": {
                    "credential": credentials,
                    "token": user["streamerInfo"]["token"],
                    "version": "1.0",
                    "qoslevel": 0
                }
            },
            {
                "service": "ACCT_ACTIVITY",
                "requestid": 6,
                "command": "SUBS",
                "account": user["accounts"][0]["accountId"],
                "source": user["streamerInfo"]["appId"],
                "parameters": {
                    "keys": user["streamerSubscriptionKeys"]["keys"][0]["key"],
                    "fields": "0,1,2,3"
                }
            }
        ]
    }
    SUBS = {
        "service": "OPTION",
        "requestid": 1,
        "command": "SUBS",
        "account": user["accounts"][0]["accountId"],
        "source": user["streamerInfo"]["appId"],
        "parameters": {
            "keys": symbols,
            "fields": "0,1,2,3,4,20,39"
        }
    }
    LOGIN = json.dumps(request["requests"][0])
    async with websockets.connect(f'wss://{user["streamerInfo"]["streamerSocketUrl"]}/ws') as websocket:
        await websocket.send(LOGIN)
        response = await websocket.recv()
        print(response)
        symbols = await websocket.send(json.dumps(SUBS))
        while(True):
            symbolResponse = await websocket.recv()
            responseData = json.loads(symbolResponse)
            print(json.dumps(responseData, indent=2))
            if(responseData.get("data")):
                if(responseData["data"][0].get("content")):
                    for content in responseData["data"][0]["content"]:
                        symbol = content["key"]
                        symbolParts = symbol.split("_")
                        symbolWithDate = symbolParse(symbol)
                        chain = Redis.r.get("chain" + symbolWithDate)
                        if(chain is not None):
                            chain = json.loads(chain)
                        else:
                            chain = Chain.getChainStrikes(accountId, symbol)
                        symbolStrikeKey = symbolParts[1][7:]+".0"
                        if(symbolStrikeKey in chain.keys()):
                            for key in content.keys():
                                field = optionField(key)
                                if(field is not None):
                                    print(field)
                                    print(symbolStrikeKey)
                                    chain[symbolStrikeKey][0][field] = content[key]
                                    Redis.r.set(
                                        "chain" + symbolWithDate, json.dumps(chain))
                                    Redis.r.expire('chain'+symbolWithDate, 8)


def startStream(account, symbols):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream(account, symbols))
