import os
import time
import threading
from PoseEstimationService import PoseEstimationService
import win32pipe, win32file, pywintypes
import queue

PIPE_NAME = r'\\.\pipe\frame_pipe'
BUFFERSIZE = 1048576

def main():
    currentFrame = None

    # Create a named pipe
    pipe = win32pipe.CreateNamedPipe(
        PIPE_NAME,
        win32pipe.PIPE_ACCESS_DUPLEX,
        win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
        1, 12288, 12288,
        0,
        None
    )
    print("Waiting for client to connect...")

    # Initialise the pose estimation service
    # TODO -- Take in userId, sequenceId, sessionId
    poseEstimationService = PoseEstimationService()
    poseEstimationService.setSessionData()
    isRunning = True

    # Create a separate thread for runVideo since it has an endless loop
    video_thread = threading.Thread(target=poseEstimationService.runVideo)
    video_thread.start()

    win32pipe.ConnectNamedPipe(pipe, None)
    print("Client connected.")
    try:
        while isRunning:
            frame_data = poseEstimationService.getFrameData()

            if frame_data is not None:
                # Continue if the frame is too big. Log it too
                frameSize = len(frame_data)
                if frameSize > BUFFERSIZE: 
                    print("Frame Size: ", frameSize, "/", BUFFERSIZE)
                    print("frame data is too large. increase the buffer size. Skipping...")
                    continue
                
                # Pad out the frame data to match the buffer size.
                paddingLength = BUFFERSIZE - (frameSize % BUFFERSIZE)
                padding = b'\x00' * paddingLength
                currentFrame = frame_data + padding

                try:
                    # Send currentFrame to pipe
                    win32file.WriteFile(pipe, currentFrame)

                except KeyboardInterrupt:
                    print("Program Interrupted. Stopping Video Loop...")
                    break

            if not isRunning:
                break

    except pywintypes.error as e:
        print(f"Error: {e}")

    except KeyboardInterrupt:
        print("KeyboardInterrupt. Exiting.")
        
    finally:
        # Close the pipe
        win32pipe.DisconnectNamedPipe(pipe)
        win32file.CloseHandle(pipe)
            

    poseEstimationService.stopVideo()
    video_thread.join(1)


if __name__ == "__main__":
    os.system("cls")
    main()