import win32pipe, win32file, pywintypes

pipe_name = r'\\.\\pipe\\MyNamedPipe'
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

print("Waiting for consumer to connect...")
win32pipe.ConnectNamedPipe(pipe, None)

# Write data to the pipe
win32file.WriteFile(pipe, message.encode('utf-8'))

print(f"Data written to pipe: {message}")

# Close the pipe
win32file.CloseHandle(pipe)
