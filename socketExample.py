from aiohttp import web
import socketio
sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


@sio.on('connect')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('reply')
async def message(sid, data):
    print("message", data)
    await sio.emit("reply", "finallyyy")

@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    web.run_app(app, host='localhost', port=6060)