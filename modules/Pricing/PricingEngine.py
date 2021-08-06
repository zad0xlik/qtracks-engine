import datetime
import time
import json
import functools
import copy
from math import *
from modules.Db import Redis
from modules.Chain import Chain
from modules.Pricing import Pricing
from modules.Order.OrderHandler import getFullOrders, updateFullOrders


def is_float(input):
  try:
    num = float(input)
  except ValueError:
    return False
  return True


def symbolParse(symbol):
    symbolParts = symbol.split("_")
    if(len(symbolParts) > 1):
        symbolWithDate = symbolParts[0]+"_" + \
            symbolParts[1][:6]+symbolParts[1][6]
        return symbolWithDate
    return symbol


def orderLegs(orderIndex, legs):
    return {orderIndex : legs}

def start():
    print("Listening for orders to calculate their price...")
    while(True):
        """
        get the orders of each user
        """
        usersKeys = Redis.r.keys('*_full_*')
        for userKey in usersKeys:
            accountId = userKey.split("_")[0]
            """
            Save the orders initial state
            """
            initialOrders = getFullOrders(accountId)
            """
            Get orders as dict
            """
            orders = copy.deepcopy(initialOrders)
            """
            Save each leg by order index
            """
            ordersLegs = []
            [ordersLegs.append(orderLegs(orderIndex, order["legs"])) for orderIndex, order in enumerate(orders)]
            print("line55 order dump:", json.dumps(orders, indent=2))
            """
            Price each leg of a given order
            """
            for order in ordersLegs:
                orderIndex = list(order.keys())[0]
                legs = order[orderIndex]
                ivAdjustment = float(orders[orderIndex]['ivAdjustment'])
                # print(orderIndex)

                for legIndex, leg in enumerate(legs):
                    print(orderIndex, legIndex)
                    accountId = orders[orderIndex]["accountId"]
                    print(accountId)
                    orderLeg = orders[orderIndex]["legs"][legIndex]
                    symbol = orderLeg["symbol"]
                    print(symbol)
                    symbolWithDate = symbolParse(symbol)
                    orderLegType = orderLeg['orderLegType']
                    #print(orderLegType)
                    if(orderLegType == "EQUITY"):
                        """
                        Check cache / download quote
                        """
                        chain = Redis.r.get('quote'+symbolWithDate)
                        if(chain is None):
                            chain = Chain.getQuote(accountId, symbol)
                        else:
                            chain = json.loads(chain)
                        if(chain is not None):
                            askPrice = float(chain[list(chain.keys())[0]]["askPrice"])
                            bidPrice = float(chain[list(chain.keys())[0]]["bidPrice"])
                            price = round((askPrice + bidPrice)/2, 2)
                            orderLeg.update({"price":price})
                            orderLeg.update({'operation': "success"})
                        continue
                    
                    """
                    Download/cache symbol chain
                    """
                    chain = Redis.r.get('chain' + symbolWithDate)
                    if(chain is None):
                        print("Downloading Snapshot for...")
                        print(symbolWithDate)
                        chain = Chain.getChainStrikes(accountId, symbol)
                    else:
                        print("Using cache for...")
                        print(symbolWithDate)
                        chain = json.loads(chain)
                    if(chain is not None):
                        print("check for non-standard chains", chain)
                        """
                        Calculate leg
                        """
                        lastunderlying = float(chain["underlying"])
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "Polyfit at 4")
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 5, "Polyfit at 5")
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 3, 1, 'nearest')
                        calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol" , 3, 2, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 5, 3, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 5, 4, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 7, 3, 'nearest')
                        calculatedPricing = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 7, 4, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 7, 3, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 11, 3, 'nearest')
                        #calculatedPricingTest = Pricing.calculate(lastunderlying, chain, leg["symbol"], ivAdjustment, 4, "savgol", 11, 4, 'nearest')

                        if(calculatedPricing is None):
                            orderLeg.update({'operation': "error"})
                            continue
                        """   
                        Pricing Strategy     
                                &
                        Append leg calculation results to orders dict
                        *orders dict is saved to a file as json
                        """
                        if(calculatedPricing.any()):
                            orderLeg.update({'marketBid': calculatedPricing.marketBid})
                            orderLeg.update({'marketAsk': calculatedPricing.marketAsk})
                            #Begin Bidding Logic
                            if(orderLeg['instruction'].split("_")[0] == "BUY"):
                            #if PricemModel == conservative
                                if(calculatedPricing.marketBid < round(calculatedPricing.CalculatedBid,2)):
                                    print("market < model, reduce bid to market")
                                    if(calculatedPricing.bidSize == float(orderLeg["quantity"])):
                                        orderLeg.update({"price": round(calculatedPricing.marketBid, 2)})
                                        print("we are top bid - bid at market")
                                    else:
                                        orderLeg.update({"price": round(calculatedPricing.marketBid, 2) + .01})
                                        print("increment a penny")
                                else:
                                    orderLeg.update({"price": round(calculatedPricing.CalculatedBid, 2)})
                                    print("model <= market, bid at model, conservative")
                            elif(orderLeg['instruction'].split("_")[0] == "SELL"):
                                if(calculatedPricing.marketAsk > round(calculatedPricing.CalculatedAsk,2)):
                                    print("market > model, increase ask to market")
                                    if(calculatedPricing.askSize == float(orderLeg["quantity"])):
                                         orderLeg.update({"price": round(calculatedPricing.marketAsk, 2)})
                                         print("we are lowest ask - keep ask at market")
                                    else:
                                        orderLeg.update({"price": round(calculatedPricing.marketAsk, 2) - .01})
                                        print("subtract a penny")
                                else:
                                    orderLeg.update({"price": round(calculatedPricing.CalculatedAsk, 2)})
                                    print("model >= market, ask at model, conservative")
                            #update the rest of the info
                            orderLeg.update({'ivAtBid': calculatedPricing.ivAtBid})
                            orderLeg.update({'ivAtAsk': calculatedPricing.ivAtAsk})
                            #orderLeg.update({'a': calculatedPricing.OutputBids})
                            #orderLeg.update({'b': calculatedPricing.OutputAsks})
                            orderLeg.update({'delta': calculatedPricing.delta})
                            orderLeg.update({'theta': calculatedPricing.theta})
                            orderLeg.update({'volatility': calculatedPricing.volatility})
                            orderLeg.update({'bid': calculatedPricing.CalculatedBid})
                            orderLeg.update({'ask': calculatedPricing.CalculatedAsk})
                            orderLeg.update({'bidSize': calculatedPricing.bidSize})
                            orderLeg.update({'askSize': calculatedPricing.askSize})
                            orderLeg.update({'operation': "success"})
                            if(orderLeg['orderLegType']=="EQUITY"):
                                orderLeg.update({'price': round(lastunderlying, 2)})
                        else:
                            orderLeg.update({'operation': "error"})
                    print(orderLeg)

            """
            Handle overall order price, order type,
            total delta, total theta
            """
            for order in ordersLegs:
                orderPrice = 0
                orderIndex = list(order.keys())[0]
                legs = order[orderIndex]
                legsSize = len(legs)-1
                equityPosition=0
                priceAdjustment = float(orders[orderIndex]['priceAdjustment'])
                quantities = []
                sumTheta = 0
                sumDelta = 0

                for legIndex, leg in enumerate(legs):
                    orderLeg = orders[orderIndex]["legs"][legIndex]
                    """
                    If leg didn't calculate, skip it
                    """
                    if(not orderLeg.get("operation")):
                        continue
                    if(orderLeg["operation"] != "success"):
                        continue
                    
                    if(orderLeg["orderLegType"] != "EQUITY"):
                        sumTheta = sumTheta + orderLeg["theta"]
                        sumDelta = sumDelta + orderLeg["delta"]
                        legMessage = orderLeg["operation"]

                    instruction = orderLeg["instruction"].split("_")[0]
                    orderLegType = orderLeg["orderLegType"]
                    price = orderLeg["price"]
                    qty = float(orderLeg["quantity"])
                    equityOrderLeg = [True for searchLeg in orders[orderIndex]["legs"] if searchLeg["orderLegType"]=="EQUITY"]
                    quantities.append(qty)

                    if(is_float(price) and legMessage == "success"):
                        if(orderLegType == "EQUITY"):
                            equityPosition = legIndex
                            if(instruction == "BUY"):
                                pass
                            else:
                                price = price*-1
                            orderPrice = orderPrice + (price*qty)
                        else:
                            if(instruction == "BUY"):
                                pass
                            else:
                                price = price*-1
                            if(equityOrderLeg):
                                orderPrice = orderPrice + (price*qty*100)
                            else:
                                orderPrice = orderPrice + (price*qty)
                    
                    """
                    Calculate order total
                    """
                    if(legIndex==legsSize):
                        """
                        Calculate equity if needed
                        """
                        if(equityOrderLeg):
                            orders[orderIndex]["price"] = orderPrice/float(orders[orderIndex]["legs"][equityPosition]["quantity"])
                        else:
                            orders[orderIndex]["price"] = orderPrice
                        
                        priceWithAdjustment = round(float(orders[orderIndex]["price"]) + float(priceAdjustment), 2)

                        """
                        calculate order total quantity
                        """
                        totalQuantity = functools.reduce(lambda a,b : a+b,quantities)
                        quantityMean = totalQuantity/len(quantities)

                        """
                        Calculate order price
                        """
                        if(quantityMean == int(leg["quantity"])):
                            orders[orderIndex].update({"calculatedPrice": round(abs(priceWithAdjustment)/quantityMean,2)})
                            orders[orderIndex]["price"] = round(abs(priceWithAdjustment)/quantityMean,2)
                        else:
                            orders[orderIndex].update({"calculatedPrice": round(abs(priceWithAdjustment),2)})
                            orders[orderIndex]["price"] = round(abs(priceWithAdjustment),2)

                        """
                        append total theta, delta results
                        """
                        orders[orderIndex].update({"totalTheta": sumTheta})
                        orders[orderIndex].update({"totalDelta": sumDelta})
    
                        """
                        set the order type
                        """
                        if(legsSize==0):
                            pass
                        elif(priceWithAdjustment > 0):
                            orders[orderIndex]["orderType"] = "NET_DEBIT"
                        elif(priceWithAdjustment < 0):
                            orders[orderIndex]["orderType"] = "NET_CREDIT"
                        else:
                            orders[orderIndex]["orderType"] = "NET_ZERO"
                        
                        """
                        control the order status
                        """
                        if(orders[orderIndex]["calculatedPrice"] == 0):
                            orders[orderIndex].update({"message": "WARNING"})
                        else:
                            orders[orderIndex].update({"message": "OK"})

                        if(orders[orderIndex]["status"] == "STAGING"):
                            orders[orderIndex]["price"] = "Calculating..."

            """
            Read the orders for a final state
            """
            currentOrders = getFullOrders(accountId)
            """
            Compare if the state changed (ex: order got deleted) to
            update the price
            """
            if(initialOrders == currentOrders):
                if(len(orders)>0):
                    print("order calculated", orders[0]["accountId"])
                    updateFullOrders(orders[0]["accountId"], orders)

        """
        Delay calculations
        """      
        time.sleep(5)