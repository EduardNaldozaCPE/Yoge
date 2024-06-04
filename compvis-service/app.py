import websockets
import asyncio
import threading
from PoseEstimationService import PoseEstimationService

ADDRESS = '127.0.0.1'
PORT = 8081
DISCONNECT_STR = "!DISCONNECT"

# Initialise the service
poseEstimationService = PoseEstimationService()


async def processVideo(websocket):
    connected = True 
    # Create a separate thread for runVideo since it has an endless loop
    video_thread = threading.Thread(target=poseEstimationService.runVideo)
    video_thread.start()

    while connected:
        frame_data = poseEstimationService.getFrameData()
        if frame_data is not None:
            try:
                await websocket.send(frame_data)
            except:
                print("Socket Disconnected. Stopping video loop")
                connected = False
            finally:
                await asyncio.sleep(0.001)
            
        if not connected:
            break

    poseEstimationService.stopVideo()
    video_thread.join()


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