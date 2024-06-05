import os
import win32file, pywintypes

import numpy as np
import cv2 as cv

import time

PIPE_NAME = r'\\.\pipe\frame_pipe'
BUFFERSIZE = 1048576

# Convert the buffer to np array, then to cv2 image using cv2.imdecode()
def showImage(data_bytes:bytes, timeLeft):
    data_np = np.frombuffer(data_bytes, np.uint8)
    frame = cv.imdecode(data_np, cv.IMREAD_COLOR)
    cv.putText(frame, timeLeft, (50, 50), cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255), 1, cv.LINE_AA)
    cv.imshow("Client", frame)


def named_pipe_client():
    # Run client for 10 seconds
    stopTime = time.time() + 10.0
    try:
        # Connect to the named pipe
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None, win32file.OPEN_EXISTING, 0, None
        )

        # Read the response from the server
        try:
            while time.time() <= stopTime:
                try:
                    result, response = win32file.ReadFile(handle, BUFFERSIZE)
                    unpadded_response = response.rstrip(b'\x00')
                    # print(f"Received response of Length: {len(response)} bytes.\nUnpadded to {len(unpadded_response)}")
                    showImage(unpadded_response, str(int(stopTime-time.time())))
                    if cv.waitKey(1) & 0xFF == 27:
                        cv.destroyAllWindows()
                        break
                except:
                    break

        except Exception as e:
            print("error: ", e)

        finally:
            win32file.CloseHandle(handle)

    except pywintypes.error as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    named_pipe_client()
