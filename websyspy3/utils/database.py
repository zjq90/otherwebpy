"""
数据库工具模块
提供数据库连接和通用操作
"""

import sqlite3
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path

from config import DATABASE_PATH


@contextmanager
def get_db():
    """
    数据库连接上下文管理器
    使用with语句自动管理连接的打开和关闭
    
    示例:
        with get_db() as (conn, cursor):
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
    """
    conn = None
    cursor = None
    try:
        # 确保数据库目录存在
        db_dir = Path(DATABASE_PATH).parent
        if not db_dir.exists():
            db_dir.mkdir(parents=True)
        
        # 创建数据库连接
        conn = sqlite3.connect(DATABASE_PATH)
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        # 设置行工厂，使查询结果可以通过列名访问
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        yield conn, cursor
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_query(sql: str, params: Tuple = (), fetchone: bool = False) -> Optional[List[Dict[str, Any]]]:
    """
    执行SQL查询语句（SELECT）
    
    参数:
        sql: SQL查询语句
        params: 参数元组
        fetchone: 是否只获取第一行
    
    返回:
        查询结果列表，每个元素是一个字典
    """
    with get_db() as (conn, cursor):
        cursor.execute(sql, params)
        rows = cursor.fetchone() if fetchone else cursor.fetchall()
        
        if rows is None:
            return None
        
        if fetchone:
            return [dict(rows)]
        
        return [dict(row) for row in rows]


def execute_insert(sql: str, params: Tuple = ()) -> int:
    """
    执行SQL插入语句
    
    参数:
        sql: SQL插入语句
        params: 参数元组
    
    返回:
        新插入记录的ID
    """
    with get_db() as (conn, cursor):
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def execute_update(sql: str, params: Tuple = ()) -> int:
    """
    执行SQL更新语句
    
    参数:
        sql: SQL更新语句
        params: 参数元组
    
    返回:
        受影响的行数
    """
    with get_db() as (conn, cursor):
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount


def execute_delete(sql: str, params: Tuple = ()) -> int:
    """
    执行SQL删除语句
    
    参数:
        sql: SQL删除语句
        params: 参数元组
    
    返回:
        受影响的行数
    """
    with get_db() as (conn, cursor):
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount


def execute_transaction(sqls: List[Tuple[str, Tuple]]) -> bool:
    """
    执行事务
    
    参数:
        sqls: SQL语句和参数对的列表
              例如: [("INSERT INTO ...", (param1, param2)), ("UPDATE ...", (param3,))]
    
    返回:
        事务是否成功执行
    """
    with get_db() as (conn, cursor):
        try:
            for sql, params in sqls:
                cursor.execute(sql, params)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"事务执行失败: {e}")
            return False


def get_pagination(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    生成分页信息
    
    参数:
        total: 总记录数
        page: 当前页码
        page_size: 每页记录数
    
    返回:
        包含分页信息的字典
    """
    total_pages = (total + page_size - 1) // page_size
    has_prev = page > 1
    has_next = page < total_pages
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": page - 1 if has_prev else None,
        "next_page": page + 1 if has_next else None
    }


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """
    将sqlite3.Row对象转换为字典
    
    参数:
        row: sqlite3.Row对象
    
    返回:
        字典形式的行数据
    """
    return dict(row) if row else None
