import csv, os, time
fp = os.path.join(os.getcwd(),'resources','cmdqueue.csv')

def _writeCommand(filePath:str, cmdString:str):
    with open(filePath, 'w') as cmdQueue:
        writer = csv.writer(cmdQueue, delimiter=',', lineterminator='\n')
        cmdId = int(time.time())
        writer.writerow(['PYTHON',cmdId, cmdString])
        print(cmdId,": written to cmd queue.")

for i in range(10):
    _writeCommand(fp, "do something")
    time.sleep(2)