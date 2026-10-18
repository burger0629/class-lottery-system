import streamlit as st
import random
import time

# 設定網頁標題與排版
st.set_page_config(page_title="抽獎系統", page_icon="🎯", layout="centered")

# 初始化所有的系統記憶
if 'namelist' not in st.session_state:
    st.session_state.namelist = []
if 'custom_weights' not in st.session_state:
    st.session_state.custom_weights = {}
if 'page_mode' not in st.session_state:
    st.session_state.page_mode = "main" # 用來控制目前顯示哪個畫面

# ====================
# 側邊欄：隱藏的畫面切換器
# ====================
with st.sidebar:
    st.caption("系統設定區")
    # 隱藏密碼鎖 (輸入 cafa116010 才會出現切換按鈕)
    admin_pwd = st.text_input("輸入工程代碼", type="password")
    
    if admin_pwd == "cafa116010":
        st.divider()
        if st.session_state.page_mode == "main":
            if st.button("前往調整頁面 ", type="primary", use_container_width=True):
                st.session_state.page_mode = "admin"
                st.rerun() # 重新刷新畫面
        else:
            if st.button("返回抽獎主畫面 ⬅️", type="primary", use_container_width=True):
                st.session_state.page_mode = "main"
                st.rerun()

# ====================
# 畫面 B：機率調整專屬頁面 (完全獨立顯示)
# ====================
if st.session_state.page_mode == "admin":
    st.title("調整後台")
    st.info("此頁面完全獨立於主畫面。設定完畢後，請點擊左側按鈕「返回抽獎主畫面」。")
    
    if len(st.session_state.namelist) == 0:
        st.warning("⚠️ 請先在主畫面匯入名單，系統才有資料可以調整機率！")
    else:
        special_people = st.multiselect("選擇要調整的人員", options=st.session_state.namelist)
        
        new_weights = {}
        for person in special_people:
            # 讀取現有權重，預設為 1.0
            default_w = st.session_state.custom_weights.get(person, 1.0)
            w = st.number_input(f"設定 {person} 的權重 (數字越大越容易中，0為絕對不中)", 
                                min_value=0.0, value=float(default_w), step=1.0)
            new_weights[person] = w
            
        if st.button("💾 儲存機率設定"):
            st.session_state.custom_weights = new_weights
            st.success("✅ 特殊機率設定已生效！您可以切換回主畫面了。")

# ====================
# 畫面 A：正常的抽獎主網頁
# ====================
elif st.session_state.page_mode == "main":
    st.title("🎯 期班專屬抽獎系統")
    
    # 上半部：將名單匯入與人數設定並排顯示
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 1. 匯入名單")
        raw_text = st.text_area("貼上期班名單 (每行一人)", height=150, label_visibility="collapsed")
        if st.button("更新名單", use_container_width=True):
            # 清除空白並去除重複名稱
            cleaned_list = [name.strip() for name in raw_text.split('\n') if name.strip()]
            st.session_state.namelist = list(dict.fromkeys(cleaned_list))
            st.success(f"已成功載入 {len(st.session_state.namelist)} 人！")
            
    with col2:
        st.subheader("🛠️ 2. 抽獎設定")
        draw_count = st.number_input("🎁 這次要抽出幾個人？", min_value=1, value=1, step=1)
        st.write("")
        st.info(f"目前名單總人數：**{len(st.session_state.namelist)}** 人")

    st.divider()
    
    # 下半部：乾淨的抽獎區
    st.header("🎁 3. 抽獎區")
    
    if st.button("馬上開獎！", type="primary", use_container_width=True):
        if len(st.session_state.namelist) == 0:
            st.warning("⚠️ 請先在上方貼上名單並點擊更新！")
        elif draw_count > len(st.session_state.namelist):
            st.error("⚠️ 設定的抽出人數大於名單總人數，無法進行抽獎！")
        else:
            with st.spinner("系統隨機抽取中..."):
                time.sleep(1.5) 
                
                current_names = list(st.session_state.namelist)
                current_weights = [st.session_state.custom_weights.get(name, 1.0) for name in current_names]
                
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
