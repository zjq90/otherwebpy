"""
操作日志数据模型
定义操作日志表结构，用于记录所有用户操作行�?
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class OperationLog(Base):
    """
    操作日志数据模型
    记录系统中所有用户的操作行为，便于追溯问题与责任认定
    """
    
    __tablename__ = "operation_logs"
    __table_args__ = {"comment": "操作日志�?}
    
    # 主键ID
    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    
    # 操作基本信息
    operation_type = Column(String(50), nullable=False, index=True, comment="操作类型（如：login, create, update, delete等）")
    operation_name = Column(String(100), nullable=False, comment="操作名称")
    operation_desc = Column(Text, nullable=True, comment="操作详细描述")
    
    # 请求信息
    request_method = Column(String(10), nullable=True, comment="请求方法（GET, POST, PUT, DELETE等）")
    request_url = Column(String(500), nullable=True, comment="请求URL")
    request_params = Column(Text, nullable=True, comment="请求参数（JSON格式�?)
    request_ip = Column(String(50), nullable=True, comment="请求IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理信息")
    
    # 响应信息
    response_status = Column(Integer, nullable=True, comment="响应状态码")
    response_data = Column(Text, nullable=True, comment="响应数据（JSON格式�?)
    
    # 操作人信�?
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="操作用户ID")
    username = Column(String(50), nullable=True, index=True, comment="操作用户�?)
    
    # 时间信息
    created_at = Column(DateTime, default=datetime.utcnow, index=True, comment="操作时间")
    duration = Column(Integer, nullable=True, comment="操作耗时（毫秒）")
    
    # 其他信息
    module = Column(String(50), nullable=True, index=True, comment="所属模块（如：user, role, permission等）")
    status = Column(String(20), default="success", comment="操作状态（success, failed等）")
    error_message = Column(Text, nullable=True, comment="错误信息（操作失败时�?)
    
    # 关系：一个用户可以有多条操作日志
    user = relationship("User", backref="operation_logs")
    
    def __repr__(self):
        """字符串表�?""
        return f"<OperationLog(id={self.id}, operation_type='{self.operation_type}', username='{self.username}')>"
    
    @staticmethod
    def create_log(
        operation_type: str,
        operation_name: str,
        operation_desc: str = None,
        request_method: str = None,
        request_url: str = None,
        request_params: str = None,
        request_ip: str = None,
        user_agent: str = None,
        response_status: int = None,
        response_data: str = None,
        user_id: int = None,
        username: str = None,
        module: str = None,
        status: str = "success",
        error_message: str = None,
        duration: int = None
    ) -> "OperationLog":
        """
        创建操作日志记录的静态方�?
        
        参数:
            各种日志字段参数
        
        返回:
            OperationLog实例
        """
        return OperationLog(
            operation_type=operation_type,
            operation_name=operation_name,
            operation_desc=operation_desc,
            request_method=request_method,
            request_url=request_url,
            request_params=request_params,
            request_ip=request_ip,
            user_agent=user_agent,
            response_status=response_status,
            response_data=response_data,
            user_id=user_id,
            username=username,
            module=module,
            status=status,
            error_message=error_message,
            duration=duration
        )
