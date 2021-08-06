import json
from pathlib import Path
from modules.Order import Order
from modules.Db import Redis

def is_float(input):
  try:
    num = float(input)
  except ValueError:
    return False
  return True

def updateFullOrders(accountId, orders):
    orders = Redis.r.set(f'{accountId}_full_orders', json.dumps(orders))

def updateReferenceOrders(accountId, orders):
    orders = Redis.r.set(f'{accountId}_reference_orders', json.dumps(orders))

def getReferenceOrders(accountId):
    orders = Redis.r.get(f'{accountId}_reference_orders')
    if(orders):
        return json.loads(orders)
    return []

def getFullOrders(accountId):
    orders = Redis.r.get(f'{accountId}_full_orders')
    if(orders):
        return json.loads(orders)
    return []

def getAllFullOrders():
    allOrders = []
    keys = Redis.r.keys('*_full_*')
    for key in keys:
        orders = Redis.r.get(key)
        if(orders):
            orders = json.loads(orders)
            allOrders.extend(orders)
    if(allOrders):
        return allOrders
    return []


def addOrder(order):
    accountId = order['accountId']
    referenceOrders = getReferenceOrders(accountId)
    newOrderLegs = []
    for leg in order['legs']:
        newOrderLegs.append({
            "orderLegType": leg["orderLegType"],
            "assetType": leg["assetType"],
            "symbol": leg["symbol"],
            "instruction": leg["instruction"],
            "quantity": leg["quantity"]
        })
    referenceOrder = {
        'accountId': order['accountId'],
        'session': order['session'],
        'duration': order['duration'],
        'legs': newOrderLegs,
        'orderStrategyType': order['orderStrategyType']
    }
    if(referenceOrder not in referenceOrders):
        fullOrders = getFullOrders(accountId)
        fullOrders.append(order)
        referenceOrders.append(referenceOrder)
        updateReferenceOrders(accountId, referenceOrders)
        updateFullOrders(accountId, fullOrders)
        return True
    return False


def deleteOrder(order):
    referenceOrders = getReferenceOrders(order['accountId'])
    fullOrders = getFullOrders(order['accountId'])
    orderSent = order
    orderSent.pop('price', None)
    if(orderSent in referenceOrders):
        index = referenceOrders.index(orderSent)
        """
        handle placed orders
        """
        if(is_float(fullOrders[index]["price"])):
            if(fullOrders[index].get("orderId")):
                Order.deleteOrder(order['accountId'], fullOrders[index]["orderId"])
                print("deleted,", fullOrders[index]["orderId"])
            else:
                """
                Get the ID of the order placed
                """
                orderFound = Order.getPlacedOrdersBySymbol(referenceOrders[index])
                if(orderFound):
                    deleted = Order.deleteOrder(order['accountId'], orderFound["orderId"])
                    if(deleted):
                        print("deleted successfully from TD")
                else:
                    print("error obtaining the order Id")
        del referenceOrders[index]
        print(fullOrders[index])
        del fullOrders[index]
        updateReferenceOrders(order['accountId'], referenceOrders)
        updateFullOrders(order['accountId'], fullOrders)


def updateOrderStatus(order):
    referenceOrders = getReferenceOrders(order['accountId'])
    fullOrders = getFullOrders(order['accountId'])
    orderSent = order
    orderSent.pop('price', None)
    if(orderSent in referenceOrders):
        index = referenceOrders.index(orderSent)
        if(fullOrders[index].get("calculatedPrice")):
            fullOrders[index]["status"] = "STAGED"
            fullOrders[index]["price"] = fullOrders[index]["calculatedPrice"]
            """
            Change broker status to know its not yet placed
            """
            fullOrders[index].update({"brokerStatus" : "NOT_PLACED"})
            updateFullOrders(order['accountId'], fullOrders)
