import json
import asyncio
import requests
from pathlib import Path
from modules.Auth import Auth

def getOrder(accountId, orderId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders/{orderId}',
        headers=header
    )
    if(response.content):
        return json.loads(response.content)
    return []


async def getOrderAsync(accountId, orderId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders/{orderId}',
        headers=header
    )
    if(response.content):
        return json.loads(response.content)
    return []

# 455032086
# https://api.tdameritrade.com/v1/accounts/455032086/orders
def getOrdersByPath(accountId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders',
        headers=header
    )
    print("header: ", header)
    print("accountId: ", accountId)
    print("response: ", response)
    print("response status code: ", response.status_code)
    print("response content: ", response.content)

    if(response.status_code == 200):
        content = json.loads(response.content)
        return content
    return False


def getPlacedOrdersBySymbol(receivedOrder):
    header = {
        "Authorization": f'Bearer {Auth.getAccessToken(receivedOrder["accountId"])}'}
    params = [{"status": "WORKING"}, {"status": "QUEUED"}]
    orderFound = []

    for param in params:
        response = requests.get(
            f'https://api.tdameritrade.com/v1/accounts/{receivedOrder["accountId"]}/orders',
            headers=header,
            params=param
        )
        print(response)
        if(response.content):
            print("response content: ", response.content)
            content = json.loads(response.content)
            if(response.status_code == 200):
                referencePlacedOrders = []
                for order in content:
                    filteredLegs = []
                    for leg in order["orderLegCollection"]:
                        filteredLegs.append({
                            "orderLegType": leg["orderLegType"],
                            "assetType": leg["instrument"]["assetType"],
                            "symbol": leg["instrument"]["symbol"],
                            "instruction": leg["instruction"],
                            "quantity": str(int(leg["quantity"]))
                        })
                    referenceOrder = {
                        'accountId': str(order['accountId']),
                        'session': order['session'],
                        'duration': order['duration'],
                        'legs': filteredLegs,
                        'orderStrategyType': order['orderStrategyType']
                    }
                    referencePlacedOrders.append(referenceOrder)
                print("reference placed orders: ", referencePlacedOrders)
                print("received order: ", receivedOrder)
                try:
                    orderFoundIndex = referencePlacedOrders.index(
                        receivedOrder)
                    orderFound.append(content[orderFoundIndex])
                    print("Order found")
                    return content[orderFoundIndex]
                except ValueError:
                    pass
            else:
                print("error getting orders")
                print(response.status_code)
        else:
            print("get order id failed")
    return orderFound

async def getPlacedOrdersBySymbolAsync(receivedOrder):
    header = {
        "Authorization": f'Bearer {Auth.getAccessToken(receivedOrder["accountId"])}'}
    params = [{"status": "WORKING"}, {"status": "QUEUED"}]
    orderFound = []

    for param in params:
        response = requests.get(
            f'https://api.tdameritrade.com/v1/accounts/{receivedOrder["accountId"]}/orders',
            headers=header,
            params=param
        )
        if(response.content):
            content = json.loads(response.content)
            if(response.status_code == 200):
                referencePlacedOrders = []
                for order in content:
                    filteredLegs = []
                    for leg in order["orderLegCollection"]:
                        filteredLegs.append({
                            "orderLegType": leg["orderLegType"],
                            "assetType": leg["instrument"]["assetType"],
                            "symbol": leg["instrument"]["symbol"],
                            "instruction": leg["instruction"],
                            "quantity": float(leg["quantity"])
                        })
                    referenceOrder = {
                        'accountId': str(order['accountId']),
                        'session': order['session'],
                        'duration': order['duration'],
                        'legs': filteredLegs,
                        'orderStrategyType': order['orderStrategyType']
                    }
                    referencePlacedOrders.append(referenceOrder)
                try:
                    orderFoundIndex = referencePlacedOrders.index(
                        receivedOrder)
                    orderFound.append(content[orderFoundIndex])
                    return content[orderFoundIndex]
                except ValueError:
                    pass
            else:
                print("error getting orders")
                print(response.status_code)
    return orderFound


def getFilledOrdersBySymbol(accountId, symbol):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    params = {"status": "FILLED"}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders',
        headers=header,
        params=params
    )
    if(response.content):
        content = json.loads(response.content)
        f = open(Path("modules/Order/filled.md"), "a+")
        f.write(json.dumps(content, indent=2))
        f.close()
        orderIds = []
        orders = []
        for order in content:
            if(symbol == order["orderLegCollection"][0]["instrument"]["symbol"]):
                print(f'Order id found: {order["orderId"]}')
                orderIds.append(order["orderId"])
        for orderId in orderIds:
            orders.append(getOrder(accountId, orderId))
        if(orders):
            print(orders)
        return orders
    return False


