"""
The Architect — 운명 챗봇
전생 리딩 · 운명 키워드 · 오늘의 설계도
"""

import streamlit as st
import anthropic
from datetime import datetime, date
from prompts import (
    get_prompt, CREDIT_COSTS, MODE_NAMES, MODE_DESCRIPTIONS, UPSELL_MESSAGE
)

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="The Architect — 운명 챗봇",
    page_icon="◈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 커스텀 CSS — 다크 테마 + The Architect 브랜딩
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Cormorant+Garamond:wght@400;600;700&display=swap');

/* 전체 배경 */
.stApp {
    background: linear-gradient(180deg, #08061A 0%, #0d0a24 50%, #120e2e 100%);
    color: #d4c5e8;
}

/* 사이드바 숨기기 */
[data-testid="stSidebar"] { display: none; }

/* 헤더 숨기기 */
header[data-testid="stHeader"] {
    background: transparent;
}

/* 메인 컨테이너 */
.block-container {
    padding-top: 2rem;
    max-width: 720px;
}

/* 타이틀 스타일 */
h1 {
    font-family: 'Cormorant Garamond', serif !important;
    color: #C5A0F0 !important;
    text-align: center;
    font-weight: 600 !important;
    letter-spacing: 3px;
}

h2, h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: #A78BDB !important;
}

/* 일반 텍스트 */
p, li, .stMarkdown {
    font-family: 'Noto Sans KR', sans-serif;
    color: #d4c5e8;
}

