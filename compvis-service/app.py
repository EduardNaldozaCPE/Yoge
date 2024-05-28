import websockets
import asyncio
import threading
from PoseEstimationService import PoseEstimationService

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


# TODO --   Read up on asyncio
# TODO --   Get the frame data from PoseEstimationService.runVideo() method
#           Follow Pipeline / Stack:
#               Request -> SocketController -> PoseEstimationService -> SocketController -> Response
poseEstimationService = PoseEstimationService()
async def processVideo():
    # frame_data = poseEstimationService.runVideo()
    # await websocket.send(data)
    pass



start_server = websockets.serve(echo, IpAddress, port)
# start_server = websockets.serve(processVideo, IpAddress, port)
asyncio.get_event_loop().run_until_complete(start_server)
print(f"WebSocket server started on ws://{IpAddress}:{port}")
asyncio.get_event_loop().run_forever()