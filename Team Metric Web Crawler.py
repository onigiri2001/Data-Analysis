# 🏀 改良版 BBall Index Metrics 爬蟲
import os
import pickle
import time
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# === 設定 ===
YR_START, YR_END = 2025, 2014
BATCH_SIZE = 5
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === 你的隊伍名順序 ===
TEAM_ORDER = [
    "ATL", "BOS", "BRK", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM",
    "MIA", "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
]

# === 匯入 metrics 清單（完整 193 項） ===
metric_list = [
    "3PT Shot Making", "3PT Shooting Talent", "3PT Shot Creation", "3PT Shot Making Efficiency", "3PT Shot Quality",
    "Assisted Shot Making", "Assisted Shooting Talent", "Assisted Shot Making Efficiency", "Assisted Shot Quality", "Assisted FG%",
    "Assisted Padded FG%", "C&S 3PT Shot Making", "C&S 3PT Shooting Talent", "C&S 3PT Shot Making Efficiency", "C&S 3PT Shot Quality",
    "C&S 3PT FG%", "C&S 3PT Padded FG%", "Deep 3PT Shot Making", "Deep 3PT Shooting Talent", "Deep 3PT Shot Creation",
    "Deep 3PT Shot Making Efficiency", "Deep 3PT Shot Quality", "Deep 3PT FG%", "Deep 3PT Padded FG%", "Rim Shot Making",
    "Rim Shooting Talent", "Rim Shot Creation", "Floater Shot Making", "Floater Shooting Talent", "Floater Shot Creation",
    "Floater Shot Making Efficiency", "Floater Shot Quality", "Floater FG%", "Floater Padded FG%", "Halfcourt Shot Making",
    "Halfcourt Shooting Talent", "Halfcourt Shot Creation", "Halfcourt Shot Making Efficiency", "Halfcourt Shot Quality", "Halfcourt FG%",
    "Halfcourt Padded FG%", "Midrange Shot Making", "Midrange Shooting Talent", "Midrange Shot Creation", "Midrange Shot Making Efficiency", "Midrange Shot Quality",
    "Midrange FG%", "Midrange Padded FG%", "Off Screen Points", "Off Screen Possessions", "Off Screen 2FGM", "Off Screen 2FGA",
    "Off Screen 3FGM", "Off Screen 3FGA", "Off Screen Turnovers", "Off Screen FT Trips", "Off Screen SF Drawn", "Overall Shot Making",
    "Overall Shooting Talent", "Overall Shot Creation", "Overall Shot Making Efficiency", "Overall Shot Quality", "Pullup 3PT Shot Making",
    "Pullup 3PT Shooting Talent", "Pullup 3PT Shot Creation", "Pullup 3PT Shot Making Efficiency", "Pullup 3PT Shot Quality", "Pullup 3PT FG%",
    "Pullup 3PT Padded FG%", "Self-Created Shot Making", "Self-Created Shooting Talent", "Self-Created Shot Making Efficiency", "Self-Created Shot Quality",
    "Self-Created FG%", "Self-Created Padded FG%", "Transition Shot Making", "Transition Shooting Talent", "Transition Shot Creation",
    "Transition Shot Making Efficiency", "Transition Shot Quality", "Transition FG%", "Transition Padded FG%", "Handoff PPP",
    "Isolation PPP", "PnR Ball Handler PPP", "PnR Roll Man PPP", "Post Up PPP", "Spot Up PPP", "Off Screen PPP",
    "Cut PPP", "Putback PPP", "Transition PPP", "Misc PPP", "Handoff Defense PPP", "Isolation Defense PPP",
    "PnR Ball Handler Defense PPP", "PnR Roll Man Defense PPP", "Post Up Defense PPP", "Spot Up Defense PPP", "Off Screen Defense PPP",
    "Handoff Turnover%", "Isolation Turnover%", "PnR Ball Handler Turnover%", "PnR Roll Man Turnover%", "Post Up Turnover%",
    "Spot Up Turnover%", "Off Screen Turnover%", "Cut Turnover%", "Putback Turnover%", "Transition Turnover%", "Misc Turnover%",
    "Handoff Defense Turnover%", "Isolation Defense Turnover%", "PnR Ball Handler Defense Turnover%", "PnR Roll Man Defense Turnover%",
    "Post Up Defense Turnover%", "Spot Up Defense Turnover%", "Off Screen Defense Turnover%", "Age", "Height", "Weight",
    "Years of Experience", "Defensive Positional Versatility", "Defensive Role Versatility", "% of Minutes in Foul Trouble",
    "Fouls Committed / 75", "Fouls Drawn / 75", "Matchup Difficulty", "Stable Handoff PPP", "Stable P&R Ball Handler PPP",
    "Stable Putbacks PPP", "Stable Spot Up PPP", "Stable Transition PPP", "Drives Per 75 Possessions", "Rim Shot Attempts Per 75 Possessions",
    "Unassisted Rim Shot Attempts Per 75 Possessions", "Percentage of Shots at Rim Contested", "Block Rate on Contests",
    "Rim Contests Per 75 Possessions", "Rim Deterrence", "Rim Points Saved Per 75 Possessions", "Rim dFG% vs Expected",
    "Cuts Per 75 Possessions", "Movement Attack Rate", "Movement Distance Rating", "Movement Scoring Impact Per 75 Possessions",
    "Movement Points Per 75 Possessions", "Movement Speed Rating", "Off-Ball Screen Possessions Per 75 Possessions",
    "Putback Scoring Impact Per 75 Possessions", "Putback per Offensive Rebound", "Putbacks Per 75 Possessions",
    "Total Isolation Impact Per 75 Possessions", "Total Isolations Per 75 Possessions", "Defensive Miles Per 75 Possessions",
    "Deflections Per 75 Possessions", "Matchup Adjusted Defensive Feet Per Minute", "Passing Lane Defense", "Pickpocket Rating",
    "BPM LA-RAPM", "Clutch WPA", "D-BPM LA-RAPM", "D-DPM", "D-DRIP", "D-LEBRON", "D-LEBRON Box Impact", "DPM", "DRIP",
    "Defensive Impact Luck", "LEBRON", "LEBRON Box Impact", "LEBRON Defensive Points Saved", "LEBRON Offensive Points Added",
    "LEBRON WAR", "Multi-Year LEBRON", "O-BPM LA-RAPM", "O-DPM", "O-DRIP", "O-LEBRON", "O-LEBRON Box Impact",
    "Offensive Impact Luck", "Stable On-Court DRtg", "Stable On-Court Net Rating", "Stable On-Court ORtg", "Time Decay LA-RAPM",
    "Time Decay RAPM", "Total Impact Luck", "Win Probability Added", "delta DRIP", "Box Creation",
    "High Value Assists Per 75 Possessions", "Potential Assists Per 100 Passes", "Role-Adjusted Potential Assists Per 100 Passes",
    "Roll Man Poss Per 75 Possessions", "Screen Assists Per 75 Possessions", "Roll Man Impact Per 75 Possessions"
]

