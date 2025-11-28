python -m venv .venv
.\.venv\Scripts\activate

pip install google-adk[a2a] google-genai

$env:GOOGLE_MAP_API_KEY = ""
$env:GOOGLE_API_KEY = ""

./start_agents.ps1 start

python app.py
./start_agents.ps1 stop



## Key Features
| Feature                                                                  | 有／無 | 理由 / 說明                                                                                                                                                                                                                        |
| ------------------------------------------------------------------------ | --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Multi-agent system**                                                   | ✅   | 你定義了多個 agent： `maps_agent`、`weather_agent`，以及一個 `orchestrator` (trip_planner_agent)，並且在 `orchestrator` 中使用 `sub_agents=[...]`。這就是典型的 multi-agent 架構 (agent-to-agent / agent orchestration) 。                                   |
| **Tools (custom tools / OpenAPI tools / tool-use)**                      | ✅   | 你的 `places_text_search` (地點查詢 via Google Maps Places API) 和 `weather_lookup` (天氣查詢 via open-meteo / geocoding API) 都是自訂工具 (custom tools / external API call)。這滿足「tools」要求。                                                     |
| **Agent-to-Agent 通訊 (A2A Protocol + sub-agent 調用)**                      | ✅   | 你用了 `to_a2a(...)` 將 `maps_agent` / `weather_agent` 轉成 A2A 可供外部呼叫的 Agent server；然後在 `orchestrator` 中把它們列為 `sub_agents`，意味著 orchestrator 會以 A2A 協定來呼叫子 agents。這就是 A2A / multi-agent interoperability。                            |
