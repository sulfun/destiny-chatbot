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
from database import (
    get_or_create_user, get_bricks, use_bricks, add_bricks,
    save_reading, get_reading_count
)
from payments import (
    BRICK_PRODUCTS, get_toss_payment_widget_html,
    confirm_toss_payment, generate_order_id
)
import streamlit.components.v1 as components

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
# Supabase 사용 여부 (키가 없으면 세션 모드로 폴백)
# ─────────────────────────────────────────────
USE_SUPABASE = all(k in st.secrets for k in ["SUPABASE_URL", "SUPABASE_SERVICE_KEY"])
USE_TOSS = all(k in st.secrets for k in ["TOSS_CLIENT_KEY", "TOSS_SECRET_KEY"])

# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
if "credits" not in st.session_state:
    st.session_state.credits = 10  # 무료 벽돌 10개 (폴백용)

if "user_data" not in st.session_state:
    st.session_state.user_data = None

if "db_user" not in st.session_state:
    st.session_state.db_user = None  # Supabase 사용자 레코드

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

if "toss_product_key" not in st.session_state:
    st.session_state.toss_product_key = None

if "toss_order_id" not in st.session_state:
    st.session_state.toss_order_id = None

# ─────────────────────────────────────────────
# 결제 완료 콜백 처리 (토스페이먼츠 redirect)
# ─────────────────────────────────────────────
query_params = st.query_params
if query_params.get("payment") == "success" and USE_TOSS:
    payment_key = query_params.get("paymentKey", "")
    order_id = query_params.get("orderId", "")
    toss_amount = int(query_params.get("amount", "0"))
    product_key = query_params.get("product_key", "")

    if payment_key and order_id and product_key and st.session_state.db_user:
        product = BRICK_PRODUCTS.get(product_key)
        if product and toss_amount == product["price_krw"]:
            # 토스 결제 승인 API 호출
            result = confirm_toss_payment(payment_key, order_id, toss_amount)
            if result and result.get("status") == "DONE":
                bricks = product["bricks"]
                user_id = st.session_state.db_user["id"]

                add_bricks(
                    user_id=user_id,
                    amount=bricks,
                    reason=f"purchase_{product_key}",
                    stripe_session_id=order_id,  # 필드 재활용 (toss order_id)
                )
                st.session_state.credits = get_bricks(user_id)
                st.query_params.clear()
                st.toast(f"🧱 벽돌 {bricks}개 충전 완료!")
            else:
                st.query_params.clear()
                st.toast("결제 승인에 실패했습니다. 다시 시도해주세요.", icon="⚠️")
    else:
        st.query_params.clear()

elif query_params.get("payment") == "fail":
    st.query_params.clear()
    st.toast("결제가 취소되었습니다.", icon="⚠️")


# ─────────────────────────────────────────────
# 벽돌 헬퍼 (Supabase or 세션)
# ─────────────────────────────────────────────
def get_current_bricks() -> int:
    """현재 벽돌 수 (DB 또는 세션)"""
    if USE_SUPABASE and st.session_state.db_user:
        return get_bricks(st.session_state.db_user["id"])
    return st.session_state.credits


