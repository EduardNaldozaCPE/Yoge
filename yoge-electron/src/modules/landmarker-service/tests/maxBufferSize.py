sizesFile = open('./tests/MAXBUFFERSIZEs.txt', 'r')

maxSize = 0
for size in sizesFile.readlines():
    iSize = int(size)
    if iSize > maxSize:
        maxSize = iSize

sizesFile.close()
print(maxSize)