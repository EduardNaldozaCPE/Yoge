from time import sleep
import win32pipe, win32file, pywintypes

pipe_name = r'\\.\\pipe\\framePipe'
message = 'Hello from Python!'

# Create a named pipe
pipe = win32pipe.CreateNamedPipe(
    pipe_name,
    win32pipe.PIPE_ACCESS_OUTBOUND,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
    1, 65536, 65536,
    0,
    None
)

# Wait for a connection
print("Waiting for consumer to connect...")
win32pipe.ConnectNamedPipe(pipe, None)


# # Write data to the pipe
# counter = 0
# while counter < 1000:
#     counter += 1
#     win32file.WriteFile(pipe, counter.to_bytes())
#     print(f"Data written to pipe: {counter}")
#     sleep(0.5)

# Write data to the pipe
counter = 1
win32file.WriteFile(pipe, counter.to_bytes())
print(f"Data written to pipe: {counter.to_bytes()}")

# Close the pipe
win32file.CloseHandle(pipe)
