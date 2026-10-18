import streamlit as st
import streamlit.components.v1 as components

# ------------------------------------------------------------
# 게임 본체(index.html)를 Vercel/Netlify 에 배포한 뒤, 그 주소를 아래에 넣으세요.
# 예) https://infinite-stairs.vercel.app
# ------------------------------------------------------------
GAME_URL = "https://여기에-배포주소.vercel.app"

st.set_page_config(
    page_title="무한의 계단 - 3D 입체 계단",
    page_icon="🪜",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw !important;
            height: 100vh !important;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)

# srcdoc 가 아닌 '실제 주소'의 페이지를 iframe 으로 불러오므로 구글 로그인이 동작합니다.
components.iframe(GAME_URL, height=850)
