import streamlit as st
import random
import time

st.set_page_config(page_title="期班抽獎系統", page_icon="🎯")

st.title("🎯 期班專屬抽獎系統")

# 初始化 Session State
if 'namelist' not in st.session_state:
    st.session_state.namelist = []
if 'custom_weights' not in st.session_state:
    st.session_state.custom_weights = {}
if 'draw_count' not in st.session_state:
    st.session_state.draw_count = 1

# ====================
# 後台管理區 (側邊欄 - 密碼鎖定)
# ====================
with st.sidebar:
    st.header("🔒 後台解鎖")
    # 使用 type="password" 讓輸入的文字變成點點點
    admin_password = st.text_input("輸入管理員密碼", type="password")
    
    # 密碼驗證 (你可以把 cafa116010 改成你想要的密碼)
    if admin_password == "cafa116010":
        st.success("✅ 後台已解鎖！")
        st.divider()
        
        st.header("⚙️ 後台 1：名單匯入")
        raw_text = st.text_area("📋 貼上期班名單 (每行一人)", height=150)
        
        if st.button("更新名單", use_container_width=True):
            cleaned_list = [name.strip() for name in raw_text.split('\n') if name.strip()]
            st.session_state.namelist = list(dict.fromkeys(cleaned_list))
            st.success(f"已成功載入 {len(st.session_state.namelist)} 人！")
            
        st.divider()
        
        st.header("🤫 後台 2：特定人士機率調整")
        if st.session_state.namelist:
            special_people = st.multiselect("選擇要特別調整機率的人員", options=st.session_state.namelist)
            
            new_weights = {}
            for person in special_people:
                default_w = st.session_state.custom_weights.get(person, 1.0)
                w = st.number_input(f"設定 {person} 的權重", min_value=0.0, value=float(default_w), step=1.0)
                new_weights[person] = w
                
            if st.button("儲存機率設定"):
                st.session_state.custom_weights = new_weights
                st.success("特殊機率設定已生效！")
        else:
            st.info("請先在上方匯入名單。")

        st.divider()
        
        st.header("🛠️ 抽獎條件設定")
        # 更新抽出人數並存入 session_state
        new_draw_count = st.number_input("🎁 這次要抽出幾個人？", min_value=1, value=st.session_state.draw_count, step=1)
        st.session_state.draw_count = new_draw_count

    elif admin_password != "":
        st.error("❌ 密碼錯誤！")

# ====================
# 前台抽獎區 (主畫面)
# ====================
st.header("🎁 抽獎區")
st.write(f"目前名單總人數：**{len(st.session_state.namelist)}** 人")
st.write(f"本次預計抽出：**{st.session_state.draw_count}** 人")

# 抽獎按鈕
if st.button("馬上開獎！", type="primary", use_container_width=True):
    if len(st.session_state.namelist) == 0:
        st.warning("⚠️ 目前沒有名單！請管理員先解鎖左側後台匯入。")
    elif st.session_state.draw_count > len(st.session_state.namelist):
        st.error("⚠️ 設定的抽出人數大於名單總人數，無法進行抽獎！")
    else:
        with st.spinner("系統隨機抽取中..."):
            time.sleep(1.5) 
            
            current_names = list(st.session_state.namelist)
            current_weights = [st.session_state.custom_weights.get(name, 1.0) for name in current_names]
            
            if sum(current_weights) <= 0:
                st.error("⚠️ 所有人的權重總和不能為 0！請回後台檢查設定。")
                st.stop()

            results = []
            for _ in range(st.session_state.draw_count):
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
