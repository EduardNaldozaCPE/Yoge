#include <iostream>
#include "includes/LinkedList.h"

int main() {
    LinkedList sampleList;
    sampleList.offer(10);

    std::cout << sampleList.peekFirst() << '\n';
    std::cin.get();

    return 0;
}