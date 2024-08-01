from watchdog.events import FileSystemEvent, FileSystemEventHandler
import sys

class IpcHandler(FileSystemEventHandler):
    """ FileSystemEventHandler Subclass - Append latest command to ipcQueue every file update """
    def __init__(self, ipc_csv_path):
        self.ipcQueue = []
        self.ipc_csv_path = ipc_csv_path

    def on_modified(self, event: FileSystemEvent) -> None:
        
        with open(self.ipc_csv_path, 'r') as cmdfile:
            try:    
                last_line = cmdfile.readlines()[-1]
                cmd = last_line.split(',')
                final_cmd = [int(cmd[0]), cmd[1].rstrip('\n')]
                self.ipcQueue.append(final_cmd)
            except Exception as e:
                print("Error found in _ipc_handler:", e, file=sys.stderr)