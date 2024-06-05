import mmap


def padBuffer(buffer:bytes, shm_size):
    # Pad out the frame data to match the buffer size.
    bufferSize = len(buffer)
    paddingLength = shm_size - (bufferSize % shm_size)
    padding = b'\x00' * paddingLength
    return buffer + padding


# buffer = b'Hello Wordl!\n'
shm_file = './shared/test'
shm_size = 1024

# # Create the file.
# with open(shm_file, "wb") as f:
#     print(padBuffer(buffer, shm_size))
#     f.write(padBuffer(buffer, shm_size))

# Open the file and map it to memory.
with open(shm_file, "r+b") as f:
    mm = mmap.mmap(f.fileno(), shm_size)

    # read content via standard file methods
    print(mm.read())

    # update content using slice notation;
    # note that new content must have same size
    mm[5:13] = b" World!\n"
    
    # ... and read again using standard file methods
    mm.seek(0)
    print(mm.read())  # prints b"Hello  world!\n"

    mm.close()