ansysEM_path = "C:/Program Files/AnsysEM"
queue_dir = 'D:/demo'

import os
import time
import json
import streamlit as st
from streamlit_autorefresh import st_autorefresh

count = st_autorefresh(interval=60000)
os.chdir(os.path.dirname(__file__))

def getAnsysEMVersions():
    import os
    result = {}
    for root, dirs, files in os.walk(ansysEM_path):
        for file in files:
            if file == 'ansysedt.exe':
                version = root.split('\\')[-2]
                result[version] = root
    return result

if 'AnsysEMversions' not in st.session_state:
    st.session_state.AnsysEMversions = getAnsysEMVersions()

def getFolders():
    folders = [i for i in os.listdir(queue_dir) if os.path.isdir(os.path.join(queue_dir, i))]
    return folders

def getExt(ext = 'aedtz'):
    files = [i for i in os.listdir(queue_dir) if i.endswith(ext)]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(queue_dir, x)))
    return files

st.title('AEDT Simulation Submit System')

st.subheader('-Submit Jobs')
with st.form(key='my_form', clear_on_submit=True):
    versions = st.session_state.AnsysEMversions.keys()
    version = st.selectbox('ANSYS EM Version', list(versions)[::-1])
    
    files = st.file_uploader("Upload .aedtz", accept_multiple_files=True, type='aedtz')

    if st.form_submit_button(label='Submit'):
        for file in files:                   
            with open(os.path.join(queue_dir, f'{version}_{file.name}'), 'wb') as f:
                f.write(file.getbuffer())


st.subheader('-The Running Job')
if len(getFolders()) == 0:
    st.write('None')

for folder in getFolders():
    with st.expander(folder):
        st.button('refresh status')
        for root, dirs, files in os.walk(os.path.join(queue_dir, folder)):
            for file in files:
                if file.endswith(".log"):
                    with open(os.path.join(root, file), encoding='UTF-8') as f:
                        st.text_area('Simulation Message', f.read(), height=600)    


st.subheader('-Waiting Jobs')
if len(getExt('aedtz')) == 0:
    st.write('None')
    
for file in getExt('aedtz'):
    with st.expander(file):
        pass
        
st.subheader('-Finished Jobs')
if len(getExt('zip')) == 0:
    st.write('None')
    
for file in getExt('zip')[::-1]:
    file_path = os.path.join(queue_dir, file)
    file_size = round(os.path.getsize(file_path)/1e6, 1)
    file_date = time.ctime(os.path.getmtime(file_path))
    with st.expander('{}'.format(file)):
        with open(os.path.join(queue_dir, file), 'rb') as f:
            data = f.read()
        st.write('{}MB, {}'.format(file_size, file_date))            
        st.download_button('download', data, file)


#st.write(password_table)
