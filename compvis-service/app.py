import os
import time
import threading
from PoseEstimationService import PoseEstimationService

PIPE_NAME = r'\\.\pipe\frame_pipe'


def main():
    # Initialise the service
    try:
        # TODO -- Take in userId, sequenceId, sessionId
        poseEstimationService = PoseEstimationService()
        poseEstimationService.setSessionData()
    except:
        return
    
    isRunning = True

    # Create a separate thread for runVideo since it has an endless loop
    video_thread = threading.Thread(target=poseEstimationService.runVideo)
    video_thread.start()

    while isRunning:
        frame_data = poseEstimationService.getFrameData()
        if frame_data is not None:
            try:
                # send frame_data to pipe
                # print(str(len(frame_data)))
                time.sleep(0.1)
                pass
            except KeyboardInterrupt:
                print("Program Interrupted. Stopping Video Loop...")
                isRunning = False
            
        if not isRunning:
            break

    poseEstimationService.stopVideo()
    video_thread.join()


if __name__ == "__main__":
    os.system("cls")
    main()