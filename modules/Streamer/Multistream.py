import daemon
import asyncio
import json
import sys
import os
from pathlib import Path
from modules.Streamer import Stream
from modules.Db import Redis
from modules.Chain import Chain


def symbolParse(symbol):
    symbolParts = symbol.split("_")
    symbolWithDate = symbolParts[0]+"_" + \
        symbolParts[1][:6]+symbolParts[1][6]
    return symbolWithDate


def start(account, symbols):
    # with daemon.DaemonContext(stdout=sys.stdout,
    #                           stderr=sys.stderr):
    with daemon.DaemonContext():
        symbolIds = []
        symbolsWithDate = []
        for symbol in symbols:
            """
            Extract symbol with date and putCall for each symbol
            from symbol list passed
            """
            symbolWithDate = symbolParse(symbol)

            if(symbolWithDate not in symbolsWithDate):
                """
                Load chain, download data if no cache available
                """
                currentChain = Redis.r.get("chain"+symbolWithDate)
                if(currentChain is None):
                    currentChain = Chain.getChainStrikes(account, symbol)
                else:
                    currentChain = json.loads(currentChain)

                if(currentChain is not None):
                    """
                    Handle underlying price from symbol
                    """
                    underlying = currentChain['underlying']
                    del currentChain['underlying']

                    """
                    Add symbol-ids to a list to use in the streamer
                    """

                    chainKeys = [symbolWithDate+str(round(float(strike)))
                                 for strike in currentChain]
                    """
                    Parsed to set first so it doens't contain duplicates
                    """
                    symbolIds.extend(list(set(chainKeys)))

                    """
                    Add the symbolWithDate to a list so it doesn't repeat
                    """
                    symbolsWithDate.append(symbolWithDate)

        """
        Make a string out of the ids
        """
        symbolIds = ','.join(symbolIds)
        print(symbolIds)

        """
        Start the streamer for the user
        """
        Stream.startStream('885084780', symbolIds)
