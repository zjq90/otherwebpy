"""
余票监控服务
负责高并发轮询、余票检测、自动下单
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import MonitorTask, Order, AlertRecord, Passenger, UserSession
from http_client import http_client


class MonitorService:
    """
    余票监控服务类
    管理监控任务的运行、暂停、停止
    """
    
    # 全局任务状态存储
    _running_tasks: Dict[int, asyncio.Task] = {}
    _task_status: Dict[int, Dict] = {}
    
    # 席别映射
    SEAT_TYPE_MAP = {
        "商务座": ("swz_num", "A"),
        "一等座": ("zy_num", "M"),
        "二等座": ("ze_num", "O"),
        "软卧": ("rw_num", "4"),
        "硬卧": ("yw_num", "3"),
        "硬座": ("yz_num", "1"),
        "无座": ("wz_num", "WZ"),
    }
    
    @classmethod
    async def start_monitor(cls, task_id: int, db: AsyncSession):
        """
        启动监控任务
        :param task_id: 任务ID
        :param db: 数据库会话
        """
        # 检查任务是否已在运行
        if task_id in cls._running_tasks and not cls._running_tasks[task_id].done():
            return {"success": False, "message": "任务已在运行中"}
        
        # 从数据库获取任务信息
        result = await db.execute(
            select(MonitorTask).where(MonitorTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            return {"success": False, "message": "任务不存在"}
        
        # 更新任务状态为运行中
        task.status = "running"
        await db.commit()
        
        # 创建并启动监控协程
        monitor_task = asyncio.create_task(
            cls._monitor_loop(task_id, db)
        )
        cls._running_tasks[task_id] = monitor_task
        cls._task_status[task_id] = {
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "check_count": 0,
            "ticket_found": False,
        }
        
        return {"success": True, "message": f"监控任务 {task.task_name} 已启动"}
    
    @classmethod
    async def stop_monitor(cls, task_id: int, db: AsyncSession):
        """
        停止监控任务
        :param task_id: 任务ID
        :param db: 数据库会话
        """
        # 取消运行中的任务
        if task_id in cls._running_tasks:
            task = cls._running_tasks[task_id]
            if not task.done():
                task.cancel()
            del cls._running_tasks[task_id]
        
        # 更新任务状态
        result = await db.execute(
            select(MonitorTask).where(MonitorTask.id == task_id)
        )
        monitor_task = result.scalar_one_or_none()
        
        if monitor_task:
            monitor_task.status = "stopped"
            await db.commit()
        
        # 更新任务状态存储
        if task_id in cls._task_status:
            cls._task_status[task_id]["status"] = "stopped"
        
        return {"success": True, "message": "监控任务已停止"}
    
    @classmethod
    def get_task_status(cls, task_id: int) -> Optional[Dict]:
        """
        获取任务运行状态
        :param task_id: 任务ID
        :return: 任务状态
        """
        return cls._task_status.get(task_id)
    
    @classmethod
    async def _monitor_loop(cls, task_id: int, db: AsyncSession):
        """
        监控循环主循环
        :param task_id: 任务ID
        :param db: 数据库会话
        """
        try:
            # 重新获取任务信息（避免会话已关闭）
            result = await db.execute(
                select(MonitorTask).where(MonitorTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return
            
            check_count = 0
            
            while True:
                check_count += 1
                
                # 执行一次余票检查
                check_result = await cls._check_tickets(task, db)
                
                # 更新任务状态
                task.last_check_time = datetime.utcnow()
                task.last_check_result = json.dumps(check_result, ensure_ascii=False, default=str)
                
                if check_result.get("has_ticket"):
                    task.ticket_found = True
                    
                    # 如果配置了自动提交
                    if task.auto_submit:
                        await cls._auto_submit_order(task, check_result, db)
                    
                    # 发送提醒
                    await cls._send_alert(task, check_result, db)
                
                await db.commit()
                
                # 更新任务状态存储
                if task_id in cls._task_status:
                    cls._task_status[task_id]["check_count"] = check_count
                    cls._task_status[task_id]["ticket_found"] = check_result.get("has_ticket", False)
                
                # 检查是否需要停止
                # 这里可以添加停止条件，比如找到票后自动停止
                
                # 等待下一次轮询
                await asyncio.sleep(task.poll_interval)
                
        except asyncio.CancelledError:
            # 任务被取消
            if task_id in cls._task_status:
                cls._task_status[task_id]["status"] = "stopped"
        except Exception as e:
            # 记录错误
            if task_id in cls._task_status:
                cls._task_status[task_id]["status"] = "error"
                cls._task_status[task_id]["error"] = str(e)
    
    @classmethod
    async def _check_tickets(cls, task: MonitorTask, db: AsyncSession) -> Dict[str, Any]:
        """
        检查余票
        :param task: 监控任务
        :param db: 数据库会话
        :return: 检查结果
        """
        try:
            # 调用HTTP客户端查询余票
            result = await http_client.query_tickets(
                from_station=task.from_station,
                to_station=task.to_station,
                train_date=task.train_date
            )
            
            if not result.get("status"):
                return {"has_ticket": False, "error": result.get("messages", "查询失败")}
            
            tickets = result.get("data", [])
            
            # 过滤符合条件的车次
            filtered_tickets = cls._filter_tickets(tickets, task)
            
            # 检查是否有余票
            available_tickets = []
            for ticket in filtered_tickets:
                available_seats = cls._check_available_seats(ticket, task)
                if available_seats:
                    ticket["available_seats"] = available_seats
                    available_tickets.append(ticket)
            
            return {
                "has_ticket": len(available_tickets) > 0,
                "total_count": len(tickets),
                "filtered_count": len(filtered_tickets),
                "available_count": len(available_tickets),
                "available_tickets": available_tickets,
                "check_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"has_ticket": False, "error": str(e)}
    
    @classmethod
    def _filter_tickets(cls, tickets: list, task: MonitorTask) -> list:
        """
        根据任务条件过滤车次
        :param tickets: 车次列表
        :param task: 监控任务
        :return: 过滤后的车次列表
        """
        result = []
        
        # 指定车次列表
        target_train_numbers = set()
        if task.train_numbers:
            target_train_numbers = set(n.strip().upper() for n in task.train_numbers.split(","))
        
        for ticket in tickets:
            train_code = ticket.get("station_train_code", "").upper()
            
            # 过滤指定车次
            if target_train_numbers and train_code not in target_train_numbers:
                continue
            
            # 检查是否可购买
            if ticket.get("canWebBuy") != "Y":
                continue
            
            result.append(ticket)
        
        return result
    
    @classmethod
    def _check_available_seats(cls, ticket: Dict, task: MonitorTask) -> list:
        """
        检查可用席别是否有余票
        :param ticket: 车次信息
        :param task: 监控任务
        :return: 可用席别列表
        """
        available = []
        
        # 目标席别列表
        target_seat_types = set()
        if task.seat_types:
            target_seat_types = set(s.strip() for s in task.seat_types.split(","))
        
        for seat_name, (seat_key, seat_code) in cls.SEAT_TYPE_MAP.items():
            # 如果指定了席别，只检查指定的
            if target_seat_types and seat_name not in target_seat_types:
                continue
            
            seat_count = ticket.get(seat_key, "--")
            
            # 判断是否有票："有"、数字、或者不是"--"和"无"
            if seat_count not in ("--", "无", ""):
                available.append({
                    "seat_type": seat_name,
                    "seat_code": seat_code,
                    "seat_count": seat_count
                })
        
        return available
    
    @classmethod
    async def _auto_submit_order(cls, task: MonitorTask, check_result: Dict, db: AsyncSession):
        """
        自动提交订单
        :param task: 监控任务
        :param check_result: 检查结果
        :param db: 数据库会话
        """
        available_tickets = check_result.get("available_tickets", [])
        if not available_tickets:
            return
        
        # 选择第一个可用的车次和席别
        selected_train = available_tickets[0]
        selected_seat = selected_train.get("available_seats", [{}])[0]
        
        # 获取乘客信息
        passengers = []
        if task.passenger_ids:
            passenger_ids = [int(pid.strip()) for pid in task.passenger_ids.split(",")]
            result = await db.execute(
                select(Passenger).where(Passenger.id.in_(passenger_ids))
            )
            passengers = result.scalars().all()
        
        if not passengers:
            # 如果没有配置乘客，使用默认乘客
            result = await db.execute(
                select(Passenger).where(
                    Passenger.user_id == task.user_id,
                    Passenger.is_default == True
                )
            )
            default_passenger = result.scalar_one_or_none()
            if default_passenger:
                passengers = [default_passenger]
        
        if not passengers:
            return {"success": False, "message": "没有可用的乘客信息"}
        
        # 转换乘客信息
        passenger_list = []
        for p in passengers:
            passenger_list.append({
                "id": p.id,
                "name": p.name,
                "id_card": p.id_card,
                "phone": p.phone,
                "passenger_type": p.passenger_type
            })
        
        # 调用提交订单（模拟）
        order_result = await http_client.submit_order(
            train_info=selected_train,
            passengers=passenger_list,
            seat_type=selected_seat.get("seat_type", "二等座")
        )
        
        if order_result.get("success"):
            # 创建订单记录
            order = Order(
                user_id=task.user_id,
                monitor_task_id=task.id,
                order_no=order_result.get("order_no"),
                train_number=order_result.get("train_number"),
                from_station=order_result.get("from_station"),
                to_station=order_result.get("to_station"),
                depart_time=order_result.get("depart_time"),
                arrive_time=order_result.get("arrive_time"),
                train_date=task.train_date,
                passenger_info=json.dumps(passenger_list, ensure_ascii=False),
                seat_type=selected_seat.get("seat_type", "二等座"),
                ticket_price=0.0,  # 实际需要从接口获取
                total_amount=0.0,
                status="submitted",
                submit_time=datetime.utcnow(),
            )
            db.add(order)
            await db.commit()
            
            return {"success": True, "order": order_result}
        
        return {"success": False, "message": order_result.get("message", "订单提交失败")}
    
    @classmethod
    async def _send_alert(cls, task: MonitorTask, check_result: Dict, db: AsyncSession):
        """
        发送提醒
        :param task: 监控任务
        :param check_result: 检查结果
        :param db: 数据库会话
        """
        available_count = check_result.get("available_count", 0)
        available_tickets = check_result.get("available_tickets", [])
        
        # 构建提醒内容
        ticket_info = []
        for ticket in available_tickets[:3]:  # 最多显示3个
            train_code = ticket.get("station_train_code", "")
            seats = ticket.get("available_seats", [])
            seat_info = ", ".join([f"{s['seat_type']}:{s['seat_count']}" for s in seats])
            ticket_info.append(f"车次{train_code}：{seat_info}")
        
        alert_title = f"【发现余票】{task.from_station}→{task.to_station} {task.train_date}"
        alert_content = f"监控到{available_count}个车次有余票！\n" + "\n".join(ticket_info)
        
        # 创建系统提醒记录
        alert = AlertRecord(
            user_id=task.user_id,
            monitor_task_id=task.id,
            alert_type="system",
            alert_title=alert_title,
            alert_content=alert_content,
            is_read=False,
            is_sent=False,
        )
        db.add(alert)
        await db.commit()
        
        # TODO: 发送短信/邮件提醒（需要配置）
        # 这里可以集成实际的短信/邮件发送服务


# 全局监控服务实例
monitor_service = MonitorService()
