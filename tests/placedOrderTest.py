from pathlib import Path

placedOrder = {'session': 'NORMAL', 'duration': 'DAY', 'orderType': 'LIMIT', 'complexOrderStrategyType': 'NONE', 'quantity': 1.0, 'filledQuantity': 0.0, 'remainingQuantity': 1.0, 'requestedDestination': 'AUTO', 'destinationLinkName': 'AutoRoute', 'price': 0.65, 'orderLegCollection': [{'orderLegType': 'OPTION', 'legId': 1, 'instrument': {'assetType': 'OPTION', 'cusip': '0SPY..DA90289000', 'symbol': 'SPY_041019C289', 'description': 'SPY APR 10 2019 289.0 Call'}, 'instruction': 'BUY_TO_OPEN', 'positionEffect': 'OPENING', 'quantity': 1.0}], 'orderStrategyType': 'SINGLE', 'orderId': 2122781353, 'cancelable': True, 'editable': True, 'status': 'QUEUED', 'enteredTime': '2019-04-08T19:58:22+0000', 'accountId': 885084780}

ourOrder = {}

with open(Path("Stream.txt"), mode="r") as f:
    linepos = 0
    for line in f:
        linepos = linepos+1
        params = line.split()
        ourOrder = {
            'accountId': params[0],
            'session': params[1],
            'duration': params[2],
            'orderType': params[3],
            'orderLegType': params[4],
            'assetType': params[5],
            'symbol': params[6],
            'putCall': params[7],
            'instruction': params[8],
            'quantity': params[9],
            'orderStrategyType': params[10],
            'x': params[11],
            'linepos': linepos
        }

instructionParts = ourOrder["instruction"].split("_")
print(instructionParts[0])

if(placedOrder["accountId"] == int(ourOrder["accountId"]) and 
    placedOrder["session"] == ourOrder["session"] and 
    placedOrder["duration"] == ourOrder["duration"] and 
    placedOrder["orderType"] == ourOrder["orderType"] and 
    placedOrder["orderLegCollection"][0]["orderLegType"] == ourOrder["orderLegType"] and 
    placedOrder["orderLegCollection"][0]["instrument"]["assetType"] == ourOrder["assetType"] and 
    placedOrder["orderLegCollection"][0]["instrument"]["symbol"] == ourOrder["symbol"] and 
    instructionParts[0] in placedOrder["orderLegCollection"][0]["instruction"] and 
    placedOrder["orderLegCollection"][0]["quantity"] == float(ourOrder["quantity"]) and 
    placedOrder["orderStrategyType"] == ourOrder["orderStrategyType"]
    ):
    print("Passed!")
else:
    print("Test didn't pass...")
    print(placedOrder)
    print(ourOrder)