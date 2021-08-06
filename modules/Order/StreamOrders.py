import aiofiles
import time
import xmltodict
import sys
import json
import socketio
import asyncio
import ssl
from aiohttp import web
from datetime import datetime
from pathlib import Path
from modules.Db import Redis

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

sslcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)

# --certfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem
# --keyfile=/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem
sslcontext.load_cert_chain('/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/cert.pem',
                           '/Users/fkolyadin/Desktop/rnd/model_approaches/development/qtrack/qtracks/server/privkey.pem')

# sslcontext.load_cert_chain('/etc/letsencrypt/live/bidasktrader.com/cert.pem',
#                            '/etc/letsencrypt/live/bidasktrader.com/privkey.pem')

disconnectedSids = []


async def streamOrders(sid, data):
    userOrders = []
    while(True):
        if(sid not in disconnectedSids):
            try:
                orders = []
                ordersByKey = {}
                newUserOrders = []
                fullOrders = Redis.r.get(f'{data}_full_orders')
                if(fullOrders):
                    orders = json.loads(fullOrders)

                for order in orders:
                    if(order['accountId'] in ordersByKey.keys()):
                        if(order not in ordersByKey[order['accountId']]):
                            ordersByKey[order['accountId']] = ordersByKey[order['accountId']] + [order]
                    else: 
                        ordersByKey.update({order['accountId']: [order]})
                if(data in ordersByKey.keys()):
                    newUserOrders = ordersByKey[data]
                if(newUserOrders != userOrders):
                    print(json.dumps(newUserOrders))
                    await sio.emit("orderReply", json.dumps(newUserOrders), room=data)
                userOrders = newUserOrders
            except IOError:
                print("Error reading Orders.txt, check the file or make sure is created")
        else:
            break
        await sio.sleep(0.7)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)


@sio.on('enterRoom')
async def enterRoom(sid, data):
    sio.enter_room(sid, data)
    print("connected to room ", data)


@sio.on('orderReply')
async def Reply(sid, data):
    await sio.emit("orderReply", "[]", room=data)
    loop = asyncio.get_event_loop()
    loop.create_task(streamOrders(sid, data))


@sio.on('disconnect')
async def disconnect(sid):
    disconnectedSids.append(sid)
    print("disconnected ", sid)


def start():
    web.run_app(app, host='0.0.0.0', port=6060, ssl_context=sslcontext)
    # web.run_app(app, host='0.0.0.0', port=6060)
