import threading

from flask import Flask, jsonify
from flask_cors import CORS

import SocketController

# instantiate flask
app1 = Flask(__name__)
app1.secret_key = "passwordlmao"
cors = CORS(app1)
app1.config['CORS_HEADERS'] = 'Content-Type'
app1.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

# instantiate pose estimation service
socketController = SocketController()
socket_thread = threading.Thread(target=socketController.startSocket)


@app1.route("/", methods=['GET'])
def home_page():
    try:
        return jsonify({"message":"working"})
    except:
        return jsonify({"message":"error"})


# TODO -- Create isRunning() Method in SocketController
# Checks whether the OpenCV VideoCapture object has been instantiated
# @app1.route("/API/status", methods=['GET'])
# def status():
#     if .isRunning():
#         return jsonify({"status":"running VideoCapture"})
#     else:
#         return jsonify({"status":"not running VideoCapture"})


# Starts the websocket 
@app1.route("/API/start", methods=['GET'])
def startSocket():
    try:
        # Start the socket thread, and return when it has started
        socket_thread.start()
        return jsonify({"status":f"running Websocket at {socketController.IpAddress}:{socketController.port}"})
    except:
        return jsonify({"status":"failed to run Websocket"})


# Stops the websocket
@app1.route('/API/stop', methods=['GET'])
def video():
    # if socketController.hasConnection():

    try:
        # TODO -- socket_thread.stop()
        return jsonify({"message":"Stopped WebSocket"})
    except:
        return jsonify({"message":"error"})
    
    # else:
    #     return jsonify({"message":f"no WebSocket connection is established. Please connect to {socketController.IpAddress}:{socketController.port}"})


if __name__ == "__main__":
    app1.run()
    # pass