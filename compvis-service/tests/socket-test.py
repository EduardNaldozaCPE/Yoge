import asyncio
import websockets


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
DISCONNECT_STR = "!DISCONNECT"


async def echo(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        if (message == DISCONNECT_STR):
            break
        await websocket.send(message)
        print(f"Sent message: {message}")

# Start the server
start_server = websockets.serve(echo, HOST, PORT)

# Run the server until manually stopped
asyncio.get_event_loop().run_until_complete(start_server)
print(f"WebSocket server started on ws://{HOST}:{PORT}")
asyncio.get_event_loop().run_forever()