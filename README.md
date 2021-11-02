# SimulationServer
1. 安裝Python3.8 (https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe) 在裝有AEDT軟體的工作站上。
2. 升級pip工具。開啟命令視窗，切換到Python安裝目錄，舉例來說，C:\Users\mlin\AppData\Local\Programs\Python\Python38：輸入.\python.exe -m pip install --upgrade pip
3. 接下來安裝streamlit及streamlit_autorefresh兩個模組。一樣開啟命令視窗，切換到Python安裝目錄當中的Scripts目錄，舉例來說，C:\Users\mlin\AppData\Local\Programs\Python\Python38\Scripts
- 輸入.\pip install streamlit
- 輸入.\pip install streamlit_autorefresh
4. 建上傳檔案要存放的目錄，比方d:\demo
5. 將ui.py及business.py及AEDTRemoteHost.bat複製到任一目錄當中，修改py當中的環境變數設定：ansysEM_path, queue_dir, days_to_keep, line_notify_handler等。
- 批次檔要填streamlit.exe存放的目錄
  * set PATH=D:\myvenv\Scripts
- python當中的參數
  * ansysEM_path：AEDT Win64的路徑
  * queue_dir：上傳檔案要存放的目錄(d:\demo)
  * days_to_keep：檔案保留天數
  * line_notify_handler：Line傳送Handle可不填
6. 執行AEDTRemoteHost.bat。成功的話會啟動瀏覽器並開啟localhost:8501頁面。
