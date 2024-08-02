import os, sys, json, threading, csv
import base64 as b64

from watchdog.observers import Observer
from landmarker import Landmarker, LandmarkerOptions, Session
from ipc_handler import IpcHandler

def main():
    config = open(os.path.join(os.getcwd(), 'resources/landmarker-config.json'), 'r')
    config_options = json.load(config)
    MODEL_PATH      = os.path.join(os.getcwd(), config_options["MODEL_PATH"])
    FRAMEWIDTH      = config_options["FRAMEWIDTH"]
    FRAMEHEIGHT     = config_options["FRAMEHEIGHT"]
    IPC_CSV_DIR = os.path.join(os.getcwd(),'resources','ipc')
    IPC_CSV_PATH = os.path.join(IPC_CSV_DIR,'to_landmarker.csv')
    config.close()

    # 1. Handle Session Arguments and Display
    imshow = False
    lenOnly = False
    for arg in sys.argv:
        keyVal = arg.split('=')
        if keyVal[0] == "-user":     userId = int(keyVal[1])
        if keyVal[0] == "-sequence": sequenceId = int(keyVal[1])
        if keyVal[0] == "-session":  sessionId = int(keyVal[1])
        if keyVal[0] == "-device":   deviceId = int(keyVal[1])
        if keyVal[0] == "-lenOnly":  lenOnly = True
        if keyVal[0] == "-imshow":   imshow = True

    if (userId is None) or (sequenceId is None) or (sessionId is None):
        print("Please enter valid arguments for: -user=<id> -sequence=<id>", file=sys.stderr)
        return

    # 2. Initialise the pose estimation service and set the session data
    landmarker_options = LandmarkerOptions(FRAMEWIDTH, FRAMEHEIGHT)
    landmarker_options.setDeviceId(deviceId).setImshow(imshow)
    landmarker_session = Session(userId, sequenceId, sessionId)
    service = Landmarker(
        MODEL_PATH,
        session=landmarker_session,
        options=landmarker_options
        )
    
    # 2a. Initialise the watchdog Observer to check for file changes in resources/ipc
    observer = Observer()
    handler = IpcHandler(IPC_CSV_PATH)
    observer.schedule(handler, IPC_CSV_DIR, recursive=True)
    observer.start()

    # 3. Start a new thread for the video capture loop.
    try:
        video_thread = threading.Thread(target=service.runVideo, daemon=True)
        video_thread.start()
    except Exception as e:
        print("Error while creating new thread:", e, file=sys.stderr)
        return
    
    isRunning = True

    # 4. Collect the frame data every loop.
    last_b64img = b''
    errCounter = 0
    while isRunning:
        if service.flagExit: break
        
        # Handle IPC Commands
        if len(handler.ipcQueue) > 0:
            lastCmd = handler.ipcQueue.pop()
            match lastCmd[1]:
                case "PLAY":
                    service.startRec()
                    print("PLAY REC",file=sys.stderr)
                case "PAUSE":
                    service.stopRec() 
                    print("PAUSE REC",file=sys.stderr)
                case _:
                    print("IPC COMMAND DOES NOT EXIST",file=sys.stderr)

        frameBuffer = service.getFrame()
        
        # Convert the buffer to base64 and Wrap it
        if frameBuffer is None:
            b64img = last_b64img
        else:
            b64img = b64.b64encode(frameBuffer)

        # Print the frame to stdout
        if len(b64img) > 0:
            if lenOnly:
                print(f"BUFFER: {len(b64img)} bytes", file=sys.stdout, end='\r')
            else:
                print(b64img, file=sys.stdout, end="")
            last_b64img = b64img
            if (errCounter != 0): errCounter = 0

        if not isRunning: break 

    observer.stop()
    service.stopVideo()
    observer.join()
    video_thread.join()
    if service.flagExit: 
        exit(1)

if __name__ == "__main__":
    main()