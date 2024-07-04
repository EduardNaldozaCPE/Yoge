class LinkedListNode {
    constructor(key, value, next) {
        this.key = key;
        this.value = value;
        this.next = next;
    }
}

class LinkedList {
    constructor(){
        this.first;
        this.last;
    }
    
    offer(value) {
        let newNode;
        
        if (this.last == undefined) {
            newNode = new LinkedListNode(0, value, 0);
        }
        else {
            newNode = new LinkedListNode(this.last.key+1, value, 0);
            this.last.next = newNode;
        }

        // Update last node. Make this the first node if there is none.
        this.last = newNode;
        if (this.first == undefined)
            this.first = this.last;
        
        // Update the Node count
        this.nodeCount++;
        
    }

    getAll() {
        if (this.first == undefined) return [];
        let allNodes = [];
        let currentNode = this.first;
        while (currentNode) {
            allNodes.push(currentNode);
            currentNode = currentNode.next;
        }
        return allNodes;
    }

    getAllValues() {
        if (this.first == undefined) return [];
        let allNodes = [];
        let currentNode = this.first;
        while (currentNode) {
            allNodes.push(currentNode.value);
            currentNode = currentNode.next;
        }
        return allNodes;
    }
}

module.exports = LinkedList;