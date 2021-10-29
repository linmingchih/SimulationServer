ansysEM_path = "C:/Program Files/AnsysEM"
queue_dir = 'D:/demo'
days_to_keep = 3
line_notify_handler = '58ceAuCRlEIZPnjkcf4LGLV32AVgwSSNfYymTfUpxRi'

import os
import time
import requests
import datetime
import shutil
import psutil
import logging
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

log_format = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(filename='simulation_status.log', filemode='w', level=logging.DEBUG, format=log_format)

def lineNotifyMessage(msg):
    if line_notify_handler:
        headers = {
            "Authorization": f"Bearer {line_notify_handler}",
            "Content-Type" : "application/x-www-form-urlencoded"
        }
        
        payload = {'message': msg}
        r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        
        return r.status_code

    else:
        return None

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
        logging.info('{} created.'.format(event.src_path))
    
    def on_deleted(self, event):
        if '.aedtz.lock' in event.src_path:

            dir_name = os.path.dirname(event.src_path)
            shutil.make_archive(dir_name, 'zip', dir_name)
            os.chdir(queue_dir)
            time.sleep(1)
            shutil.rmtree(dir_name)
            logging.info('{} removed.'.format(event.src_path))
            lineNotifyMessage(f'{dir_name} is Accomplished!')

def deleteFilesOverDays():
    for dirpath, dirnames, filenames in os.walk(queue_dir):
       for file in filenames:
          curpath = os.path.join(dirpath, file)
          file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(curpath))
          if datetime.datetime.now() - file_modified > datetime.timedelta(days=days_to_keep):
              os.remove(curpath)

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def solveAEDTZ(aedtz_path):
    print(aedtz_path)
    os.chdir(queue_dir)
    folder = os.path.dirname(aedtz_path)
    p = subprocess.Popen(['ansysedt', 
                          '-BatchSolve', 
                          '-ng', 
                          '-monitor', 
                          '-autoextract', 
                          'reports', 
                          '-machinelist', 
                          'list="localhost:4:20:90%:1"', 
                          aedtz_path])
    last_size = 0
    while(p.poll() == None):
        print(f'processa id: {p.poll()}')
        process = psutil.Process(p.pid)
        size_m = process.memory_info().rss
        size_f = get_size(folder)
        size = size_m + size_f
        print(f'total size:{size}')
        time.sleep(10)
        
        if size != last_size:
            last_size = size
        else:
            p.terminate()
            time.sleep(1)
            for f in os.listdir(folder):
                if f.endswith('.aedtz.lock'):
                    os.remove(os.path.join(folder, f))
    
    print(f'process return code:{p.poll()}')

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
                    logging.info(f'{aedtz} is running.')
                    
                    solveAEDTZ(new_aedt_path)

                except:
                    time.sleep(10)

            deleteFilesOverDays()
                
    except:
        logging.exception('ERROR')
        observer.stop()

    observer.join()
