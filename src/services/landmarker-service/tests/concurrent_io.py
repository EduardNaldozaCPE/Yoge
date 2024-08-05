import threading
import time

willExit = False

def read_input():
    global willExit
    while True:
        user_input = input()
        if user_input.lower() == 'exit':
            willExit = True
            break
        print(f"Input received: {user_input}")

def continuously_print():
    global willExit
    while True:
        if (willExit): break
        print("Printing to stdout...")
        time.sleep(1)

# Create threads for reading input and printing
input_thread = threading.Thread(target=read_input)
print_thread = threading.Thread(target=continuously_print)

# Start the threads
input_thread.start()
print_thread.start()

# Wait for the input thread to finish
input_thread.join()
print_thread.join()
print("Exiting program...")