def spend_bricks(amount: int, reason: str) -> bool:
    """벽돌 사용 (DB 또는 세션)"""
    if USE_SUPABASE and st.session_state.db_user:
        success = use_bricks(st.session_state.db_user["id"], amount, reason)
        if success:
            st.session_state.credits = get_bricks(st.session_state.db_user["id"])
        return success
    else:
        if st.session_state.credits >= amount:
            st.session_state.credits -= amount
            return True
        return False


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
    credits = get_current_bricks()
    if credits > 0:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<span class="credit-badge">🧱 벽돌: {credits}개</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="text-align:right;">'
            f'<span class="credit-badge" style="border-color:#ff6b6b44;color:#ff6b6b;">🧱 벽돌: 0개</span>'
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
            '<div class="mode-card" style="text-align:center;">'
            '<p style="font-size:2.5rem; margin:0 0 8px 0;">🪞</p>'
            '<h4>전생 리딩</h4>'
            '<p>당신의 전생 — 시대, 역할, 이번 생에 가져온 것</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<p style="font-size:2.5rem; margin:0 0 8px 0;">🔑</p>'
            '<h4>운명 키워드</h4>'
            '<p>본질, 무기, 함정 — 세 개의 키워드로 압축</p>'
            '</div>',
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<p style="font-size:2.5rem; margin:0 0 8px 0;">🌅</p>'
            '<h4>오늘의 설계도</h4>'
            '<p>오늘 하루의 에너지 흐름 — 밀 때와 빠질 때</p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("")
    st.markdown(
        '<p style="text-align:center; color:#a090b8; font-size:13px;">'
        '🧱 무료 벽돌 10개 제공 · 리딩 1회 벽돌 7개'
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
        email = st.text_input("이메일", placeholder="hello@example.com")
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
            if not email or "@" not in email:
                st.error("이메일을 정확히 입력해주세요.")
            elif not name:
                st.error("이름을 입력해주세요.")
            elif not birth_time:
                st.error("출생시간을 입력해주세요. 모르면 '모름'이라고 적어주세요.")
            else:
                # Supabase 사용자 생성/조회
                if USE_SUPABASE:
                    db_user = get_or_create_user(
                        email=email,
                        name=name,
                        birth_date=birth_date.strftime("%Y-%m-%d"),
                        birth_time=birth_time,
                        gender=gender,
                    )
                    st.session_state.db_user = db_user
                    st.session_state.credits = db_user.get("bricks", 10)
                    st.session_state.readings_done = db_user.get("total_readings", 0)

                st.session_state.user_data = {
                    "name": name,
                    "email": email,
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

    current_bricks = get_current_bricks()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🪞 전생 리딩", use_container_width=True):
            if current_bricks >= 7:
                st.session_state.current_mode = "past_life"
                st.session_state.page = "reading"
                st.rerun()
            else:
                st.session_state.page = "no_credits"
                st.rerun()

    with col2:
        if st.button("🔑 운명 키워드", use_container_width=True):
            if current_bricks >= 7:
                st.session_state.current_mode = "keywords"
                st.session_state.page = "reading"
                st.rerun()
            else:
                st.session_state.page = "no_credits"
                st.rerun()

    with col3:
        if st.button("🌅 오늘의 설계도", use_container_width=True):
            if current_bricks >= 7:
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
            f'🧱 지금까지 {st.session_state.readings_done}회 리딩 · 벽돌 {current_bricks}개 남음'
            f'</p>',
            unsafe_allow_html=True
        )

    # 2회 이상 리딩 시 서브스택 + 운명책 업셀
    if st.session_state.readings_done >= 2:
        st.markdown("---")
        st.markdown(
            '<div class="upsell-box">'
            '<p style="color:#C5A0F0; font-size:14px; margin-bottom:8px;">여기서 읽은 건 밑그림의 밑그림이다.</p>'
            '<p style="color:#a090b8; font-size:13px; margin-bottom:8px;">'
            '운명책은 서브스택 연간 구독자만 신청할 수 있다.'
            '</p>'
            '<a href="https://lifeonearthlog.substack.com" target="_blank" '
            'style="color:#C5A0F0; font-size:15px; font-weight:600;">서브스택 구독하기 →</a>'
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
        # 벽돌 차감
        cost = CREDIT_COSTS[mode]
        if not spend_bricks(cost, f"reading_{mode}"):
            st.session_state.page = "no_credits"
            st.rerun()
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

        # 리딩 결과 DB 저장
        if USE_SUPABASE and st.session_state.db_user:
            save_reading(st.session_state.db_user["id"], mode, full_response, cost)

        st.rerun()

    # 심화 질문 입력
    if question := st.chat_input("더 궁금한 게 있어? (심화 분석 벽돌 3개)"):
        # 유저 메시지 표시
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        # 벽돌 체크
        if get_current_bricks() < 3:
            no_credit_msg = (
                "🧱 벽돌이 부족하다.\n\n"
                "충전하고 다시 와. "
                "아니면 열두 체계 전체를 한 권에 담은 운명책이라는 방법도 있다.\n\n"
                "운명책은 [서브스택 연간 구독자](https://lifeonearthlog.substack.com) 만 신청할 수 있다."
            )
            with st.chat_message("assistant", avatar="🔮"):
                st.markdown(no_credit_msg)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": no_credit_msg
            })
        else:
            # 심화 분석 실행
            spend_bricks(3, "reading_deep_dive")
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

            # 심화 리딩 DB 저장
            if USE_SUPABASE and st.session_state.db_user:
                save_reading(st.session_state.db_user["id"], "deep_dive", full_response, 3)

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
# 결제 헬퍼
# ─────────────────────────────────────────────
def _handle_purchase(product_key: str):
    """결제 버튼 클릭 시 처리"""
    if USE_TOSS and st.session_state.db_user:
        st.session_state.toss_product_key = product_key
        st.session_state.toss_order_id = generate_order_id(product_key)
        st.rerun()
    else:
        # 폴백: 토스 키 없으면 세션 크레딧 직접 추가 (개발/테스트용)
        product = BRICK_PRODUCTS[product_key]
        st.session_state.credits += product["bricks"]
        st.session_state.page = "select_mode"
        st.rerun()


