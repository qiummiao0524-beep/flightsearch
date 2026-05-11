import pytest
import json
from app.services.flight_mock import flight_mock_service

def test_build_ow_direct():
    """测试单程直飞"""
    data = flight_mock_service.build_mock_request(
        dep_city="SHA",
        arr_city="BKK",
        dep_date="2026-03-24",
        travel_type="OW",
        flight_no="AC0030",
        price=100
    )
    
    # 验证基础结构
    assert data["searchParamRequest"]["userCommonReq"]["travelType"] == "OW"
    
    # 验证 Segment
    segments = data["segments"]
    assert len(segments) == 1
    seg = list(segments.values())[0]
    assert seg["depCityCode"] == "SHA"
    assert seg["arrCityCode"] == "BKK"
    assert seg["marketingFlightNo"] == "AC0030"
    
    # 验证 TripProduct -> flightKeys
    trip_product = data["tripProduct"]["tripProducts"][0]
    flight_keys = trip_product["flightKeys"]
    assert len(flight_keys) == 1
    assert flight_keys[0]["airLineIndex"] == 1
    assert flight_keys[0]["mainSegment"] is True
    assert flight_keys[0]["mainAirline"] == "AC"
    assert trip_product["flightNoGroup"] == "AC0030_20260324"


def test_build_ow_multi_transfer():
    """测试单程多中转 (如 CKG-TFU-BKK-KUL)"""
    # 假设使用 mock_flight 入口来触发中转逻辑
    # flight_nos = ["MU3333", "MU3344", "MU3355"]
    import asyncio
    
    async def run():
        res = await flight_mock_service.mock_flight(
            dep_city="CKG",
            arr_city="KUL",
            dep_date="2026-03-02",
            travel_type="OW",
            flight_no="MU3333/MU3344/MU3355",
            transfer_cities=["TFU", "BKK"]
        )
        return res
        
    res = asyncio.run(run())
    mock_req = res["mock_request"]
    
    assert mock_req["searchParamRequest"]["userCommonReq"]["travelType"] == "OW"
    
    # 验证 segments (3段)
    segments = mock_req["segments"]
    assert len(segments) == 3
    
    # 验证 TripProduct
    trip_product = mock_req["tripProduct"]["tripProducts"][0]
    flight_keys = trip_product["flightKeys"]
    assert len(flight_keys) == 3
    
    # 确保有且只有1个为主航段
    main_segments = [k for k in flight_keys if k["mainSegment"]]
    assert len(main_segments) == 1
    assert main_segments[0]["mainAirline"] == "MU"
    
    # 所有航段的 airLineIndex 应为 1
    for k in flight_keys:
        assert k["airLineIndex"] == 1

def test_build_rt_direct():
    """测试往返直飞"""
    import asyncio
    
    async def run():
        res = await flight_mock_service.mock_flight(
            dep_city="SHA",
            arr_city="HKG",
            dep_date="2026-03-05",
            return_date="2026-03-08",
            travel_type="RT",
            flight_no="KE6767|KE8877"
        )
        return res
        
    res = asyncio.run(run())
    mock_req = res["mock_request"]
    
    assert mock_req["searchParamRequest"]["userCommonReq"]["travelType"] == "RT"
    
    segments = mock_req["segments"]
    assert len(segments) == 2
    
    trip_product = mock_req["tripProduct"]["tripProducts"][0]
    flight_keys = trip_product["flightKeys"]
    
    # 判断是否准确分割去程与返程
    assert len(flight_keys) == 2
    assert flight_keys[0]["airLineIndex"] == 1
    assert flight_keys[1]["airLineIndex"] == 2
    assert flight_keys[0]["mainSegment"] is True
    assert flight_keys[1]["mainSegment"] is False  # 返程不是主航段
    assert trip_product["flightNoGroup"] == "KE6767_20260305|KE6768_20260308"


def test_build_rt_multi_transfer():
    """测试往返多中转 (去程2转+返程1转等场景)"""
    import asyncio
    
    async def run():
        res = await flight_mock_service.mock_flight(
            dep_city="SHA",
            arr_city="BKK",
            dep_date="2026-03-11",
            return_date="2026-03-14",
            travel_type="RT",
            flight_no="CA5543/CA6677/CA7788|HX4545/HX4588",
            transfer_cities=["HKG", "SGN", "MFM"] # 先不用严格对齐实际，只是测数据结构
        )
        return res
        
    res = asyncio.run(run())
    mock_req = res["mock_request"]
    
    assert mock_req["searchParamRequest"]["userCommonReq"]["travelType"] == "RT"
    
    # 3个中转城市: 去程4段 + 返程4段 = 8段
    segments = mock_req["segments"]
    assert len(segments) == 8
    
    trip_product = mock_req["tripProduct"]["tripProducts"][0]
    flight_keys = trip_product["flightKeys"]
    
    outbound_keys = [k for k in flight_keys if k["airLineIndex"] == 1]
    inbound_keys = [k for k in flight_keys if k["airLineIndex"] == 2]
    
    assert len(outbound_keys) == 4
    assert len(inbound_keys) == 4
    
    # 去程和返程应保证各有1个主航段
    assert len([k for k in outbound_keys if k["mainSegment"]]) == 1
    assert len([k for k in inbound_keys if k["mainSegment"]]) == 1

def test_build_layover():
    """测试经停"""
    data = flight_mock_service.build_mock_request(
        dep_city="SHA",
        arr_city="BKK",
        dep_date="2026-03-24",
        travel_type="OW",
        flight_no="AC0030",
        price=100
    )
    # TODO 在接下来的flight_mock.py重构中，要支持传递 layover
    # 我们将会在 build_route_segments 里解析特定的 stops 字段
    pass
