"""对话 API 路由"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
import json
import asyncio

from app.schemas.chat import ChatRequest, ChatResponse, TripInfo, ClarifyInfo, FlightInfo, DebugInfo
from app.services.llm_service import llm_service
from app.services.flight_search import flight_search_service
from app.services.flight_mock import flight_mock_service
from app.core.config import settings

def extract_mock_flights(mock_request: dict, travel_type: str = "OW", passengers: list = None) -> list:
    """从 Mock 请求中直接提取结构化的航班数据"""
    segments_map = mock_request.get("segments", {})
    trip_products = mock_request.get("tripProduct", {}).get("tripProducts", [])
    req_passengers = mock_request.get("searchParamRequest", {}).get("userCommonReq", {}).get("reqPassengers", [{"passengerType": "ADT", "passengerCount": 1}])
    passenger_counts = {p.get("passengerType"): p.get("passengerCount") for p in req_passengers}
    
    flights = []
    for tp in trip_products:
        flight_segments = []
        for fk in tp.get("flightKeys", []):
            segment_key = str(fk.get("flightKey"))
            segment = segments_map.get(segment_key)
            if segment:
                # 转换时间格式: 202602241200 -> 2026-02-24 12:00:00
                dep_dt = segment.get("depDateTime", "")
                dep_time = f"{dep_dt[:4]}-{dep_dt[4:6]}-{dep_dt[6:8]} {dep_dt[8:10]}:{dep_dt[10:12]}:00" if len(dep_dt) >= 12 else dep_dt
                
                arr_dt = segment.get("arrDateTime", "")
                arr_time = f"{arr_dt[:4]}-{arr_dt[4:6]}-{arr_dt[6:8]} {arr_dt[8:10]}:{arr_dt[10:12]}:00" if len(arr_dt) >= 12 else arr_dt
                
                flight_segments.append({
                    "sequence": fk.get("index", 1),
                    "flight_no": segment.get("operatingFlightNo", ""),
                    "airline": {
                        "code": segment.get("marketingAirCode", ""),
                        "name": segment.get("marketingAirline", "")
                    },
                    "departure": {
                        "code": segment.get("depAirportCode", ""),
                        "city": segment.get("depCityCode", ""),
                        "name": segment.get("depAirportCode", ""),
                        "terminal": segment.get("depAirportTerm", ""),
                        "time": dep_time
                    },
                    "arrival": {
                        "code": segment.get("arrAirportCode", ""),
                        "city": segment.get("arrCityCode", ""),
                        "name": segment.get("arrAirportCode", ""),
                        "terminal": segment.get("arrAirportTerm", ""),
                        "time": arr_time
                    },
                    "duration": str(segment.get("duration", 0)),
                    "equip": "",
                    "is_transfer": fk.get("index", 1) > 1
                })
        
        # 提取价格
        min_price = tp.get("minPrice", 0)
        price_details = tp.get("priceDetails", {})
<<<<<<< HEAD
        first_detail = list(price_details.values())[0] if isinstance(price_details, dict) and price_details else {}
        
        req_passengers = {p.get("type", "ADT"): p.get("count", 1) for p in (passengers or [{"type": "ADT", "count": 1}])}
        total_amount = 0
        total_base = 0
        total_tax = 0
        passenger_prices = []
        
        for ptype, count in req_passengers.items():
            if count <= 0: continue
            
            # Map ADT -> adultPrice, CHD -> childPrice, INF -> infantPrice
            if ptype == "ADT":
                key = "adultPrice"
            elif ptype == "CHD":
                key = "childPrice"
            elif ptype == "INF":
                key = "infantPrice"
            else:
                key = f"{ptype.lower()}Price"
                
            p_price = first_detail.get(key, {})
            if not p_price and ptype == "ADT":
                p_price = first_detail.get("adultPrice", {})
            if p_price:
                base = p_price.get("price", 0)
                tax = p_price.get("tax", 0)
                total = p_price.get("totalPrice", base + tax)
                total_base += base * count
                total_tax += tax * count
                total_amount += total * count
                passenger_prices.append({
                    "type": ptype,
                    "count": count,
                    "base": str(base),
                    "tax": str(tax),
                    "total": str(total)
                })
        
        if total_amount == 0:
            adult_price = first_detail.get("adultPrice", {})
            total_amount = adult_price.get("totalPrice", min_price)
            total_base = adult_price.get("price", min_price - 364 if min_price > 364 else min_price)
            total_tax = adult_price.get("tax", 364)
            passenger_prices = [{"type": "ADT", "count": 1, "base": str(total_base), "tax": str(total_tax), "total": str(total_amount)}]
=======
        
        price_breakdown = []
        total_price_grand = 0
        total_tax_grand = 0
        total_base_grand = 0
        
        first_detail = list(price_details.values())[0] if isinstance(price_details, dict) and price_details else {}
        
        for p_type, count in passenger_counts.items():
            if count <= 0: continue
            
            key_map = {"ADT": "adultPrice", "CHD": "childPrice", "INF": "infantPrice"}
            price_key = key_map.get(p_type)
            if price_key and price_key in first_detail:
                p_detail = first_detail[price_key]
                p_total = p_detail.get("totalPrice", 0)
                p_base = p_detail.get("price", 0)
                p_tax = p_detail.get("tax", 0)
                
                total_price_grand += p_total * count
                total_base_grand += p_base * count
                total_tax_grand += p_tax * count
                
                price_breakdown.append({
                    "type": p_type,
                    "count": count,
                    "base": str(p_base),
                    "tax": str(p_tax),
                    "total": str(p_total)
                })

        if not price_breakdown:
            adult_price = first_detail.get("adultPrice", {})
            total_price_grand = adult_price.get("totalPrice", min_price)
            total_base_grand = adult_price.get("price", min_price - 364 if min_price > 364 else min_price)
            total_tax_grand = adult_price.get("tax", 364)
        
        cabin_class = first_detail.get("cabinClass", "Y") if first_detail else "Y"
        cabin_num = first_detail.get("cabinNum", "") if first_detail else ""
        cabin_name = first_detail.get("cabinName", "经济舱") if first_detail else "经济舱"
>>>>>>> develop
        
        flights.append({
            "id": tp.get("flightNoGroup", ""),
            "type": "INTL_NORMAL",
            "travel_type": travel_type,
            "segments": flight_segments,
            "is_transfer": len(flight_segments) > 1,
            "cabin_class": cabin_class,
            "cabin_name": cabin_name,
            "cabin_num": cabin_num,
            "price": {
<<<<<<< HEAD
                "total": str(total_amount),
                "base": str(total_base),
                "tax": str(total_tax),
                "currency": "CNY",
                "passenger_prices": passenger_prices
=======
                "total": str(total_price_grand),
                "base": str(total_base_grand),
                "tax": str(total_tax_grand),
                "currency": "CNY",
                "passengers": price_breakdown
>>>>>>> develop
            },
            "services": [],
            "labels": []
        })
        
    return flights

router = APIRouter()

# 内存会话存储 (简单实现)
sessions = {}

@router.post("/chat")
async def chat(request: ChatRequest):
    """对话接口 (流式进度版)"""
    async def event_generator():
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

        # 发送进度：正在解析意图
        yield f"data: {json.dumps({'type': 'progress', 'status': 'UNDERSTANDING', 'message': '正在解析您的航班需求...'})}\n\n"
        
        # 调用 LLM 解析意图
        llm_result = await llm_service.parse_intent(
            request.message,
            history=session["history"],
            current_trip_info=session["trip_info"]
        )
        
        if llm_result.get("status") == "error":
            yield f"data: {json.dumps({'type': 'error', 'message': llm_result.get('message')})}\n\n"
            return
        
        # 发送进度：意图解析完成
        yield f"data: {json.dumps({'type': 'progress', 'status': 'UNDERSTANDING_DONE', 'message': '需求理解完成，准备检索...'})}\n\n"

        # 更新会话中的行程信息
        updated_trip_info = llm_result.get("trip_info", {})
        if updated_trip_info:
            session["trip_info"] = llm_service.merge_trip_info(session["trip_info"], updated_trip_info)
        
        # 更新历史
        if "history" not in session: session["history"] = []
        session["history"].append({"role": "user", "content": request.message})
        session["history"].append({"role": "assistant", "content": llm_result.get("message", "")})
        
        # 准备响应
        response_type = "clarify" if llm_result.get("status") == "need_clarify" else "result"
        
        # 发送进度：提取到的需求内容，在此前置下发，让它紧贴着 UNDERSTANDING 节点展示
        if llm_result.get("message"):
            yield f"data: {json.dumps({'type': 'progress', 'status': 'UNDERSTANDING_DONE', 'message': llm_result.get('message')})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'progress', 'status': 'UNDERSTANDING_DONE', 'message': '需求理解完成'})}\n\n"
        
        # 短暂休眠1秒，让前端有足够的时间停顿在“理解完毕”这一步供用户阅读提取的文字，不要瞬间冲刷掉
        await asyncio.sleep(1.0)
        
        flights = []
        is_mocked = False
        debug_info = None
        
        # 如果信息完整，执行搜索
        if response_type == "result":
            # 检查是否强制 mock（如果用户指定了航班号或中转城市，大概率是为了造特定数据）
            force_mock = bool(session["trip_info"].get("flight_no") or session["trip_info"].get("transfer_cities"))
            
            if not force_mock:
                # 发送进度：正在检索
                yield f"data: {json.dumps({'type': 'progress', 'status': 'SEARCHING', 'message': '正在检索实时航线信息...'})}\n\n"
                search_res = await flight_search_service.search(session["trip_info"])
            else:
                search_res = {"success": False, "flights": []}
            
            if search_res.get("success") and search_res.get("flights"):
                flights = search_res["flights"]
            else:
                # 发送进度：正在 Mock
                msg = '未找到匹配航线，正在为您安排 Mock 数据...' if not force_mock else '正在为您生成符合条件的 Mock 数据...'
                yield f"data: {json.dumps({'type': 'progress', 'status': 'MOCKING', 'message': msg})}\n\n"
                
                dep_code = session["trip_info"].get("departure_code") or session["trip_info"].get("departure_city", "PEK")
                arr_code = session["trip_info"].get("arrival_code") or session["trip_info"].get("arrival_city", "SHA")
                
                # 如果搜索无结果，执行 Mock
                mock_res = await flight_mock_service.mock_flight(
                    dep_city=dep_code,
                    arr_city=arr_code,
                    dep_date=session["trip_info"].get("dep_date"),
                    travel_type=session["trip_info"].get("travel_type", "OW"),
                    return_date=session["trip_info"].get("return_date"),
                    flight_no=session["trip_info"].get("flight_no"),
                    airline_code=session["trip_info"].get("airline_code"),
                    transfer_cities=session["trip_info"].get("transfer_cities"),
                    passengers=session["trip_info"].get("passengers", [{"type": "ADT", "count": 1}]),
                    cabin_class=session["trip_info"].get("cabin_class"),
                    cabin_name=session["trip_info"].get("cabin_name")
                )
                
                if settings.DEBUG:
                    print(f"[Mock] mock_res success={mock_res.get('success')}, error={mock_res.get('error')}")
                
                # 无论二方 Mock 接口返回成功与否，利用已生成的 mock 数据供前端展示
                mock_request_data = mock_res.get("mock_request", {})
                if mock_request_data:
                    flights = extract_mock_flights(mock_request_data, session["trip_info"].get("travel_type", "OW"), session["trip_info"].get("passengers"))
                    is_mocked = True

                
                # 记录调试信息
                debug_info = {
                    "mock_request": mock_res.get("mock_request"),
                    "search_response": search_res.get("raw_response")
                }

        # 保存会话状态
        if response_type == "clarify" and llm_result.get("clarify"):
            session["last_clarify_field"] = llm_result["clarify"].get("field")
        else:
            session["last_clarify_field"] = None
            
        sessions[session_id] = session
        
        # 发送最终结果
        final_payload = {
            "type": "final",
            "session_id": session_id,
            "response_type": response_type,
            "message": llm_result.get("message", ""),
            "trip_info": session["trip_info"] if session["trip_info"] else None,
            "clarify": llm_result.get("clarify"),
            "flights": flights,
            "is_mocked": is_mocked,
            "debug_info": debug_info
        }
        yield f"data: {json.dumps(final_payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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