def _show_toss_payment_widget():
    """토스페이먼츠 결제위젯 표시"""
    product_key = st.session_state.toss_product_key
    order_id = st.session_state.toss_order_id
    product = BRICK_PRODUCTS[product_key]

    st.markdown('<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown(f"### 🧱 {product['name']} 결제")
    st.markdown("---")

    # 토스 결제위젯 렌더링
    widget_html = get_toss_payment_widget_html(
        product_key=product_key,
        user_id=str(st.session_state.db_user["id"]),
        user_email=st.session_state.user_data.get("email", ""),
        order_id=order_id,
    )
    components.html(widget_html, height=600, scrolling=True)

    st.markdown("")
    if st.button("← 돌아가기", use_container_width=True, key="back_from_payment"):
        st.session_state.toss_product_key = None
        st.session_state.toss_order_id = None
        st.rerun()


# ─────────────────────────────────────────────
# 페이지: 크레딧 부족
# ─────────────────────────────────────────────
def page_no_credits():
    # 결제위젯 모드 체크 — 버튼 클릭으로 진입
    if st.session_state.get("toss_product_key"):
        _show_toss_payment_widget()
        return

    st.markdown('<div class="architect-symbol">◈</div>', unsafe_allow_html=True)
    st.markdown("### 🧱 벽돌이 부족합니다")
    st.markdown("---")

    st.markdown(
        '<p style="text-align:center; color:#d4c5e8; font-size:15px; line-height:2;">'
        '한 번 맛봤으면 알 거다. 밑그림은 한 번 읽는 게 아니라 계속 읽는 거다.<br>'
        '벽돌을 충전하고 나머지도 확인해라. 🧱'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # 벽돌 충전 옵션
    st.markdown("#### 🧱 벽돌 충전")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<p style="font-size:2rem; margin:0;">🧱</p>'
            '<h4>벽돌 1개</h4>'
            '<p style="color:#C5A0F0; font-size:1.5rem; font-weight:700;">₩1,000</p>'
            '<p style="font-size:0.8rem; color:#a090b8;">맛보기용</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("1개 충전", use_container_width=True, key="buy_1"):
            _handle_purchase("brick_1")

    with col2:
        st.markdown(
            '<div class="mode-card" style="text-align:center; border-color:#C5A0F066;">'
            '<p style="font-size:2rem; margin:0;">🏗️</p>'
            '<h4>벽돌 10개</h4>'
            '<p style="color:#C5A0F0; font-size:1.5rem; font-weight:700;">₩9,500</p>'
            '<p style="font-size:0.8rem; color:#a090b8;">5% 할인</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("10개 충전", use_container_width=True, key="buy_10"):
            _handle_purchase("brick_10")

    with col3:
        st.markdown(
            '<div class="mode-card" style="text-align:center;">'
            '<p style="font-size:2rem; margin:0;">🏛️</p>'
            '<h4>벽돌 20개</h4>'
            '<p style="color:#C5A0F0; font-size:1.5rem; font-weight:700;">₩17,900</p>'
            '<p style="font-size:0.8rem; color:#a090b8;">10% 할인</p>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("20개 충전", use_container_width=True, key="buy_20"):
            _handle_purchase("brick_20")

    st.markdown("")
    st.markdown(
        '<p style="text-align:center; color:#a090b8; font-size:12px;">'
        '오늘의 설계도는 매일 새로 바뀝니다. 매일 와서 벽돌 쌓으세요. 🧱'
        '</p>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 서브스택 구독 안내
    st.markdown(
        '<div class="upsell-box">'
        '<p style="color:#C5A0F0; font-size:18px; font-weight:700; margin-bottom:10px;">'
        '더 깊이 들어가는 방법'
        '</p>'
        '<p style="color:#d4c5e8; font-size:14px; margin-bottom:16px; line-height:1.8;">'
        'The Architect의 서브스택을 구독하면<br>'
        '운명학 인사이트를 매주 받아볼 수 있다.'
        '</p>'
        '<div style="display:flex; justify-content:center; gap:20px; margin-bottom:16px;">'
        '<div style="text-align:center;">'
        '<p style="color:#a090b8; font-size:12px; margin:0;">월간 구독</p>'
        '<p style="color:#C5A0F0; font-size:1.3rem; font-weight:700; margin:4px 0;">$5/월</p>'
        '</div>'
        '<div style="text-align:center;">'
        '<p style="color:#a090b8; font-size:12px; margin:0;">연간 구독</p>'
        '<p style="color:#C5A0F0; font-size:1.3rem; font-weight:700; margin:4px 0;">$50/년</p>'
        '</div>'
        '</div>'
        '<a href="https://lifeonearthlog.substack.com" target="_blank" '
        'style="color:#C5A0F0; font-size:15px; font-weight:600;">서브스택 구독하기 →</a>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("")

    # 운명책 — 연간 구독자 전용
    st.markdown(
        '<div class="upsell-box" style="border-color:#C5A0F055;">'
        '<p style="color:#C5A0F0; font-size:16px; font-weight:700; margin-bottom:8px;">'
        '운명책 — 연간 구독자 전용'
        '</p>'
        '<p style="color:#a090b8; font-size:14px; margin-bottom:12px; line-height:1.7;">'
        '열두 체계 전체를 교차 분석해서 당신의 설계 논리를 한 권에 담는다.<br>'
        '삶의 10원칙 + 향후 10년 운의 흐름까지.<br>'
        '한 사람당 한 권. 두 번 만들지 않는다.'
        '</p>'
        '<p style="color:#d4c5e8; font-size:13px; margin-bottom:8px;">'
        '서브스택 연간 구독($50/년) 이상만 신청 가능'
        '</p>'
        '<a href="https://lifeonearthlog.substack.com" target="_blank" '
        'style="color:#C5A0F0; font-size:15px; font-weight:600;">서브스택에서 연간 구독하기 →</a>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("")
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
