#include <iostream>
#include <string>

#include "lib/menus.cpp"

void routeOption(int * option);

Dog dogs[10] = {
        {1, "Stalin",   2,  "Has mustache, might be dictator(?)",   true},
        {2, "Cotton",   5,  "White, Short Tail",                    true},
        {3, "Magnum",   6,  "Husky, Beeg",                          true},
        {4, "Davinky",  2,  "Pomeranian, Fluffy asf",               true},
    };

int main() {
    // Print options
    int option;
    do {
        system("cls");
        std::cout << "Welcome to Doggo DB!\n";
        std::cout << "--------------------\n";
        std::cout << "Select an option:\n";
        std::cout << "1. Show All Dogs\n";
        std::cout << "9. Exit\n\n";
        userInput(&option);
        routeOption(&option);
    } while (option != 9);
    
    return 0;
}


void routeOption(int * option) {
    system("cls");
    switch (*option)
    {
    case 1:
        showAllDogs(dogs);
        break;

    case 2:
        addNewDog(dogs);
        break;

    case 9:
        std::cout << "Thank you for using Doggo DB!";
        exit(0);
        break;
    
    default:
        alertMsg("Please choose a valid option. Press Enter anything to try again.");
        break;
    }
}