
import asyncio
import traceback

from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from agents.orch_server import orchestrator
from google.adk.runners import Runner


import os
from dotenv import load_dotenv

load_dotenv()

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MAP_API_KEY = os.getenv("GOOGLE_MAP_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["GOOGLE_MAP_API_KEY"] = GOOGLE_MAP_API_KEY
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




def get_main_text_response(events):
    for event in reversed(events):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    return part.text
    return None

async def chat_loop():
    print("[INFO] CLI Chatbot Ready! Type 'exit', 'quit', 'bye' to leave.")
    conversation_history = []

    while True:
        try:
            user_input = input("👤 User: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("[INFO] Exiting chatbot.")
                break

            # 多輪對話：把 user message 放入 history
            conversation_history.append({"role": "user", "content": user_input})

            # 呼叫 runner
            reply = await runner.run_debug(user_input)
            response = get_main_text_response(reply)

            # 印出 AI 回覆
            print("🤖 Bot:", response)

            # 更新 conversation_history
            conversation_history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print("[INFO] Exiting chatbot due to keyboard interrupt.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            traceback.print_exc()


if __name__ == "__main__":
    # import asyncio
    # asyncio.run(main()) 
    asyncio.run(chat_loop())
    
