import mediapipe as mp
from mediapipe import Image, ImageFormat
import cv2

# TODO -- FIND THE CAUSE OF THE "Feedback manager requires a model with a single signature inference." ERROR

def main():
    model_path = "./cv/pose_landmarker_lite.task"
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    PoseLandmarkerResult = mp.tasks.vision.PoseLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    mp_image = None

    # Create a pose landmarker instance with the live stream mode:
    def print_result(result : mp.tasks.vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        # print('pose landmarker result: {}'.format(result))
        pass

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result
        )
    
    feed = cv2.VideoCapture(0)
    if not feed.isOpened():
        print("Failed to open capture device")
        exit(1)

    while feed.isOpened():
        ret, img = feed.read()

        if not ret:
            break

        mp_image = Image(image_format=ImageFormat.SRGB, data=img)

        with PoseLandmarker.create_from_options(options) as landmarker:
            landmarker.detect_async(mp_image, 1)

        cv2.imshow('img', img)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        
    feed.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
