#include <iostream>
#include "tests/shmtest.cpp"

int main() {
	char userInput[] = "";

	std::cout << "Run ShmTest!\n";

	char shmName[] = "psm_12345";

	runShmTest(shmName);

	return 0;
}