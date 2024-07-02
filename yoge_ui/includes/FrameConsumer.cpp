#include <FrameConsumer.h>

FrameConsumer::FrameConsumer(char* name)
{
    // Connect to the named pipe
    pipeName = name;
    hPipe = CreateFile(
        pipeName,
        GENERIC_READ,
        0,
        NULL,
        OPEN_EXISTING,
        0,
        NULL
    );

    if (hPipe == INVALID_HANDLE_VALUE) {
        std::cerr << "Failed to open named pipe. Error: " << GetLastError() << std::endl;
        return 1;
    }
}

FrameConsumer::~FrameConsumer()
{
    // Close the pipe
    CloseHandle(hPipe);
}

char* FrameConsumer::readFrame()
{
    // Read data from the pipe
    BOOL success = ReadFile(
        hPipe,
        buffer,
        sizeof(buffer) - 1,
        &bytesRead,
        NULL
    );

    if (!success || bytesRead == 0) {
        std::cerr << "Failed to read from named pipe. Error: " << GetLastError() << std::endl;
    } else {
        buffer[bytesRead] = '\0'; // Null-terminate the string
        std::cout << "Data read from pipe: " << buffer << std::endl;
    }
    
    return 0;
}