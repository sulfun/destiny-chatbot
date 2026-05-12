"""
Supabase 데이터베이스 클라이언트
사용자 관리, 벽돌 잔액, 리딩 기록
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime


def get_supabase() -> Client:
    """Supabase 클라이언트 반환 (싱글톤)"""
    if "supabase" not in st.session_state:
        st.session_state.supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_SERVICE_KEY"]  # service role key (서버사이드)
        )
    return st.session_state.supabase


# ─────────────────────────────────────────────
# 사용자 관리
# ─────────────────────────────────────────────

def get_or_create_user(email: str, name: str = None, birth_date: str = None,
                       birth_time: str = None, gender: str = None) -> dict:
    """이메일로 사용자 조회 또는 생성. 신규 시 벽돌 10개 지급."""
    sb = get_supabase()

    # 기존 사용자 조회
    result = sb.table("users").select("*").eq("email", email).execute()

    if result.data:
        user = result.data[0]
        # 프로필 업데이트 (이름, 생년월일 등이 바뀌었을 수 있음)
        updates = {}
        if name and name != user.get("name"):
            updates["name"] = name
        if birth_date and birth_date != user.get("birth_date"):
            updates["birth_date"] = birth_date
        if birth_time and birth_time != user.get("birth_time"):
            updates["birth_time"] = birth_time
        if gender and gender != user.get("gender"):
            updates["gender"] = gender

        if updates:
            sb.table("users").update(updates).eq("id", user["id"]).execute()
            user.update(updates)

        return user

    # 신규 사용자 생성
    new_user = {
        "email": email,
        "name": name or "",
        "birth_date": birth_date or "",
        "birth_time": birth_time or "",
        "gender": gender or "",
        "bricks": 10,  # 가입 보너스
        "total_readings": 0,
    }
    result = sb.table("users").insert(new_user).execute()
    user = result.data[0]

    # 가입 보너스 트랜잭션 기록
    sb.table("brick_transactions").insert({
        "user_id": user["id"],
        "amount": 10,
        "reason": "signup_bonus",
    }).execute()

    return user


def get_user_by_email(email: str) -> dict | None:
    """이메일로 사용자 조회"""
    sb = get_supabase()
    result = sb.table("users").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


# ─────────────────────────────────────────────
# 벽돌 관리
# ─────────────────────────────────────────────

def get_bricks(user_id: str) -> int:
    """현재 벽돌 잔액 조회"""
    sb = get_supabase()
    result = sb.table("users").select("bricks").eq("id", user_id).execute()
    return result.data[0]["bricks"] if result.data else 0


def use_bricks(user_id: str, amount: int, reason: str) -> bool:
    """벽돌 사용. 잔액 부족 시 False 반환."""
    sb = get_supabase()

    # 현재 잔액 확인
    current = get_bricks(user_id)
    if current < amount:
        return False

    # 차감
    sb.table("users").update({
        "bricks": current - amount
    }).eq("id", user_id).execute()

    # 트랜잭션 기록
    sb.table("brick_transactions").insert({
        "user_id": user_id,
        "amount": -amount,
        "reason": reason,
    }).execute()

    return True


def add_bricks(user_id: str, amount: int, reason: str,
               stripe_session_id: str = None) -> int:
    """벽돌 충전. 충전 후 잔액 반환."""
    sb = get_supabase()

    current = get_bricks(user_id)
    new_balance = current + amount

    sb.table("users").update({
        "bricks": new_balance
    }).eq("id", user_id).execute()

    # 트랜잭션 기록
    sb.table("brick_transactions").insert({
        "user_id": user_id,
        "amount": amount,
        "reason": reason,
        "stripe_session_id": stripe_session_id,
    }).execute()

    return new_balance


# ─────────────────────────────────────────────
# 리딩 기록
# ─────────────────────────────────────────────

def save_reading(user_id: str, mode: str, content: str, bricks_used: int):
    """리딩 결과 저장"""
    sb = get_supabase()

    sb.table("readings").insert({
        "user_id": user_id,
        "mode": mode,
        "content": content,
        "bricks_used": bricks_used,
    }).execute()

    # total_readings 증가
    user = sb.table("users").select("total_readings").eq("id", user_id).execute()
    if user.data:
        sb.table("users").update({
            "total_readings": user.data[0]["total_readings"] + 1
        }).eq("id", user_id).execute()


def get_readings(user_id: str, limit: int = 10) -> list:
    """사용자 리딩 기록 조회"""
    sb = get_supabase()
    result = (
        sb.table("readings")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def get_reading_count(user_id: str) -> int:
    """총 리딩 횟수"""
    sb = get_supabase()
    result = sb.table("users").select("total_readings").eq("id", user_id).execute()
    return result.data[0]["total_readings"] if result.data else 0
