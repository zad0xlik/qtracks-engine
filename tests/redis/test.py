import redis
import json

r = redis.Redis(
    host='127.0.0.1',
    port=6379,
    password='',
    decode_responses=True
)

ORDER = {
    "accountId": "1215141",
    "session": "not normal",
    "duration": "DAY",
    "orderType": "LIMIT",
    "legs": [
        {
            "orderLegType": "OPTION",
            "assetType": "OPTION",
            "symbol": "TSLA_011521C650",
            "putCall": "CALL",
            "instruction": "BUY_TO_OPEN",
            "quantity": "1",
            "ticker": "TSLA",
            "expiration": "011521",
            "strike": "650",
            "price": 1.91,
            "ivAtBid": 0.4274,
            "ivAtAsk": 0.4375,
            "a": 0.42229322547812453,
            "b": 0.43775214654413086,
            "delta": 0.052,
            "theta": -0.012,
            "volatility": 43.32,
            "marketBid": 2.05,
            "marketAsk": 2.35,
            "bid": 1.9062555250833597,
            "ask": 2.3582971652943474,
            "bidSize": 38.0,
            "askSize": 38.0,
            "timestamp": "2019-06-24 19:53:44.405549",
            "runtime": 0.3135693073272705,
            "timeToExpiry": 1.5671232876712329,
            "operation": "success"
        }
    ],
    "orderStrategyType": "SINGLE",
    "price": "Calculating...",
    "ivAdjustment": "0",
    "priceAdjustment": "0",
    "timeToExpiryModifier": "true",
    "status": "STAGING",
    "calculatedPrice": 1.91,
    "totalTheta": -0.012,
    "totalDelta": 0.052,
    "message": "OK"
}


r.set('testaccount', json.dumps(ORDER))
value = r.get('testaccount')
value = json.loads(value)
print(value['session'])
