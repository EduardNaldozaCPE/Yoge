#ifndef LINKEDLIST_H
#define LINKEDLIST_H
/**
 * LLNode_int is is a structure for a single Node for the Linked List class.
 */
struct LLNode_int 
{
    int value;
    struct LLNode_int * nextNode;
};

/**
 * The LinkedList class follows the data structure named "linked lists".
 */
class LinkedList {
    struct LLNode_int * pFirstNode;
    struct LLNode_int * pLastNode;
    
    public:
        LinkedList();
        ~LinkedList();
        void offer(int newVal);
        int peekFirst();
};

#endif