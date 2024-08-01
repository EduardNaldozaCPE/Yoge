import os, sys, json, threading, csv
import base64 as b64

from watchdog.observers import Observer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from landmarker import Landmarker

IPC_CMD_DIR = os.path.join(os.getcwd(),'resources','ipc')
IPC_CMD_PATH = os.path.join(IPC_CMD_DIR,'to_landmarker.csv')
ipcQueue = []

class _ipc_handler(FileSystemEventHandler):    
    # Append latest command to ipcQueue every file update
    def on_modified(self, event: FileSystemEvent) -> None:
        with open(IPC_CMD_PATH, 'r') as cmdfile:
            try:    
                last_line = cmdfile.readlines()[-1]
                cmd = last_line.split(',')
                final_cmd = [int(cmd[0]), cmd[1].rstrip('\n')]
                ipcQueue.append(final_cmd)
            except Exception as e:
                print("Error found in _ipc_handler:", e, file=sys.stderr)
            

def parseArgs() -> tuple:
    lenOnly = False
    noCV = False
    imshow = False
    for arg in sys.argv:
        keyVal = arg.split('=')
        if keyVal[0] == "-user":     usr = int(keyVal[1])
        if keyVal[0] == "-sequence": seq = int(keyVal[1])
        if keyVal[0] == "-session":  ses = int(keyVal[1])
        if keyVal[0] == "-device":   dev = int(keyVal[1])
        if keyVal[0] == "-noCV":     noCV = True
        if keyVal[0] == "-lenOnly":  lenOnly = True
        if keyVal[0] == "-imshow":   imshow = True

    if (usr is None) or (seq is None):
        raise IndexError
    else:
        return (usr, seq, ses, dev, noCV, lenOnly, imshow)


def main():
    # 1. Handle Session Arguments and Display
    try:  
        (
            userId,
            sequenceId,
            sessionId,
            deviceId,
            noCV,
            lenOnly,
            imshow
        ) = parseArgs()
    except IndexError as e: print("Please enter valid arguments for: -user=<id> -sequence=<id>", file=sys.stderr)

    # 2. Initialise the pose estimation service and set the session data
    try:
        poseService = Landmarker(MODEL_PATH, options={"width":FRAMEWIDTH, "height":FRAMEHEIGHT})
        poseService.setSessionData(
            int(userId),
            int(sequenceId),
            int(sessionId),
            int(deviceId),
            noCV,
            imshow
        )
    except Exception as e:
        print("Error setting session data:", e, file=sys.stderr)
        return
    
    # 2a. Initialise the watchdog Observer to check for file changes in resources/ipc
    observer = Observer()
    handler = _ipc_handler()
    observer.schedule(handler, IPC_CMD_DIR, recursive=True)
    observer.start()

    # 3. Start a new thread for the video capture loop.
    try:
        video_thread = threading.Thread(target=poseService.runVideo, daemon=True)
        video_thread.start()
    except Exception as e:
        print("Error while creating new thread:", e, file=sys.stderr)
        return
    
    isRunning = True

    # 4. Collect the frame data every loop.
    last_b64img = b''
    try:
        errCounter = 0
        while isRunning:
            if poseService.flagExit: 
                break
            
            # Handle IPC Commands
            if len(ipcQueue) > 0:
                lastCmd = ipcQueue.pop()
                match lastCmd[1]:
                    case "PLAY":
                        poseService.startRec()
                        print("PLAY REC",file=sys.stderr)
                    case "PAUSE":
                        poseService.stopRec() 
                        print("PAUSE REC",file=sys.stderr)
                    case _:
                        print("IPC COMMAND DOES NOT EXIST",file=sys.stderr)

            try:
                # Take current frame from poseService object state
                frameBuffer = poseService.getFrame()
            
                # Convert the buffer to base64 and Wrap it
                b64img = b64.b64encode(frameBuffer)

            except Exception as e:
                # print(e, file=sys.stderr)
                b64img = last_b64img

            # Print the frame to stdout
            try:
                if len(b64img) > 0:
                    if lenOnly:
                        print(f"BUFFER: {len(b64img)} bytes", file=sys.stdout, end='\r')
                    else:
                        print(b64img, file=sys.stdout, end="")
                    last_b64img = b64img
                    if (errCounter != 0): errCounter = 0
            except Exception as e:
                print(e, file=sys.stderr)
                if (errCounter > 10): break
                errCounter = errCounter + 1

            if not isRunning: break 

    except KeyboardInterrupt: print("KeyboardInterrupt. Exiting.", file=sys.stderr)
    except Exception as e: print(f"Error: {e}", file=sys.stderr)
    finally:
        observer.stop()
        poseService.stopVideo()
        observer.join()
        video_thread.join()
        
    if poseService.flagExit: 
        exit(1)


if __name__ == "__main__":
    # Initialise Constants from config.json
    config = open(os.path.join(os.getcwd(), 'resources/landmarker-config.json'), 'r')
    config_options = json.load(config)
    MODEL_PATH      = os.path.join(os.getcwd(), config_options["MODEL_PATH"])
    FRAMEWIDTH      = config_options["FRAMEWIDTH"]
    FRAMEHEIGHT     = config_options["FRAMEHEIGHT"]
    config.close()
    main()