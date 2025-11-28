import requests
import os
os.environ["DISABLE_AIOHTTP_TRANSPORT"] = "True"

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from retry_config import retry_config
from google.adk.runners import InMemoryRunner


def places_text_search(query: str) -> dict:
    print("places_text_search called with query:", query)
    """
    使用 Google Maps Places Text Search 查詢地點
    query: 查詢字串，例如 "Taipei 101"
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": os.environ["GOOGLE_MAP_API_KEY"],
        "language": "zh-TW",  # 中文  
    }

    resp = requests.get(url, params=params).json()

    if resp.get("status") != "OK":
        return {"summary": f"查詢失敗: {resp.get('status')}"}

    # 取前 5 筆結果
    results = resp.get("results", [])[:5]
    summary_list = []
    for r in results:
        name = r.get("name")
        address = r.get("formatted_address")
        rating = r.get("rating", "無評分")
        summary_list.append(f"{name}，地址: {address}，評分: {rating}")

    summary_text = "\n".join(summary_list)
    return {"summary": f"查詢 '{query}' 結果如下:\n{summary_text}"}




maps_agent = LlmAgent(
    name="maps_agent",
    model=Gemini(model="gemini-2.5-flash", retry_options=retry_config),
    instruction="""
你是一個地圖查詢助理。

使用者會提供地點名稱或關鍵字，請使用 places_text_search 工具查詢地點。
回覆時用自然語言，包含：
- 地點名稱
- 地址
- 評分（如果有）
保持簡短且清楚。
""",
    tools=[places_text_search]
)



app = to_a2a(maps_agent, port=8002)


async def test_runner():
    runner = InMemoryRunner(agent=maps_agent)
    
    response = await runner.run_debug("請幫我查 Taipei 101 附近的餐廳")
    
import asyncio
if __name__ == "__main__":    
    asyncio.run(test_runner())