import mediapipe as mp
import cv2 as cv

import pickle
import struct
import queue

# Initialise MediaPipe Pose Landmarker
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
feed = None
frame_queue = queue.Queue()
feed = cv.VideoCapture(0)

def print_result(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    # print('pose landmarker result: {}'.format(result))
    pass
options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="./cv/pose_landmarker_lite.task"),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

print("PoseEstimationService Object Created")
    
# Gets the latest frame data in the queue
def getFrameData():
    return frame_queue.get()

# Starts video feed and puts frame data in the queue to be sent via websocket
def runVideo():        
    print('\n[Method Called] runVideo()')
    with PoseLandmarker.create_from_options(options) as landmarker:
        t = 0
        print("running the loop")
        while True:
            success, frame = feed.read()
            if not success:
                print("There was a problem reading the video feed.")
                break
        
            print(1)
            rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

            print(2)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            print(3)
            if not mp_image:
                print("could not read image") 
                continue
            
            print(4)
            landmarker.detect_async(mp_image, t)
            t += 1

            print(5)
            cv.imshow('img', frame)

            print(6)
            # Serialize the frame using pickle
            # data = pickle.dumps(frame)
            # message = struct.pack ("Q", len(data)) + data
            # frame_queue.put(message)

            if cv.waitKey(1) & 0xFF == 27:
                print('Exit key pressed. Exiting...')
                cv.destroyAllWindows()
                feed.release()
                break

    # cv.destroyAllWindows()
    # feed.release()

if __name__ == "__main__":
    runVideo()