"""
数据库初始化脚本
创建数据库表结构和初始化数据
"""

import sqlite3
import os
from datetime import datetime, timedelta
import hashlib

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'device_management.db')

# 确保数据目录
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def create_connection():
    """创建数据库连接"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # 启用外键约束
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    except sqlite3.Error as e:
        print(f"数据库连接错误: {e}")
    return conn


def create_tables(conn):
    """创建所有数据库表"""
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        real_name TEXT NOT NULL,
        role TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 设备表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_code TEXT NOT NULL UNIQUE,
        device_name TEXT NOT NULL,
        device_type TEXT NOT NULL,
        location TEXT,
        install_date DATE,
        specification TEXT,
        manufacturer TEXT,
        status TEXT DEFAULT 'normal',
        total_running_hours REAL DEFAULT 0,
        last_maintenance_date DATE,
        next_maintenance_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 设备状态历史表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS device_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        current REAL,
        temperature REAL,
        voltage REAL,
        power REAL,
        running_hours REAL,
        status TEXT,
        alarm_level TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id)
    )
    ''')

    # 保养任务表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        task_name TEXT NOT NULL,
        task_description TEXT,
        maintenance_cycle_hours REAL NOT NULL,
        last_maintenance_hours REAL DEFAULT 0,
        next_maintenance_hours REAL,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        operation_guide TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id)
    )
    ''')

    # 保养记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maintenance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        device_id INTEGER NOT NULL,
        operator_id INTEGER NOT NULL,
        maintenance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        maintenance_content TEXT,
        maintenance_result TEXT,
        remark TEXT,
        photo_urls TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES maintenance_tasks (id),
        FOREIGN KEY (device_id) REFERENCES devices (id),
        FOREIGN KEY (operator_id) REFERENCES users (id)
    )
    ''')

    # 故障报修表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fault_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id INTEGER NOT NULL,
        reporter_id INTEGER NOT NULL,
        fault_title TEXT NOT NULL,
        fault_description TEXT,
        fault_level TEXT DEFAULT 'medium',
        photo_urls TEXT,
        status TEXT DEFAULT 'pending',
        assigned_to INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id),
        FOREIGN KEY (reporter_id) REFERENCES users (id),
        FOREIGN KEY (assigned_to) REFERENCES users (id)
    )
    ''')

    # 维修记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS repair_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        operator_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        description TEXT,
        progress INTEGER DEFAULT 0,
        photo_urls TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES fault_reports (id),
        FOREIGN KEY (operator_id) REFERENCES users (id)
    )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_status_device_id ON device_status_history (device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_status_recorded_at ON device_status_history (recorded_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_device_id ON maintenance_tasks (device_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_tasks_status ON maintenance_tasks (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fault_reports_status ON fault_reports (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fault_reports_assigned_to ON fault_reports (assigned_to)')

    conn.commit()
    print("数据库表创建成功")


def init_test_data(conn):
    """初始化测试数据"""
    cursor = conn.cursor()

    # 密码哈希
    def hash_password(password):
        return hashlib.md5(password.encode()).hexdigest()

    # 用户数据
    users = [
        ('admin', hash_password('123456'), '系统管理员', 'admin', '13800138000', 'admin@example.com', 'active'),
        ('operator1', hash_password('123456'), '张操作员', 'operator', '13800138001', 'operator1@example.com', 'active'),
        ('operator2', hash_password('123456'), '李操作员', 'operator', '13800138002', 'operator2@example.com', 'active'),
        ('repair1', hash_password('123456'), '王维修', 'repair', '13800138003', 'repair1@example.com', 'active'),
        ('repair2', hash_password('123456'), '赵维修', 'repair', '13800138004', 'repair2@example.com', 'active')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO users (username, password, real_name, role, phone, email, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', users)

    # 设备数据
    devices = [
        ('MIX-001', '1号搅拌主机', 'mixer', '生产车间A区1号', '2023-01-15', '型号：JS2000', '中联重科', 'normal', 1250.5, '2024-03-10', '2024-06-10'),
        ('MIX-002', '2号搅拌主机', 'mixer', '生产车间A区2号', '2023-02-20', '型号：JS2000', '中联重科', 'normal', 980.2, '2024-04-05', '2024-07-05'),
        ('BELT-001', '1号皮带秤', 'belt_scale', '原料输送线1号', '2023-03-10', '型号：ICS-14', '赛摩电气', 'normal', 2100.8, '2024-02-20', '2024-05-20'),
        ('BELT-002', '2号皮带秤', 'belt_scale', '原料输送线2号', '2023-03-15', '型号：ICS-14', '赛摩电气', 'warning', 1850.3, '2024-01-15', '2024-04-15'),
        ('COMP-001', '1号空压机', 'compressor', '动力机房1号', '2023-04-01', '型号：GA11', '阿特拉斯科普柯', 'normal', 3200.0, '2024-01-10', '2024-04-10'),
        ('COMP-002', '2号空压机', 'compressor', '动力机房2号', '2023-04-05', '型号：GA11', '阿特拉斯科普柯', 'fault', 2850.5, '2024-02-01', '2024-05-01')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO devices (device_code, device_name, device_type, location, install_date, specification, manufacturer, status, total_running_hours, last_maintenance_date, next_maintenance_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', devices)

    # 设备状态历史数据
    now = datetime.now()
    status_history = []
    
    # 为每个设备生成最近24小时的状态数据
    for device_id in range(1, 7):
        for hour in range(24):
            recorded_at = (now - timedelta(hours=24-hour)).strftime('%Y-%m-%d %H:%M:%S')
            current = round(100 + device_id * 10 + hour * 0.5, 2)
            temperature = round(35 + device_id * 2 + hour * 0.3, 1)
            voltage = 380
            power = round(current * voltage * 0.85 / 1000, 2)
            running_hours = 1200 + device_id * 300 + hour / 24
            
            # 设备状态
            if device_id == 6:  # 2号空压机故障
                status = 'fault'
                alarm_level = 'high'
            elif device_id == 4:  # 2号皮带秤预警
                status = 'warning'
                alarm_level = 'medium'
                temperature = round(temperature + 15, 1)  # 温度偏高
            else:
                status = 'normal'
                alarm_level = 'none'
            
            status_history.append((
                device_id, current, temperature, voltage, power, running_hours,
                status, alarm_level, recorded_at
            ))

    cursor.executemany('''
    INSERT INTO device_status_history (device_id, current, temperature, voltage, power, running_hours, status, alarm_level, recorded_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', status_history)

    # 保养任务数据
    maintenance_tasks = [
        (1, '搅拌主机日常检查', '检查搅拌主机运行状态、润滑油位、电流温度等参数', 500, 1000, 1500, 'pending', 'medium', '1. 检查润滑油油位是否正常；2. 检查电流、温度是否在正常范围；3. 检查搅拌叶片磨损情况；4. 清理搅拌桶内积料'),
        (1, '搅拌主机月度保养', '月度全面保养，包括润滑系统检查、易损件检查等', 720, 720, 1440, 'completed', 'high', '1. 更换润滑油；2. 检查搅拌臂和叶片；3. 检查密封系统；4. 检查电气系统'),
        (2, '搅拌主机日常检查', '检查搅拌主机运行状态、润滑油位、电流温度等参数', 500, 500, 1000, 'pending', 'medium', '1. 检查润滑油油位是否正常；2. 检查电流、温度是否在正常范围；3. 检查搅拌叶片磨损情况；4. 清理搅拌桶内积料'),
        (3, '皮带秤日常校准', '检查皮带秤运行状态，进行零点校准', 300, 1800, 2100, 'pending', 'medium', '1. 检查皮带张紧度；2. 清洁称重传感器；3. 进行零点校准；4. 检查速度传感器'),
        (4, '皮带秤日常校准', '检查皮带秤运行状态，进行零点校准', 300, 1500, 1800, 'overdue', 'high', '1. 检查皮带张紧度；2. 清洁称重传感器；3. 进行零点校准；4. 检查速度传感器'),
        (5, '空压机日常检查', '检查空压机运行状态、油位、温度等参数', 200, 3000, 3200, 'pending', 'medium', '1. 检查油位是否正常；2. 检查排气温度；3. 检查空气滤芯；4. 检查油气分离器'),
        (6, '空压机故障检查', '故障空压机全面检查', 200, 2600, 2800, 'overdue', 'high', '1. 检查油位是否正常；2. 检查排气温度；3. 检查空气滤芯；4. 检查油气分离器')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO maintenance_tasks (device_id, task_name, task_description, maintenance_cycle_hours, last_maintenance_hours, next_maintenance_hours, status, priority, operation_guide)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', maintenance_tasks)

    # 保养记录数据
    maintenance_records = [
        (2, 1, 4, '2024-03-15 09:30:00', '完成搅拌主机月度保养', 'completed', '润滑油已更换，所有检查项目正常', ''),
        (1, 1, 4, '2024-02-20 14:00:00', '完成1号搅拌主机日常检查', 'completed', '运行状态良好，润滑油位正常', '')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO maintenance_records (task_id, device_id, operator_id, maintenance_date, maintenance_content, maintenance_result, remark, photo_urls)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', maintenance_records)

    # 故障报修数据
    fault_reports = [
        (6, 2, '2号空压机异常高温', '空压机运行时排气温度持续超过100度，报警停机', 'high', '', 'pending', None),
        (4, 2, '2号皮带秤计量不准确', '皮带秤计量数据波动较大，误差超过允许范围', 'medium', '', 'processing', 4),
        (1, 3, '1号搅拌主机异响', '搅拌主机运行时有异常金属摩擦声', 'medium', '', 'completed', 4)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO fault_reports (device_id, reporter_id, fault_title, fault_description, fault_level, photo_urls, status, assigned_to)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', fault_reports)

    # 维修记录数据
    repair_records = [
        (2, 4, 'assigned', '工单已分配给王维修进行处理', 10, ''),
        (2, 4, 'inspection', '已到达现场，开始检查皮带秤故障原因', 20, ''),
        (2, 4, 'diagnosis', '初步诊断为称重传感器受干扰，需要校准和清洁', 40, ''),
        (3, 4, 'assigned', '工单已分配给王维修进行处理', 10, ''),
        (3, 4, 'inspection', '已检查搅拌主机，发现叶片磨损严重', 30, ''),
        (3, 4, 'repair', '已更换磨损的搅拌叶片', 70, ''),
        (3, 4, 'completed', '维修完成，试运行正常', 100, '')
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO repair_records (report_id, operator_id, action, description, progress, photo_urls)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', repair_records)

    conn.commit()
    print("测试数据初始化成功")


def init_database():
    """初始化数据库"""
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        init_test_data(conn)
        conn.close()
        print("数据库初始化完成")
    else:
        print("无法创建数据库连接")


if __name__ == "__main__":
    init_database()
