import sys, json, threading
import base64 as b64

from landmarker import Landmarker

def parseArgs() -> tuple:
    for arg in sys.argv:
        keyVal = arg.split('=')
        if keyVal[0] == "-user":
            usr = int(keyVal[1])
        if keyVal[0] == "-sequence":
            seq = int(keyVal[1])
        if keyVal[0] == "-session":
            ses = int(keyVal[1])

    if (usr is None) or (seq is None) or (ses is None):
        raise IndexError
    else:
        return (usr, seq, ses)


def main():
    # 1. Handle Session Arguments and Display
    try:  userId, sequenceId, sessionId = parseArgs()
    except IndexError as e: print("Please enter valid arguments for: -user=<id> -sequence=<id> -session=<id>", file=sys.stderr)

    # 2. Initialise the pose estimation service and set the session data
    try:
        poseService = Landmarker(MODEL_PATH)
        poseService.setSessionData(
            int(userId),
            int(sequenceId),
            int(sessionId)
        )
    except Exception as e:
        print("Error setting session data:", e)
        return

    video_thread = threading.Thread(target=poseService.runVideo, daemon=True)
    try:
        isRunning = True
        video_thread.start()
    except Exception as e:
        print("Error while opening shared memory:", e, file=sys.stderr)
        return

    # 4. Collect the frame data every loop.
    try:
        errCounter = 0
        while isRunning:
            # Take current frame from poseService object state
            frameBuffer = poseService.getFrame()
            if frameBuffer is None: continue

            # Skip if the frame is too big.
            frameSize = len(frameBuffer)
            if frameSize > MAXBUFFERSIZE:
                print("Frame data is too large. increase the buffer size. Skipping...\nFrame Size: ", frameSize, "/", MAXBUFFERSIZE, file=sys.stderr)
                continue
            
            # Pad out the frame data to match the buffer size.
            try:
                # Convert the buffer to base64 and Wrap it
                b64img = b64.b64encode(frameBuffer) 
                paddedFrame = b'BUFFERSTART' + b64img + b'BUFFEREND'
            except Exception as e: print(e, file=sys.stderr)

            # Write the frame to stdout
            try:
                print(paddedFrame)
                if (errCounter != 0): errCounter = 0
            except KeyboardInterrupt:
                print("Program Interrupted. Stopping Video Loop...", file=sys.stderr)
                break
            except Exception as e:
                print(e, file=sys.stderr)
                if (errCounter > 10): break
                errCounter = errCounter + 1

            # [TEST] Frame
            # with open('bytes', 'bw') as bf:
                # bf.write(paddedFrame)

            if not isRunning: break 

    except KeyboardInterrupt: print("KeyboardInterrupt. Exiting.", file=sys.stderr)
    except Exception as e: print(f"Error: {e}", file=sys.stderr)
    finally:
        poseService.stopVideo()
        video_thread.join()


if __name__ == "__main__":
    # Initialise Constants from config.json
    config = open('./src/modules/landmarker-service/config.json', 'r')
    config_options = json.load(config)
    MODEL_PATH  = config_options["MODEL_PATH"]
    MAXBUFFERSIZE  = config_options["MAXBUFFERSIZE"]
    config.close()
    main()