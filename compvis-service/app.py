import websockets
import asyncio
import threading
import time
from PoseEstimationService import PoseEstimationService
import numpy as np

IpAddress = '127.0.0.1'
port = 8081
DISCONNECT_STR = "!DISCONNECT"

async def echo(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        if (message == DISCONNECT_STR):
            break
        await websocket.send(message)
        print(f"Sent message: {message}")


# TODO --   Use ZeroMQ for interprocess communication
# TODO --   Get the frame data from PoseEstimationService.runVideo() method
#           Follow Pipeline / Stack:
#               Request -> SocketController -> PoseEstimationService -> SocketController -> Response

# Initialise the service
poseEstimationService = PoseEstimationService()
# Create it's own separate thread since it has an endless loop
video_thread = threading.Thread(target=poseEstimationService.runVideo)
video_thread.start()


async def processVideo(websocket):
    counter = 0
    while counter < 10:
        frame_data = poseEstimationService.getFrameData()
        # print(f'ooga {counter} {frame_data}')
        if frame_data is not None:
            decoded_frame = str(len(frame_data))
            with open("./tests/byte-dump.txt", "w") as text_file:
                print("writing byte dump")
                text_file.write(decoded_frame)
        # await websocket.send(frame_data)
        counter += 1
        time.sleep(1)
    poseEstimationService.stopVideo()


# start_server = websockets.serve(echo, IpAddress, port)
start_server = websockets.serve(processVideo, IpAddress, port)
asyncio.get_event_loop().run_until_complete(start_server)
print(f"WebSocket server started on ws://{IpAddress}:{port}")
asyncio.get_event_loop().run_forever()