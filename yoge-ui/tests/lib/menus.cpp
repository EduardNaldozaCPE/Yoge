#include <iostream>
#include "structs/Dog.cpp"
#include "utils/iofuncs.cpp"

/**
 * Lists 10 dogs.
 *
 * @param dogs Array of Dogs
 */
void showAllDogs(Dog (&dogs)[10]) {
    int dogsLength = sizeof(dogs)/sizeof(dogs[0]);
    int userOption;

    for (int i = 0; i < dogsLength; i++) {
        if (!dogs[i].isValid) continue;

        std::cout << "\n" << i+1 << ". ----------\n";
        std::cout << "\n";
        std::cout << "Name: " << dogs[i].name << "\n";
        std::cout << "Age: " << dogs[i].age << " y/o\n";
        std::cout << "Description: " << dogs[i].desc << "\n";
    }
    std::cout << "\n" << "-------------\n\n";
    std::cout << "Enter '1' to continue. ";
    do {
        std::cin >> userOption;
    } while (userOption != 1);
}


/**
 * Display user prompts to add a new Dog.
 *
 * @param dogs Array of Dogs
 */
void addNewDog(Dog (&dogs)[10]) {
    int dogsLength = sizeof(dogs)/sizeof(dogs[0]);
    int userOption;

    // 1. Get first available Dog ID to use (Use find alogrithm).
    //  - If there are no more slots, return early with a message.

    // 2. If the first available ID is not the same as the array index, sort the array.
    
    // 3. Create and insert the new Dog.

    do {
        std::cin >> userOption;
    } while (userOption != 1);
}