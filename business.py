ansysEM_path = r"C:/Program Files/AnsysEM"
queue_dir = 'c:/demo/'
days_to_keep = 3

import os
import time
import requests
import datetime
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



def lineNotifyMessage(msg):
    headers = {
        "Authorization": "Bearer " + '58ceAuCRlEIZPnjkcf4LGLV32AVgwSSNfYymTfUpxRi', 
        "Content-Type" : "application/x-www-form-urlencoded"
    }
	
    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

def getAnsysEMVersions():
    import os
    result = {}
    for root, dirs, files in os.walk(ansysEM_path):
        for file in files:
            if file == 'ansysedt.exe':
                version = root.split('\\')[-2]
                result[version] = root
    return result

ansysEMversions = getAnsysEMVersions()

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
            lineNotifyMessage(f'{dir_name} is Accomplished!')

def deleteFilesOverDays():
    for dirpath, dirnames, filenames in os.walk(queue_dir):
       for file in filenames:
          curpath = os.path.join(dirpath, file)
          file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
          if datetime.datetime.now() - file_modified > datetime.timedelta(days=days_to_keep):
              os.remove(curpath)


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
                    base_name = os.path.basename(aedtz)[:-6]
                    version = base_name.split('_')[0]
                    os.environ['PATH'] = ansysEMversions[version]
                    
                    new_folder = os.path.join(os.path.dirname(aedtz), base_name)
                    os.mkdir(new_folder)
                    new_aedt_path = os.path.join(new_folder, os.path.basename(aedtz))
                    shutil.move(aedtz, new_aedt_path)
                    os.chdir(new_folder)
                    lineNotifyMessage(f'{aedtz} is Running!')
                    os.system(f'ansysedt -BatchSolve -ng -monitor -autoextract reports -machinelist list="localhost:4:20:90%:1" {new_aedt_path}')
                except:
                    time.sleep(10)

            deleteFilesOverDays()
                
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
