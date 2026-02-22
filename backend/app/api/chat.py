"""对话 API 路由"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid
import json

from app.schemas.chat import ChatRequest, ChatResponse, TripInfo, ClarifyInfo, FlightInfo, DebugInfo
from app.services.llm_service import llm_service
from app.services.flight_search import flight_search_service
from app.services.flight_mock import flight_mock_service
from app.core.config import settings

router = APIRouter()

# 内存会话存储 (简单实现)
sessions = {}

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    session_id = request.session_id or str(uuid.uuid4())
    
    # 获取会话历史和当前行程信息
    session = sessions.get(session_id, {
        "history": [],
        "trip_info": {}
    })
    
    # 如果用户选择了澄清选项，更新行程信息
    if request.selected_option and session.get("last_clarify_field"):
        field = session["last_clarify_field"]
        session["trip_info"][field] = request.selected_option
    
    # 调用 LLM 解析意图
    llm_result = await llm_service.parse_intent(
        request.message,
        history=session["history"],
        current_trip_info=session["trip_info"]
    )
    
    if llm_result.get("status") == "error":
        raise HTTPException(status_code=500, detail=llm_result.get("message"))
    
    # 更新会话中的行程信息
    updated_trip_info = llm_result.get("trip_info", {})
    if updated_trip_info:
        session["trip_info"] = llm_service.merge_trip_info(session["trip_info"], updated_trip_info)
    
    # 更新历史
    session["history"].append({"role": "user", "content": request.message})
    session["history"].append({"role": "assistant", "content": llm_result.get("message", "")})
    
    # 准备响应
    response_type = "clarify" if llm_result.get("status") == "need_clarify" else "result"
    
    flights = []
    is_mocked = False
    debug_info = None
    
    # 如果信息完整，执行搜索
    if response_type == "result":
        search_res = await flight_search_service.search(session["trip_info"])
        
        if search_res.get("success") and search_res.get("flights"):
            flights = search_res["flights"]
        else:
            # 如果搜索无结果，执行 Mock
            mock_res = await flight_mock_service.mock_flight(
                dep_city=session["trip_info"].get("departure_code"),
                arr_city=session["trip_info"].get("arrival_code"),
                dep_date=session["trip_info"].get("dep_date"),
                travel_type=session["trip_info"].get("travel_type", "OW"),
                return_date=session["trip_info"].get("return_date"),
                flight_no=session["trip_info"].get("flight_no"),
                airline_code=session["trip_info"].get("airline_code"),
                transfer_cities=session["trip_info"].get("transfer_cities")
            )
            
            if mock_res.get("success"):
                # Mock 成功后再次搜索
                search_res_retry = await flight_search_service.search(session["trip_info"])
                if search_res_retry.get("success"):
                    flights = search_res_retry["flights"]
                    is_mocked = True
            
            # 记录调试信息
            debug_info = DebugInfo(
                mock_request=mock_res.get("mock_request"),
                search_response=search_res.get("raw_response")
            )

    # 保存会话状态
    if response_type == "clarify" and llm_result.get("clarify"):
        session["last_clarify_field"] = llm_result["clarify"].get("field")
    else:
        session["last_clarify_field"] = None
        
    sessions[session_id] = session
    
    return ChatResponse(
        session_id=session_id,
        type=response_type,
        message=llm_result.get("message", ""),
        trip_info=TripInfo(**session["trip_info"]) if session["trip_info"] else None,
        clarify=llm_result.get("clarify"),
        flights=flights,
        is_mocked=is_mocked,
        debug_info=debug_info
    )

@router.post("/session/new")
async def create_session():
    """创建新会话"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "history": [],
        "trip_info": {}
    }
    return {"session_id": session_id}

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """获取会话信息"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]
