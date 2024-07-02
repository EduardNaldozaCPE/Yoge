#include <iostream>
#include <string>
#include "includes/FrameConsumer.h"


int main() {
	// 1. Create the FrameConsumer Instance
	FrameConsumer fc;

	// 2. Connect to the Named pipe. Retries if unsuccessful.
	bool success = fc.connect();
	if (!success)
		return 1;

	// 3. Take the latest data from the Named Pipe (TODO: Change to state).
	char* buffer;
	while (true) {
		fc.readFrame(&buffer);

		// 4. Print out the data.

		std::cout << "Data read from pipe: " << buffer << std::endl;
		std::cin.get();
		//Sleep(1000);
	}

	return 0;
}