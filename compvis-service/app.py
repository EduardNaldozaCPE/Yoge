import websockets
import asyncio
import threading
import time
from PoseEstimationService import PoseEstimationService
import numpy as np

ADDRESS = '127.0.0.1'
PORT = 8081
DISCONNECT_STR = "!DISCONNECT"

# Initialise the service and 
# Create it's own separate thread since it has an endless loop
poseEstimationService = PoseEstimationService()
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
        # TODO await websocket.send(frame_data)
        counter += 1
        time.sleep(1)
    poseEstimationService.stopVideo()


start_server = websockets.serve(processVideo, ADDRESS, PORT)
asyncio.get_event_loop().run_until_complete(start_server)
print(f"WebSocket server started on ws://{ADDRESS}:{PORT}")
asyncio.get_event_loop().run_forever()