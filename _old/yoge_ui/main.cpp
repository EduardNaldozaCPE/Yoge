#include <iostream>
#include <string>
#include "includes/FrameConsumer.h"

const wchar_t* pipeDir = TEXT("\\\\.\\pipe\\framePipe");

int main() {
	// 1. Create the FrameConsumer Instance
	FrameConsumer fc(pipeDir);

	// 2. Connect to the Named pipe. Retries if unsuccessful.
	bool success = fc.connect();
	if (!success)
		return 1;

	// 3. Take the latest data from the Named Pipe.
	char* mainBuffer = new char[BUFFERSIZE];
	const int siz_buffer = strlen(mainBuffer);
	while (true) {
		fc.readFrame(&mainBuffer);

		//// 4. Print out the data.
		//std::cout << "Size of Data: " << siz_buffer << "\n";
		
		Sleep(50);		
		// TODO -- Find a way to decode the bytes to a png format.
	}

	delete[] mainBuffer;
	mainBuffer = nullptr;
	return 0;
}