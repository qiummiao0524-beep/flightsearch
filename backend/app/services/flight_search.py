"""航班搜索服务 - 调用二方搜索接口"""
import asyncio
import httpx
from datetime import datetime
from typing import Optional
from app.core.config import settings


class FlightSearchService:
    """航班搜索服务"""
    
    def __init__(self):
        self.api_url = settings.SEARCH_API_URL
        self.api_token = settings.SEARCH_API_TOKEN
    
    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_token:
            headers["Labrador-Token"] = self.api_token
            headers["Labrador-Trace-Log"] = "true"
        return headers
    
    def build_search_request(
        self,
        trip_info: dict,
        user_line_index: int = 1,
        selected_lines: list = None,
        trace_id: str = None
    ) -> dict:
        """构建搜索请求
        
        Args:
            trip_info: 行程信息
            user_line_index: 当前查询的行程索引 (1=去程, 2=返程)
            selected_lines: 已选择的航班列表
            trace_id: 追踪ID，轮询时需要保持一致
        """
        # 构建行程路线
        req_user_lines = []
        travel_type = trip_info.get("travel_type", "OW")
        
        if travel_type == "OW":  # 单程
            req_user_lines = [{
                "index": 1,
                "depCityCode": trip_info.get("departure_code"),
                "arrCityCode": trip_info.get("arrival_code"),
                "depDate": trip_info.get("dep_date")
            }]
        elif travel_type == "RT":  # 往返
            req_user_lines = [
                {
                    "index": 1,
                    "depCityCode": trip_info.get("departure_code"),
                    "arrCityCode": trip_info.get("arrival_code"),
                    "depDate": trip_info.get("dep_date")
                },
                {
                    "index": 2,
                    "depCityCode": trip_info.get("arrival_code"),
                    "arrCityCode": trip_info.get("departure_code"),
                    "depDate": trip_info.get("return_date")
                }
            ]
        
        # 构建乘客信息
        passengers = trip_info.get("passengers", [{"type": "ADT", "count": 1}])
        req_passengers = []
        for p in passengers:
            req_passengers.append({
                "passengerType": p.get("type", "ADT"),
                "passengerCount": str(p.get("count", 1))
            })
        
        # 补齐乘客类型
        passenger_types = {p["passengerType"] for p in req_passengers}
        for ptype in ["ADT", "CHD", "INF"]:
            if ptype not in passenger_types:
                req_passengers.append({"passengerType": ptype, "passengerCount": "0"})
        
        # 构建舱位
        cabin_class = trip_info.get("cabin_class", "Y")
        if cabin_class == "ALL":
            booking_class = "Y|S|C|F"
        else:
            booking_class = cabin_class
        
        # 使用传入的 traceId 或生成新的
        if not trace_id:
            trace_id = f"AI{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        
        return {
            "travelType": travel_type,
            "reqUserLines": req_user_lines,
            "userLineIndex": user_line_index,
            "selectedLines": selected_lines or [],
            "reqPassengers": req_passengers,
            "bookingClass": booking_class,
            "scene": "",
            "platId": "984",
            "refId": "",
            "language": "zh_cn",
            "locale": "zh_cn",
            "currencyCode": "CNY",
            "selectClass": "",
            "blackHole": False,
            "deviceId": "",
            "buddha": "",
            "thunder": "",
            "recommendTag": "",
            "transitCityCodes": [],
            "traceId": trace_id,
            "memberInfo": {
                "memberId": "",
                "openId": "",
                "unionId": "",
                "userSign": "",
                "queryIp": "127.0.0.1"
            },
            "config": {
                "ab": {},
                "lat": "",
                "lon": "",
                "locType": "",
                "sortType": "DEFAULT"
            },
            "ext": {}
        }
    
    def transform_response(self, resp: dict) -> list:
        req_passengers_list = resp.get("data", resp).get("req", {}).get("userCommonReq", {}).get("reqPassengers", [])
        req_passengers = {p.get("passengerType", "ADT"): int(p.get("passengerCount", 1)) for p in req_passengers_list}
        """将二方接口响应转换为前端展示格式
        
        Args:
            resp: 搜索接口响应
            
        Returns:
            航班列表
        """
        flights = []
        
        if not resp.get("success") or not resp.get("route"):
            return flights
        
        req_travel_type = resp.get("data", resp).get("req", {}).get("userCommonReq", {}).get("travelType", "OW")
        
        route = resp["route"]
        segments_map = route.get("segments", {})
        
        for trip_product in route.get("tripProducts", []):
            trip = trip_product.get("trip", {})
            price_quote = trip_product.get("priceQuote", {})
            
            # 收集所有航段信息
            flight_segments = []
            for item in trip.get("items", []):
                for fk in item.get("flightKeys", []):
                    flight_key = str(fk.get("flightKey"))
                    segment = segments_map.get(flight_key)
                    if segment:
                        dep_station = segment.get("depStation", {})
                        arr_station = segment.get("arrStation", {})
                        
                        flight_segments.append({
                            "sequence": fk.get("sequence", 1),
                            "flight_no": segment.get("lineNo", ""),
                            "airline": {
                                "code": segment.get("mktCode", ""),
                                "name": segment.get("mktName", "")
                            },
                            "departure": {
                                "code": dep_station.get("stationCode", ""),
                                "city": dep_station.get("cityName", ""),
                                "name": dep_station.get("stationName", ""),
                                "terminal": dep_station.get("terminal", ""),
                                "time": segment.get("depDate", "")
                            },
                            "arrival": {
                                "code": arr_station.get("stationCode", ""),
                                "city": arr_station.get("cityName", ""),
                                "name": arr_station.get("stationName", ""),
                                "terminal": arr_station.get("terminal", ""),
                                "time": segment.get("arrDate", "")
                            },
                            "duration": str(segment.get("travelTime", 0)),
                            "equip": segment.get("equip", {}).get("craftName", "") if segment.get("equip") else "",
                            "is_transfer": fk.get("index", 1) > 1
                        })
            
            # 按 sequence 排序
            flight_segments.sort(key=lambda x: x["sequence"])
            
            # 判断是否中转
            is_transfer = trip.get("hasTransferItem", False) or len(flight_segments) > 1
            
            # 提取价格
            total_price_quote = price_quote.get("totalPrice", {})
            
            total_amount = 0
            total_base = 0
            total_tax = 0
            passenger_prices = []
            
            # 使用提取的请求乘客信息结构，如果没有就使用默认成人1
            pas_map = req_passengers if req_passengers else {"ADT": 1}
            
            for ptype, count in pas_map.items():
                if count <= 0: continue
                key = f"{ptype.lower()}Price" if ptype != "ADT" else "adultPrice"
                p_price = total_price_quote.get(key, {})
                if not p_price and ptype == "ADT":
                    p_price = total_price_quote.get("adultPrice", {})
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
                adult_price = total_price_quote.get("adultPrice", {})
                base = adult_price.get("price", 0)
                tax = adult_price.get("tax", 0)
                total = adult_price.get("totalPrice", base + tax)
                total_base = base
                total_tax = tax
                total_amount = total
            
            cabin_class_code = price_quote.get("cabinClassCode", "Y")
            cabin_name_map = {
                "Y": "经济舱",
                "S": "超级经济舱",
                "C": "商务舱",
                "F": "头等舱"
            }
            
            flights.append({
                "id": trip.get("id", ""),
                "type": trip.get("type", "INTL_NORMAL"),
                "travel_type": req_travel_type,
                "segments": flight_segments,
                "is_transfer": is_transfer,
                "cabin_class": cabin_class_code,
                "cabin_name": cabin_name_map.get(cabin_class_code, "经济舱"),
                "cabin_num": price_quote.get("cabinNum", ""),
                "price": {
                    "total": str(total_amount),
                    "base": str(total_base),
                    "tax": str(total_tax),
                    "foreign_total": total_price_quote.get("adultPrice", {}).get("foreignTotalPrice", "0"),
                    "currency": "CNY",
                    "passenger_prices": passenger_prices
                },
                "services": [],
                "labels": trip_product.get("labels", [])
            })
        
        return flights
    
    async def search(
        self,
        trip_info: dict,
        user_line_index: int = 1,
        selected_lines: list = None,
        max_retries: int = 20,
        trace_id: str = None
    ) -> dict:
        """执行搜索（支持轮询）
        
        搜索接口需要多次交互：
        - 利用 sleepTime 进行内部等待
        - 使用相同的 traceId 再次请求
        - 直到 finished 为 true 才停止
        
        Args:
            trip_info: 行程信息
            user_line_index: 当前查询行程索引
            selected_lines: 已选航班
            max_retries: 最大轮询次数，防止无限循环
            trace_id: 可选的 traceId（Mock 后重试搜索时使用 Mock 的 traceId）
            
        Returns:
            {success: bool, flights: list, raw_response: dict, error: str}
        """
        # 使用传入的 traceId 或生成新的
        if not trace_id:
            trace_id = f"AI{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        
        retry_count = 0
        last_resp_data = None
        
        try:
            start_time = datetime.now()
            async with httpx.AsyncClient(timeout=90.0) as client:
                while retry_count < max_retries:
                    retry_count += 1
                    
                    # 构建请求，使用相同的 traceId
                    request = self.build_search_request(
                        trip_info, 
                        user_line_index, 
                        selected_lines,
                        trace_id=trace_id
                    )
                    
                    if settings.DEBUG:
                        print(f"[Search] 第 {retry_count} 次请求, traceId={trace_id}")
                    
                    response = await client.post(
                        self.api_url, 
                        json=request,
                        headers=self._get_headers()
                    )
                    
                    if response.status_code != 200:
                        return {
                            "success": False,
                            "flights": [],
                            "raw_response": None,
                            "error": f"HTTP {response.status_code}"
                        }
                    
                    resp_json = response.json()
                    resp_data = resp_json.get("data", resp_json)
                    last_resp_data = resp_data
                    
                    if settings.DEBUG:
                        print(f"[Search] 响应: success={resp_data.get('success')}, "
                              f"finished={resp_data.get('finished')}, "
                              f"sleepTime={resp_data.get('sleepTime')}, "
                              f"resultCount={resp_data.get('resultCount')}")
                    
                    # 检查是否成功
                    if not resp_data.get("success"):
                        # 如果失败但有 sleepTime，可能需要继续等待
                        sleep_time = resp_data.get("sleepTime", 0)
                        if sleep_time > 0 and not resp_data.get("finished"):
                            await asyncio.sleep(sleep_time / 1000.0)
                            continue
                        
                        return {
                            "success": False,
                            "flights": [],
                            "raw_response": resp_data,
                            "error": resp_data.get("message", "搜索失败")
                        }
                    
                    # 检查是否完成
                    finished = resp_data.get("finished", False)
                    if finished:
                        # 使用最后一次的航班结果
                        flights = self.transform_response(resp_data)
                        duration = (datetime.now() - start_time).total_seconds()
                        if settings.DEBUG:
                            print(f"[Search] 搜索完成, 共 {len(flights)} 个航班, 耗时 {duration:.2f}s")
                        return {
                            "success": True,
                            "flights": flights,
                            "raw_response": resp_data,
                            "error": None
                        }
                    
                    # 获取等待时间
                    sleep_time = resp_data.get("sleepTime", 0)
                    if sleep_time > 0:
                        if settings.DEBUG:
                            print(f"[Search] 等待 {sleep_time}ms 后继续...")
                        await asyncio.sleep(sleep_time / 1000.0)
                    else:
                        # 没有 sleepTime 且未完成，等待一个默认时间
                        await asyncio.sleep(0.5)
                
                # 达到最大重试次数，返回最后一次的结果
                flights = self.transform_response(last_resp_data) if last_resp_data else []
                return {
                    "success": True,
                    "flights": flights,
                    "raw_response": last_resp_data,
                    "error": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "flights": [],
                "raw_response": last_resp_data,
                "error": str(e)
            }
    
    def filter_flights(
        self,
        flights: list,
        airline_code: str = None,
        flight_no: str = None,
        direct_only: bool = False
    ) -> list:
        """过滤航班
        
        Args:
            flights: 航班列表
            airline_code: 航司代码过滤
            flight_no: 航班号过滤
            direct_only: 仅直飞
        """
        result = flights
        
        if direct_only:
            result = [f for f in result if not f.get("is_transfer")]
        
        if airline_code:
            result = [
                f for f in result 
                if any(seg.get("airline", {}).get("code") == airline_code for seg in f.get("segments", []))
            ]
        
        if flight_no:
            flight_no_upper = flight_no.upper()
            result = [
                f for f in result
                if any(flight_no_upper in seg.get("flight_no", "").upper() for seg in f.get("segments", []))
            ]
        
        return result


# 全局单例
flight_search_service = FlightSearchService()
