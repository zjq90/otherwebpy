"""
数据库连接配置文件
包含SQLAlchemy的引擎、会话工厂和基础模型类
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# 创建数据库引擎
# SQLite需要设置check_same_thread=False以支持多线程访问
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # 设置为True可以打印SQL语句，方便调试
)

# 创建会话工厂
# autocommit=False: 不自动提交事务
# autoflush=False: 不自动刷新对象到数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
# 所有的ORM模型都需要继承这个类
Base = declarative_base()

# 数据库依赖函数
# 用于FastAPI的依赖注入，每个请求获取一个数据库会话
def get_db():
    """
    获取数据库会话的依赖函数
    
    使用方法:
    @app.get("/items/")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    
    Yields:
        Session: 数据库会话对象
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # 确保会话被关闭，释放数据库连接
        db.close()

# 初始化数据库表的函数
def init_db():
    """
    初始化数据库，创建所有表
    
    注意: 这个函数应该在应用启动时调用一次
    """
    # 导入所有模型，确保它们被注册到Base.metadata中
    from models import User, Course, Coach, MemberPreference, Message, ChatSession, ChatMessage, Review, NutritionProduct, Recommendation, Booking
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表创建成功!")
