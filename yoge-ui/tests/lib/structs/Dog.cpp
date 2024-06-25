#include <string>

struct Dog {
    int id;
    
    public:
        std::string name;
        int age;
        std::string desc;
        bool isValid;
};


void updateDogName(Dog *dog, std::string newName) {
    dog->name = newName;
}

void updateDogAge(Dog *dog, int age) {
    dog->age = age;
}

void updateDogDesc(Dog *dog, std::string desc) {
    dog->desc = desc;
}