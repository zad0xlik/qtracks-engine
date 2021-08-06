from flask import Flask
from flask import request
from pathlib import Path
import logging

app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route("/")
def hello():
    key=request.args.get('code')
    try:
        f=open(Path("modules/Auth/key.qt"),"w+")
        f.write(request.args.get('code'))
        f.close()
        shutdown_server()
        return "Authenticated, you may close this window and go back to console..."
    except IOError:
        shutdown_server()
        return "There was an error, the file did not write..."

if __name__ == '__main__':
    context = (Path('server/server.crt'), Path('server/server.key'))
    app.run(host='127.0.0.1',port='5000', debug=False, ssl_context=context)
