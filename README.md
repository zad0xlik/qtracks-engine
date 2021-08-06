# Qtracks
Repository containing qtracks cli sourcecode

https://docs.google.com/document/d/1H9lZfbJ7wAShl2oIAH35fhX1WlYMBVlO8V-pj39-Rqw/edit

## Steps to run the project
project is running certbot and would need more info on updating certificates:
https://community.letsencrypt.org/t/not-getting-pem-files-when-requesting-new-certificate/91063

if certificates are not updated then all servers commands need to exclude ssl


## Commands
this has been changed to postgres 
to install mysqcllient on a mac with python3 or greater the following needs to be performed:

brew install mysql-connector-c # macOS (Homebrew)
find / -name mysql_config and open in editor
go to like 112 and change:

#### on macOS, on or about line 112:
#### Create options
libs="-L$pkglibdir"
libs="$libs -l "

to 

#### Create options
libs="-L$pkglibdir"
libs="$libs -lmysqlclient -lssl -lcrypto"

installing additional libraries might require:
```
python3.7 -m ensurepip --upgrade
```


if you need to get keys or if you get error due to keys missing load them from server:
```
scp root@142.93.5.201:/etc/letsencrypt/live/bidasktrader.com/cert.pem ~/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem
scp root@142.93.5.201:/etc/letsencrypt/live/bidasktrader.com/privkey.pem ~/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem
```

attaching to a new shell in a running container:
```
docker exec -it 40808676a616 bash
```

Python needs to be 3.7

dev bash 0 - 
```
python app.py
```
prod bash 0 - 
```
gunicorn --certfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem --keyfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem --bind 0.0.0.0:5000 app:app
```

if you need to kill all screens before you run
```killall SCREEN```

if you need to kill another redis-server running
```redis-cli shutdown```

