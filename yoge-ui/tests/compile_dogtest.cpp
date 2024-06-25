#include <iostream>
#include <string>

int main() {
    char * tempInput;
    int ooga = system("g++ main.cpp -o DoggoDb comp.res");
    if (ooga == 0) {
        std::cout << "\nCompilation Success.\n";
    } else {
        std::cout << "\nCompilation Failed.\n";
    }
    std::cin >> tempInput;
    return 0;
}