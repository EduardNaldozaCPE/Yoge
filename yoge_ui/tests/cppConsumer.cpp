// consumer.cpp
#include <windows.h>
#include <iostream>
#include <string>
#include <cstring>

// TODO -- READ: https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipes

int main() {
    const char* pipeName = R"(\\.\\pipe\\MyNamedPipe)";
    HANDLE hPipe;
    char buffer[128];
    DWORD bytesRead;

    // Connect to the named pipe
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
        //buffer[bytesRead] = '\0'; // Null-terminate the string
        std::cout << "Data read from pipe: " << buffer << std::endl;
    }

    // Close the pipe
    CloseHandle(hPipe);

    return 0;
}
