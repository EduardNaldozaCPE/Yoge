#include <iostream>
#include "structs/Dog.cpp"
#include "utils/iofuncs.cpp"

/**
 * Clears the terminal to show 10 dogs
 *
 * @param dogs Array of Dog struct
 */
void showAllDogs(Dog (&dogs)[10]) {
    int dogsLength = sizeof(dogs[0])/sizeof((dogs));
    int userOption;

    // if (dogsLength <= 0) return;
    system("cls");
    
    // Find the number of valid Dogs in the array.
    // for (int i = 0; i < dogsLength; i++)
    // {
    //     // if (dogs[i] == NULL) continue;
    // }
    
    std::cout << "sizeof(dogs): " << sizeof((dogs)) << "\n";
    std::cout << "sizeof(dogs[0]): " << sizeof(dogs[0]) << "\n";
    std::cout << "dogsLength: " << dogsLength << "\n";

    for (int i = 0; i < dogsLength; i++)
    {
        std::cout << "\n";
        std::cout << dogs[i].name << "\n";
        std::cout << dogs[i].age << "\n";
        std::cout << dogs[i].desc << "\n";
    }
    
    std::cout << "\nEnter anything to continue. ";
    std::cin >> userOption;
}