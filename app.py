import streamlit as st
import random
import time
import json
import os

st.set_page_config(page_title="期班抽獎系統", page_icon="🎯")

# ====================
# 資料庫連線設定 (利用 JSON 檔案讓手機跟電腦互通資料)
# ====================
DB_FILE = "shared_data.json"

def load_data():
    """讀取臨時資料庫"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 如果還沒有檔案，回傳預設空資料
    return {"namelist": [], "custom_weights": {}}

def save_data(data):
    """寫入臨時資料庫"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 讀取當前資料
db = load_data()

# ====================
# 核心：利用網址參數切換前後台
# ====================
# 系統會檢查網址後面有沒有夾帶 ?admin=116010
params = st.query_params
is_admin = params.get("admin") == "116010"

if is_admin:
    # ----------------------------------------
    # 網頁 B：手機專屬後台 (隱藏網頁)
    # ----------------------------------------
    st.title("🤫 專屬機率調整後台")
    st.info("💡 這個頁面是獨立的，你可以存到手機裡。在台下調整機率後，台上電腦會自動同步！")
    
    if len(db["namelist"]) == 0:
        st.warning("⚠️ 請先在電腦版的主網頁匯入名單，再來這裡調整！")
    else:
        st.write(f"目前讀取到 {len(db['namelist'])} 人")
        special_people = st.multiselect("選擇要特別調整機率的人員", options=db["namelist"])
        
        new_weights = {}
        for person in special_people:
            # 讀取原本設定的值，預設是 1.0
            default_w = db["custom_weights"].get(person, 1.0)
            w = st.number_input(f"設定 {person} 的權重 (0=不中)", min_value=0.0, value=float(default_w), step=1.0)
            new_weights[person] = w
            
        if st.button("💾 儲存機率設定", type="primary", use_container_width=True):
            db["custom_weights"] = new_weights
            save_data(db) # 存進資料庫
            st.success("✅ 機率已更新！電腦版按下抽獎時會自動使用最新機率。")

else:
    # ----------------------------------------
    # 網頁 A：電腦主畫面 (給大眾看)
    # ----------------------------------------
    st.title("🎯 期班專屬抽獎系統")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 1. 匯入名單")
        raw_text = st.text_area("貼上期班名單 (每行一人)", height=150, label_visibility="collapsed")
        
        if st.button("更新名單", use_container_width=True):
            cleaned_list = [name.strip() for name in raw_text.split('\n') if name.strip()]
            db["namelist"] = list(dict.fromkeys(cleaned_list))
            save_data(db) # 把名單存進資料庫，讓手機後台能讀到
            st.success(f"已成功載入 {len(db['namelist'])} 人！")
            
    with col2:
        st.subheader("🛠️ 2. 抽獎設定")
        draw_count = st.number_input("🎁 這次要抽出幾個人？", min_value=1, value=1, step=1)
        st.write("")
        st.info(f"目前名單總人數：**{len(db['namelist'])}** 人")

    st.divider()
    
    st.header("🎁 3. 抽獎區")
    
    if st.button("馬上開獎！", type="primary", use_container_width=True):
        # 關鍵：按下按鈕的瞬間，重新讀取資料庫。
        # 這樣就算你在台下用手機剛改好機率，電腦不需重整網頁就能直接吃到最新設定！
        db = load_data() 
        
        if len(db["namelist"]) == 0:
            st.warning("⚠️ 請先在上方貼上名單並點擊更新！")
        elif draw_count > len(db["namelist"]):
            st.error("⚠️ 設定的抽出人數大於名單總人數，無法進行抽獎！")
        else:
            with st.spinner("系統隨機抽取中..."):
                time.sleep(1.5) 
                
                current_names = list(db["namelist"])
                # 套用手機設定好的機率，沒有被設定到的人就是預設 1.0
                current_weights = [db["custom_weights"].get(name, 1.0) for name in current_names]
                
                if sum(current_weights) <= 0:
                    st.error("⚠️ 所有人的權重總和不能為 0！")
                    st.stop()

                results = []
                for _ in range(draw_count):
                    winner = random.choices(current_names, weights=current_weights, k=1)[0]
                    results.append(winner)
                    
                    idx = current_names.index(winner)
                    current_names.pop(idx)
                    current_weights.pop(idx)
                    
                    if sum(current_weights) <= 0:
                        break
                    
            st.success("🎊 恭喜以下幸運兒中獎：")
            
            for i, winner in enumerate(results, 1):
                st.write(f"### 🏆 第 {i} 位：**{winner}**")
                
            st.balloons()
