"""
系统配置模块
包含数据库配置、文件上传配置等
"""
import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库配置
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'access_control.db')}"

# 文件上传配置
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FACE_PHOTO_DIR = os.path.join(UPLOAD_DIR, "face_photos")
CAPTURE_PHOTO_DIR = os.path.join(UPLOAD_DIR, "captures")

# 允许的图片类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# 人脸识别配置（模拟）
FACE_SIMILARITY_THRESHOLD = 0.8  # 人脸相似度阈值

# 考勤配置
DEFAULT_WORK_START_TIME = "09:00"  # 默认上班时间
DEFAULT_WORK_END_TIME = "18:00"    # 默认下班时间
GRACE_PERIOD_MINUTES = 30          # 考勤宽容时间（分钟）

# 创建必要的目录
def create_directories():
    """创建项目所需的目录"""
    for directory in [UPLOAD_DIR, FACE_PHOTO_DIR, CAPTURE_PHOTO_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
