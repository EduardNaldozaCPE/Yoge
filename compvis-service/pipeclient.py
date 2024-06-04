import os
import win32file, pywintypes

import numpy as np
import cv2 as cv

PIPE_NAME = r'\\.\pipe\frame_pipe'
BUFFERSIZE = 1048576

def showImage(data_bytes:bytes):
    data_np = np.frombuffer(data_bytes, np.uint8)
    frame = cv.imdecode(data_np, cv.IMREAD_COLOR)
    cv.imshow("Client", frame)


def named_pipe_client():
    try:
        # Connect to the named pipe
        handle = win32file.CreateFile(
            PIPE_NAME,
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0, None, win32file.OPEN_EXISTING, 0, None
        )

        # Read the response from the server
        try:
            while True:
                try:
                    result, response = win32file.ReadFile(handle, BUFFERSIZE)
                    unpadded_response = response.rstrip(b'\x00')
                    print(f"Received response of Length: {len(response)} bytes.\nUnpadded to {len(unpadded_response)}")
                    showImage(unpadded_response)
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
    os.system('cls')
    named_pipe_client()
