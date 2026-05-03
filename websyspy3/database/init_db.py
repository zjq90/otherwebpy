import sqlite3
import os
import hashlib

# 尝试导入bcrypt，如果没有则使用备用方案
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


def _preprocess_password(password: str) -> bytes:
    """
    预处理密码，处理bcrypt 72字节限制
    
    bcrypt只支持最多72字节的密码。为了支持更长的密码，
    我们先对密码进行SHA256哈希，得到64字节的十六进制字符串，
    这样可以支持任意长度的密码。
    
    参数:
        password: 明文密码
    
    返回:
        预处理后的密码字节
    """
    # 使用SHA256哈希密码，得到64字节的十六进制字符串
    # 这样可以支持任意长度的密码，同时避免超过bcrypt的72字节限制
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed.encode('utf-8')


def hash_password(password):
    """
    使用bcrypt哈希密码
    
    参数:
        password: 明文密码
    
    返回:
        哈希后的密码字符串
    """
    if BCRYPT_AVAILABLE:
        # 预处理密码
        password_bytes = _preprocess_password(password)
        # 生成盐并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    else:
        # 备用方案：使用SHA256（仅用于开发/测试）
        return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    """
    获取数据库连接
    如果数据库不存在，会自动创建
    """
    db_path = os.path.join(os.path.dirname(__file__), 'cd_management.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """
    创建数据库表结构
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # CD分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # CD信息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            total_quantity INTEGER DEFAULT 1,
            available_quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # 借还记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cd_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            return_date TIMESTAMP,
            status TEXT DEFAULT 'borrowed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (cd_id) REFERENCES cds (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库表创建成功！")

def insert_test_data():
    """
    插入测试数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否已有测试数据
        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()['count'] > 0:
            print("测试数据已存在，跳过插入")
            return
        
        # 创建管理员用户
        admin_password = hash_password('admin123')
        cursor.execute('''
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_password, 'admin@example.com', 'admin'))
        
        # 创建普通用户
        user_password = hash_password('user123')
        cursor.execute('''
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('user1', user_password, 'user1@example.com', 'user'))
        
        cursor.execute('''
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        ''', ('user2', user_password, 'user2@example.com', 'user'))
        
        # 插入CD分类
        categories = [
            ('流行音乐', '流行歌曲和热门专辑'),
            ('古典音乐', '古典音乐作品'),
            ('摇滚乐', '摇滚音乐专辑'),
            ('爵士乐', '爵士乐作品'),
            ('电子音乐', '电子音乐专辑'),
            ('原声音乐', '电影原声和游戏音乐'),
            ('儿童音乐', '儿童歌曲和音乐'),
            ('世界音乐', '世界各国民间音乐')
        ]
        
        for name, description in categories:
            cursor.execute('''
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            ''', (name, description))
        
        # 插入CD信息
        cds = [
            ('《25》', '阿黛尔', 1, '阿黛尔的经典专辑，包含多首热门歌曲', 10, 10),
            ('《1989》', '泰勒·斯威夫特', 1, '泰勒·斯威夫特的流行专辑', 8, 8),
            ('《贝多芬第九交响曲》', '贝多芬', 2, '贝多芬最著名的交响曲之一', 5, 5),
            ('《莫扎特钢琴协奏曲》', '莫扎特', 2, '莫扎特的经典钢琴协奏曲', 6, 6),
            ('《黑暗边缘》', '平克·弗洛伊德', 3, '摇滚史上最伟大的专辑之一', 12, 12),
            ('《别介意》', '涅槃', 3, '垃圾摇滚的里程碑之作', 9, 9),
            ('《蓝色笔记》', '迈尔斯·戴维斯', 4, '爵士乐的经典之作', 7, 7),
            ('《巨人的步伐》', '约翰·柯川', 4, '硬波普爵士乐的代表作', 6, 6),
            ('《Discovery》', '蠢朋克', 5, '电子音乐的经典专辑', 11, 11),
            ('《Born This Way》', 'Lady Gaga', 5, '电子流行音乐专辑', 10, 10),
            ('《泰坦尼克号原声带》', '詹姆斯·霍纳', 6, '电影《泰坦尼克号》的原声音乐', 15, 15),
            ('《星球大战原声带》', '约翰·威廉姆斯', 6, '电影《星球大战》的经典配乐', 12, 12),
            ('《迪士尼经典儿歌》', '迪士尼', 7, '迪士尼经典儿童歌曲合集', 20, 20),
            ('《儿歌精选》', '佚名', 7, '精选儿童喜爱的歌曲', 18, 18),
            ('《爱尔兰民间音乐》', '佚名', 8, '爱尔兰传统民间音乐', 8, 8),
            ('《非洲鼓乐》', '佚名', 8, '非洲传统鼓乐作品', 7, 7)
        ]
        
        for title, artist, category_id, description, total, available in cds:
            cursor.execute('''
                INSERT INTO cds (title, artist, category_id, description, total_quantity, available_quantity)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, artist, category_id, description, total, available))
        
        # 插入一些借还记录
        borrow_records = [
            (2, 1, '2026-04-01 10:00:00', '2026-04-15 14:30:00', 'returned'),
            (2, 3, '2026-04-10 09:00:00', None, 'borrowed'),
            (3, 5, '2026-04-05 11:00:00', '2026-04-20 16:00:00', 'returned'),
            (3, 8, '2026-04-15 10:30:00', None, 'borrowed'),
            (2, 11, '2026-04-08 09:00:00', '2026-04-22 11:00:00', 'returned')
        ]
        
        for user_id, cd_id, borrow_date, return_date, status in borrow_records:
            cursor.execute('''
                INSERT INTO borrow_records (user_id, cd_id, borrow_date, return_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, cd_id, borrow_date, return_date, status))
        
        # 更新CD的可用数量（模拟借出的情况）
        cursor.execute("UPDATE cds SET available_quantity = available_quantity - 1 WHERE id IN (3, 8)")
        
        conn.commit()
        print("测试数据插入成功！")
        print("\n测试账号信息：")
        print("管理员账号：admin / admin123")
        print("普通用户1：user1 / user123")
        print("普通用户2：user2 / user123")
        
    except Exception as e:
        print(f"插入测试数据时出错：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(__file__), exist_ok=True)
    
    # 创建表
    create_tables()
    
    # 插入测试数据
    insert_test_data()
    
    print("\n数据库初始化完成！")
