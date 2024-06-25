#include <iostream>


void userInput(int * option) {
    int input;
    std::cout << "Doggo> ";
    std::cin >> input;
    *option = input;
}


void alertMsg(std::string message) {
    int tempOption;
    system("cls");
    std::cout << message << "\n";
    userInput(&tempOption);
}