"""
HTTP客户端模块
用于模拟浏览器请求票务系统，处理Session和Cookie
"""
import asyncio
import json
import re
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import aiohttp
from config import settings


class TicketHttpClient:
    """
    票务系统HTTP客户端
    模拟真实浏览器行为，维护Session和Cookie
    """
    
    def __init__(self):
        """初始化HTTP客户端"""
        self.session: Optional[aiohttp.ClientSession] = None
        self.cookies: Dict[str, str] = {}
        self.headers: Dict[str, str] = {
            "User-Agent": settings.USER_AGENT,
            "Referer": settings.REFERER,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.base_url = settings.TICKET_API_BASE_URL
        self.access_token: Optional[str] = None
        self.session_id: Optional[str] = None
    
    async def init_session(self):
        """初始化HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def update_cookies(self, cookies: Dict[str, str]):
        """
        更新Cookie
        :param cookies: Cookie字典
        """
        self.cookies.update(cookies)
    
    def set_session_id(self, session_id: str):
        """
        设置Session ID
        :param session_id: Session ID
        """
        self.session_id = session_id
        self.cookies["JSESSIONID"] = session_id
    
    def set_access_token(self, access_token: str):
        """
        设置Access Token
        :param access_token: Access Token
        """
        self.access_token = access_token
        self.headers["Authorization"] = f"Bearer {access_token}"
    
    def load_from_session_data(self, session_data: Dict[str, Any]):
        """
        从数据库加载会话数据
        :param session_data: 会话数据字典
        """
        if session_data.get("session_id"):
            self.set_session_id(session_data["session_id"])
        if session_data.get("cookie"):
            # 解析Cookie字符串
            cookie_str = session_data["cookie"]
            for item in cookie_str.split(";"):
                if "=" in item:
                    key, value = item.strip().split("=", 1)
                    self.cookies[key] = value
        if session_data.get("access_token"):
            self.set_access_token(session_data["access_token"])
        if session_data.get("user_agent"):
            self.headers["User-Agent"] = session_data["user_agent"]
        if session_data.get("referer"):
            self.headers["Referer"] = session_data["referer"]
    
    async def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> aiohttp.ClientResponse:
        """
        发送GET请求
        :param url: URL（可以是完整URL或相对路径）
        :param params: 查询参数
        :param kwargs: 其他参数
        :return: 响应对象
        """
        await self.init_session()
        full_url = url if url.startswith("http") else self.base_url + url
        
        # 合并headers和cookies
        request_headers = {**self.headers, **kwargs.pop("headers", {})}
        request_cookies = {**self.cookies, **kwargs.pop("cookies", {})}
        
        return await self.session.get(
            full_url,
            params=params,
            headers=request_headers,
            cookies=request_cookies,
            **kwargs
        )
    
    async def post(self, url: str, data: Optional[Dict] = None, 
                   json_data: Optional[Dict] = None, **kwargs) -> aiohttp.ClientResponse:
        """
        发送POST请求
        :param url: URL（可以是完整URL或相对路径）
        :param data: 表单数据
        :param json_data: JSON数据
        :param kwargs: 其他参数
        :return: 响应对象
        """
        await self.init_session()
        full_url = url if url.startswith("http") else self.base_url + url
        
        # 合并headers和cookies
        request_headers = {**self.headers, **kwargs.pop("headers", {})}
        request_cookies = {**self.cookies, **kwargs.pop("cookies", {})}
        
        return await self.session.post(
            full_url,
            data=data,
            json=json_data,
            headers=request_headers,
            cookies=request_cookies,
            **kwargs
        )
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        模拟登录票务系统
        注意：这是一个模拟实现，实际使用时需要对接真实的登录API
        :param username: 用户名
        :param password: 密码
        :return: 登录结果
        """
        # 这里是模拟实现，实际项目中需要调用真实的登录接口
        # 例如12306的登录流程包含验证码、加密密码等步骤
        
        # 模拟登录成功，生成测试用的session和token
        mock_session_id = f"mock_session_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        mock_token = f"mock_token_{datetime.now().timestamp()}"
        mock_cookie = f"JSESSIONID={mock_session_id}; route=6f50b51faa11b987e576cdb301e545c4"
        
        self.set_session_id(mock_session_id)
        self.set_access_token(mock_token)
        
        return {
            "success": True,
            "session_id": mock_session_id,
            "access_token": mock_token,
            "cookie": mock_cookie,
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "user_agent": self.headers["User-Agent"],
            "referer": self.headers["Referer"],
        }
    
    async def query_tickets(self, from_station: str, to_station: str, 
                             train_date: str) -> Dict[str, Any]:
        """
        查询余票
        注意：这是一个模拟实现，实际使用时需要调用真实的查询API
        :param from_station: 出发站代码
        :param to_station: 到达站代码
        :param train_date: 日期（格式：YYYY-MM-DD）
        :return: 余票信息
        """
        # 这里是模拟实现，实际项目中需要调用真实的余票查询接口
        # 例如：https://kyfw.12306.cn/otn/leftTicket/query
        
        # 模拟返回一些测试数据
        mock_tickets = [
            {
                "train_no": "G1",
                "station_train_code": "G1",
                "start_station_telecode": "BJP",
                "start_station_name": "北京南",
                "end_station_telecode": "SHH",
                "end_station_name": "上海虹桥",
                "from_station_telecode": from_station,
                "to_station_telecode": to_station,
                "start_time": "07:00",
                "arrive_time": "11:28",
                "day_difference": "0",
                "train_class_name": "高速动车",
                "lishi": "04:28",
                "canWebBuy": "Y",
                "lishiValue": "268",
                "yp_info": "",
                "control_train_day": "20260510",
                "start_train_date": train_date.replace("-", ""),
                "seat_feature": "O3M3",
                "yp_ex": "",
                "train_seat_feature": "3",
                "seat_types": "OM9",
                "location_code": "Q7",
                "from_station_no": "01",
                "to_station_no": "10",
                "is_support_card": "1",
                "controlled_train_flag": "0",
                "gg_num": "--",
                "gr_num": "--",
                "qt_num": "--",
                "rw_num": "--",
                "rz_num": "--",
                "tz_num": "--",
                "wz_num": "无",
                "yb_num": "--",
                "yw_num": "--",
                "yz_num": "--",
                "ze_num": "有",  # 二等座
                "zy_num": "有",  # 一等座
                "swz_num": "10",  # 商务座
                "dw_num": "--",
            },
            {
                "train_no": "G5",
                "station_train_code": "G5",
                "start_station_telecode": "BJP",
                "start_station_name": "北京南",
                "end_station_telecode": "SHH",
                "end_station_name": "上海虹桥",
                "from_station_telecode": from_station,
                "to_station_telecode": to_station,
                "start_time": "08:00",
                "arrive_time": "12:28",
                "day_difference": "0",
                "train_class_name": "高速动车",
                "lishi": "04:28",
                "canWebBuy": "Y",
                "seat_types": "OM9",
                "gg_num": "--",
                "gr_num": "--",
                "qt_num": "--",
                "rw_num": "--",
                "rz_num": "--",
                "tz_num": "--",
                "wz_num": "无",
                "yb_num": "--",
                "yw_num": "--",
                "yz_num": "--",
                "ze_num": "有",
                "zy_num": "无",
                "swz_num": "无",
                "dw_num": "--",
            }
        ]
        
        return {
            "status": True,
            "data": mock_tickets,
            "messages": "查询成功"
        }
    
    async def submit_order(self, train_info: Dict, passengers: list, 
                           seat_type: str) -> Dict[str, Any]:
        """
        提交订单
        注意：这是一个模拟实现
        :param train_info: 车次信息
        :param passengers: 乘客列表
        :param seat_type: 席别
        :return: 订单结果
        """
        # 模拟提交订单
        order_no = f"E{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "order_no": order_no,
            "train_number": train_info.get("station_train_code", ""),
            "from_station": train_info.get("from_station_name", ""),
            "to_station": train_info.get("to_station_name", ""),
            "depart_time": train_info.get("start_time", ""),
            "arrive_time": train_info.get("arrive_time", ""),
            "seat_type": seat_type,
            "passengers": passengers,
            "submit_time": datetime.now().isoformat(),
            "pay_deadline": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "message": "订单提交成功，请在30分钟内完成支付"
        }


# 全局HTTP客户端实例
http_client = TicketHttpClient()
