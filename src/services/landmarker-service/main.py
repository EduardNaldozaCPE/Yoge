import os, sys, json, threading
import base64 as b64

from watchdog.observers import Observer
from landmarker import Landmarker, LandmarkerOptions, LandmarkerSession

ipcInput =  ''

def inputHandler():
    global ipcInput
    while True:
        line = input()
        ipcInput = line.strip().lower()
        if ipcInput == 'novid':
            print("Exiting inputhandler", file=sys.stderr)
            break

def main():
    global ipcInput
    config = open(os.path.join(os.getcwd(), 'resources/landmarker-config.json'), 'r')
    config_options = json.load(config)
    MODEL_PATH      = os.path.join(os.getcwd(), config_options["MODEL_PATH"])
    FRAMEWIDTH      = config_options["FRAMEWIDTH"]
    FRAMEHEIGHT     = config_options["FRAMEHEIGHT"]
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
    landmarker_session = LandmarkerSession(userId, sequenceId, sessionId)
    landmarker_options = LandmarkerOptions(FRAMEWIDTH, FRAMEHEIGHT)
    landmarker_options.setDeviceId(deviceId).setImshow(imshow)
    service = Landmarker(
        MODEL_PATH,
        session=landmarker_session,
        options=landmarker_options
        )

    # 3a. Threading - Start a new thread for the video capture loop.
    try:
        video_thread = threading.Thread(target=service.runVideo, daemon=True)
        video_thread.start()
    except Exception as e:
        print("Error while creating video thread:", e, file=sys.stderr)
        return
    
    # 3b. Threading - Start a new thread for IPC inputs.
    try:
        input_thread = threading.Thread(target=inputHandler)
        input_thread.start()
    except Exception as e:
        print("Error while creating input thread:", e, file=sys.stderr)
    
    isRunning = True

    # 4. Collect the frame data every loop.
    last_b64img = b''
    errCounter = 0
    while isRunning:
        if service.flagExit: break

        if len(ipcInput) > 0:
            print("COMMAND RECEIVED: "+ipcInput, file=sys.stderr)
            match ipcInput.lower():
                case 'play':
                    service.startRec()
                case 'pause':
                    service.stopRec()
                case _:
                    print("IPC COMMAND DOES NOT EXIST", file=sys.stderr)
            ipcInput = ''

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

    video_thread.join()
    input_thread.join()
    
    if service.flagExit:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    main()