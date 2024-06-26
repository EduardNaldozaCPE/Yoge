#include <iostream>

// NOTE -- Compile using -> g++ shmtest.cpp -Wall -o shmtest -I ./libs/boost_1_82_0
// TODO -- Read up on: https://www.boost.org/doc/libs/1_78_0/doc/html/interprocess.html
//  REFERENCE: https://www.youtube.com/watch?v=uyKLnwBjskg 

#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/mapped_region.hpp>

using namespace boost::interprocess;

const char* shmName = "psm_12345";

int main()
{
    std::cout << "shmName: " << shmName << '\n';
    try {
        // Open the shared memory object
        shared_memory_object shm(open_only, "psm_12345", read_only);
        
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
