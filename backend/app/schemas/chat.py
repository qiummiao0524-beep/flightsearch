"""对话相关的数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class PassengerInfo(BaseModel):
    """乘客信息"""
    type: Literal["ADT", "CHD", "INF"] = Field(description="乘客类型: ADT成人/CHD儿童/INF婴儿")
    count: int = Field(ge=0, description="乘客数量")


class AirportInfo(BaseModel):
    """机场信息"""
    city: str = Field(description="城市名称")
    code: str = Field(description="机场三字码")
    name: Optional[str] = Field(default=None, description="机场名称")


class TripInfo(BaseModel):
    """行程信息"""
    travel_type: Literal["OW", "RT", "OJ"] = Field(description="行程类型: OW单程/RT往返/OJ缺口程")
    departure: Optional[AirportInfo] = Field(default=None, description="出发地")
    arrival: Optional[AirportInfo] = Field(default=None, description="目的地")
    dep_date: Optional[str] = Field(default=None, description="出发日期 yyyy-MM-dd")
    return_date: Optional[str] = Field(default=None, description="返程日期 yyyy-MM-dd")
    passengers: list[PassengerInfo] = Field(default_factory=lambda: [PassengerInfo(type="ADT", count=1)])
    cabin_class: str = Field(default="Y", description="舱位等级: Y经济/C公务/F头等/S超经/ALL全部")
    cabin_name: Optional[str] = Field(default="经济舱", description="舱位名称")
    airline_code: Optional[str] = Field(default=None, description="航司二字码")
    flight_no: Optional[str] = Field(default=None, description="航班号，支持用/分割表示中转航班")
    transfer_cities: Optional[list[str]] = Field(default=None, description="中转城市三字码列表")


class ClarifyOption(BaseModel):
    """澄清选项"""
    label: str = Field(description="显示文本")
    value: str = Field(description="选项值")


class ClarifyInfo(BaseModel):
    """澄清信息"""
    field: str = Field(description="需要澄清的字段")
    question: str = Field(description="澄清问题")
    options: list[ClarifyOption] = Field(description="选项列表")


class FlightSegment(BaseModel):
    """航段信息"""
    sequence: int = Field(description="航段序号")
    flight_no: str = Field(description="航班号")
    airline: dict = Field(description="航司信息 {code, name}")
    departure: dict = Field(description="出发信息 {code, city, name, time, terminal}")
    arrival: dict = Field(description="到达信息 {code, city, name, time, terminal}")
    duration: str = Field(description="飞行时长(分钟)")
    equip: Optional[str] = Field(default=None, description="机型")
    is_transfer: bool = Field(default=False, description="是否为中转段")


class FlightInfo(BaseModel):
    """航班信息"""
    id: str = Field(description="航班唯一标识")
    type: str = Field(description="行程类型")
    travel_type: str = Field(default="OW", description="单程(OW)或往返(RT)")
    segments: list[FlightSegment] = Field(description="航段列表")
    is_transfer: bool = Field(default=False, description="是否中转")
    cabin_class: str = Field(description="舱位等级")
    cabin_num: Optional[str] = Field(default=None, description="剩余座位")
    price: dict = Field(description="价格信息 {total, base, tax, currency}")
    services: list[str] = Field(default_factory=list, description="服务列表")
    labels: list[dict] = Field(default_factory=list, description="标签列表")


class ChatRequest(BaseModel):
    """对话请求"""
    session_id: Optional[str] = Field(default=None, description="会话ID，首次对话可为空")
    message: str = Field(description="用户消息")
    selected_option: Optional[str] = Field(default=None, description="用户选择的澄清选项值")


class DebugInfo(BaseModel):
    """调试信息"""
    mock_request: Optional[dict] = Field(default=None, description="Mock 请求数据")
    search_response: Optional[dict] = Field(default=None, description="搜索接口原始返回")


class ChatResponse(BaseModel):
    """对话响应"""
    session_id: str = Field(description="会话ID")
    type: Literal["clarify", "result", "searching", "mocking", "error"] = Field(
        description="响应类型: clarify需要澄清/result搜索结果/searching搜索中/mocking正在Mock/error错误"
    )
    message: str = Field(description="响应消息")
    trip_info: Optional[TripInfo] = Field(default=None, description="解析出的行程信息")
    clarify: Optional[ClarifyInfo] = Field(default=None, description="澄清信息")
    flights: list[FlightInfo] = Field(default_factory=list, description="航班列表")
    is_mocked: bool = Field(default=False, description="数据是否来自Mock")
    debug_info: Optional[DebugInfo] = Field(default=None, description="调试信息（无结果时返回）")
