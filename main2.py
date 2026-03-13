from datetime import datetime
import time
from DrissionPage import ChromiumOptions, Chromium
import os
import json
import logging

# 設置日誌
# log_file = 'autologin.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        # logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # 同時輸出到控制台
    ]
)
logging.info(f"=== 自動登入服務啟動 ===")
# logging.info(f"日誌檔案: {os.path.abspath(log_file)}")

class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self, headless=True):
        """初始化瀏覽器"""
        co = self._get_browser_options(headless)
        
        # 嘗試多次初始化瀏覽器
        max_retries = 3
        for i in range(max_retries):
            try:
                logging.info(f"嘗試初始化瀏覽器 (第 {i+1} 次)")
                self.browser = Chromium(co)
                logging.info("瀏覽器初始化成功")
                return self.browser
            except Exception as e:
                logging.error(f"初始化瀏覽器失敗 (第 {i+1} 次): {e}")
                if i < max_retries - 1:
                    time.sleep(2)  # 等待一段時間後重試
        
        logging.error(f"無法初始化瀏覽器，已重試 {max_retries} 次")
        return None

    def _get_browser_options(self, headless=True):
        """獲取瀏覽器配置"""
        co = ChromiumOptions()
        
        # 設置無頭模式
        co.headless(headless)
        
        # 設置其他選項以提高穩定性
        co.set_argument("--disable-gpu")
        # co.set_argument("--no-sandbox")
        co.set_argument("--disable-dev-shm-usage")  # 減少崩潰
        co.set_argument("--disable-features=TranslateUI")  # 禁用翻譯提示
        co.set_argument("--disable-extensions")  # 禁用擴展
        co.set_argument("--disable-popup-blocking")  # 禁用彈窗攔截
        co.set_argument("--blink-settings=imagesEnabled=false")  # 禁用圖片以提高速度
        co.set_pref("credentials_enable_service", False)
        
        return co

    def quit(self):
        """關閉瀏覽器"""
        if self.browser:
            try:
                self.browser.quit()
                logging.info("瀏覽器已關閉")
            except Exception as e:
                logging.error(f"關閉瀏覽器時發生錯誤: {e}")

# 讀取外部檔案settings.json
with open('settings.json') as f:
    settings = json.load(f)
username = settings['empNo']
password = settings['password']
interval = settings['interval']
showBrowser = settings['showBrowser']
# Convert showBrowser value to boolean
headless = True if showBrowser == 'Y' else False
headless = False