# 分批
metric_batches = [metric_list[i:i+BATCH_SIZE] for i in range(0, len(metric_list), BATCH_SIZE)]

# === 初始化 Chrome ===
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# === 載入 cookie 並登入 ===
driver.get("https://www.bball-index.com/")
time.sleep(2)
with open("cookies.pkl", "rb") as f:
    cookies = pickle.load(f)
    for cookie in cookies:
        cookie.pop("sameSite", None)
        try:
            driver.add_cookie(cookie)
        except:
            pass

# 開啟主頁面
driver.get("https://www.bball-index.com/team-leaderboards/")
time.sleep(2)
driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[1])
print("✅ 成功切入 Shiny App iframe")

# 點選 Team Leaderboards tab
tab = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Team Leaderboards']/..")))
driver.execute_script("arguments[0].click();", tab)
print("✅ 成功點選 Team Leaderboards tab")

# === 爬蟲主程式 ===
for year in range(YR_START, YR_END - 1, -1):
    print(f"📅 開始擷取 {year} 年資料...")
    all_data = []  # 🔧 每年都要重置這個 list，不然會報錯！
    print("✅ all_data 已初始化")

    try:
        print(f"📅 正在切換年份：{year}")

        # ✅ 改用 selectize 的 setValue 選年分
        driver.execute_script(f'''
              var select = $('#Years')[0];
              var selectize = select.selectize;
              selectize.setValue("{year}");
            ''')
        time.sleep(1.5)  # 確保年份變更後頁面刷新

        driver.find_element(By.ID, "make_table").click()
        print("🚀 已點擊 Run Query")

        # ✅ 等待表格載入完成
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable")))
        print("📊 資料表格已載入！")

        # TODO：擷取表格、存成 Excel，接在這

    except Exception as e:
        print(f"❌ {year} 年處理失敗：{e}")
        continue

    for batch in metric_batches:
        try:
            # 開啟 metrics 選單
            driver.execute_script('$("#Metric")[0].selectize.open();')
            time.sleep(1)

            # 設定一批 metric
            values_str = '\", \"'.join(batch)
            driver.execute_script(f'''
                var sel = $("#Metric")[0].selectize;
                sel.clear();
                ["{values_str}"].forEach(v => sel.addItem(v));
            ''')

            # 點選 Run Query
            driver.find_element(By.ID, "make_table").click()
            time.sleep(4)

            # 點選 Team 排序按鈕（確保隊伍順序正確）
            team_header = wait.until(EC.element_to_be_clickable((By.XPATH, "//th[contains(., 'Team')]")))
            team_header.click()
            time.sleep(1)

            # 取得表格
            table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable")))
            html = table.get_attribute("outerHTML")
            df = pd.read_html(StringIO(html))[0]

            # 去掉第一欄數字 + Season 欄 + 用隊名對齊
            df = df.drop(columns=[df.columns[0], "Season"], errors="ignore")
            df.set_index("Team", inplace=True)
            df = df.reindex(TEAM_ORDER)
            all_data.append(df)
            print(f"✅ 擷取 {batch[0]} 等 {len(batch)} 個 metrics，共 {df.shape[1]} 欄")

        except Exception as e:
            print(f"⚠️ 擷取失敗：{e}")
            continue

    if all_data:
        final_df = pd.concat(all_data, axis=1)
        final_df.insert(0, "Team", TEAM_ORDER)
        final_df.to_csv(f"{OUTPUT_DIR}/{year}_metrics.csv", index=False)
        print(f"💾 {year} 年資料儲存成功，共 {final_df.shape[1]} 欄")
    else:
        print(f"❌ {year} 無資料儲存")

print("🎉 所有年度資料爬取完成！")
