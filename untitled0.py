import os
import time
import subprocess
os.environ['PATH'] = 'C:\Program Files\AnsysEM\AnsysEM21.1\Win64'


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
        print(f'process id: {p.poll()}')
        size = get_size(os.path.dirname(aedtz_path))
        print(f'folder size:{size}')
        time.sleep(10)
        if size > last_size:
            last_size = size
        else:
            p.kill()
            return False
    
    print(p.poll())
    return True

aedtz_path = 'd:/demo13/test.aedtz'
solveAEDTZ(aedtz_path)