
import requests
import time
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini


# Wait for server to start (poll until it responds)
max_attempts = 30
for attempt in range(max_attempts):
    try:
        response = requests.get(
            "http://localhost:8001/.well-known/agent-card.json", timeout=1
        )
        if response.status_code == 200:
            print(f"\n✅ Product Catalog Agent server is running!")
            print(f"   Server URL: http://localhost:8001")
            print(f"   Agent card: http://localhost:8001/.well-known/agent-card.json")
            print(response.json())
            break
    except requests.exceptions.RequestException:
        time.sleep(5)
        print(".", end="", flush=True)
else:
    print("\n⚠️  Server may not be ready yet. Check manually if needed.")


# Wait for server to start (poll until it responds)
max_attempts = 30
for attempt in range(max_attempts):
    try:
        response = requests.get(
            "http://localhost:8001/.well-known/agent-card.json", timeout=1
        )
        if response.status_code == 200:
            print(f"\n✅ Product Catalog Agent server is running!")
            print(f"   Server URL: http://localhost:8002")
            print(f"   Agent card: http://localhost:8002/.well-known/agent-card.json")
            print(response.json())
            break
    except requests.exceptions.RequestException:
        time.sleep(5)
        print(".", end="", flush=True)
else:
    print("\n⚠️  Server may not be ready yet. Check manually if needed.")



from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
)

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

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors  
)


orchestrator = LlmAgent(
    model=Gemini(model="gemini-2.0-flash", retry_options=retry_config),
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

    sub_agents=[remote_maps_agent, remote_weather_agent],  # ⭐ 正在這裡！
)


from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent=orchestrator)

response = await runner.run_debug("11 月 18 日想去台北，有什麼建議？請評估天氣跟附近景點。")
