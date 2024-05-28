import mediapipe as mp
import cv2 as cv

import pickle
import struct

class PoseEstimationService:
    def __init__(self):
        # Initialise MediaPipe Pose Landmarker
        self.BaseOptions = mp.tasks.BaseOptions
        self.PoseLandmarker = mp.tasks.vision.PoseLandmarker
        self.PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        self.PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
        self.VisionRunningMode = mp.tasks.vision.RunningMode
        self.feed = None

        def print_result(self, result: mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
            # print('pose landmarker result: {}'.format(result))
            pass

        self.options = self.PoseLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path="./cv/pose_landmarker_lite.task"),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=print_result)
        
        print("PoseEstimationService Object Created")
        

    # Starts video feed and yields data to be sent via websocket
    def runVideo(self):        
        self.feed = cv.VideoCapture(0)
        with self.PoseLandmarker.create_from_options(self.options) as landmarker:
            t = 0
            while True:
                success, frame = self.feed.read()
                if not success: 
                    break

                rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                if not mp_image: 
                    continue
                
                landmarker.detect_async(mp_image, t)
                t += 1

                cv.imshow('img', mp_image)

                # Serialize the frame using pickle
                data = pickle.dumps(frame)
                message = struct.pack ("Q", len(data)) + data
                yield message

                if cv.waitKey(1) & 0xFF == 27: 
                    break

            cv.destroyAllWindows()
            self.feed.release()