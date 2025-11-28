
import requests
import time
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from google.genai import types
from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)
from google.adk.tools import preload_memory, google_search
from tools.day_trip import plan_day_trip_tool
from retry_config import retry_config



async def auto_save_to_memory(callback_context):
    """Automatically save session memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )
    
    # print("\nSaved session content:", callback_context._invocation_context.session)

print("✅ Auto-memory callback ready.")



def check_server_ready(url: str, max_attempts: int = 5, delay: int = 2) -> bool:
    """Check if a server is ready by polling its URL."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print(f"\n✅ {url} Server is running!")
                return True
        except requests.RequestException:
            time.sleep(delay)
    return False


check_server_ready("http://localhost:8001/.well-known/agent-card.json")
check_server_ready("http://localhost:8002/.well-known/agent-card.json")

# Weather Agent (Remote)
remote_weather_agent = RemoteA2aAgent(
    name="weather_agent",
    description="Remote weather forecast agent via A2A.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Maps Agent (Remote)
remote_maps_agent = RemoteA2aAgent(
    name="maps_agent",
    description="Remote Google Maps-based place lookup agent via A2A.",
    agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)



orchestrator = LlmAgent(
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    name="trip_planner_agent",
    description="An orchestrator that plans trips using maps and weather remote A2A agents.",
    instruction="""
你是一個旅遊行程規劃助理。

你可以使用以下兩個遠端子 Agent：
1. maps_agent：查詢地點、餐廳、評分、地址等。
2. weather_agent：查詢城市的天氣預報（高低溫、降雨機率）。

流程：
- 若使用者給地點關鍵字，請呼叫 maps_agent。
- 若使用者給城市＋日期，請呼叫 weather_agent。
- 最後整合地點＋天氣，提供合理的旅遊建議。
回覆請保持簡潔、自然。
""",
    tools=[preload_memory], 
    after_agent_callback=auto_save_to_memory,  # 🔥 每次 agent turn 都會自動存
    sub_agents=[remote_maps_agent, remote_weather_agent],  # ⭐ 正在這裡！
)
