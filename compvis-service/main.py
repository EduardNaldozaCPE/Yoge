import os, sys, posix_ipc, mmap, time, json, threading
from services.landmarker_service import LandmarkerService

# Pad out the frame data to match the buffer size.
def padBuffer(buffer:bytes, maxSize:int) -> bytes:
    bufferSize = len(buffer)
    paddingLength = maxSize - (bufferSize % maxSize)
    padding = b'\x00' * paddingLength
    return buffer + padding



def main():
    # Initialise the pose estimation service
    poseService = LandmarkerService(MODEL_PATH)
    print("Started MediaPipe Pose Landmark Detection Service.\n")
    try:
        userId = int(sys.argv[1])
        sequenceId = int(sys.argv[2])
        sessionId = int(sys.argv[3])     
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
    except Exception as e:
        print("Error setting session data:", e)
        return

    # Create a separate thread for runVideo since it has an endless loop.
    video_thread = threading.Thread(target=poseService.runVideo, daemon=True)

    try:
        # Open the mmap. If it doesn't work, stop the main method.
        with open(SHM_FILE, "r+b") as f:
            try:
                mm = mmap.mmap(f.fileno(), 0)
                mm.write(padBuffer(b'\x00', BUFFERSIZE))
                isRunning = True
                video_thread.start()
            except Exception as e:
                print("Error while opening mmap:", e)
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

                # Write the frame to mmap
                try:
                    mm.seek(0)
                    mm.write(paddedFrame)
                    mm.flush()
                except KeyboardInterrupt:
                    print("Program Interrupted. Stopping Video Loop...")
                    break
                except Exception as e:
                    print("Error while writing to mmap:", e)

                if not isRunning:
                    break
                
            mm.close()
            poseService.stopVideo()
            video_thread.join()

    except KeyboardInterrupt:
        print("KeyboardInterrupt. Exiting.")

    except Exception as e:
        print(f"Error: {e}")



if __name__ == "__main__":
    os.system("cls")

    # Initialise Constants from config.json
    config = open('./compvis-service/config.json', 'r')
    config_options = json.load(config)
    MODEL_PATH  = config_options["MODEL_PATH"]
    SHM_FILE    = config_options["SHM_FILE"]
    BUFFERSIZE  = config_options["BUFFERSIZE"]
    config.close()

    # Initialise mmap file then run the main loop
    try:
        mmap_file = open(SHM_FILE, "wb")
        mmap_file.write(padBuffer(b"Hello Python!\n", BUFFERSIZE))
        mmap_file.close()
        del mmap_file
    except:
        print("oopsies")
    finally:
        main()