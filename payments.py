"""
Stripe 결제 모듈
벽돌 충전을 위한 Checkout Session 생성
"""

import stripe
import streamlit as st


def init_stripe():
    """Stripe API 키 초기화"""
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]


# ─────────────────────────────────────────────
# 벽돌 상품 정의
# ─────────────────────────────────────────────

BRICK_PRODUCTS = {
    "brick_1": {
        "name": "🧱 벽돌 1개",
        "bricks": 1,
        "price_krw": 1000,
        "description": "운명 리딩 맛보기",
    },
    "brick_10": {
        "name": "🏗️ 벽돌 10개",
        "bricks": 10,
        "price_krw": 9500,
        "description": "5% 할인 — 리딩 1회 + 심화 질문",
    },
    "brick_20": {
        "name": "🏛️ 벽돌 20개",
        "bricks": 20,
        "price_krw": 17900,
        "description": "10% 할인 — 리딩 2회 + 심화 질문",
    },
}


# ─────────────────────────────────────────────
# Stripe Checkout Session
# ─────────────────────────────────────────────

def create_checkout_session(product_key: str, user_email: str, user_id: str) -> str:
    """
    Stripe Checkout Session 생성.
    결제 완료 후 success_url로 리디렉트.
    Returns: Checkout Session URL
    """
    init_stripe()

    product = BRICK_PRODUCTS[product_key]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "krw",
                "product_data": {
                    "name": product["name"],
                    "description": product["description"],
                },
                "unit_amount": product["price_krw"],  # KRW는 소수점 없음
            },
            "quantity": 1,
        }],
        mode="payment",
        metadata={
            "user_id": user_id,
            "product_key": product_key,
            "bricks": str(product["bricks"]),
        },
        success_url=st.secrets.get("APP_URL", "https://destiny-chatbot.streamlit.app")
            + "?payment=success&session_id={CHECKOUT_SESSION_ID}",
        cancel_url=st.secrets.get("APP_URL", "https://destiny-chatbot.streamlit.app")
            + "?payment=cancel",
    )

    return session.url


def verify_payment(session_id: str) -> dict | None:
    """
    결제 완료 확인.
    Returns: {"user_id": ..., "bricks": ..., "product_key": ...} or None
    """
    init_stripe()

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            return {
                "user_id": session.metadata.get("user_id"),
                "bricks": int(session.metadata.get("bricks", 0)),
                "product_key": session.metadata.get("product_key"),
                "session_id": session_id,
            }
    except Exception:
        pass

    return None
