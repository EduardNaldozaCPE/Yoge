import mmap
from PIL import Image, ImageFile
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True
output_file_path = 'output_image.png'

def padBuffer(buffer:bytes, shm_size):
    # Pad out the frame data to match the buffer size.
    bufferSize = len(buffer)
    paddingLength = shm_size - (bufferSize % shm_size)
    padding = b'\x00' * paddingLength
    return buffer + padding


shm_file = './shared/frame'
shm_size = 1048576
img_byte_array = None

# Open the file and map it to memory.
with open(shm_file, "r+b") as f:
    mm = mmap.mmap(f.fileno(), shm_size)
    mm.seek(0)
    img_byte_array = mm.read().strip(b'\x00')
    mm.close()

# Convert image byte array to .png file
if img_byte_array is not None:
    with open('testimgbytes1.txt', 'w+') as f:
        f.write(str(img_byte_array))

    # Convert byte array back to an image and save it
    image = Image.open(BytesIO(img_byte_array))
    image.save(output_file_path, format='PNG')
    print("Image saved successfully.")