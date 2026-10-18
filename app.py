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

# ====================
# 後台管理區 (側邊欄)
# ====================
with st.sidebar:
    st.header("⚙️ 後台 1：名單匯入")
    raw_text = st.text_area("📋 貼上期班名單 (每行一人)", height=150)
    
    if st.button("更新名單", use_container_width=True):
        cleaned_list = [name.strip() for name in raw_text.split('\n') if name.strip()]
        # 利用 dict.fromkeys 去除重複的名字，避免同名同姓造成系統錯亂
        st.session_state.namelist = list(dict.fromkeys(cleaned_list))
        st.success(f"已成功載入 {len(st.session_state.namelist)} 人！")
        
    st.divider()
    
    # 隱藏版機率調整區塊
    st.header("🤫 後台 2：特定人士機率調整")
    st.caption("預設每個人的權重為 1。把權重調高，中獎機率就越高；設為 0 則絕對不會中。")
    
    if st.session_state.namelist:
        # 讓你可以從名單中多選出「要調整機率」的人
        special_people = st.multiselect("選擇要特別調整機率的人員", options=st.session_state.namelist)
        
        new_weights = {}
        for person in special_people:
            # 預設顯示原本設定好的權重，如果沒有設定過就是 1.0
            default_w = st.session_state.custom_weights.get(person, 1.0)
            # 使用數字輸入框讓使用者調整權重
            w = st.number_input(f"設定 {person} 的權重", min_value=0.0, value=float(default_w), step=1.0)
            new_weights[person] = w
            
        if st.button("儲存機率設定"):
            st.session_state.custom_weights = new_weights
            st.success("特殊機率設定已生效！")
    else:
        st.info("請先在上方匯入名單。")

    st.divider()
    
    st.header("🛠️ 抽獎條件設定")
    draw_count = st.number_input("🎁 這次要抽出幾個人？", min_value=1, value=1, step=1)

# ====================
# 前台抽獎區 (主畫面)
# ====================
st.header("🎁 抽獎區")
st.write(f"目前名單總人數：**{len(st.session_state.namelist)}** 人")

# 抽獎按鈕
if st.button("馬上開獎！", type="primary", use_container_width=True):
    if len(st.session_state.namelist) == 0:
        st.warning("⚠️ 請先在左側後台貼上名單！")
    elif draw_count > len(st.session_state.namelist):
        st.error("⚠️ 設定的抽出人數大於名單總人數，無法進行抽獎！")
    else:
        with st.spinner("系統隨機抽取中..."):
            time.sleep(1.5) 
            
            # 準備抽獎池與對應的權重陣列
            current_names = list(st.session_state.namelist)
            current_weights = [st.session_state.custom_weights.get(name, 1.0) for name in current_names]
            
            # 防呆機制：如果所有人的權重加起來等於 0，程式會報錯
            if sum(current_weights) <= 0:
                st.error("⚠️ 所有人的權重總和不能為 0！請回後台檢查設定。")
                st.stop()

            results = []
            # 執行抽出不放回的加權抽獎
            for _ in range(draw_count):
                # 根據權重抽出一名幸運兒
                winner = random.choices(current_names, weights=current_weights, k=1)[0]
                results.append(winner)
                
                # 將這名得獎者從名單與權重陣列中移除 (避免重複中獎)
                idx = current_names.index(winner)
                current_names.pop(idx)
                current_weights.pop(idx)
                
                # 如果剩下的人權重全部都是 0，就提早結束迴圈
                if sum(current_weights) <= 0:
                    break
                
        st.success("🎊 恭喜以下幸運兒中獎：")
        
        # 顯示中獎名單
        for i, winner in enumerate(results, 1):
            st.write(f"### 🏆 第 {i} 位：**{winner}**")
            
        st.balloons()
