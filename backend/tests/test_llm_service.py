import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    return LLMService()

@pytest.mark.asyncio
async def test_parse_intent_complete(llm_service, mocker):
    """测试完整信息的意图解析"""
    # 模拟 DeepSeek 的响应
    mock_content = {
        "status": "complete",
        "trip_info": {
            "travel_type": "OW",
            "departure_city": "上海",
            "departure_code": "SHA",
            "arrival_city": "香港",
            "arrival_code": "HKG",
            "dep_date": "2026-02-23",
            "return_date": None,
            "passengers": [{"type": "ADT", "count": 1}],
            "cabin_class": "Y",
            "cabin_name": "经济舱",
            "airline_code": None,
            "flight_no": None,
            "transfer_cities": None
        },
        "clarify": None,
        "message": "好的，正在为您搜索明天上海到香港的航班..."
    }
    
    # 模拟 OpenAI 客户端
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock()]
    mock_response.choices[0].message.content = json.dumps(mock_content)
    
    mocker.patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response)
    
    result = await llm_service.parse_intent("明天上海到香港")
    
    assert result["status"] == "complete"
    assert result["trip_info"]["departure_city"] == "上海"
    assert result["trip_info"]["arrival_city"] == "香港"
    assert result["trip_info"]["dep_date"] == "2026-02-23"

@pytest.mark.asyncio
async def test_parse_intent_need_clarify(llm_service, mocker):
    """测试信息缺失时的澄清逻辑"""
    mock_content = {
        "status": "need_clarify",
        "trip_info": {
            "travel_type": "OW",
            "departure_city": "上海",
            "departure_code": "SHA",
            "arrival_city": None,
            "arrival_code": None,
            "dep_date": "2026-02-23",
            "return_date": None,
            "passengers": [{"type": "ADT", "count": 1}],
            "cabin_class": "Y",
            "cabin_name": "经济舱",
            "airline_code": None,
            "flight_no": None,
            "transfer_cities": None
        },
        "clarify": {
            "field": "arrival_city",
            "question": "请问您想去哪个城市？",
            "options": []
        },
        "message": "好的，上海出发。请问您想去哪里呢？"
    }
    
    mock_response = mocker.Mock()
    mock_response.choices = [mocker.Mock()]
    mock_response.choices[0].message.content = json.dumps(mock_content)
    
    mocker.patch.object(llm_service.client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response)
    
    result = await llm_service.parse_intent("明天从上海出发")
    
    assert result["status"] == "need_clarify"
    assert result["clarify"]["field"] == "arrival_city"
    assert "去哪里" in result["message"]

@pytest.mark.asyncio
async def test_extract_json_with_markdown(llm_service):
    """测试从 Markdown 代码块中提取 JSON"""
    content = """
这里解析后的结果：
```json
{
  "status": "complete",
  "message": "OK"
}
```
祝您旅途愉快！
"""
    result = llm_service._extract_json(content)
    assert result["status"] == "complete"
    assert result["message"] == "OK"

def test_merge_trip_info(llm_service):
    """测试行程信息合并逻辑"""
    base = {"departure_city": "上海", "dep_date": None}
    update = {"dep_date": "2026-02-23", "passengers": [{"type": "ADT", "count": 2}]}
    
    result = llm_service.merge_trip_info(base, update)
    
    assert result["departure_city"] == "上海"
    assert result["dep_date"] == "2026-02-23"
    assert result["passengers"][0]["count"] == 2
