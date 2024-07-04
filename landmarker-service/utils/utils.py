# Pad out the frame data to match the buffer size.
def padBuffer(buffer:bytes, maxSize:int) -> bytes:
    bufferSize = len(buffer)
    paddingLength = maxSize - (bufferSize % maxSize)
    padding = b'\x00' * paddingLength
    return buffer + padding