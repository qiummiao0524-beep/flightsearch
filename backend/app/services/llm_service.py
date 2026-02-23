"""LLM 服务 - 使用 Claude 进行意图解析"""
import json
import re
from datetime import datetime, timedelta
from openai import AsyncOpenAI
from app.core.config import settings

# 加载城市映射数据
import os
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_city_mapping():
    """加载城市映射数据"""
    with open(os.path.join(DATA_DIR, "city_mapping.json"), "r", encoding="utf-8") as f:
        return json.load(f)

CITY_DATA = load_city_mapping()

# 构建城市代码参考
CITY_CODE_REFERENCE = "\n".join([
    f"- {city['city_name']}: " + "/".join([f"{a['code']}({a['name']})" for a in city['airports']])
    for city in CITY_DATA["cities"]
])

AIRLINE_REFERENCE = "\n".join([
    f"- {a['code']}: {a['name']}" for a in CITY_DATA["airlines"]
])

SYSTEM_PROMPT = f"""你是航班搜索助手，负责从用户输入中提取搜索参数，并判断信息是否完整。

## 任务
1. 从用户输入中提取航班搜索参数
2. 如果必填信息缺失或需要澄清，生成澄清问题（逐项确认）
3. 输出结构化 JSON

## 需要提取的参数

### 必填参数（缺失时必须询问）
- travel_type: 行程类型 (OW=单程, RT=往返)，默认 OW
- departure_city: 出发城市名称
- departure_code: 出发机场三字码
- arrival_city: 到达城市名称
- arrival_code: 到达机场三字码
- dep_date: 出发日期 (yyyy-MM-dd 格式)

### 往返必填
- return_date: 返程日期 (yyyy-MM-dd 格式，往返时必填)

### 可选参数（使用默认值，不询问）
- passengers: 乘客信息，默认 [{{"type": "ADT", "count": 1}}]
  - type: ADT=成人, CHD=儿童, INF=婴儿
- cabin_class: 舱位等级 (Y=经济舱, S=超值经济舱, C=公务舱, F=头等舱)，默认 Y
- airline_code: 指定航司二字码
- flight_no: 指定航班号，支持用 "/" 分割表示中转航班（如 "MU5001/MU5002"）
- transfer_cities: 中转城市三字码列表（如用户说"经曼谷中转"则为 ["BKK"]）

## 中转航班说明
- 用户可以通过航班号中的 "/" 来表示中转航班
- 例如：MU5001/MU5002 表示两段中转
- 例如：CZ3001/CZ3002/CZ3003 表示三段中转（两次中转）
- 用户说"经XX中转"、"在XX转机"时，提取中转城市到 transfer_cities

## 城市/机场代码参考
{CITY_CODE_REFERENCE}

## 航司代码参考
{AIRLINE_REFERENCE}

## 日期处理规则
- 今天是 {datetime.now().strftime('%Y-%m-%d')}（星期{['一','二','三','四','五','六','日'][datetime.now().weekday()]}）
- 如果用户说"明天"，转换为 {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}
- 如果用户说"后天"，转换为 {(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}
- 如果用户说"下周X"，计算具体日期
- 如果用户说"X月X日"但没说年份，默认今年，如果日期已过则为明年

## 澄清规则（按优先级逐项确认）
1. **意图不明确**：如果用户只说"查机票"、"帮我订票"等模糊表述，没有任何航线信息，询问具体航线
2. **出发地缺失**：询问从哪里出发
3. **目的地缺失**：询问要去哪里
4. **日期缺失**：询问出发日期
5. **往返无返程日期**：如果用户说往返但没给返程日期，询问返程日期

## 默认值（不需要询问确认）
- 人数：默认1成人
- 舱位：默认经济舱
- 行程类型：默认单程
- 机场：多机场城市如用户未指定具体机场，使用城市主代码（如上海用SHA表示不限机场）

## 输出格式
必须严格输出以下 JSON 格式（不要有其他内容）：

```json
{{
  "status": "complete" | "need_clarify",
  "trip_info": {{
    "travel_type": "OW" | "RT",
    "departure_city": "城市名",
    "departure_code": "三字码",
    "arrival_city": "城市名", 
    "arrival_code": "三字码",
    "dep_date": "yyyy-MM-dd",
    "return_date": "yyyy-MM-dd 或 null",
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": "MU 或 null",
    "flight_no": "MU5101 或 MU5001/MU5002（中转）或 null",
    "transfer_cities": ["BKK"] 或 null
  }},
  "clarify": {{
    "field": "需要澄清的字段名",
    "question": "向用户提问的问题",
    "options": [
      {{"label": "显示文本", "value": "选项值"}},
      ...
    ]
  }} 或 null,
  "message": "给用户的回复消息"
}}
```

## 示例

### 示例1：意图模糊
用户: 帮我查机票
输出:
```json
{{
  "status": "need_clarify",
  "trip_info": {{
    "travel_type": "OW",
    "departure_city": null,
    "departure_code": null,
    "arrival_city": null,
    "arrival_code": null,
    "dep_date": null,
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": null,
    "flight_no": null,
    "transfer_cities": null
  }},
  "clarify": {{
    "field": "route",
    "question": "请告诉我您想查询的航线，从哪里出发到哪里？",
    "options": []
  }},
  "message": "好的，请告诉我您想从哪里出发，要去哪里呢？"
}}
```

### 示例2：缺少日期
用户: 上海到香港
输出:
```json
{{
  "status": "need_clarify",
  "trip_info": {{
    "travel_type": "OW",
    "departure_city": "上海",
    "departure_code": null,
    "arrival_city": "香港",
    "arrival_code": "HKG",
    "dep_date": null,
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": null,
    "flight_no": null,
    "transfer_cities": null
  }},
  "clarify": {{
    "field": "dep_date",
    "question": "请问您想哪天出发？",
    "options": [
      {{"label": "明天 ({(datetime.now() + timedelta(days=1)).strftime('%m月%d日')})", "value": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}"}},
      {{"label": "后天 ({(datetime.now() + timedelta(days=2)).strftime('%m月%d日')})", "value": "{(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}"}}
    ]
  }},
  "message": "好的，上海到香港。请问您想哪天出发？"
}}
```

### 示例3：多机场城市（不限机场）
用户: 明天上海到香港
输出:
```json
{{
  "status": "complete",
  "trip_info": {{
    "travel_type": "OW",
    "departure_city": "上海",
    "departure_code": "SHA",
    "arrival_city": "香港",
    "arrival_code": "HKG",
    "dep_date": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}",
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": null,
    "flight_no": null,
    "transfer_cities": null
  }},
  "clarify": null,
  "message": "提取出行信息：明天上海至香港（不限机场）"
}}
```

### 示例4：信息完整及多乘客类型
用户: 2月15号从上海浦东到香港，2个大人1个小孩1个婴儿
输出:
```json
{{
  "status": "complete",
  "trip_info": {{
    "travel_type": "OW",
    "departure_city": "上海",
    "departure_code": "PVG",
    "arrival_city": "香港",
    "arrival_code": "HKG",
    "dep_date": "2026-02-15",
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 2}}, {{"type": "CHD", "count": 1}}, {{"type": "INF", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": null,
    "flight_no": null,
    "transfer_cities": null
  }},
  "clarify": null,
  "message": "提取出行信息：2月15日上海浦东至香港，2成人1儿童1婴儿"
}}
```

### 示例5：中转航班
用户: 查一下MU5001/MU5002，上海到新加坡，经曼谷中转，明天的
输出:
```json
{{
  "status": "complete",
  "trip_info": {{
    "travel_type": "OW",
    "departure_city": "上海",
    "departure_code": "SHA",
    "arrival_city": "新加坡",
    "arrival_code": "SIN",
    "dep_date": "{(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}",
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": "MU",
    "flight_no": "MU5001/MU5002",
    "transfer_cities": ["BKK"]
  }},
  "clarify": null,
  "message": "提取出行信息：明天 MU5001/MU5002 中转航班，上海至新加坡（经曼谷中转）"
}}
```

### 示例6：往返航班
用户: 查一下下周三从北京去上海然后再回到北京的往返航班
输出:
```json
{{
  "status": "complete",
  "trip_info": {{
    "travel_type": "RT",
    "departure_city": "北京",
    "departure_code": "BJS",
    "arrival_city": "上海",
    "arrival_code": "SHA",
    "dep_date": "{(datetime.now() + timedelta(days=7 - datetime.now().weekday() + 2 if datetime.now().weekday() <= 2 else 14 - datetime.now().weekday() + 2)).strftime('%Y-%m-%d')}",
    "return_date": null,
    "passengers": [{{"type": "ADT", "count": 1}}],
    "cabin_class": "Y",
    "cabin_name": "经济舱",
    "airline_code": null,
    "flight_no": null,
    "transfer_cities": null
  }},
  "clarify": {{
    "field": "return_date",
    "question": "请问您想哪天返回北京？",
    "options": []
  }},
  "message": "提取出行信息：下周三北京至上海的往返航班，请问您想哪天返回？"
}}
```
"""


