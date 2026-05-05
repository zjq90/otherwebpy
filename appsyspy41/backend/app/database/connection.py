"""
数据库连接模块
提供SQLite数据库连接和操作的封装
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'device_management.db')


class Database:
    """数据库操作类"""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        # 启用外键约束
        conn.execute('PRAGMA foreign_keys = ON')
        # 设置返回字典格式
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute(self, sql: str, params: tuple = ()) -> int:
        """
        执行SQL语句（INSERT、UPDATE、DELETE）
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            int: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
    
    def execute_insert(self, sql: str, params: tuple = ()) -> int:
        """
        执行INSERT语句并返回新插入的ID
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            int: 新插入记录的ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
    
    def query_one(self, sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        查询单条记录
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            Optional[Dict]: 记录字典，不存在则返回None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def query_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        查询多条记录
        
        Args:
            sql: SQL语句
            params: 参数元组
            
        Returns:
            List[Dict]: 记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def query_paginated(self, sql: str, params: tuple = (), 
                        page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        分页查询
        
        Args:
            sql: SQL语句
            params: 参数元组
            page: 页码，从1开始
            page_size: 每页大小
            
        Returns:
            Dict: 包含total、items、page、page_size的字典
        """
        # 计算总数
        count_sql = f"SELECT COUNT(*) as total FROM ({sql}) as subquery"
        count_result = self.query_one(count_sql, params)
        total = count_result['total'] if count_result else 0
        
        # 计算偏移
        offset = (page - 1) * page_size
        paginated_sql = f"{sql} LIMIT {page_size} OFFSET {offset}"
        items = self.query_all(paginated_sql, params)
        
        return {
            'total': total,
            'items': items,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }


# 全局数据库实例
db = Database()
