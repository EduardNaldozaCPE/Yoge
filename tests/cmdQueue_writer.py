import csv, os, time, logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
fdir = os.path.join(os.getcwd(),'resources','ipc')
fp = os.path.join(os.getcwd(),'resources','ipc','cmdqueue.csv')

def _writeCommand(filePath:str, cmdString:str):
    with open(filePath, 'w') as cmdQueue:
        writer = csv.writer(cmdQueue, delimiter=',', lineterminator='\n')
        cmdId = int(time.time())
        writer.writerow(['PYTHON',cmdId, cmdString])
        print(cmdId,": written to cmd queue.")

# for i in range(10):
#     _writeCommand(fp, "do something")
#     time.sleep(2)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    observer = Observer()
    event_handler = LoggingEventHandler()
    observer.schedule(event_handler, fdir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
