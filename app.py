
from google.genai import types

from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from agents.orch_server import orchestrator
from google.adk.runners import Runner

import os
from dotenv import load_dotenv

load_dotenv()

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["GOOGLE_MAPS_API_KEY"] = GOOGLE_MAPS_API_KEY
    print("✅ Setup and authentication complete.")
except Exception as e:
    print(
        f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}"
    )


# --- 建立 Session 與 Memory ---
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
# ---------------------------------------------
# 全域 Runner 單例
# ---------------------------------------------
runner = Runner(
    agent=orchestrator,
    app_name="agents",
    session_service=session_service,
    memory_service=memory_service
)


async def run_trip_request(num_spots: int, city: str, user_id="demo_user", session_id="trip_session"):
    # 建立或取得 session
    try:
        session = await session_service.create_session(
            app_name="agents", user_id=user_id, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name="agents", user_id=user_id, session_id=session_id
        )

    # User query
    query_text = f"我想安排一天行程，去 {num_spots} 個景點在 {city}，請幫我規劃。"
    query_content = types.Content(role="user", parts=[types.Part(text=query_text)])
    

    agent_events = runner.run_async(user_id=user_id, session_id=session.id, new_message=query_content)

    async for event in agent_events:
        # Agent 回覆文字
        # 合併所有文字部分
        if getattr(event, "content", None) and event.content.parts:
            text_parts = [p.text for p in event.content.parts if getattr(p, "text", None)]
            if text_parts:
                print("Agent 回覆文字:", " ".join(text_parts))

        # 等待人工批准
        tool_call = getattr(event, "tool_call", None)
        print(f"tool_call.status {tool_call.status} , tool_call.message {tool_call.message}")
        if tool_call and tool_call.status == "pending":
            print(f"\n⚠️ Agent 暫停，等待人工批准：\n{tool_call.message}")
            while True:
                decision = input("請輸入 Y 批准 / N 拒絕: ").strip().upper()
                if decision in ["Y", "N"]:
                    confirmed = decision == "Y"
                    # 這裡 resume_tool 可以讓 Agent 繼續
                    await runner.resume_tool(
                        user_id=user_id,
                        session_id=session.id,
                        tool_call_id=tool_call.id,
                        confirmed=confirmed
                    )
                    break
                print("❌ 請輸入 Y 或 N")
async def main():
    
    # response = await runner.run_debug("11 月 18 日想去台北，有什麼建議？請評估天氣跟附近景點。")
    import uuid
    
    
        
    app_name = "agents"
    user_id = "demo_user"
    session_id = f"demo_session_{uuid.uuid4().hex[:8]}"

    # 建立 session
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )

    # 包成 Content，role 必須是 "user"
    test_content = types.Content(
        role="user",
        parts=[types.Part(text="11 月 18 日想去台北，有什麼建議？請評估天氣跟附近景點。")]
    )

    # 迭代 agent events
    async for event in runner.run_async(
        user_id=user_id, 
        session_id=session.id,  # 🔥 一定要用 session.id
        new_message=test_content
    ):
        if getattr(event, "is_final_response", lambda: False)() and getattr(event, "content", None):
            for part in event.content.parts:
                if hasattr(part, "text"):
                    print(part.text)
        print("-" * 60)


    # await run_trip_request(num_spots=5, city="台北")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 

