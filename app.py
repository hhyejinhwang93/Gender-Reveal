import streamlit as st
import datetime

# Page configuration
st.set_page_config(page_title="Our Little Baby Reveal", page_icon="🍼", layout="centered")

# Language Dictionary
translations = {
    "English": {
        "title": "🍼 Our Little Baby Reveal",
        "date_banner": "The Big Reveal Date: November 9th, 2026",
        "countdown": "⏳ Countdown to November 9, 2026 - Voting is open!",
        "guest_tab": "🎈 Guest Voting Page",
        "name": "Your Name",
        "vote": "What do you think it is?",
        "boy": "Team Boy 💙",
        "girl": "Team Girl 🩷",
        "submit": "Submit Vote 💌",
        "host_tab": "🔒 Host Dashboard",
        "event_name": "Event Name",
        "save": "Save Settings"
    },
    "Korean (한국어)": {
        "title": "🍼 우리 아기 성별 공개",
        "date_banner": "성별 공개일: 2026년 11월 9일",
        "countdown": "⏳ 2026년 11월 9일 카운트다운 - 투표 진행 중!",
        "guest_tab": "🎈 하객 투표 페이지",
        "name": "성함",
        "vote": "어떤 성별일 것 같나요?",
        "boy": "청순 왕자님 (Team Boy) 💙",
        "girl": "사랑 공주님 (Team Girl) 🩷",
        "submit": "투표 제출하기 💌",
        "host_tab": "🔒 주최자 대시보드",
        "event_name": "이벤트 이름",
        "save": "설정 저장"
    },
    "Traditional Chinese (繁體中文)": {
        "title": "🍼 我們的小寶貝性別揭曉",
        "date_banner": "揭曉日期：2026年11月9日",
        "countdown": "⏳ 距離 2026年11月9日 倒數計時 - 投票開放中！",
        "guest_tab": "🎈 賓客投票頁面",
        "name": "您的姓名",
        "vote": "您覺得是哪一個？",
        "boy": "男寶隊 (Team Boy) 💙",
        "girl": "女寶隊 (Team Girl) 🩷",
        "submit": "提交投票 💌",
        "host_tab": "🔒 主辦人控制面板",
        "event_name": "活動名稱",
        "save": "儲存設定"
    }
}

# Language Selector Sidebar / Top
lang = st.selectbox("🌐 Choose Language / 언어 / 語言", ["English", "Korean (한국어)", "Traditional Chinese (繁體中文)"])
t = translations[lang]

st.title(t["title"])
st.markdown(f"<h4 style='color: #e87a90; text-align: center;'>{t['date_banner']}</h4>", unsafe_allow_html=True)
st.info(t["countdown"])

tab1, tab2 = st.tabs([t["guest_tab"], t["host_tab"]])

with tab1:
    st.subheader(t["guest_tab"])
    guest_name = st.text_input(t["name"])
    guest_vote = st.radio(t["vote"], [t["boy"], t["girl"]])
    if st.button(t["submit"]):
        if guest_name:
            st.success(f"💖 Thank you {guest_name}! Your vote has been recorded.")
        else:
            st.error("Please enter your name.")

with tab2:
    st.subheader(t["host_tab"])
    st.text_input(t["event_name"], "Our Little Baby Reveal")
    st.date_input("Reveal Date", datetime.date(2026, 11, 9))
    if st.button(t["save"]):
        st.success("Event settings saved successfully!")
