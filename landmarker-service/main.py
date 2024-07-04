import os, sys, json, threading
import subprocess as sp
from multiprocessing import shared_memory
from landmarker import Landmarker

# Pad out the frame data to match the buffer size.
def padBuffer(buffer:bytes, maxSize:int) -> bytes:
    bufferSize = len(buffer)
    paddingLength = maxSize - (bufferSize % maxSize)
    padding = b'\x00' * paddingLength
    return buffer + padding


def main():
    # Initialise the pose estimation service
    poseService = Landmarker(MODEL_PATH)
    print("Started MediaPipe Pose Landmark Detection Service.\n")
    userId = None
    sequenceId = None
    sessionId = None
    try:
        for arg in sys.argv:
            keyVal = arg.split('=')
            if keyVal[0] == "-user":
                userId = int(keyVal[1])
            if keyVal[0] == "-sequence":
                sequenceId = int(keyVal[1])
            if keyVal[0] == "-session":
                sessionId = int(keyVal[1])
        if userId is None or sequenceId is None or sessionId is None:
            return
        print(f"Starting Session:") 
        print(f"\tUser Id: {userId}") 
        print(f"\tSequence Id: {sequenceId}") 
        print(f"\tSession Id: {sessionId}")
        print('\n')
        poseService.setSessionData(
            int(userId),
            int(sequenceId),
            int(sessionId)
        )
    except IndexError:
        print("Please enter valid arguments for: -user=<id> -sequence=<id> -session=<id>")
        return
    except Exception as e:
        print("Error setting session data:", e)
        return

    # Create a separate thread for runVideo since it has an endless loop.
    video_thread = threading.Thread(target=poseService.runVideo, daemon=True)
    try:
        # Open the shared memory object
        try:
            # shm = shared_memory.SharedMemory(create=True, size=BUFFERSIZE, name=SHMNAME)
            isRunning = True
            video_thread.start()
        except Exception as e:
            print("Error while opening shared memory:", e)
            return
        
        # Collect the frame data every loop. Then write it to the mmap.
        while isRunning:
            frame_data = poseService.getFrameData()
            if frame_data is None: continue

            # Skip if the frame is too big. Log when true.
            frameSize = len(frame_data)
            if frameSize > BUFFERSIZE: 
                print("Frame Size: ", frameSize, "/", BUFFERSIZE)
                print("frame data is too large. increase the buffer size. Skipping...")
                continue
            
            # Pad out the frame data to match the buffer size.
            paddedFrame = padBuffer(frame_data, BUFFERSIZE)

            with open('bytes', 'wb') as f:
                f.write(paddedFrame)

            # Write the frame to mmap
            try:
                # shm.buf[0:BUFFERSIZE] = paddedFrame
                pass
            except KeyboardInterrupt:
                print("Program Interrupted. Stopping Video Loop...")
                break
            except Exception as e:
                print("Error while writing to shm:", e)
                print(len(paddedFrame))
                print(BUFFERSIZE)

            if not isRunning:
                break
            
        # shm.close()
        # shm.unlink()
        poseService.stopVideo()
        video_thread.join()


    except KeyboardInterrupt:
        print("KeyboardInterrupt. Exiting.")

    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    os.system("cls")

    # Initialise Constants from config.json
    config = open('./config.json', 'r')
    config_options = json.load(config)
    MODEL_PATH  = config_options["MODEL_PATH"]
    BUFFERSIZE  = config_options["BUFFERSIZE"]
    config.close()

    # Initialise mmap file then run the main loop
    main()