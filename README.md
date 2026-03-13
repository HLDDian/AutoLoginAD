# 自動網路認證腳本

這是一個使用 DrissionPage 自動進行網路認證的 Python 腳本。

## 功能

- 定期檢查網路連接狀態
- 自動登入網路認證頁面
- 支援無頭瀏覽器模式
- 可配置的執行間隔和顯示選項

## 安裝

1. 確保已安裝 Python 3.6 或更高版本。

2. 建立並啟用虛擬環境：

   ### Windows:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

   ### macOS/Linux:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 安裝所需的依賴:

   ```
   pip install -r requirements.txt
   ```

## 配置

在專案根目錄建立一個 `settings.json` 檔案，包含以下內容:

```json
{
  "empNo": "您的員工編號",
  "password": "您的密碼",
  "interval": 5,
  "showBrowser": "N"
}
```

- `empNo`: 您的員工編號
- `password`: 您的密碼
- `interval`: 檢查間隔(秒)
- `showBrowser`: 是否顯示瀏覽器 ("Y" 顯示, "N" 不顯示)

## 使用

啟用虛擬環境後，執行以下指令啟動腳本:

```
python main.py
```

腳本將按照設定的間隔時間自動檢查網路連接並在需要時進行認證。

## 自動化啟動

若要讓系統自動啟動腳本，可以更新 `AutoLoginAD.bat` 文件：

```
cd 您的專案路徑
call venv\Scripts\activate
python main.py
pause
```

## 注意事項

- 請確保 `settings.json` 檔案中的資訊正確且安全。
- 腳本使用 DrissionPage，無需額外安裝 ChromeDriver。
- 如遇到問題，請檢查控制台輸出的錯誤訊息。
- 每次使用前請確保虛擬環境已啟用。

## 授權

[在此添加您的授權資訊]
