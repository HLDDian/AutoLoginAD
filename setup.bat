@echo off
echo 正在創建虛擬環境...
python -m venv venv

echo 正在啟用虛擬環境...
call venv\Scripts\activate

echo 正在安裝依賴...
pip install -r requirements.txt

echo 設置完成！
echo 您可以通過運行 AutoLoginAD.bat 啟動程序。
pause 