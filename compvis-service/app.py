# Written by Eduard Naldoza, Bachelor of Science in Computer Engineering
# De La Salle University - Dasmariñas (2022)
# https://github.com/EduardNaldozaCPE/yogaposeestim-Thesis

from flask import Flask, json, redirect, request, url_for, Response, jsonify
from flask_cors import CORS
from VideoController import PoseEstimationService
from multiprocessing import Pool

app1 = Flask(__name__)
app1.secret_key = "passwordlmao"
cors = CORS(app1)
app1.config['CORS_HEADERS'] = 'Content-Type'
app1.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

poseEstimationService = PoseEstimationService()

@app1.route("/", methods=['POST', 'GET'])
def home_page():
    try:
        return jsonify({"message":"working"})
    except:
        return jsonify({"message":"error"})


@app1.route("/API/status", methods=['POST', 'GET'])
def status():
    if poseEstimationService.isRunning():
        return jsonify({"status":"running VideoCapture"})
    else:
        return jsonify({"status":"not running VideoCapture"})


@app1.route('/API/video')
def video():
    if poseEstimationService.hasConnection():
        try:

            # TODO -- Add multiprocessing here for run video
            poseEstimationService.runVideo()
            # Have runVideo run as
            return jsonify({"message":f"running video websocket at {poseEstimationService.IpAddress}:{poseEstimationService.port}"})
        except:
            return jsonify({"message":"error"})
        
    else:
        return jsonify({"message":f"no WebSocket connection is established. Please connect to {poseEstimationService.IpAddress}:{poseEstimationService.port}"})


if __name__ == "__main__":
    app1.run()
    # pass