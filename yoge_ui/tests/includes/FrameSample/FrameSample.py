class FrameSample:
    def __init__(self):
        f = open('./includes/FrameSample/framebytes', "rb")
        self.bFrame = f.read()
        f.close()

if __name__ == "__main__":
    fs = FrameSample()
    # print(fs.bFrame)
    print(len(fs.bFrame))