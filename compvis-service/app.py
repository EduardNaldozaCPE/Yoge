import os
import json
import sys
import threading
from PoseEstimationService import PoseEstimationService

# TODO -- Rewrite code to use MMAPs
import mmap

def padBuffer(buffer:bytes, maxSize:int) -> bytes:
    # Pad out the frame data to match the buffer size.
    bufferSize = len(buffer)
    paddingLength = maxSize - (bufferSize % maxSize)
    padding = b'\x00' * paddingLength
    return buffer + padding


def main():
    # Initialise the pose estimation service
    # TODO -- Take in userId, sequenceId, sessionId
    poseEstimationService = PoseEstimationService(MODEL_PATH)
    poseEstimationService.setSessionData()

    # Create a separate thread for runVideo since it has an endless loop
    video_thread = threading.Thread(target=poseEstimationService.runVideo, daemon=True)

    # Collect the frame data every loop. Then write it to the pipe.
    # NOTE -- The client must be running a loop
    try:
        with open(SHM_FILE, "r+b") as f:
            try:
                mm = mmap.mmap(f.fileno(), 0)
                mm.write(padBuffer(b'Hello World!\n', BUFFERSIZE))
                print(mm[:50])
                # mm.seek(0)
                
                print("MMAP SIZE:", mm.size())
                isRunning = True
                video_thread.start()

            except Exception as e:
                print("Error while opening mmap:", e)
                return
            
            while isRunning:
                print('isRunning 1')
                try:
                    frame_data = poseEstimationService.getFrameData()
                    print(frame_data[:10])
                except:
                    print('what')
                print('isRunning 2')
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
                except KeyboardInterrupt:
                    print("Program Interrupted. Stopping Video Loop...")
                    break
                except Exception as e:
                    print("Error while writing to mmap:", e)

                if not isRunning:
                    break
            
            mm.flush()
            mm.close()
            poseEstimationService.stopVideo()
            # video_thread.join()

    except KeyboardInterrupt:
        print("KeyboardInterrupt. Exiting.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    os.system("cls")

    config = open('./compvis-service/config.json', 'r')
    config_options = json.load(config)

    MODEL_PATH  = config_options["MODEL_PATH"]
    SHM_FILE    = config_options["SHM_FILE"]
    BUFFERSIZE  = config_options["BUFFERSIZE"]

    config.close()

    # Initialise mmap file
    try:
        with open(SHM_FILE, "wb") as f:
            f.write(padBuffer(b"Hello Python!\n", BUFFERSIZE))
    except:
        print("oopsies")
    finally:
        main()