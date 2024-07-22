import sys, json, threading
import base64 as b64

from landmarker import Landmarker

def parseArgs() -> tuple:
    lenOnly = False
    for arg in sys.argv:
        keyVal = arg.split('=')
        if keyVal[0] == "-user":     usr = int(keyVal[1])
        if keyVal[0] == "-sequence": seq = int(keyVal[1])
        if keyVal[0] == "-session":  ses = int(keyVal[1])
        if keyVal[0] == "-lenOnly":  lenOnly = True

    if (usr is None) or (seq is None) or (ses is None):
        raise IndexError
    else:
        return (usr, seq, ses, lenOnly)


def main():
    # 1. Handle Session Arguments and Display
    try:  userId, sequenceId, sessionId, lenOnly = parseArgs()
    except IndexError as e: print("Please enter valid arguments for: -user=<id> -sequence=<id> -session=<id>", file=sys.stderr)

    # 2. Initialise the pose estimation service and set the session data
    try:
        poseService = Landmarker(MODEL_PATH, options={"width":FRAMEWIDTH, "height":FRAMEHEIGHT})
        poseService.setSessionData(
            int(userId),
            int(sequenceId),
            int(sessionId)
        )
    except Exception as e:
        print("Error setting session data:", e, file=sys.stderr)
        return

    video_thread = threading.Thread(target=poseService.runVideo, daemon=True)
    try:
        isRunning = True
        video_thread.start()
    except Exception as e:
        print("Error while creating new thread:", e, file=sys.stderr)
        return

    # 4. Collect the frame data every loop.
    try:
        errCounter = 0
        while isRunning:
            # Take current frame from poseService object state
            frameBuffer = poseService.getFrame()
            if frameBuffer is None: continue
            
            # Pad out the frame data to match the buffer size.
            try:
                # Convert the buffer to base64 and Wrap it
                b64img = b64.b64encode(frameBuffer)
            except Exception as e: print(e, file=sys.stderr)

            # Print the frame to stdout
            try:
                if lenOnly:
                    print(f"BUFFER: {len(b64img)} bytes", file=sys.stdout)
                else:
                    print(b64img, file=sys.stdout, end="")
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


if __name__ == "__main__":
    # Initialise Constants from config.json
    config = open('./landmarker-config.json', 'r')
    config_options = json.load(config)
    MODEL_PATH      = config_options["MODEL_PATH"]
    MAXBUFFERSIZE   = config_options["MAXBUFFERSIZE"]
    FRAMEWIDTH      = config_options["FRAMEWIDTH"]
    FRAMEHEIGHT     = config_options["FRAMEHEIGHT"]
    config.close()
    main()