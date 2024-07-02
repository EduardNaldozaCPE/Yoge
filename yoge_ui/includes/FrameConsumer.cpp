#include "FrameConsumer.h"

//#include <fileapi.h>
#include <iostream>
#include <Windows.h>
#include <stdio.h>

#define PIPEDIR "\\\\.\\pipe\\framePipe"

FrameConsumer::FrameConsumer()
{
    // Connect to the named pipe
    pipeName = TEXT(PIPEDIR);
}

FrameConsumer::~FrameConsumer()
{
    // Close the pipe
    CloseHandle(hPipe);
}

bool FrameConsumer::connect() {
    std::cout << "Connecting to Named Pipe.\n";
    do {
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
            //std::cerr << "Failed to open named pipe. Error: " << GetLastError() << std::endl;
            Sleep(1000);
        } else {
            std::cout << "Named pipe connected successfully.\n";
            isConnected = true;
        }
    } while (!isConnected);

    return true;
}

void FrameConsumer::readFrame(char* outbuffer[])
{
    // Read data from the pipe
    std::cout << "Reading from named pipe: \"" << PIPEDIR << "\"\n";
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
        *outbuffer = buffer;
    }
}