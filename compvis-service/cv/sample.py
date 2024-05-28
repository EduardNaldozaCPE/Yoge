import mediapipe as mp
import cv2 as cv
import sqlite3

import pickle
import socket
import struct

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind (('0.0.0.0', 8080))
server_socket.listen(5)


def print_result(result: PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    # print('pose landmarker result: {}'.format(result))
    pass

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="./cv/pose_landmarker_lite.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

print("Server listening...")
connection, address = server_socket.accept()
print(f"Connection from {address} established!")

feed = cv.VideoCapture(0)

with PoseLandmarker.create_from_options(options) as landmarker:
    t = 0
    while True:
        success, frame = feed.read()
        if not success: 
            break

        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        if not mp_image: 
            continue
        
        landmarker.detect_async(mp_image, t)
        t += 1

        cv.imshow('img', mp_image)

        # Serialize the frame using pickle
        data = pickle.dumps(frame)
        message = struct.pack ("Q", len(data)) + data
        connection.sendall(message)

        if cv.waitKey(1) & 0xFF == 27: 
            break


cv.destroyAllWindows()
feed.release()