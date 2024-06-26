#include <iostream>

// TODO -- Learn https://www.youtube.com/watch?v=a5kUr-u2UNo to find out how to compile this including boost

#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>

using namespace boost::interprocess;

int main()
{
    try {
        // Open the shared memory object
        shared_memory_object shm(open_only, "my_shared_memory", read_only);
        
        // Map the shared memory into this process's address space
        mapped_region region(shm, read_only);
        
        // Get a pointer to the shared memory region
        char* mem = static_cast<char*>(region.get_address());
        
        // Read and print the shared data
        std::cout << "Received: " << mem << std::endl;
        
    } catch (const std::exception& ex) {
        std::cerr << ex.what() << std::endl;
        return 1;
    }
    
    return 0;
}
