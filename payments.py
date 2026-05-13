"""
토스페이먼츠 결제 모듈
벽돌 충전을 위한 결제위젯 + 결제 승인
"""

import requests
import base64
import uuid
import streamlit as st


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
# 토스페이먼츠 결제위젯 HTML 생성
# ─────────────────────────────────────────────

def get_toss_payment_widget_html(
    product_key: str,
    user_id: str,
    user_email: str,
    order_id: str,
) -> str:
    """
    토스페이먼츠 결제위젯 HTML을 반환.
    Streamlit의 st.components.v1.html()로 렌더링.
    """
    product = BRICK_PRODUCTS[product_key]
    client_key = st.secrets.get("TOSS_CLIENT_KEY", "")
    app_url = st.secrets.get("APP_URL", "https://destiny-chatbot.streamlit.app")

    success_url = f"{app_url}?payment=success&orderId={order_id}&product_key={product_key}"
    fail_url = f"{app_url}?payment=fail"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://js.tosspayments.com/v2/standard"></script>
    </head>
    <body style="margin:0; padding:0; background:transparent;">
        <div id="payment-method"></div>
        <button id="payment-button" style="
            background: linear-gradient(135deg, #2d1b4e 0%, #1a0e33 100%);
            border: 1px solid #C5A0F044;
            color: #C5A0F0;
            font-family: 'Noto Sans KR', sans-serif;
            font-weight: 600;
            font-size: 16px;
            border-radius: 8px;
            padding: 12px 32px;
            cursor: pointer;
            width: 100%;
            margin-top: 16px;
        ">
            {product['name']} 결제하기 (₩{product['price_krw']:,})
        </button>
        <script>
            async function initPayment() {{
                const tossPayments = TossPayments("{client_key}");
                const widgets = tossPayments.widgets({{
                    customerKey: "{user_id}",
                }});

                await widgets.setAmount({{
                    currency: "KRW",
                    value: {product['price_krw']},
                }});

                await widgets.renderPaymentMethods({{
                    selector: "#payment-method",
                    variantKey: "DEFAULT",
                }});

                document.getElementById("payment-button")
                    .addEventListener("click", async function () {{
                        await widgets.requestPayment({{
                            orderId: "{order_id}",
                            orderName: "{product['name']}",
                            customerEmail: "{user_email}",
                            successUrl: "{success_url}",
                            failUrl: "{fail_url}",
                        }});
                    }});
            }}
            initPayment();
        </script>
    </body>
    </html>
    """


# ─────────────────────────────────────────────
# 토스페이먼츠 결제 승인
# ─────────────────────────────────────────────

def confirm_toss_payment(payment_key: str, order_id: str, amount: int) -> dict | None:
    """
    토스페이먼츠 결제 승인 API 호출.
    Returns: 승인 응답 dict or None (실패 시)
    """
    secret_key = st.secrets.get("TOSS_SECRET_KEY", "")
    if not secret_key:
        return None

    # Basic Auth: secretKey + ":"
    auth_string = base64.b64encode(f"{secret_key}:".encode()).decode()

    try:
        response = requests.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            headers={
                "Authorization": f"Basic {auth_string}",
                "Content-Type": "application/json",
            },
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
            },
            timeout=30,
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"토스 결제 승인 실패: {response.status_code} — {response.text}")
            return None

    except Exception as e:
        print(f"토스 결제 승인 오류: {e}")
        return None


def generate_order_id(product_key: str) -> str:
    """고유 주문 ID 생성"""
    short_uuid = str(uuid.uuid4()).replace("-", "")[:12]
    return f"brick_{product_key}_{short_uuid}"
