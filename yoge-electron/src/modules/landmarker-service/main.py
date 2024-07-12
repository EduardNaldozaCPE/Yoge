import os, sys, json, threading

from click import echo

from landmarker import Landmarker
from utils import padBuffer

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
    try: 
        userId, sequenceId, sessionId = parseArgs()
    except IndexError as e:
        print("Please enter valid arguments for: -user=<id> -sequence=<id> -session=<id>")

    # 2. Initialise the pose estimation service and set the session data
    try:
        print(f"""
              New Session:
                User Id: {userId}
                Sequence Id: {sequenceId}
                Session Id: {sessionId}
        """)
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
        print("Error while opening shared memory:", e)
        return

    # 4. Collect the frame data every loop. Then write it to the mmap.
    os.system('cls')
    try:
        errCounter = 0
        while isRunning:
            # Take current frame from poseService object state
            frame_data = poseService.getFrameData()
            if frame_data is None: continue

            # Skip if the frame is too big.
            frameSize = len(frame_data)
            if frameSize > BUFFERSIZE: 
                print("Frame Size: ", frameSize, "/", BUFFERSIZE)
                print("Frame data is too large. increase the buffer size. Skipping...")
                continue
            
            # Pad out the frame data to match the buffer size.
            paddedFrame = padBuffer(frame_data, BUFFERSIZE)
            print(paddedFrame)
            # print()

            # [TEST] Frame
            # with open('bytes', 'bw') as bf:
            #     bf.write(paddedFrame)

            # Write the frame to the named pipe
            try:
                if (errCounter != 0): 
                    errCounter = 0
            except KeyboardInterrupt:
                print("Program Interrupted. Stopping Video Loop...")
                break
            except Exception as e:
                if (errCounter > 10):
                    break
                errCounter = errCounter + 1

            if not isRunning:
                break 
    except KeyboardInterrupt: 
        print("KeyboardInterrupt. Exiting.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        poseService.stopVideo()
        video_thread.join()


if __name__ == "__main__":
    os.system("cls")

    # Initialise Constants from config.json
    config = open('./landmarker-service/config.json', 'r')
    config_options = json.load(config)
    MODEL_PATH  = config_options["MODEL_PATH"]
    BUFFERSIZE  = config_options["BUFFERSIZE"]
    config.close()
    main()