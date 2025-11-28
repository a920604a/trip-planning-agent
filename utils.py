import os
import json
import requests
from datetime import datetime
# ——— Long‑Term Memory 存取 (JSON) ———
USER_PROFILE_DB = "user_profiles.json"

def load_user_profile(user_id: str) -> dict:
    if os.path.exists(USER_PROFILE_DB):
        with open(USER_PROFILE_DB, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {}
    return db.get(user_id, {})

def save_user_profile(user_id: str, profile: dict):
    if os.path.exists(USER_PROFILE_DB):
        with open(USER_PROFILE_DB, "r", encoding="utf-8") as f:
            db = json.load(f)
    else:
        db = {}
    db[user_id] = profile
    with open(USER_PROFILE_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def save_conversation_summary(user_id: str, summary: str):
    profile = load_user_profile(user_id)
    history = profile.get("memory_summaries", [])
    history.append({
        "timestamp": datetime.utcnow().isoformat(),
        "summary": summary
    })
    profile["memory_summaries"] = history
    save_user_profile(user_id, profile)

def get_user_preferences(user_id: str) -> dict:
    profile = load_user_profile(user_id)
    return profile.get("preferences", {})

def update_user_preferences(user_id: str, new_prefs: dict):
    profile = load_user_profile(user_id)
    prefs = profile.get("preferences", {})
    prefs.update(new_prefs)
    profile["preferences"] = prefs
    save_user_profile(user_id, profile)

# ——— LLM-based summarization function (你自己實作 /呼叫 Gemini) ———
def llm_summarize_conversation(history: list[dict]) -> str:
    # 將 history 轉成對話文本
    transcript = ""
    for turn in history:
        role = turn.get("role", "")
        content = turn.get("content", "").strip()
        if not content:
            continue
        transcript += f"{role}: {content}\n"
    # prompt for summarization
    prompt = f"""請幫我總結以下對話內容 (中文) — 只保留對使用者偏好、旅行需求 (目的地、天數、預算、偏好類型)、重要決定 (例如城市 /景點 /天數 /偏好) 及 agent 提出的建議摘要：\n\n{transcript}\n\n請以「簡潔摘要」形式回覆 (3–6 句 /段落)。"""
    # 這裡假設你用 Gemini 或其他 LLM 呼叫方式
    response = YOUR_LLM_CALL(prompt)  # TODO: 替換成你實際呼叫 LLM 的函式
    return response

# ——— Itinerary 評估 (簡易) ———
def validate_itinerary(itinerary: dict) -> dict:
    issues = []
    days = itinerary.get("days", [])
    if not days:
        issues.append("Itinerary has no days.")
    for day in days:
        spots = day.get("spots", [])
        if not spots:
            issues.append(f"某天 ({day.get('date', '?')}) 無景點安排")
        if len(spots) > 6:
            issues.append(f"{day.get('date', '?')} 安排 {len(spots)} 個景點 (可能太多)")
    valid = len(issues) == 0
    return {"valid": valid, "issues": issues}