class LLMService:
    """LLM 服务类 (DeepSeek 版)"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL
        )
        self.model = settings.DEEPSEEK_MODEL
    
    async def parse_intent(
        self, 
        user_message: str, 
        history: list = None,
        current_trip_info: dict = None
    ) -> dict:
        """解析用户意图
        
        Args:
            user_message: 用户消息
            history: 对话历史
            current_trip_info: 当前累积的行程信息
            
        Returns:
            解析结果 dict
        """
        messages = []
        
        # 添加历史消息（简化版本）
        if history:
            for msg in history[-6:]:  # 只保留最近6条
                if msg.get("role") == "user":
                    messages.append({"role": "user", "content": msg.get("content", "")})
                elif msg.get("role") == "assistant":
                    messages.append({"role": "assistant", "content": msg.get("content", "")})
        
        # 构建当前消息
        current_context = ""
        if current_trip_info:
            current_context = f"\n\n当前已收集的信息：{json.dumps(current_trip_info, ensure_ascii=False)}\n请基于已有信息继续补充。"
        
        messages.append({
            "role": "user",
            "content": f"{user_message}{current_context}"
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *messages
                ],
                max_tokens=2000,
                temperature=0.7,
                stream=False
            )
            
            # 提取响应内容
            content = response.choices[0].message.content
            
            # 解析 JSON
            result = self._extract_json(content)
            return result
            
        except Exception as e:
            import traceback
            print(f"DEBUG: LLM Parse Intent failed for message: {user_message}")
            print(f"DEBUG: Error details: {str(e)}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"解析失败: {str(e)}",
                "trip_info": current_trip_info,
                "clarify": None
            }
    
    def _extract_json(self, content: str) -> dict:
        """从响应中提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(content)
        except:
            pass
        
        # 尝试从 markdown 代码块中提取
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        
        # 尝试找到第一个 { 和最后一个 }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(content[start:end+1])
            except:
                pass
        
        # 返回错误
        return {
            "status": "error",
            "message": "无法解析响应",
            "trip_info": None,
            "clarify": None
        }
    
    def merge_trip_info(self, base: dict, update: dict) -> dict:
        """合并行程信息，保留非空值"""
        if not base:
            return update
        if not update:
            return base
        
        result = base.copy()
        for key, value in update.items():
            if value is not None:
                result[key] = value
        return result


# 全局单例
llm_service = LLMService()
