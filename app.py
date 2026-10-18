import streamlit as st
import random
import time

st.set_page_config(page_title="期班抽獎系統", page_icon="🎯")

st.title("🎯 期班專屬抽獎系統")

# 初始化 Session State (確保切換畫面時資料不會不見)
if 'namelist' not in st.session_state:
    st.session_state.namelist = []

# ====================
# 後台管理區 (側邊欄)
# ====================
with st.sidebar:
    st.header("⚙️ 後台：名單與設定")
    
    # 讓使用者可以從 Excel 複製貼上近 200 人的名單
    raw_text = st.text_area("📋 貼上期班名單 (每行一人)", height=300, 
                            help="可以直接從 Excel 複製名單貼上，系統會自動過濾空白行")
    
    if st.button("更新名單", use_container_width=True):
        # 處理空白行與換行符號
        cleaned_list = [name.strip() for name in raw_text.split('\n') if name.strip()]
        st.session_state.namelist = cleaned_list
        st.success(f"已成功載入 {len(st.session_state.namelist)} 人！")
        
    st.divider()
    
    # 抽獎設定
    st.subheader("🛠️ 抽獎條件設定")
    draw_count = st.number_input("🎁 這次要抽出幾個人？", min_value=1, value=1, step=1)
    
    # 是否允許同一個人重複中獎 (預設為不允許)
    allow_duplicate = st.checkbox("允許重複中獎 (抽出放回)", value=False)

# ====================
# 前台抽獎區 (主畫面)
# ====================
st.header("🎁 抽獎區")
st.write(f"目前名單總人數：**{len(st.session_state.namelist)}** 人")

# 抽獎按鈕
if st.button("馬上開獎！", type="primary", use_container_width=True):
    if len(st.session_state.namelist) == 0:
        st.warning("⚠️ 請先在左側後台貼上名單，並點擊「更新名單」！")
    elif not allow_duplicate and draw_count > len(st.session_state.namelist):
        st.error("⚠️ 設定的抽出人數大於名單總人數，無法進行抽獎！")
    else:
        with st.spinner("系統隨機抽取中..."):
            time.sleep(1.5) # 模擬抽獎的懸念感
            
            if allow_duplicate:
                # 允許重複 (抽出放回)：使用 random.choices
                results = random.choices(st.session_state.namelist, k=draw_count)
            else:
                # 不允許重複 (抽出不放回)：使用 random.sample
                results = random.sample(st.session_state.namelist, k=draw_count)
                
        st.success("🎊 恭喜以下幸運兒中獎：")
        
        # 顯示中獎名單
        for i, winner in enumerate(results, 1):
            st.write(f"### 🏆 第 {i} 位：**{winner}**")
            
        st.balloons() # 釋放慶祝氣球動畫
