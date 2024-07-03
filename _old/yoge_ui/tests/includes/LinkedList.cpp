#include "./LinkedList.h"

LinkedList::LinkedList() {
    return;
}


LinkedList::~LinkedList() {
    return;
}


void LinkedList::offer(int newVal) {
    struct LLNode_int newNode = {newVal, nullptr};

    // The offered node will become the first and last node if they don't exist yet
    if (pFirstNode == nullptr) {
        pFirstNode = &newNode;
    }
    if (pLastNode == nullptr) {
        pLastNode = &newNode;
    }
};

int LinkedList::peekFirst() {
    if (pFirstNode != nullptr) {
        return pFirstNode->value;
    }
    return 0;
};