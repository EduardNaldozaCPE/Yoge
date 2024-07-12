import mmap, cv2, numpy
from PIL import Image, ImageFile
from io import BytesIO

ImageFile.LOAD_TRUNCATED_IMAGES = True
output_file_path = 'output_image.png'

# Continuously read the image file
def displayCv2Image(frameBytes:bytes):
    if not frameBytes: return
    # bytes_np_dec = frameBytes.decode('unicode-escape').encode('ISO-8859-1')[2:-1]
    npFrame = numpy.frombuffer(frameBytes, dtype=numpy.uint8)
    decodedFrame = cv2.imdecode(npFrame, cv2.IMREAD_COLOR)
    cv2.imshow("ooga", decodedFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()


def padBuffer(buffer:bytes, shm_size):
    # Pad out the frame data to match the buffer size.
    MAXBUFFERSIZE = len(buffer)
    paddingLength = shm_size - (MAXBUFFERSIZE % shm_size)
    padding = b'\x00' * paddingLength
    return buffer + padding


shm_file = './shared/frame'
shm_size = 1048576
img_byte_array = None

# Open the file and map it to memory.
with open(shm_file, "r+b") as f:
    running = True
    print("Running")
    mm = mmap.mmap(f.fileno(), shm_size)
    while running:
        mm.seek(0)
        try:
            img_byte_array = mm.read().strip(b'\x00')
            displayCv2Image(img_byte_array)
        except Exception as e:
            print(e)
            running = False
            
    mm.close()

# [ SAVE TO PNG FILE TEST ]
# # Open the file and map it to memory.
# with open(shm_file, "r+b") as f:
#     mm = mmap.mmap(f.fileno(), shm_size)
#     mm.seek(0)
#     img_byte_array = mm.read().strip(b'\x00')
#     mm.close()
# # Convert image byte array to .png file
# if img_byte_array is not None:
#     with open('testimgbytes1.txt', 'w+') as f:
#         f.write(str(img_byte_array))

#     # Convert byte array back to an image and save it
#     image = Image.open(BytesIO(img_byte_array))
#     image.save(output_file_path, format='PNG')
#     print("Image saved successfully.")
