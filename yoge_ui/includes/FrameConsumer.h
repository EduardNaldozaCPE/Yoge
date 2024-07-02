#ifndef FRAMECONSUMER_H
#define FRAMECONSUMER_H

#include <iostream>
#include <Windows.h>
#include <stdio.h>

class FrameConsumer
{
private:
    HANDLE hPipe;
    char buffer[1024];
    DWORD bytesRead;
    LPCWSTR pipeName;
    bool isConnected = false;

public:
    /** FrameConsumer Module allows connection to the named pipe storing the frame data.
     * @param name Directory to the named pipe. Default: `R"(\\.\\pipe\\MyNamedPipe)"`
     */
    FrameConsumer();

    /** Close from named pipe and cleanup.
     */
    ~FrameConsumer();

    /** Connect the named pipe storing the frame data. 
    * Only run once and use FrameConsumer::readFrame() to get the frame data.
    */
    bool connect();

    /** Consume the bytestring written in the named pipe.
     * 
     */
    char* readFrame();
};

#endif