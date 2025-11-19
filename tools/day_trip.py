
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool

LARGE_BOOKING_THRESHOLD = 3  # 超過 3 個景點需要人工確認



def plan_day_trip(num_spots: int, destination: str, tool_context: ToolContext) -> dict:
    """計劃一天行程，超過 LARGE_BOOKING_THRESHOLD 個景點需要人工確認"""
    if num_spots <= LARGE_BOOKING_THRESHOLD:
        return {
            "status": "approved",
            "num_spots": num_spots,
            "destination": destination,
            "message": f"行程自動批准: {num_spots} 個景點在 {destination}"
        }

    if not tool_context.tool_confirmation:
        tool_context.request_confirmation(
            hint=f"⚠️ 行程包含 {num_spots} 個景點在 {destination}，是否批准？",
            payload={"num_spots": num_spots, "destination": destination},
        )
        return {"status": "pending", "message": "等待使用者批准"}

    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "num_spots": num_spots,
            "destination": destination,
            "message": f"行程獲得批准: {num_spots} 個景點在 {destination}"
        }
    else:
        return {"status": "rejected", "message": "行程被使用者拒絕"}

# 包裝成 FunctionTool
plan_day_trip_tool = FunctionTool(func=plan_day_trip)
