from multiprocessing import shared_memory
import numpy

def client():
    shm = shared_memory.SharedMemory(name='psm_12345')
    try:
        data = bytes(shm.buf[:]).rstrip(b'\x00')
        npFrame = numpy.frombuffer(data, dtype=numpy.uint8)
        print('Received:', npFrame)
        print('Size:', len(npFrame))
    finally:
        shm.close()

if __name__ == '__main__':
    client()
