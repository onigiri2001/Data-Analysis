from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

driver.get("https://www.bball-index.com/")
input("🔐 請在開啟的網頁中手動登入，登入後按 Enter 繼續...")

# 儲存 cookie
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
print("✅ Cookie 已儲存成功")
driver.quit()


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle
import time

options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# 必須先打開一次頁面才能加 cookie
driver.get("https://www.bball-index.com/")
time.sleep(2)

# 載入 cookie
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    if 'sameSite' in cookie:
        del cookie['sameSite']  # 避免錯誤
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print(f"⚠️ 加入 cookie 發生錯誤: {e}")

# 再次開啟登入後的頁面
driver.get("https://www.bball-index.com/team-leaderboards/")
