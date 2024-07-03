#ifndef FRAMECONSUMER_H
#define FRAMECONSUMER_H

#include <iostream>
#include <Windows.h>
#include <stdio.h>

#define BUFFERSIZE 1048576

class FrameConsumer {
private:
    HANDLE hPipe;
    DWORD bytesRead;
    LPCWSTR pipeName;
    char* currentBuffer = new char[BUFFERSIZE];
    bool isConnected = false;

public:
    /** FrameConsumer Module allows connection to the named pipe storing the frame data.
     * @param name Directory to the named pipe. Default: `R"(\\.\\pipe\\MyNamedPipe)"`
     */
    FrameConsumer(const wchar_t* arg_pipeDir);

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
    void readFrame(char* outbuffer[]);
};

#endif