def open_url(tab, url):
    """開啟網址並等待頁面加載完成"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logging.info(f"嘗試開啟網址: {url} (第 {retry_count+1} 次)")
            tab.get(url)
            # 等待頁面加載一段時間
            time.sleep(3)  # 增加等待時間
            
            # 檢查頁面是否有效載入
            if tab.html and len(tab.html) > 100:  # 簡單檢查HTML是否有內容
                logging.info(f"成功開啟網址: {url}")
                return True
            else:
                logging.warning(f"頁面內容似乎為空，可能未完全載入")
                retry_count += 1
                time.sleep(2)
        except Exception as e:
            logging.error(f"開啟網址 {url} 時發生錯誤: {e}")
            retry_count += 1
            time.sleep(2)
    
    logging.error(f"無法開啟網址 {url}，已重試 {max_retries} 次")
    return False

def login(tab, username, password):
    """登入網路認證系統"""
    try:
        tab.get("https://hltchnet.tzuchi.com.tw:1003/portal?")
        
        # 檢查是否已經登入成功
        if "上網認證成功" in tab.html:
            return True
        else:
            # 等待頁面載入一段時間
            # time.sleep(2)
            
            # 嘗試獲取用戶名輸入框
            try:
                username_field = tab.ele('#ft_un', timeout=5)  # 使用id選擇器，並設置超時
                username_field.input(username)
                logging.info("成功輸入用戶名")
            except Exception as e:
                logging.error(f"無法找到用戶名輸入框: {e}")
                return False
            
            try:
                password_field = tab.ele('#ft_pd', timeout=5)  # 使用id選擇器，並設置超時
                password_field.input(password)
                logging.info("成功輸入密碼")
            except Exception as e:
                logging.error(f"無法找到密碼輸入框: {e}")
                return False
            
            # 找到提交按鈕並點擊 - 嘗試多種方法
            try:
                # 方法1: 使用value屬性
                submit_button = tab.ele('@value=登入')
                submit_button.click()
                logging.info("使用value屬性找到提交按鈕")
            except Exception as e1:
                logging.warning(f"方法1失敗: {e1}")
                try:
                    # 方法2: 嘗試使用css選擇器的父元素
                    submit_button = tab.ele('css:.fer').ele('tag:input')
                    submit_button.click()
                    logging.info("使用父元素找到提交按鈕")
                except Exception as e2:
                    logging.warning(f"方法2失敗: {e2}")
                    try:
                        # 方法3: 使用form提交
                        tab.ele('tag:form').submit()
                        logging.info("使用表單提交")
                    except Exception as e3:
                        logging.warning(f"方法3失敗: {e3}")
                        try:
                            # 方法4: 模擬Enter鍵提交
                            password_field.click(by="enter")
                            logging.info("使用Enter鍵提交表單")
                        except Exception as e4:
                            logging.error(f"所有提交方法均失敗: {e4}")
                            return False
            
            # 等待登入成功的提示出現
            # time.sleep(3)  # 使用更長的等待時間確保登入完成
            if "上網認證成功" in tab.html:
                logging.info("登入成功!")
                return True
            else:
                logging.warning("登入可能失敗，未找到成功提示")
                return False
    except Exception as e:
        logging.error(f"登入過程中發生錯誤: {e}")
        return False

def check_login_status(tab):
    """檢查是否需要登入"""
    try:
        # 檢查是否有登入表單或特定文字
        has_login_form = False
        try:
            has_login_form = bool(tab.ele('#ft_un', timeout=2)) or bool(tab.ele('#ft_pd', timeout=2))
        except:
            pass
        
        has_login_text = "花蓮慈院上網認證" in tab.html
        
        if has_login_form or has_login_text:
            logging.info("檢測到登入頁面")
            return True
        
        # 檢查是否已經成功認證
        if "上網認證成功" in tab.html:
            logging.info("已經成功認證")
            return False
        
        return False
    except Exception as e:
        logging.error(f"檢查登入狀態時發生錯誤: {e}")
        return False

def main():
    """主程序"""
    # 創建瀏覽器管理器
    browser_manager = BrowserManager()
    browser = browser_manager.init_browser(headless)
    
    if browser is None:
        logging.error("無法初始化瀏覽器，程式將退出")
        return
        
    # 獲取頁面標籤
    tab = browser.latest_tab
    
    disconnection_count = 0
    max_disconnections = 3
    
    try:
        while True:
            try:
                # 開啟測試頁面
                if open_url(tab, "https://lms.tzuchi.com.tw/tzuchi/"):
                    # 檢查是否需要登入
                    if check_login_status(tab):
                        logging.info(f"檢測到花蓮慈院上網認證頁面，嘗試登入")
                        if login(tab, username, password):
                            logging.info(f"登入成功")
                            disconnection_count = 0  # 重置斷開計數器
                        else:
                            logging.error(f"登入失敗")
                    else:
                        logging.info(f"連線成功")
                        disconnection_count = 0  # 重置斷開計數器
                else:
                    logging.warning(f"無法開啟測試頁面")
                    disconnection_count += 1
            except Exception as err:
                logging.error(f"發生錯誤 {err.__class__.__name__}: {err}")
                if "断开" in str(err) or "connection" in str(err).lower():
                    disconnection_count += 1
                    logging.warning(f"瀏覽器連接可能已斷開 (第 {disconnection_count} 次)")
            
            # 如果連續多次斷開連接，重新初始化瀏覽器
            if disconnection_count >= max_disconnections:
                logging.warning(f"連續 {disconnection_count} 次連接問題，重新初始化瀏覽器")
                try:
                    browser_manager.quit()
                except:
                    pass
                
                time.sleep(5)  # 等待更長時間以確保舊的瀏覽器完全關閉
                
                # 重新創建瀏覽器管理器
                browser_manager = BrowserManager()
                browser = browser_manager.init_browser(headless)
                
                # 檢查瀏覽器是否成功初始化
                if browser is None:
                    logging.error("重新初始化瀏覽器失敗，等待30秒後重試")
                    time.sleep(30)  # 等待較長時間後再重試
                    continue
                    
                tab = browser.latest_tab
                disconnection_count = 0
                logging.info("瀏覽器已重新初始化")
            
            # 等待下一次檢查
            time.sleep(interval)
    finally:
        browser_manager.quit()

if __name__ == "__main__":
    main()