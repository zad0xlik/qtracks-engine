import sys
import time
import json
import asyncio
import aiofiles
import xmltodict
import copy
from pathlib import Path
from datetime import datetime
from modules.Auth import Auth
from modules.Order import Order
from modules.Db import Redis
from modules.Order.OrderHandler import getFullOrders, getReferenceOrders, updateFullOrders

def is_float(input):
  try:
    num = float(input)
  except ValueError:
    return False
  return True


def formatStamp(stamp):
    return datetime.fromtimestamp(stamp/1000).isoformat()


def begin():
    print("Listening for orders to send...")
    while(True):
        """
        get the orders of each user
        """
        usersKeys = Redis.r.keys('*_full_*')
        for userKey in usersKeys:
            accountId = userKey.split("_")[0]
            currentOrders = getFullOrders(accountId)
            initialRead = copy.deepcopy(currentOrders)
            referenceOrders = getReferenceOrders(accountId)
            if(currentOrders and referenceOrders):
                """
                Handling place/replace
                """
                for orderNum, referenceOrder in enumerate(referenceOrders):
                    """
                    case: place new order
                    """
                    if(currentOrders[orderNum].get("orderId") is None and currentOrders[orderNum].get("brokerStatus")):
                        if(currentOrders[orderNum]["brokerStatus"] != "NOT_PLACED"):
                            continue
                        """
                        check if order is staged by looking at the price
                        (Not float  = Not staged)
                        """
                        if(is_float(currentOrders[orderNum]["price"])):
                            """
                            place the order
                            if the order price has not updated in mid transaction
                            """
                            placed = False
                            """
                            check the latest prices
                            """
                            latestRead = getFullOrders(accountId)
                            if(latestRead == initialRead):
                                if(currentOrders[orderNum]["price"] == 0):
                                    continue
                                placed = Order.placeOrder(currentOrders[orderNum])
                                print("Order placed: ")
                                print(currentOrders[orderNum])
                            if(placed):
                                """
                                Get the info of the order just placed from TD
                                """
                                orderFound = Order.getPlacedOrdersBySymbol(referenceOrder)
                                if(orderFound):
                                    currentOrders[orderNum].update({"orderId" : orderFound["orderId"]})
                                    currentOrders[orderNum].update({"brokerStatus" : orderFound["status"]})
                                    updateFullOrders(accountId, currentOrders)
                                    print(orderFound["orderId"])
                                else:
                                    currentOrders[orderNum].update({"brokerStatus" : "ID_NOT_FOUND"})
                                    updateFullOrders(accountId, currentOrders)
                            else:
                                currentOrders[orderNum].update({"brokerStatus" : "ERROR"})
                                updateFullOrders(accountId, currentOrders)
                                print("Order didn't place because of reasons")
                    """
                    case: replace changed order
                    """
                    if(currentOrders[orderNum].get("orderId") is not None):
                        """
                        Cache order info
                        """
                        placedOrder = Redis.r.get(currentOrders[orderNum]["orderId"])
                        if(placedOrder):
                            placedOrder = json.loads(placedOrder)
                        else:
                            """
                            1. Download order data with order id
                            """
                            placedOrder = Order.getOrder(
                                accountId
                                , currentOrders[orderNum]["orderId"]
                            )
                            """
                            Save data in cache
                            """
                            if(placedOrder):
                                Redis.r.set(
                                    currentOrders[orderNum]["orderId"]
                                    , json.dumps(placedOrder)
                                )
                                Redis.r.expire(currentOrders[orderNum]["orderId"], 1)
                        """
                        Check that the broker status is correct before replacing
                        *Not filled, not rejected, not cancelled
                        """
                        if(placedOrder.get("status")):
                            if(placedOrder["status"] == "FILLED" or
                                placedOrder["status"] == "REJECTED" or
                                placedOrder["status"] == "CANCELED"
                            ):
                                continue
                        """
                        3. Check if the price is the same as the stored full order
                        """
                        if(currentOrders[orderNum]["price"] == placedOrder["price"]):
                            continue

                        """
                        Check new price is not 0
                        """
                        if(currentOrders[orderNum]["price"] == 0):
                            continue
                        else:
                            latestRead = getFullOrders(accountId)
                            if(latestRead == initialRead):
                                replaced = Order.replaceOrder(
                                                currentOrders[orderNum]
                                                , currentOrders[orderNum]["orderId"]
                                                , currentOrders[orderNum]["price"]
                                            )
                                """
                                4. Get the new order Id and save it to redis
                                """
                                if(replaced):
                                    """
                                    Get the ID of the order just placed and save it to redis
                                    """
                                    orderFound = Order.getPlacedOrdersBySymbol(referenceOrder)
                                    if(orderFound):
                                        currentOrders[orderNum].update({"orderId" : orderFound["orderId"]})
                                        updateFullOrders(accountId, currentOrders)
                                        print(orderFound["orderId"])

                                    print("Order replaced:")
                                    print(json.dumps(currentOrders[orderNum]))         
        time.sleep(0.6)
                    
def start():
    begin()
