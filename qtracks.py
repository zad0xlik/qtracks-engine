from modules.Auth import Auth
from modules.Order import Order
from modules.Chain import Chain
from modules.Order import SendOrders
from modules.Order import StreamOrders
from modules.Pricing import PricingEngine
from modules.Pricing import PriceApi
from modules.Streamer import Stream
from modules.Streamer import Multistream
from modules.Streamer import TestStream
from modules.Streamer import StreamChain
from pathlib import Path
import asyncio
import os
import click
import json


@click.group()
def cli():
    pass


@click.command()
@click.option('-a', '--account', required=True)
def orders(account):
    click.echo('Getting orders...')
    # Test acc. no. 885084780
    Order.getOrdersByPath(account)


@click.command()
@click.option('-o', '--order', type=(
    str,  # ACCOUNT NUMBER
    str  # Symbol
))
def placed(order):
    click.echo('Getting orders...')
    # Test acc. no. 885084780
    Order.getPlacedOrderId(order[0], order[1])


@click.command()
@click.option('-o', '--order', type=(
    str,  # ACCOUNT NUMBER
    str  # ORDER ID
))
def check(order):
    click.echo('Getting order...')
    Order.getOrder(*order)


@click.command()
@click.option('-o', '--order', type=(
    str,  # ACCOUNT NUMBER
    click.Choice(['NORMAL', 'AM', 'PM', 'SEAMLESS']),  # SESSION
    click.Choice(['DAY', 'GOOD_TILL_CANCEL', 'FILL_OR_KILL']),  # DURATION
    click.Choice(['MARKET',
                  'LIMIT',
                  'STOP',
                  'STOP_LIMIT',
                  'TRAILING_STOP',
                  'MARKET_ON_CLOSE',
                  'EXERCISE',
                  'TRAILING_STOP_LIMIT',
                  'NET_DEBIT',
                  'NET_CREDIT',
                  'NET_ZERO']),  # ORDER TYPE
    float,  # PRICE
    click.Choice(['EQUITY',
                  'OPTION',
                  'INDEX',
                  'MUTUAL_FUND',
                  'CASH_EQUIVALENT',
                  'FIXED_INCOME',
                  'CURRENCY']),  # ORDER LEG TYPE
    click.Choice(['EQUITY',
                  'OPTION',
                  'INDEX',
                  'MUTUAL_FUND',
                  'CASH_EQUIVALENT',
                  'FIXED_INCOME',
                  'CURRENCY']),  # ASSET TYPE
    str,  # SYMBOL
    click.Choice(['PUT', 'CALL']),  # PUTCALL
    click.Choice(['BUY',
                  'SELL',
                  'BUY_TO_COVER',
                  'SELL_SHORT',
                  'BUY_TO_OPEN',
                  'BUY_TO_CLOSE',
                  'SELL_TO_OPEN',
                  'SELL_TO_CLOSE',
                  'EXCHANGE']),  # INSTRUCTION
    int,  # QUANTITY
    click.Choice(['SINGLE',
                  'OCO',
                  'TRIGGER'])  # ORDER STRATEGY TYPE
))
def place(order):
    print(*order)
    Order.placeOrder(*order)


@click.command()
@click.option('-o', '--order', type=(
    str,  # ACCOUNT NUMBER
    str,  # ORDER ID
    click.Choice(['NORMAL', 'AM', 'PM', 'SEAMLESS']),  # SESSION
    click.Choice(['DAY', 'GOOD_TILL_CANCEL', 'FILL_OR_KILL']),  # DURATION
    click.Choice(['MARKET',
                  'LIMIT',
                  'STOP',
                  'STOP_LIMIT',
                  'TRAILING_STOP',
                  'MARKET_ON_CLOSE',
                  'EXERCISE',
                  'TRAILING_STOP_LIMIT',
                  'NET_DEBIT',
                  'NET_CREDIT',
                  'NET_ZERO']),  # ORDER TYPE
    float,  # PRICE
    click.Choice(['EQUITY',
                  'OPTION',
                  'INDEX',
                  'MUTUAL_FUND',
                  'CASH_EQUIVALENT',
                  'FIXED_INCOME',
                  'CURRENCY']),  # ORDER LEG TYPE
    click.Choice(['EQUITY',
                  'OPTION',
                  'INDEX',
                  'MUTUAL_FUND',
                  'CASH_EQUIVALENT',
                  'FIXED_INCOME',
                  'CURRENCY']),  # ASSET TYPE
    str,  # SYMBOL
    click.Choice(['PUT', 'CALL']),  # PUTCALL
    click.Choice(['BUY',
                  'SELL',
                  'BUY_TO_COVER',
                  'SELL_SHORT',
                  'BUY_TO_OPEN',
                  'BUY_TO_CLOSE',
                  'SELL_TO_OPEN',
                  'SELL_TO_CLOSE',
                  'EXCHANGE']),  # INSTRUCTION
    int,  # QUANTITY
    click.Choice(['SINGLE',
                  'OCO',
                  'TRIGGER'])  # ORDER STRATEGY TYPE
))
def replace(order):
    print(*order)
    Order.replaceOrder(*order)


@click.command()
@click.option('-o', '--order', type=(
    str,  # ACCOUNT NUMBER
    str  # ORDER ID
))
def delete(order):
    print(*order)
    Order.deleteOrder(*order)


@click.command()
def sendorders():
    SendOrders.start()


@click.command()
def streamorders():
    StreamOrders.start()


@click.command()
def pricing():
    PricingEngine.start()


@click.command()
def price():
    print(json.dumps(PriceApi.price('885084780', [
          'TSLA_011521C650', 'TSLA_011521C600']), indent=2))


@click.command()
@click.option('-s', '--symbols', type=(
    str  # SYMBOLS
))
def daemon(symbols):
    symbols = symbols.split(",")
    Multistream.start('885084780', symbols)


@click.command()
def teststream():
    TestStream.start()

# CHK_011521C2


@click.command()
def streamchain():
    StreamChain.stream()

cli.add_command(orders)
cli.add_command(check)
cli.add_command(placed)
cli.add_command(place)
cli.add_command(replace)
cli.add_command(delete)
cli.add_command(sendorders)
cli.add_command(streamorders)
cli.add_command(pricing)
cli.add_command(price)
cli.add_command(daemon)
cli.add_command(streamchain)
cli.add_command(teststream)


if __name__ == '__main__':
    cli()
