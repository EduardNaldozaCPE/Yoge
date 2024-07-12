# Pad out the frame data to match the buffer size.
def padBuffer(buffer:bytes, maxSize:int) -> bytes:
    
    bufferSize = len(buffer)
    paddingLength = (maxSize - 9) - (bufferSize % maxSize)
    padding = b'\x00' * paddingLength
    
    # Wrap the buffer
    return buffer + b'BUFFEREND' + padding