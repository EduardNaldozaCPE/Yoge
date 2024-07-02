from time import sleep
import win32pipe, win32file, pywintypes
from includes.FrameSample import FrameSample

pipe_name = r'\\.\\pipe\\framePipe'
fs = FrameSample() 
frameSample = fs.bFrame

BUFFERSIZE = 1048576

# Create a named pipe
pipe = win32pipe.CreateNamedPipe(
    pipe_name,
    win32pipe.PIPE_ACCESS_OUTBOUND,
    win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_WAIT,
    1, BUFFERSIZE, BUFFERSIZE,
    0,
    None
)

# Wait for a connection
print("Waiting for consumer to connect...")
win32pipe.ConnectNamedPipe(pipe, None)


# Write data to the pipe
counter = 0
while counter < 1000:
    counter += 1

    try:
        win32file.WriteFile(pipe, frameSample)
    except pywintypes.error: break
    except Exception as e:
        print(e)
        break

    print(f"Size written to pipe: {len(frameSample)}")  
    sleep(1)


# Close the pipe
print("Closing Handle")
win32file.CloseHandle(pipe)
