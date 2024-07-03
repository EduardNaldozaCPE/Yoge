#include "FrameConsumer.h"

//#include <fileapi.h>
#include <iostream>
#include <Windows.h>
#include <stdio.h>

FrameConsumer::FrameConsumer(const wchar_t* arg_pipeDir) {
    pipeName = arg_pipeDir;
}

FrameConsumer::~FrameConsumer() {
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
            Sleep(1000);
        } else {
            std::cout << "Named pipe connected successfully.\n";
            isConnected = true;
        }
    } while (!isConnected);

    return true;
}

void FrameConsumer::readFrame(char* bufferOut[]) {
    // Read data from the pipe
    BOOL success = ReadFile(
        hPipe,
        currentBuffer,
        BUFFERSIZE,
        &bytesRead,
        NULL
    );

    if (!success) {
        std::cerr << "Failed to read from named pipe. Error: " << GetLastError() << std::endl;
    }
    else {
        currentBuffer[bytesRead] = '\0'; // Null-terminate the string
        *bufferOut = currentBuffer;
    }
}