need to install redis (if can't start then install redis):
start redis prior running app.py
```
brew services start redis
brew services stop redis
```

bash 1 - 
```
python qtracks.py streamorders
```
bash 2 -
``` 
python qtracks.py pricing
```
bash 3 - 
```
python qtracks.py streamchain
```
bash 4 - 
```
python qtracks.py sendorders
```

this is old and not used anymore bash 3 - 
```
sudo service nginx restart
```
bash 4 - 
```
python qtracks.py sendorders ***
```

Execute this in order to run the entire backend with all the other modules
gunicorn --certfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem --keyfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem --bind 0.0.0.0:5000 app:app

Need to update certificates in "StreamOrders.py"

if you create or copy shell files you need to make them into executables:
```
chmod +x proc_exec.sh
```



6. Redis setup

need to install redis 
start redis prior running app.py

>brew services start redis

need to use conf file from server:
```
scp root@142.93.5.201:/etc/redis/redis.conf modules/Db/redis.conf
```

this file contains default password information required by Redis.py code


```
{
    "session": "'NORMAL' or 'AM' or 'PM' or 'SEAMLESS'",
    "duration": "'DAY' or 'GOOD_TILL_CANCEL' or 'FILL_OR_KILL'",
    "orderType": "'MARKET' or 'LIMIT' or 'STOP' or 'STOP_LIMIT' or 'TRAILING_STOP' or 'MARKET_ON_CLOSE' or 'EXERCISE' or 'TRAILING_STOP_LIMIT' or 'NET_DEBIT' or 'NET_CREDIT' or 'NET_ZERO'",
    "cancelTime": {
        "date": "string",
        "shortFormat": false
    },
    "complexOrderStrategyType": "'NONE' or 'COVERED' or 'VERTICAL' or 'BACK_RATIO' or 'CALENDAR' or 'DIAGONAL' or 'STRADDLE' or 'STRANGLE' or 'COLLAR_SYNTHETIC' or 'BUTTERFLY' or 'CONDOR' or 'IRON_CONDOR' or 'VERTICAL_ROLL' or 'COLLAR_WITH_STOCK' or 'DOUBLE_DIAGONAL' or 'UNBALANCED_BUTTERFLY' or 'UNBALANCED_CONDOR' or 'UNBALANCED_IRON_CONDOR' or 'UNBALANCED_VERTICAL_ROLL' or 'CUSTOM'",
    "quantity": 0,
    "filledQuantity": 0,
    "remainingQuantity": 0,
    "requestedDestination": "'INET' or 'ECN_ARCA' or 'CBOE' or 'AMEX' or 'PHLX' or 'ISE' or 'BOX' or 'NYSE' or 'NASDAQ' or 'BATS' or 'C2' or 'AUTO'",
    "destinationLinkName": "string",
    "releaseTime": "string",
    "stopPrice": 0,
    "stopPriceLinkBasis": "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
    "stopPriceLinkType": "'VALUE' or 'PERCENT' or 'TICK'",
    "stopPriceOffset": 0,
    "stopType": "'STANDARD' or 'BID' or 'ASK' or 'LAST' or 'MARK'",
    "priceLinkBasis": "'MANUAL' or 'BASE' or 'TRIGGER' or 'LAST' or 'BID' or 'ASK' or 'ASK_BID' or 'MARK' or 'AVERAGE'",
    "priceLinkType": "'VALUE' or 'PERCENT' or 'TICK'",
    "price": 0,
    "taxLotMethod": "'FIFO' or 'LIFO' or 'HIGH_COST' or 'LOW_COST' or 'AVERAGE_COST' or 'SPECIFIC_LOT'",
    "orderLegCollection": [
        {
            "orderLegType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
            "legId": 0,
            "instrument": "The type <Instrument> has the following subclasses [Option, MutualFund, CashEquivalent, Equity, FixedIncome] descriptions are listed below\"",
            "instruction": "'BUY' or 'SELL' or 'BUY_TO_COVER' or 'SELL_SHORT' or 'BUY_TO_OPEN' or 'BUY_TO_CLOSE' or 'SELL_TO_OPEN' or 'SELL_TO_CLOSE' or 'EXCHANGE'",
            "positionEffect": "'OPENING' or 'CLOSING' or 'AUTOMATIC'",
            "quantity": 0,
            "quantityType": "'ALL_SHARES' or 'DOLLARS' or 'SHARES'"
        }
    ],
    "activationPrice": 0,
    "specialInstruction": "'ALL_OR_NONE' or 'DO_NOT_REDUCE' or 'ALL_OR_NONE_DO_NOT_REDUCE'",
    "orderStrategyType": "'SINGLE' or 'OCO' or 'TRIGGER'",
    "orderId": 0,
    "cancelable": false,
    "editable": false,
    "status": "'AWAITING_PARENT_ORDER' or 'AWAITING_CONDITION' or 'AWAITING_MANUAL_REVIEW' or 'ACCEPTED' or 'AWAITING_UR_OUT' or 'PENDING_ACTIVATION' or 'QUEUED' or 'WORKING' or 'REJECTED' or 'PENDING_CANCEL' or 'CANCELED' or 'PENDING_REPLACE' or 'REPLACED' or 'FILLED' or 'EXPIRED'",
    "enteredTime": "string",
    "closeTime": "string",
    "tag": "string",
    "accountId": 0,
    "orderActivityCollection": [
        "\"The type <OrderActivity> has the following subclasses [Execution] descriptions are listed below\""
    ],
    "replacingOrderCollection": [
        {}
    ],
    "childOrderStrategies": [
        {}
    ],
    "statusDescription": "string"
}
```

//The class <Instrument> has the 
//following subclasses: 
//-Option
//-MutualFund
//-CashEquivalent
//-Equity
//-FixedIncome
//JSON for each are listed below: 

//Option:
```
{
  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
  "cusip": "string",
  "symbol": "string",
  "description": "string",
  "type": "'VANILLA' or 'BINARY' or 'BARRIER'",
  "putCall": "'PUT' or 'CALL'",
  "underlyingSymbol": "string",
  "optionMultiplier": 0,
  "optionDeliverables": [
    {
      "symbol": "string",
      "deliverableUnits": 0,
      "currencyType": "'USD' or 'CAD' or 'EUR' or 'JPY'",
      "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'"
    }
  ]
}
```
//OR

//MutualFund:

```
{
  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
  "cusip": "string",
  "symbol": "string",
  "description": "string",
  "type": "'NOT_APPLICABLE' or 'OPEN_END_NON_TAXABLE' or 'OPEN_END_TAXABLE' or 'NO_LOAD_NON_TAXABLE' or 'NO_LOAD_TAXABLE'"
}
```
//OR

//CashEquivalent:

```
{
  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
  "cusip": "string",
  "symbol": "string",
  "description": "string",
  "type": "'SAVINGS' or 'MONEY_MARKET_FUND'"
}
```
//OR

//Equity:
```
{
  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
  "cusip": "string",
  "symbol": "string",
  "description": "string"
}
```
//OR

//FixedIncome:
```
{
  "assetType": "'EQUITY' or 'OPTION' or 'INDEX' or 'MUTUAL_FUND' or 'CASH_EQUIVALENT' or 'FIXED_INCOME' or 'CURRENCY'",
  "cusip": "string",
  "symbol": "string",
  "description": "string",
  "maturityDate": "string",
  "variableRate": 0,
  "factor": 0
}
```
//The class <OrderActivity> has the 
//following subclasses: 
//-Execution
//JSON for each are listed below: 

//Execution:
```
{
  "activityType": "'EXECUTION' or 'ORDER_ACTION'",
  "executionType": "'FILL'",
  "quantity": 0,
  "orderRemainingQuantity": 0,
  "executionLegs": [
    {
      "legId": 0,
      "quantity": 0,
      "mismarkedQuantity": 0,
      "price": 0,
      "time": "string"
    }
  ]
}
```

#### Make migrations
```bash
$ alembic revision --autogenerate -m "message"
$ alembic upgrade head
```

#### Redis keys
```
f'{username}_refresh_token'
f'{username}_access_token'
f'{username}_access_token'
'chain'+symbolWithDate   //symbolWithDate example(TSLA_210121C)
'quote'+symbolWithDate   //symbolWithDate example(TSLA_210121C)
'streaming'              // symbols currently streaming
f'{accountId}_full_orders'
f'{accountId}_reference_orders'
```

#### Running API server on production
```bash
$ gunicorn --certfile=/etc/letsencrypt/live/bidasktrer.com/cert.pem --keyfile=/etc/letsencrypt/live/bidasktrader.com/privkey.pem --bind 0.0.0.0:5000 app:app
```