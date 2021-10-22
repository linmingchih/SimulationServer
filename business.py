queue_dir = 'c:/demo/'

import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


os.environ['PATH']='C:\Program Files\AnsysEM\AnsysEM21.1\Win64'

def getFolders():
    folders = [os.path.join(queue_dir, i) for i in os.listdir(queue_dir) if os.path.isdir(os.path.join(queue_dir, i))]
    return folders

def getExt(ext = 'aedtz'):
    files = [os.path.join(queue_dir, x) for x in os.listdir(queue_dir) if x.endswith(ext)]
    files.sort(key=lambda x: os.path.getmtime(x))
    return files
    
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        pass
    
    def on_deleted(self, event):
        if '.aedtz.lock' in event.src_path:
            time.sleep(1)
            dir_name = os.path.dirname(event.src_path)
            shutil.make_archive(dir_name, 'zip', dir_name)
            os.chdir(queue_dir)
            shutil.rmtree(dir_name)
        
if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=queue_dir, recursive=True)
    observer.start()
    
    try:
        while True:
            if getFolders():
                time.sleep(10)
            else:
                try:
                    aedtz = getExt('aedtz')[0]
                    base_name = os.path.basename(aedtz).split('.')[0]
                    new_folder = os.path.join(os.path.dirname(aedtz), base_name)
                    os.mkdir(new_folder)
                    new_aedt_path = os.path.join(new_folder, os.path.basename(aedtz))
                    shutil.move(aedtz, new_aedt_path)
                    os.chdir(new_folder)
                    os.system(f'ansysedt -BatchSolve -ng -monitor -autoextract reports -machinelist list="localhost:4:20:90%:1" {new_aedt_path}')
                except:
                    pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
