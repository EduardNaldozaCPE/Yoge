const LinkedList = require("./modules/LinkedList.js");

petList = new LinkedList();

petList.offer("Cotton");
petList.offer("Magnum");
petList.offer("Poggie");
petList.offer("Luna");
petList.offer("Madu");

console.log(petList.getAll());
console.log(petList.getAllValues());