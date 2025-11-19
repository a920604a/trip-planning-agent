import requests
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from retry_config import retry_config



def weather_lookup(location: str, date: str) -> dict:
    # Geocoding
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=zh"
    geo_resp = requests.get(geo_url).json()
    if 'results' not in geo_resp or len(geo_resp['results']) == 0:
        return {"error": f"找不到城市: {location}"}

    lat = geo_resp['results'][0]['latitude']
    lon = geo_resp['results'][0]['longitude']

    # 天氣預報
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=Asia/Taipei"
    )
    weather_resp = requests.get(weather_url).json()

    # 篩選指定日期
    try:
        idx = weather_resp['daily']['time'].index(date)
        result = {
            "location": location,
            "date": date,
            "temperature_max": weather_resp['daily']['temperature_2m_max'][idx],
            "temperature_min": weather_resp['daily']['temperature_2m_min'][idx],
            "precipitation": weather_resp['daily']['precipitation_sum'][idx]
        }
        return result
    except ValueError:
        return {"error": f"找不到日期 {date} 的天氣資料"}



weather_agent = LlmAgent(
    name="weather_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
你是一個天氣助理。

使用者會提供城市名稱與日期，請使用 weather_lookup 工具查詢天氣。
回覆時請用自然語言，包含：
- 城市
- 日期
- 最高溫
- 最低溫
- 降雨機率
保持簡短且清楚。
""",
    tools=[weather_lookup]
)




app = to_a2a(weather_agent, port=8001)
