import os
import sys, json, threading
import base64 as b64

from landmarker import Landmarker

def parseArgs() -> tuple:
    lenOnly = False
    noCV = False
    imshow = False
    for arg in sys.argv:
        keyVal = arg.split('=')
        if keyVal[0] == "-user":     usr = int(keyVal[1])
        if keyVal[0] == "-sequence": seq = int(keyVal[1])
        if keyVal[0] == "-device":   dev = int(keyVal[1])
        if keyVal[0] == "-noCV":     noCV = True
        if keyVal[0] == "-lenOnly":  lenOnly = True
        if keyVal[0] == "-imshow":   imshow = True

    if (usr is None) or (seq is None):
        raise IndexError
    else:
        return (usr, seq, dev, noCV, lenOnly, imshow)


def main():
    # 1. Handle Session Arguments and Display
    try:  
        (
            userId, 
            sequenceId,
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
            int(deviceId),
            noCV,
            imshow
        )
    except Exception as e:
        print("Error setting session data:", e, file=sys.stderr)
        return

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
        poseService.stopVideo()
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