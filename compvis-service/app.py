import websockets
import asyncio
import threading
from PoseEstimationService import PoseEstimationService

ADDRESS = '127.0.0.1'
PORT = 8081
DISCONNECT_STR = "!DISCONNECT"

# Initialise the service and 
# Create it's own separate thread since it has an endless loop
poseEstimationService = PoseEstimationService()
video_thread = threading.Thread(target=poseEstimationService.runVideo)
video_thread.start()


async def processVideo(websocket):
    connected = True
    while connected:
        frame_data = poseEstimationService.getFrameData()
        print(type(frame_data))
        if frame_data is not None:
            decoded_frame = str(len(frame_data))
            await websocket.send(frame_data)
            await asyncio.sleep(0.001)
            
        if not connected:
            break

    poseEstimationService.stopVideo()


print("Running app.py")
start_server = websockets.serve(processVideo, ADDRESS, PORT)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
print(f"WebSocket server started on ws://{ADDRESS}:{PORT}")
try:
    loop.run_forever()
except KeyboardInterrupt:
    print("Stopped by user")
finally:
    poseEstimationService.stopVideo()
    loop.stop()
    loop.close()