import sys, threading

def process_input(data):
    return f"Processed data: {data}"

# Read from stdin
def read_ipc():
    counter = 0
    for line in sys.stdin:
        counter += 1
        if line.strip().lower() == 'exit':
            print("Exiting Python script...")
            break
        if line.strip().lower() == 'ooga':
            print(f"ooga: {counter}")
        result = process_input(line.strip())
        print(result)
        sys.stdout.flush()  # Ensure the output is flushed immediately


ipc_thread = threading.Thread(target=read_ipc, daemon=True)
ipc_thread.start()
ipc_thread.join()