def getPlacedOrderId(accountId, symbol):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    params = {"status": "QUEUED"}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders',
        headers=header,
        params=params
    )
    content = json.loads(response.content)
    f = open(Path("modules/Order/orders.md"), "w+")
    f.write(json.dumps(content, indent=2))
    f.close()
    for order in content:
        if(symbol == order["orderLegCollection"][0]["instrument"]["symbol"]):
            print(f'Order id found: {order["orderId"]}')
            return order["orderId"]
    return False

def placeOrder(order):
    legs = []
    accountId = order["accountId"]
    session = order["session"]
    duration = order["duration"]
    orderType = order["orderType"]
    price = order["price"]
    orderStrategyType = order["orderStrategyType"]
    for leg in order["legs"]:
        if(leg["orderLegType"] == "EQUITY"):
            legs.append({
                "orderLegType": leg["orderLegType"],
                "instrument": {
                    "assetType": leg["assetType"],
                    "symbol": leg["symbol"]
                },
                "instruction": leg["instruction"],
                "quantity": leg["quantity"]
            })
        else:
            putCall = ""
            if(leg["symbol"].split("_")[1][6] == "P"):
                putCall = "PUT"
            else:
                putCall = "CALL"
            legs.append({
                "orderLegType": leg["orderLegType"],
                "instrument": {
                    "assetType": leg["assetType"],
                    "symbol": leg["symbol"],
                    "putCall": putCall
                },
                "instruction": leg["instruction"],
                "quantity": leg["quantity"]
            })
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    body = {
        "session": session,
        "duration": duration,
        "orderType": orderType,
        "price": price,
        "orderLegCollection": legs,
        "orderStrategyType": orderStrategyType
    }
    response = requests.post(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders',
        headers=header,
        json=body
    )
    print(response)
    if(response.content):
        print(response.content)
    if(response.status_code == 201):
        return True
    return False

def replaceOrder(order, orderId, newPrice):
    accountId = order["accountId"]
    session = order["session"]
    duration = order["duration"]
    orderType = order["orderType"]
    legs = []
    orderStrategyType = order["orderStrategyType"]
    for leg in order["legs"]:
        if(leg["orderLegType"] == "EQUITY"):
            legs.append({
                "orderLegType": leg["orderLegType"],
                "instrument": {
                    "assetType": leg["assetType"],
                    "symbol": leg["symbol"]
                },
                "instruction": leg["instruction"],
                "quantity": leg["quantity"]
            })
        else:
            putCall = ""
            if(leg["symbol"].split("_")[1][6] == "P"):
                putCall = "PUT"
            else:
                putCall = "CALL"
            legs.append({
                "orderLegType": leg["orderLegType"],
                "instrument": {
                    "assetType": leg["assetType"],
                    "symbol": leg["symbol"],
                    "putCall": putCall
                },
                "instruction": leg["instruction"],
                "quantity": leg["quantity"]
            })
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    body = {
        "session": session,
        "duration": duration,
        "orderType": orderType,
        "price": newPrice,
        "orderLegCollection": legs,
        "orderStrategyType": orderStrategyType
    }
    response = requests.put(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders/{orderId}',
        headers=header,
        json=body
    )
    print(response)
    if(response.content):
        print(json.dumps(json.loads(response.content), indent=2))
    if(response.status_code == 201):
        return True
    else:
        return False

def deleteOrder(accountId, orderId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    response = requests.delete(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders/{orderId}',
        headers=header
    )
    print("-------------------------------------")
    print("Deleted order id: ", orderId)
    print("Deletion response code: ", response.status_code)
    print(response)
    return response.status_code


async def deleteOrderAsync(accountId, orderId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    response = requests.delete(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}/orders/{orderId}',
        headers=header
    )
    print(response)
    if(response.status_code == 200):
        return True
    else:
        return False

def getPositions(accountId):
    header = {"Authorization": f'Bearer {Auth.getAccessToken(accountId)}'}
    params = {"fields": "positions"}
    response = requests.get(
        f'https://api.tdameritrade.com/v1/accounts/{accountId}',
        headers=header,
        params=params
    )
    if(response.content):
        return json.loads(response.content)
