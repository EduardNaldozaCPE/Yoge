import sys


f = open("query-queue.txt", "w+")
while True:
    try:
        pipe_in = input()
        print(pipe_in, file=sys.stderr)
    except EOFError as e:
        # print("EOF Caught", file=sys.stderr)
        continue
    if pipe_in == "STOP": break 
    f.write(pipe_in)
f.close()