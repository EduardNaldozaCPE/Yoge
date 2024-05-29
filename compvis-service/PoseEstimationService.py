import mediapipe as mp
import cv2 as cv

# import pickle
# import struct
import numpy as np
import queue

class PoseEstimationService:
    def __init__(self):
        # Initialise MediaPipe Pose Landmarker
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        self.feed = None

        def print_result(result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
            # print('pose landmarker result: {}'.format(result))
            pass
        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path="./cv/pose_landmarker_lite.task"),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=print_result)
        
        # Initialise Class States
        self.frame_queue = queue.Queue()
        self.running = False
        print("PoseEstimationService Object Created")
        

    # Gets the latest frame data in the queue
    def getFrameData(self) -> bytes:
        print("[Method Called] getFrameData()")
        return self.frame_queue.get()
    

    # Stops the video feed loop in runVideo()
    def stopVideo(self):
        print("[Method Called] stopVideo()")
        self.running = False


    # Starts video feed and puts frame data in the queue to be sent via websocket
    # MUST RUN IN SEPERATE THREAD
    def runVideo(self):        
        print('\n[Method Called] runVideo()')
        self.feed = cv.VideoCapture(0)
        self.running = True
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            t = 0
            while True:
                if not self.running:
                    break

                success, frame = self.feed.read()
                frame = cv.resize(frame, (854, 480))

                if not success:
                    print("There was a problem reading the video feed.")
                    break
            
                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                if not mp_image:
                    print("could not read image") 
                    continue
                
                landmarker.detect_async(mp_image, t)
                t += 1


                # Encode the frame data then convert to numpy array then convert to bytes 
                _, data = cv.imencode('.jpg', frame)
                # data_np = np.array(data)
                # data_bytes = data_np.tobytes()
                self.frame_queue.put(data)

                # # [FOR TESTING]
                # cv.imshow('img', frame)
                # if cv.waitKey(1) & 0xFF == 27:
                #     print('Exit key pressed. Exiting...')
                #     cv.destroyAllWindows()
                #     self.feed.release()
                #     break

            cv.destroyAllWindows()
            self.feed.release()


if __name__ == "__main__":
    p = PoseEstimationService()
    p.runVideo()