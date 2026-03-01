"""航班 Mock 服务 - 调用二方 Mock 接口"""
import httpx
import random
from datetime import datetime
from typing import Optional
from app.core.config import settings


class FlightMockService:
    """航班 Mock 服务"""
    
    def __init__(self):
        self.api_url = settings.MOCK_API_URL

    def _build_price_detail(self, price: int, tax: int, passengers: list) -> dict:
            """构建多乘客价格明细"""
            price_detail = {
                "abnormal": False,
                "adultPrice": {
                    "QValue": 0,
                    "bidMaxPrice": price,
                    "bidMinPrice": price,
                    "enginePrice": price,
                    "gdsPrice": {"QValue": 0.0, "currency": "CNY", "netPrice": float(price), "netTax": float(tax)},
                    "merchantPrice": price,
                    "netPrice": price,
                    "passengerType": "ADT",
                    "price": price,
                    "tax": tax,
                    "totalPrice": price + tax
                }
            }
            
            all_price = 0
            for p in passengers:
                ptype = p.get("type", "ADT")
                count = p.get("count", 0)
                if count <= 0:
                    continue
                    
                if ptype == "ADT":
                    all_price += (price + tax) * count
                elif ptype == "CHD":
                    child_price = int(price * 0.75)
                    child_tax = int(tax / 2)
                    price_detail["childPrice"] = {
                        "QValue": 0,
                        "bidMaxPrice": child_price,
                        "bidMinPrice": child_price,
                        "enginePrice": child_price,
                        "gdsPrice": {"QValue": 0.0, "currency": "CNY", "netPrice": float(child_price), "netTax": float(child_tax)},
                        "merchantPrice": child_price,
                        "netPrice": child_price,
                        "passengerType": "CHD",
                        "price": child_price,
                        "tax": child_tax,
                        "totalPrice": child_price + child_tax
                    }
                    all_price += (child_price + child_tax) * count
                elif ptype == "INF":
                    infant_price = int(price * 0.1)
                    infant_tax = 0
                    price_detail["infantPrice"] = {
                        "QValue": 0,
                        "bidMaxPrice": infant_price,
                        "bidMinPrice": infant_price,
                        "enginePrice": infant_price,
                        "gdsPrice": {"QValue": 0.0, "currency": "CNY", "netPrice": float(infant_price), "netTax": float(infant_tax)},
                        "merchantPrice": infant_price,
                        "netPrice": infant_price,
                        "passengerType": "INF",
                        "price": infant_price,
                        "tax": infant_tax,
                        "totalPrice": infant_price + infant_tax
                    }
                    all_price += (infant_price + infant_tax) * count
                    
            price_detail["allPrice"] = all_price
            return price_detail

    
    def build_mock_request(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        travel_type: str = "OW",
        return_date: str = None,
        flight_no: str = None,
        airline_code: str = None,
        dep_time: str = "12:00",
        price: int = 1000,
        passengers: list = None
    ) -> dict:
        """构建 Mock 接口请求
        
        Args:
            dep_city: 出发城市三字码
            arr_city: 到达城市三字码
            dep_date: 出发日期 yyyy-MM-dd
            travel_type: 行程类型 OW/RT
            return_date: 返程日期（往返时）
            flight_no: 指定航班号
            airline_code: 指定航司
            dep_time: 出发时间
            price: 票价
            
        Returns:
            Mock 请求体
        """
        # 生成航班号（如未指定）
        if not flight_no:
            airline = airline_code or "9C"
            flight_no = f"{airline}{random.randint(1000, 9999)}"
        else:
            airline = flight_no[:2] if len(flight_no) >= 2 else "9C"
        
        trace_id = f"MOCK{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        
        if travel_type == "OW":
            return self._build_ow_mock_request(
                dep_city, arr_city, dep_date, flight_no, airline,
                dep_time, price, trace_id, passengers
            )
        else:  # RT
            return self._build_rt_mock_request(
                dep_city, arr_city, dep_date, return_date,
                flight_no, airline, dep_time, price, trace_id, passengers
            )
    
    def _build_ow_mock_request(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        flight_no: str,
        airline: str,
        dep_time: str,
        price: int,
        trace_id: str,
        passengers: list = None
    ) -> dict:
        """构建单程 Mock 请求"""
        passengers = passengers or [{"type": "ADT", "count": 1}]
        total_p_count = sum(p.get("count", 0) for p in passengers)

        # 生成 segment key
        segment_key = str(hash(f"{flight_no}_{dep_date}_{dep_time}") % (10**10))
        
        # 格式化时间
        dep_date_fmt = dep_date.replace("-", "")
        dep_datetime = f"{dep_date_fmt}{dep_time.replace(':', '')}"
        
        try:
            dep_timestamp = int(datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
        except:
            dep_timestamp = int(datetime.now().timestamp() * 1000)
            
        # 随机生成飞行时长（120分钟到300分钟之间）
        import random
        duration_minutes = random.randint(120, 300)
        arr_timestamp = dep_timestamp + duration_minutes * 60 * 1000
        
        # 格式化出抵达的日期和时间
        arr_dt = datetime.fromtimestamp(arr_timestamp / 1000)
        arr_datetime_fmt = arr_dt.strftime("%Y%m%d%H%M00")
        
        # 构建航段
        segment = {
            "aircraft": "A320",
            "arrAirportCode": arr_city,
            "arrAirportTerm": "T2",
            "arrCityCode": arr_city,
            "arrDateTime": arr_datetime_fmt,
            "arrTime": arr_timestamp,
            "depAirportCode": dep_city,
            "depAirportTerm": "T2",
            "depCityCode": dep_city,
            "depDateTime": dep_datetime,
            "depTime": dep_timestamp,
            "duration": duration_minutes,
            "flightShare": False,
            "key": segment_key,
            "marketingAirCode": airline,
            "marketingAirline": airline,
            "marketingFlightNo": flight_no,
            "mileage": 0,
            "operatingAirline": airline,
            "operatingFlightNo": flight_no,
            "stopTime": 0,
            "stops": []
        }
        
        # 构建价格详情
        price_detail_key = str(hash(f"{flight_no}_{price}") % (10**10))
        price_detail = self._build_price_detail(price, 364, passengers)
        price_detail.update({
            "cabinClass": "Y",
            "cabinNum": "9",
            "flightKeys": [{"flightKey": segment_key, "index": 1, "mainSegment": True, "airLineIndex": 1, "mainAirline": airline}],
            "id": price_detail_key,
            "merchantId": 317,
            "resourceType": "GW",
            "gds": "GW"
        })
        
        # 构建完整请求
        filter2 = f"{dep_city}-{arr_city}-{dep_date_fmt}"
        
        return {
            "filter2": filter2,
            "flatType": "TC",
            "resourceId": "EBOOKING-PRICING",
            "resourceType": "GW",
            "traceId": trace_id,
            "searchScene": "AUTOMATIC",
            "searchParamRequest": {
                "limitReq": {"maxAge": 0, "minAge": 0, "nations": []},
                "userCommonReq": {
                    "travelType": "OW",
                    "bookingClass": ["Y", "S", "C", "F"],
                    "passengerCount": total_p_count,
                    "reqPassengers": [
                        {"passengerType": p["type"], "passengerCount": p["count"]} for p in passengers
                    ],
                    "reqUserLines": [{
                        "index": 1,
                        "depCityCode": dep_city,
                        "arrCityCode": arr_city,
                        "depDate": f"{dep_date} 00:00:00.000"
                    }]
                }
            },
            "segments": {segment_key: segment},
            "tripProduct": {
                "traceId": trace_id,
                "createTime": int(datetime.now().timestamp() * 1000),
                "tripProducts": [{
                    "flightKeys": [{"flightKey": segment_key, "index": 1, "mainSegment": True, "airLineIndex": 1, "mainAirline": airline}],
                    "flightNoGroup": f"{flight_no}_{dep_date_fmt}",
                    "minPrice": price + 364,
                    "nearTakeoff": False,
                    "priceDetails": {price_detail_key: price_detail},
                    "ext": {"PGS_FLOW_SWITCH": "1"}
                }]
            },
            "ext": {
                "searchType": "AUTOMATIC",
                "FILTER2": filter2,
                "flatType": "TC"
            },
            "boardFlightNoGroup": "",
            "boardProductCode": "",
            "checkFlightNoGroup": ""
        }
    
    def _build_rt_mock_request(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        return_date: str,
        flight_no: str,
        airline: str,
        dep_time: str,
        price: int,
        trace_id: str,
        passengers: list = None
    ) -> dict:
        """构建往返 Mock 请求"""
        passengers = passengers or [{"type": "ADT", "count": 1}]
        total_p_count = sum(p.get("count", 0) for p in passengers)
        dep_date_fmt = dep_date.replace("-", "")
        return_date_fmt = return_date.replace("-", "") if return_date else dep_date_fmt
        
        # 生成去程航班号
        outbound_flight = flight_no
        # 生成返程航班号（航班号+1）
        try:
            inbound_num = int(flight_no[2:]) + 1
            inbound_flight = f"{airline}{inbound_num:04d}"
        except:
            inbound_flight = f"{airline}{random.randint(1000, 9999)}"
        
        # 生成 segment keys
        outbound_key = str(hash(f"{outbound_flight}_{dep_date}_{dep_time}") % (10**10))
        inbound_key = str(hash(f"{inbound_flight}_{return_date}_{dep_time}") % (10**10))
        
        dep_datetime = f"{dep_date_fmt}{dep_time.replace(':', '')}"
        return_datetime = f"{return_date_fmt}{dep_time.replace(':', '')}"
        
        try:
            dep_timestamp = int(datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
            return_timestamp = int(datetime.strptime(f"{return_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
        except:
            dep_timestamp = int(datetime.now().timestamp() * 1000)
            return_timestamp = dep_timestamp + 86400000
        
        # 去程航段
        outbound_segment = {
            "aircraft": "777",
            "arrAirportCode": arr_city,
            "arrAirportTerm": "T1",
            "arrCityCode": arr_city,
            "arrDateTime": dep_datetime,
            "arrTime": dep_timestamp,
            "depAirportCode": dep_city,
            "depAirportTerm": "T1",
            "depCityCode": dep_city,
            "depDateTime": dep_datetime,
            "depTime": dep_timestamp,
            "duration": 210,
            "flightShare": False,
            "key": outbound_key,
            "marketingAirCode": airline,
            "marketingAirline": airline,
            "marketingFlightNo": outbound_flight,
            "mileage": 0,
            "operatingAirline": airline,
            "operatingFlightNo": outbound_flight,
            "stopTime": 0,
            "stops": []
        }
        
        # 返程航段
        inbound_segment = {
            "aircraft": "777",
            "arrAirportCode": dep_city,
            "arrAirportTerm": "T1",
            "arrCityCode": dep_city,
            "arrDateTime": return_datetime,
            "arrTime": return_timestamp,
            "depAirportCode": arr_city,
            "depAirportTerm": "T1",
            "depCityCode": arr_city,
            "depDateTime": return_datetime,
            "depTime": return_timestamp,
            "duration": 210,
            "flightShare": False,
            "key": inbound_key,
            "marketingAirCode": airline,
            "marketingAirline": airline,
            "marketingFlightNo": inbound_flight,
            "mileage": 0,
            "operatingAirline": airline,
            "operatingFlightNo": inbound_flight,
            "stopTime": 0,
            "stops": []
        }
        
        # 价格详情（往返总价）
        price_detail_key = str(hash(f"{outbound_flight}_{inbound_flight}_{price}") % (10**10))
        total_price = price * 2 + 100  # 基准往返总价（成人），这里改用统一计算
        
        price_detail = self._build_price_detail(total_price - 50, 50, passengers) # 调整基础价格匹配原来的 RT 格式
        price_detail.update({
            "cabinClass": "Y",
            "cabinNum": "9",
            "flightKeys": [
                {"flightKey": outbound_key, "index": 1, "mainSegment": True, "airLineIndex": 1, "mainAirline": airline},
                {"flightKey": inbound_key, "index": 2, "mainSegment": True, "airLineIndex": 2, "mainAirline": airline}
            ],
            "id": price_detail_key,
            "merchantId": 1047258,
            "resourceType": "TCPL",
            "gds": "TCPL"
        })
        
        filter2 = f"{dep_city}-{arr_city}-{dep_date_fmt}-{return_date_fmt}"
        
        return {
            "filter2": filter2,
            "flatType": "TC",
            "resourceId": "EBOOKING-PRICING",
            "resourceType": "TCPL",
            "traceId": trace_id,
            "searchScene": "NORMAL",
            "searchParamRequest": {
                "limitReq": {"maxAge": 0, "minAge": 0, "nations": []},
                "userCommonReq": {
                    "travelType": "RT",
                    "bookingClass": ["Y", "S", "C", "F"],
                    "passengerCount": total_p_count,
                    "reqPassengers": [
                        {"passengerType": p["type"], "passengerCount": p["count"]} for p in passengers
                    ],
                    "reqUserLines": [
                        {"index": 1, "depCityCode": dep_city, "arrCityCode": arr_city, "depDate": f"{dep_date} 00:00:00.000"},
                        {"index": 2, "depCityCode": arr_city, "arrCityCode": dep_city, "depDate": f"{return_date} 00:00:00.000"}
                    ]
                }
            },
            "segments": {
                outbound_key: outbound_segment,
                inbound_key: inbound_segment
            },
            "tripProduct": {
                "traceId": trace_id,
                "createTime": int(datetime.now().timestamp() * 1000),
                "tripProducts": [{
                    "flightKeys": [
                        {"flightKey": outbound_key, "index": 1, "mainSegment": True, "airLineIndex": 1, "mainAirline": airline},
                        {"flightKey": inbound_key, "index": 2, "mainSegment": True, "airLineIndex": 2, "mainAirline": airline}
                    ],
                    "flightNoGroup": f"{outbound_flight}_{dep_date_fmt}|{inbound_flight}_{return_date_fmt}",
                    "minPrice": total_price,
                    "nearTakeoff": False,
                    "priceDetails": {price_detail_key: price_detail},
                    "ext": {"PGS_FLOW_SWITCH": "1"}
                }]
            },
            "ext": {
                "searchType": "NORMAL",
                "FILTER2": filter2,
                "flatType": "TC"
            },
            "boardFlightNoGroup": "",
            "boardProductCode": "",
            "checkFlightNoGroup": ""
        }
    
    def _build_transfer_ow_mock_request(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        flight_nos: list[str],
        transfer_cities: list[str],
        dep_time: str,
        price: int,
        trace_id: str,
        passengers: list = None
    ) -> dict:
        """构建中转单程 Mock 请求
        
        Args:
            dep_city: 出发城市三字码
            arr_city: 到达城市三字码
            dep_date: 出发日期 yyyy-MM-dd
            flight_nos: 航班号列表，如 ["MU5001", "MU5002"]
            transfer_cities: 中转城市三字码列表，如 ["BKK"]
            dep_time: 出发时间
            price: 票价
            trace_id: 追踪ID
            passengers: 乘客信息列表
        """
        passengers = passengers or [{"type": "ADT", "count": 1}]
        total_p_count = sum(p.get("count", 0) for p in passengers)
        
        dep_date_fmt = dep_date.replace("-", "")
        
        # 构建城市列表：出发 -> 中转1 -> 中转2 -> ... -> 到达
        cities = [dep_city] + transfer_cities + [arr_city]
        
        # 确保航班数与航段数匹配
        num_segments = len(cities) - 1
        if len(flight_nos) < num_segments:
            # 补齐航班号
            airline = flight_nos[0][:2] if flight_nos else "MU"
            for i in range(len(flight_nos), num_segments):
                flight_nos.append(f"{airline}{random.randint(1000, 9999)}")
        
        segments = {}
        segment_keys = []
        flight_key_list = []
        
        # 计算每段的时间间隔（假设每段2小时飞行 + 1.5小时中转）
        try:
            base_timestamp = int(datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
        except:
            base_timestamp = int(datetime.now().timestamp() * 1000)
        
        FLIGHT_DURATION_MS = 2 * 60 * 60 * 1000  # 2小时
        TRANSFER_TIME_MS = 90 * 60 * 1000  # 1.5小时
        
        for i in range(num_segments):
            from_city = cities[i]
            to_city = cities[i + 1]
            flight_no = flight_nos[i]
            airline = flight_no[:2] if len(flight_no) >= 2 else "MU"
            
            # 计算时间
            seg_dep_timestamp = base_timestamp + i * (FLIGHT_DURATION_MS + TRANSFER_TIME_MS)
            seg_arr_timestamp = seg_dep_timestamp + FLIGHT_DURATION_MS
            
            seg_dep_dt = datetime.fromtimestamp(seg_dep_timestamp / 1000)
            seg_arr_dt = datetime.fromtimestamp(seg_arr_timestamp / 1000)
            
            seg_dep_datetime = seg_dep_dt.strftime("%Y%m%d%H%M")
            seg_arr_datetime = seg_arr_dt.strftime("%Y%m%d%H%M")
            
            segment_key = str(hash(f"{flight_no}_{from_city}_{to_city}_{i}") % (10**10))
            segment_keys.append(segment_key)
            
            segment = {
                "aircraft": "A320",
                "arrAirportCode": to_city,
                "arrAirportTerm": "T2",
                "arrCityCode": to_city,
                "arrDateTime": seg_arr_datetime,
                "arrTime": seg_arr_timestamp,
                "depAirportCode": from_city,
                "depAirportTerm": "T2",
                "depCityCode": from_city,
                "depDateTime": seg_dep_datetime,
                "depTime": seg_dep_timestamp,
                "duration": 120,  # 2小时
                "flightShare": False,
                "key": segment_key,
                "marketingAirCode": airline,
                "marketingAirline": airline,
                "marketingFlightNo": flight_no,
                "mileage": 0,
                "operatingAirline": airline,
                "operatingFlightNo": flight_no,
                "stopTime": 0 if i == 0 else int(TRANSFER_TIME_MS / 60000),  # 中转等待时间（分钟）
                "stops": []
            }
            
            segments[segment_key] = segment
            flight_key_list.append({
                "flightKey": segment_key,
                "index": i + 1,
                "mainSegment": i == 0,
                "airLineIndex": 1,
                "mainAirline": airline
            })
        
        # 价格详情
        price_detail_key = str(hash(f"{'_'.join(flight_nos)}_{price}") % (10**10))
        price_detail = self._build_price_detail(price, 364, passengers)
        price_detail.update({
            "cabinClass": "Y",
            "cabinNum": "9",
            "flightKeys": flight_key_list,
            "id": price_detail_key,
            "merchantId": 317,
            "resourceType": "GW",
            "gds": "GW"
        })
        
        # 构建完整请求
        filter2 = f"{dep_city}-{arr_city}-{dep_date_fmt}"
        flight_no_group = "_".join([f"{fn}_{dep_date_fmt}" for fn in flight_nos])
        
        return {
            "filter2": filter2,
            "flatType": "TC",
            "resourceId": "EBOOKING-PRICING",
            "resourceType": "GW",
            "traceId": trace_id,
            "searchScene": "AUTOMATIC",
            "searchParamRequest": {
                "limitReq": {"maxAge": 0, "minAge": 0, "nations": []},
                "userCommonReq": {
                    "travelType": "OW",
                    "bookingClass": ["Y", "S", "C", "F"],
                    "passengerCount": total_p_count,
                    "reqPassengers": [
                        {"passengerType": p["type"], "passengerCount": p["count"]} for p in passengers
                    ],
                    "reqUserLines": [{
                        "index": 1,
                        "depCityCode": dep_city,
                        "arrCityCode": arr_city,
                        "depDate": f"{dep_date} 00:00:00.000"
                    }]
                }
            },
            "segments": segments,
            "tripProduct": {
                "traceId": trace_id,
                "createTime": int(datetime.now().timestamp() * 1000),
                "tripProducts": [{
                    "flightKeys": flight_key_list,
                    "flightNoGroup": flight_no_group,
                    "minPrice": price + 364,
                    "nearTakeoff": False,
                    "priceDetails": {price_detail_key: price_detail},
                    "ext": {"PGS_FLOW_SWITCH": "1"}
                }]
            },
            "ext": {
                "searchType": "AUTOMATIC",
                "FILTER2": filter2,
                "flatType": "TC"
            },
            "boardFlightNoGroup": "",
            "boardProductCode": "",
            "checkFlightNoGroup": ""
        }
    
    def _build_transfer_rt_mock_request(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        return_date: str,
        flight_nos: list[str],
        transfer_cities: list[str],
        dep_time: str,
        price: int,
        trace_id: str,
        passengers: list = None
    ) -> dict:
        """构建中转往返 Mock 请求"""
        passengers = passengers or [{"type": "ADT", "count": 1}]
        total_p_count = sum(p.get("count", 0) for p in passengers)
        
        dep_date_fmt = dep_date.replace("-", "")
        return_date_fmt = return_date.replace("-", "") if return_date else dep_date_fmt
        
        # 构建去程城市列表：出发 -> 中转1 -> ... -> 到达
        outbound_cities = [dep_city] + transfer_cities + [arr_city]
        num_outbound_segments = len(outbound_cities) - 1
        
        # 构建返程城市列表：到达 -> 中转N -> ... -> 出发
        inbound_cities = [arr_city] + list(reversed(transfer_cities)) + [dep_city]
        num_inbound_segments = len(inbound_cities) - 1
        
        total_segments = num_outbound_segments + num_inbound_segments
        
        # 补齐航班号
        if len(flight_nos) < total_segments:
            airline = flight_nos[0][:2] if flight_nos else "MU"
            for i in range(len(flight_nos), total_segments):
                flight_nos.append(f"{airline}{random.randint(1000, 9999)}")
        
        segments = {}
        flight_key_list = []
        outbound_flight_group = []
        inbound_flight_group = []
        
        try:
            out_base_timestamp = int(datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
            in_base_timestamp = int(datetime.strptime(f"{return_date} {dep_time}", "%Y-%m-%d %H:%M").timestamp() * 1000)
        except:
            out_base_timestamp = int(datetime.now().timestamp() * 1000)
            in_base_timestamp = out_base_timestamp + 86400000

        FLIGHT_DURATION_MS = 2 * 60 * 60 * 1000
        TRANSFER_TIME_MS = 90 * 60 * 1000
        
        segment_index = 1
        
        # 生成去程
        for i in range(num_outbound_segments):
            from_city = outbound_cities[i]
            to_city = outbound_cities[i + 1]
            flight_no = flight_nos[i]
            airline = flight_no[:2] if len(flight_no) >= 2 else "MU"
            
            seg_dep_timestamp = out_base_timestamp + i * (FLIGHT_DURATION_MS + TRANSFER_TIME_MS)
            seg_arr_timestamp = seg_dep_timestamp + FLIGHT_DURATION_MS
            seg_dep_dt = datetime.fromtimestamp(seg_dep_timestamp / 1000)
            seg_arr_dt = datetime.fromtimestamp(seg_arr_timestamp / 1000)
            
            segment_key = str(hash(f"OUT_{flight_no}_{from_city}_{to_city}_{i}") % (10**10))
            
            segment = {
                "aircraft": "A320",
                "arrAirportCode": to_city,
                "arrAirportTerm": "T2",
                "arrCityCode": to_city,
                "arrDateTime": seg_arr_dt.strftime("%Y%m%d%H%M"),
                "arrTime": seg_arr_timestamp,
                "depAirportCode": from_city,
                "depAirportTerm": "T2",
                "depCityCode": from_city,
                "depDateTime": seg_dep_dt.strftime("%Y%m%d%H%M"),
                "depTime": seg_dep_timestamp,
                "duration": 120,
                "flightShare": False,
                "key": segment_key,
                "marketingAirCode": airline,
                "marketingAirline": airline,
                "marketingFlightNo": flight_no,
                "mileage": 0,
                "operatingAirline": airline,
                "operatingFlightNo": flight_no,
                "stopTime": 0 if i == 0 else int(TRANSFER_TIME_MS / 60000),
                "stops": []
            }
            segments[segment_key] = segment
            flight_key_list.append({
                "flightKey": segment_key,
                "index": segment_index,
                "mainSegment": i == 0,
                "airLineIndex": 1,
                "mainAirline": airline if i == 0 else ""
            })
            outbound_flight_group.append(f"{flight_no}_{dep_date_fmt}")
            segment_index += 1
            
        # 生成返程
        for i in range(num_inbound_segments):
            from_city = inbound_cities[i]
            to_city = inbound_cities[i + 1]
            flight_no = flight_nos[num_outbound_segments + i]
            airline = flight_no[:2] if len(flight_no) >= 2 else "MU"
            
            seg_dep_timestamp = in_base_timestamp + i * (FLIGHT_DURATION_MS + TRANSFER_TIME_MS)
            seg_arr_timestamp = seg_dep_timestamp + FLIGHT_DURATION_MS
            seg_dep_dt = datetime.fromtimestamp(seg_dep_timestamp / 1000)
            seg_arr_dt = datetime.fromtimestamp(seg_arr_timestamp / 1000)
            
            segment_key = str(hash(f"IN_{flight_no}_{from_city}_{to_city}_{i}") % (10**10))
            
            segment = {
                "aircraft": "A320",
                "arrAirportCode": to_city,
                "arrAirportTerm": "T2",
                "arrCityCode": to_city,
                "arrDateTime": seg_arr_dt.strftime("%Y%m%d%H%M"),
                "arrTime": seg_arr_timestamp,
                "depAirportCode": from_city,
                "depAirportTerm": "T2",
                "depCityCode": from_city,
                "depDateTime": seg_dep_dt.strftime("%Y%m%d%H%M"),
                "depTime": seg_dep_timestamp,
                "duration": 120,
                "flightShare": False,
                "key": segment_key,
                "marketingAirCode": airline,
                "marketingAirline": airline,
                "marketingFlightNo": flight_no,
                "mileage": 0,
                "operatingAirline": airline,
                "operatingFlightNo": flight_no,
                "stopTime": 0 if i == 0 else int(TRANSFER_TIME_MS / 60000),
                "stops": []
            }
            segments[segment_key] = segment
            flight_key_list.append({
                "flightKey": segment_key,
                "index": segment_index,
                "mainSegment": i == 0,
                "airLineIndex": 2,
                "mainAirline": airline if i == 0 else ""
            })
            inbound_flight_group.append(f"{flight_no}_{return_date_fmt}")
            segment_index += 1

        total_price = price * 2 + 100
        price_detail_key = str(hash(f"{'_'.join(flight_nos)}_{price}") % (10**10))
        price_detail = self._build_price_detail(price, 50, passengers)
        price_detail.update({
            "cabinClass": "Y",
            "cabinNum": "9",
            "flightKeys": flight_key_list,
            "id": price_detail_key,
            "merchantId": 1047258,
            "resourceType": "TCPL",
            "gds": "TCPL"
        })
        
        filter2 = f"{dep_city}-{arr_city}-{dep_date_fmt}-{return_date_fmt}"
        flight_no_group = "_".join(outbound_flight_group) + "|" + "_".join(inbound_flight_group)
        
        return {
            "filter2": filter2,
            "flatType": "TC",
            "resourceId": "EBOOKING-PRICING",
            "resourceType": "TCPL",
            "traceId": trace_id,
            "searchScene": "NORMAL",
            "searchParamRequest": {
                "limitReq": {"maxAge": 0, "minAge": 0, "nations": []},
                "userCommonReq": {
                    "travelType": "RT",
                    "bookingClass": ["Y", "S", "C", "F"],
                    "passengerCount": total_p_count,
                    "reqPassengers": [
                        {"passengerType": p["type"], "passengerCount": p["count"]} for p in passengers
                    ],
                    "reqUserLines": [
                        {"index": 1, "depCityCode": dep_city, "arrCityCode": arr_city, "depDate": f"{dep_date} 00:00:00.000"},
                        {"index": 2, "depCityCode": arr_city, "arrCityCode": dep_city, "depDate": f"{return_date} 00:00:00.000"}
                    ]
                }
            },
            "segments": segments,
            "tripProduct": {
                "traceId": trace_id,
                "createTime": int(datetime.now().timestamp() * 1000),
                "tripProducts": [{
                    "flightKeys": flight_key_list,
                    "flightNoGroup": flight_no_group,
                    "minPrice": total_price,
                    "nearTakeoff": False,
                    "priceDetails": {price_detail_key: price_detail},
                    "ext": {"PGS_FLOW_SWITCH": "1"}
                }]
            },
            "ext": {
                "searchType": "NORMAL",
                "FILTER2": filter2,
                "flatType": "TC"
            },
            "boardFlightNoGroup": "",
            "boardProductCode": "",
            "checkFlightNoGroup": ""
        }

    def _wrap_request(self, mock_data: dict) -> dict:
        """将 Mock 数据包装成接口需要的格式
        
        接口格式：
        {
            "requestBody": "航班数据协议（JSON字符串）",
            "wikiUrl": "/callBack/entity",
            "version": "1.0.0",
            "serviceName": "callBack"
        }
        """
        import json
        return {
            "requestBody": json.dumps(mock_data, ensure_ascii=False),
            "wikiUrl": "/callBack/entity",
            "version": "1.0.0",
            "serviceName": "callBack"
        }
    
    async def mock_flight(
        self,
        dep_city: str,
        arr_city: str,
        dep_date: str,
        travel_type: str = "OW",
        return_date: str = None,
        flight_no: str = None,
        airline_code: str = None,
        transfer_cities: list[str] = None,
        passengers: list = None
    ) -> dict:
        """调用 Mock 接口创建航班数据
        
        Args:
            dep_city: 出发城市三字码
            arr_city: 到达城市三字码
            dep_date: 出发日期 yyyy-MM-dd
            travel_type: 行程类型 OW/RT
            return_date: 返程日期（往返时）
            flight_no: 航班号，支持用 "/" 分割表示中转航班（如 "MU5001/MU5002"）
            airline_code: 航司代码
            transfer_cities: 中转城市三字码列表
        
        Returns:
            {success: bool, error: str}
        """
        trace_id = f"MOCK{datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]}"
        
        # 检查是否为中转航班（航班号包含 / 或是指定了中转城市）
        is_transfer = (flight_no and "/" in flight_no) or (transfer_cities and len(transfer_cities) > 0)
        
        if is_transfer:
            # 中转航班 Mock
            if flight_no and "/" in flight_no:
                flight_nos = [fn.strip() for fn in flight_no.split("/")]
            else:
                num_segments = (len(transfer_cities) + 1) * (2 if travel_type == "RT" else 1)
                airline = airline_code or "MU"
                flight_nos = [f"{airline}{1000 + i}" for i in range(num_segments)]
                
            # 确保 transfer_cities 存在且数量正确
            if not transfer_cities:
                if travel_type == "RT":
                    # 往返如果没给城市，假设单程的转机数为 (总段数/2)-1 或 至少1
                    num_transfers = max(1, len(flight_nos) // 2 - 1 if len(flight_nos) > 2 else len(flight_nos) - 1)
                else:
                    num_transfers = len(flight_nos) - 1
                    
                transfer_cities = [f"TR{i+1}" for i in range(num_transfers)]
            
            if travel_type == "OW":
                mock_data = self._build_transfer_ow_mock_request(
                    dep_city=dep_city,
                    arr_city=arr_city,
                    dep_date=dep_date,
                    flight_nos=flight_nos,
                    transfer_cities=transfer_cities,
                    dep_time="12:00",
                    price=1000,
                    trace_id=trace_id,
                    passengers=passengers
                )
            else:
                mock_data = self._build_transfer_rt_mock_request(
                    dep_city=dep_city,
                    arr_city=arr_city,
                    dep_date=dep_date,
                    return_date=return_date,
                    flight_nos=flight_nos,
                    transfer_cities=transfer_cities,
                    dep_time="12:00",
                    price=1000,
                    trace_id=trace_id,
                    passengers=passengers
                )
        else:
            # 普通航班 Mock
            mock_data = self.build_mock_request(
                dep_city=dep_city,
                arr_city=arr_city,
                dep_date=dep_date,
                travel_type=travel_type,
                return_date=return_date,
                flight_no=flight_no,
                airline_code=airline_code,
                passengers=passengers
            )
        
        # 包装成接口需要的格式
        request_body = self._wrap_request(mock_data)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url, 
                    json=request_body,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    resp_data = response.json()
                    # 检查响应：result=true 且 obj.success=true 表示成功
                    if resp_data.get("result") and resp_data.get("obj", {}).get("success"):
                        return {"success": True, "error": None, "mock_request": mock_data}
                    elif resp_data.get("result"):
                        # 接口调用成功但 Mock 失败
                        return {"success": True, "error": None, "mock_request": mock_data}  # 仍视为成功，因为数据已发送
                    else:
                        return {"success": False, "error": resp_data.get("message", "Mock 失败"), "mock_request": mock_data}
                else:
                    return {"success": False, "error": f"HTTP {response.status_code}", "mock_request": mock_data}
                    
        except Exception as e:
            return {"success": False, "error": str(e), "mock_request": mock_data}


# 全局单例
flight_mock_service = FlightMockService()