/* 버튼 스타일 */
.stButton > button {
    background: linear-gradient(135deg, #2d1b4e 0%, #1a0e33 100%);
    border: 1px solid #A78BDB44;
    color: #C5A0F0;
    font-family: 'Noto Sans KR', sans-serif;
    font-weight: 500;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    transition: all 0.3s;
    width: 100%;
}
.stButton > button:hover {
    border-color: #C5A0F0;
    background: linear-gradient(135deg, #3d2560 0%, #2a1845 100%);
    color: #e0d0f5;
}

/* 인풋 스타일 */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: #0d0a24 !important;
    border: 1px solid #A78BDB33 !important;
    color: #d4c5e8 !important;
    font-family: 'Noto Sans KR', sans-serif;
    border-radius: 8px;
}

/* 라디오 버튼 */
.stRadio > div {
    background: transparent;
}
.stRadio label {
    color: #d4c5e8 !important;
}

/* 채팅 메시지 */
[data-testid="stChatMessage"] {
    background: #0d0a2488;
    border: 1px solid #A78BDB15;
    border-radius: 12px;
    padding: 1rem;
}

/* 채팅 입력 */
[data-testid="stChatInput"] textarea {
    background: #0d0a24 !important;
    border: 1px solid #A78BDB33 !important;
    color: #d4c5e8 !important;
}

/* 크레딧 배지 */
.credit-badge {
    background: linear-gradient(135deg, #2d1b4e, #1a0e33);
    border: 1px solid #C5A0F044;
    border-radius: 20px;
    padding: 6px 16px;
    display: inline-block;
    font-size: 14px;
    color: #C5A0F0;
    font-family: 'Noto Sans KR', sans-serif;
}

/* 모드 카드 */
.mode-card {
    background: linear-gradient(135deg, #13102a 0%, #0d0a24 100%);
    border: 1px solid #A78BDB22;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    transition: all 0.3s;
}
.mode-card:hover {
    border-color: #C5A0F066;
}
.mode-card h4 {
    color: #C5A0F0;
    font-family: 'Cormorant Garamond', serif;
    margin: 0 0 8px 0;
    font-size: 1.2rem;
}
.mode-card p {
    color: #a090b8;
    font-size: 0.9rem;
    margin: 0;
}

/* 구분선 */
hr {
    border-color: #A78BDB22;
}

/* 운명책 업셀 박스 */
.upsell-box {
    background: linear-gradient(135deg, #1a0e33, #2d1b4e);
    border: 1px solid #C5A0F033;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.upsell-box a {
    color: #C5A0F0 !important;
    text-decoration: none;
    font-weight: 600;
}

/* 로고/심볼 */
.architect-symbol {
    text-align: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.5rem;
    color: #C5A0F0;
    opacity: 0.8;
    margin: 1rem 0;
    letter-spacing: 5px;
}

/* Expander */
.streamlit-expanderHeader {
    background: #13102a !important;
    border: 1px solid #A78BDB22 !important;
    color: #C5A0F0 !important;
}

/* 워닝/인포 숨기기 */
.stAlert { display: none; }

/* 스피너 */
.stSpinner > div {
    border-top-color: #C5A0F0 !important;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #0d0a24;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #a090b8;
    border-radius: 6px;
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: #2d1b4e !important;
    color: #C5A0F0 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
if "credits" not in st.session_state:
    st.session_state.credits = 3  # 무료 크레딧

if "user_data" not in st.session_state:
    st.session_state.user_data = None

if "current_mode" not in st.session_state:
    st.session_state.current_mode = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "readings_done" not in st.session_state:
    st.session_state.readings_done = 0

if "last_reading" not in st.session_state:
    st.session_state.last_reading = ""

if "page" not in st.session_state:
    st.session_state.page = "intro"


# ─────────────────────────────────────────────
# Claude API 호출
# ─────────────────────────────────────────────
def call_claude(system_prompt: str, user_prompt: str) -> str:
    """Claude API 호출 — 스트리밍"""
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
    except Exception as e:
        return f"연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요.\n\n(Error: {str(e)[:100]})"


def stream_claude(system_prompt: str, user_prompt: str):
    """Claude API 스트리밍 호출"""
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception as e:
        yield f"연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요."


# ─────────────────────────────────────────────
# 크레딧 표시
# ─────────────────────────────────────────────
def show_credits():
    credits = st.session_state.credits
    if credits > 0:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<span class="credit-badge">◈ 크레딧: {credits}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<span class="credit-badge" style="border-color:#ff6b6b44;color:#ff6b6b;">◈ 크레딧: 0</span>'
            f'</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# 페이지: 인트로
# ─────────────────────────────────────────────
def page_intro():
    st.markdown('<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown("# The Architect")
    st.markdown(
        '<p style="text-align:center; color:#a090b8; font-size:15px; letter-spacing:2px;">'
        '운명의 설계를 읽는 자'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<p style="text-align:center; color:#d4c5e8; font-size:15px; line-height:1.8;">'
        '당신의 출생 데이터에는 설계 논리가 담겨 있다.<br>'
        '사주명리, 점성학, 수비학, 인간디자인 — 열두 체계가 읽는 당신의 밑그림.<br><br>'
        '세 가지를 볼 수 있다.'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # 3개 모드 카드
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="mode-card">'
            '<h4>전생 리딩</h4>'
            '<p>당신의 전생 — 시대, 역할, 이번 생에 가져온 것</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="mode-card">'
            '<h4>운명 키워드</h4>'
            '<p>본질, 무기, 함정 — 세 개의 키워드로 압축</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="mode-card">'
            '<h4>오늘의 설계도</h4>'
            '<p>오늘 하루의 에너지 흐름 — 밀 때와 빠질 때</p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("")
    st.markdown(
        '<p style="text-align:center; color:#a090b8; font-size:13px;">'
        '무료 크레딧 3개 제공 · 각 리딩 1크레딧'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("")
    if st.button("시작하기", use_container_width=True):
        st.session_state.page = "input"
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center; color:#A78BDB55; font-size:12px; letter-spacing:3px;">'
        'POWERED BY THE ARCHITECT'
        '</p>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────
# 페이지: 출생 정보 입력
# ─────────────────────────────────────────────
def page_input():
    show_credits()

    st.markdown('<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown("# 출생 정보")
    st.markdown(
        '<p style="text-align:center; color:#a090b8; font-size:14px;">'
        '당신의 밑그림을 읽기 위해 필요합니다'
        '</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")

    with st.form("birth_info"):
        name = st.text_input("이름 (한글 또는 영문)", placeholder="홍길동")

        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input(
                "생년월일",
                value=date(1990, 1, 1),
                min_value=date(1940, 1, 1),
                max_value=date(2010, 12, 31),
            )
        with col2:
            birth_time = st.text_input(
                "출생시간 (모르면 '모름' 입력)",
                placeholder="14:30 또는 오후 2시 30분",
            )

        gender = st.radio(
            "성별",
            options=["남성", "여성"],
            horizontal=True,
        )

        submitted = st.form_submit_button("설계도 열기", use_container_width=True)

        if submitted:
            if not name:
                st.error("이름을 입력해주세요.")
            elif not birth_time:
                st.error("출생시간을 입력해주세요. 모르면 '모름'이라고 적어주세요.")
            else:
                st.session_state.user_data = {
                    "name": name,
                    "birth_date": birth_date.strftime("%Y년 %m월 %d일"),
                    "birth_time": birth_time,
                    "gender": gender,
                    "today": datetime.now().strftime("%Y년 %m월 %d일 %A"),
                }
                st.session_state.page = "select_mode"
                st.rerun()


# ─────────────────────────────────────────────
# 페이지: 모드 선택
# ─────────────────────────────────────────────
def page_select_mode():
    show_credits()

    user = st.session_state.user_data
    st.markdown(f'<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown(f"### {user['name']}의 설계도")
    st.markdown("---")

    st.markdown(
        '<p style="color:#d4c5e8; font-size:15px; text-align:center;">'
        '무엇을 읽을까?'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔮\n전생 리딩", use_container_width=True):
            if st.session_state.credits >= 1:
                st.session_state.current_mode = "past_life"
                st.session_state.page = "reading"
                st.rerun()
            else:
                st.session_state.page = "no_credits"
                st.rerun()

    with col2:
        if st.button("◈\n운명 키워드", use_container_width=True):
            if st.session_state.credits >= 1:
                st.session_state.current_mode = "keywords"
                st.session_state.page = "reading"
                st.rerun()
            else:
                st.session_state.page = "no_credits"
                st.rerun()

    with col3:
        if st.button("☀\n오늘의 설계도", use_container_width=True):
            if st.session_state.credits >= 1:
                st.session_state.current_mode = "daily"
                st.session_state.page = "reading"
                st.rerun()
            else:
                st.session_state.page = "no_credits"
                st.rerun()

    # 리딩 히스토리 표시
    if st.session_state.readings_done > 0:
        st.markdown("---")
        st.markdown(
            f'<p style="color:#a090b8; font-size:13px; text-align:center;">'
            f'지금까지 {st.session_state.readings_done}회 리딩 완료'
            f'</p>',
            unsafe_allow_html=True
        )

    # 5회 이상 리딩 시 운명책 업셀
    if st.session_state.readings_done >= 3:
        st.markdown("---")
        st.markdown(
            '<div class="upsell-box">'
            '<p style="color:#C5A0F0; font-size:14px; margin-bottom:8px;">여기서 읽은 건 밑그림의 밑그림이다.</p>'
            '<p style="color:#a090b8; font-size:13px; margin-bottom:12px;">'
            '열두 체계 전체를 한 권에 — 운명책'
            '</p>'
            '<a href="https://destiny-book.streamlit.app" target="_blank" '
            'style="color:#C5A0F0; font-size:15px; font-weight:600;">운명책 알아보기 →</a>'
            '</div>',
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────────
# 페이지: 리딩 실행 (챗봇 인터페이스)
# ─────────────────────────────────────────────
def page_reading():
    show_credits()

    mode = st.session_state.current_mode
    user = st.session_state.user_data

    st.markdown(f"### ◈ {MODE_NAMES[mode]}")
    st.markdown(f"*{user['name']} · {user['birth_date']}*")
    st.markdown("---")

    # 채팅 히스토리 표시
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🔮" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    # 첫 리딩이면 자동 실행
    if not st.session_state.chat_history:
        # 크레딧 차감
        st.session_state.credits -= CREDIT_COSTS[mode]
        st.session_state.readings_done += 1

        system_prompt, user_prompt = get_prompt(mode, user)

        with st.chat_message("assistant", avatar="🔮"):
            response_placeholder = st.empty()
            full_response = ""

            with st.spinner("설계도를 읽는 중..."):
                for chunk in stream_claude(system_prompt, user_prompt):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response
        })
        st.session_state.last_reading = full_response
        st.rerun()

    # 심화 질문 입력
    if question := st.chat_input("더 궁금한 게 있어? (심화 분석 1크레딧)"):
        # 유저 메시지 표시
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # 크레딧 체크
        if st.session_state.credits < 1:
            no_credit_msg = (
                "크레딧이 부족하다.\n\n"
                "충전하거나, 열두 체계 전체를 한 권에 담은 "
                "[운명책](https://destiny-book.streamlit.app)을 확인해봐."
            )
            with st.chat_message("assistant", avatar="🔮"):
                st.markdown(no_credit_msg)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": no_credit_msg
            })
        else:
            # 심화 분석 실행
            st.session_state.credits -= 1
            st.session_state.readings_done += 1

            system_prompt, user_prompt = get_prompt(
                "deep_dive",
                user,
                previous_reading=st.session_state.last_reading,
                question=question,
            )

            with st.chat_message("assistant", avatar="🔮"):
                response_placeholder = st.empty()
                full_response = ""

                with st.spinner("더 깊이 읽는 중..."):
                    for chunk in stream_claude(system_prompt, user_prompt):
                        full_response += chunk
                        response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_response
            })
            st.session_state.last_reading = full_response

        st.rerun()

    # 하단 네비게이션
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 다른 리딩 선택", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_mode = None
            st.session_state.page = "select_mode"
            st.rerun()
    with col2:
        if st.button("처음으로", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_mode = None
            st.session_state.page = "intro"
            st.rerun()


# ─────────────────────────────────────────────
# 페이지: 크레딧 부족
# ─────────────────────────────────────────────
def page_no_credits():
    st.markdown('<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown("### 크레딧이 부족합니다")
    st.markdown("---")

    st.markdown(
        '<p style="text-align:center; color:#d4c5e8; font-size:15px; line-height:2;">'
        '무료 크레딧 3개를 모두 사용했습니다.<br>'
        '더 깊이 읽고 싶다면 크레딧을 충전하세요.'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # 크레딧 충전 옵션
    st.markdown("#### 크레딧 충전")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<h4>10 크레딧</h4>'
            '<p style="color:#C5A0F0; font-size:1.3rem; font-weight:700;">₩4,900</p>'
            '<p style="font-size:0.8rem;">크레딧당 ₩490</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("충전하기 (10)", use_container_width=True, key="buy_10"):
            # TODO: 결제 연동 (Stripe/토스)
            st.session_state.credits += 10
            st.session_state.page = "select_mode"
            st.rerun()

    with col2:
        st.markdown(
            '<div class="mode-card" style="text-align:center; border-color:#C5A0F066;">'
            '<h4>25 크레딧</h4>'
            '<p style="color:#C5A0F0; font-size:1.3rem; font-weight:700;">₩9,900</p>'
            '<p style="font-size:0.8rem;">크레딧당 ₩396</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("충전하기 (25)", use_container_width=True, key="buy_25"):
            # TODO: 결제 연동
            st.session_state.credits += 25
            st.session_state.page = "select_mode"
            st.rerun()

    with col3:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<h4>월 구독</h4>'
            '<p style="color:#C5A0F0; font-size:1.3rem; font-weight:700;">₩14,900/월</p>'
            '<p style="font-size:0.8rem;">매일 1회 무료 + 할인</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("구독하기", use_container_width=True, key="subscribe"):
            # TODO: 구독 결제 연동
            st.session_state.credits += 30
            st.session_state.page = "select_mode"
            st.rerun()

    st.markdown("---")

    # 운명책 업셀
    st.markdown(
        '<div class="upsell-box">'
        '<p style="color:#C5A0F0; font-size:16px; font-weight:600; margin-bottom:8px;">'
        '아니면, 한 번에 전부 읽는 방법이 있다.'
        '</p>'
        '<p style="color:#a090b8; font-size:14px; margin-bottom:12px;">'
        '열두 체계 전체를 교차 분석해서 당신의 설계 논리를 한 권에 담는다.<br>'
        '삶의 10원칙 + 향후 10년 운의 흐름까지.'
        '</p>'
        '<p style="margin-bottom:4px;">'
        '<a href="https://destiny-book.streamlit.app" target="_blank" '
        'style="color:#C5A0F0; font-size:17px; font-weight:700;">운명책 알아보기 →</a>'
        '</p>'
        '<p style="color:#a090b8; font-size:12px;">한 사람당 한 권. 두 번 만들지 않는다.</p>'
        '</div>',
        unsafe_allow_html=True
    )

    if st.button("← 돌아가기", use_container_width=True):
        st.session_state.page = "select_mode"
        st.rerun()


# ─────────────────────────────────────────────
# 라우터
# ─────────────────────────────────────────────
def main():
    page = st.session_state.page

    if page == "intro":
        page_intro()
    elif page == "input":
        page_input()
    elif page == "select_mode":
        if st.session_state.user_data is None:
            st.session_state.page = "input"
            st.rerun()
        page_select_mode()
    elif page == "reading":
        if st.session_state.user_data is None:
            st.session_state.page = "input"
            st.rerun()
        page_reading()
    elif page == "no_credits":
        page_no_credits()
    else:
        st.session_state.page = "intro"
        st.rerun()


if __name__ == "__main__":
    main()
