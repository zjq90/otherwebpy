"""
测试辅助功能模块
提供API测试的辅助函数和示例数据
"""
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime, date


class FitnessApiTester:
    """
    健身API测试助手类
    封装常用的API调用方法，方便功能测试
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化测试助手
        
        Args:
            base_url: API基础URL
        """
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url)
        self.access_token: Optional[str] = None
        self.current_user: Optional[Dict] = None
    
    def close(self):
        """
        关闭HTTP客户端
        """
        self.client.close()
    
    # ==================== 用户相关测试方法 ====================
    
    def register(self, username: str, password: str, nickname: str = None) -> Dict[str, Any]:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            nickname: 昵称（可选）
        
        Returns:
            用户信息字典
        """
        data = {
            "username": username,
            "password": password
        }
        if nickname:
            data["nickname"] = nickname
        
        response = self.client.post("/api/users/register", json=data)
        response.raise_for_status()
        return response.json()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            登录结果（包含令牌和用户信息）
        """
        data = {
            "username": username,
            "password": password
        }
        
        response = self.client.post("/api/users/login", json=data)
        response.raise_for_status()
        result = response.json()
        
        self.access_token = result.get("access_token")
        self.current_user = result.get("user")
        
        return result
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典
        """
        response = self.client.get(f"/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def update_user_info(self, user_id: int, update_data: Dict) -> Dict[str, Any]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            update_data: 更新的数据字典
        
        Returns:
            更新后的用户信息
        """
        response = self.client.put(f"/api/users/{user_id}", json=update_data)
        response.raise_for_status()
        return response.json()
    
    # ==================== 体测记录相关测试方法 ====================
    
    def add_body_measurement(self, user_id: int, weight: float, body_fat_rate: float, 
                               muscle_mass: float, **kwargs) -> Dict[str, Any]:
        """
        添加体测记录
        
        Args:
            user_id: 用户ID
            weight: 体重(kg)
            body_fat_rate: 体脂率(%)
            muscle_mass: 肌肉量(kg)
            **kwargs: 其他可选参数
        
        Returns:
            体测记录信息
        """
        data = {
            "weight": weight,
            "body_fat_rate": body_fat_rate,
            "muscle_mass": muscle_mass,
            **kwargs
        }
        
        response = self.client.post(f"/api/measurements/user/{user_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_measurements(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        获取用户体测记录列表
        
        Args:
            user_id: 用户ID
            skip: 跳过数量（分页）
            limit: 限制数量（分页）
        
        Returns:
            体测记录列表
        """
        response = self.client.get(
            f"/api/measurements/user/{user_id}",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_measurement_stats(self, user_id: int, limit: int = 30) -> Dict[str, Any]:
        """
        获取体测数据统计（用于折线图）
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
        
        Returns:
            统计数据（包含日期和各项指标列表）
        """
        response = self.client.get(
            f"/api/measurements/stats/user/{user_id}",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_latest_measurement(self, user_id: int) -> Optional[Dict]:
        """
        获取用户最新体测记录
        
        Args:
            user_id: 用户ID
        
        Returns:
            最新体测记录，如无则返回None
        """
        response = self.client.get(f"/api/measurements/latest/user/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    # ==================== 训练项目相关测试方法 ====================
    
    def get_all_exercises(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        获取所有训练项目列表
        
        Args:
            skip: 跳过数量（分页）
            limit: 限制数量（分页）
        
        Returns:
            训练项目列表
        """
        response = self.client.get(
            "/api/exercises/",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_exercises_by_category(self, category: str) -> List[Dict]:
        """
        按分类获取训练项目
        
        Args:
            category: 分类名称
        
        Returns:
            训练项目列表
        """
        response = self.client.get(f"/api/exercises/category/{category}")
        response.raise_for_status()
        return response.json()
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有训练项目分类
        
        Returns:
            分类名称列表
        """
        response = self.client.get("/api/exercises/categories/list")
        response.raise_for_status()
        return response.json()
    
    # ==================== 训练日志相关测试方法 ====================
    
    def add_training_log(self, user_id: int, duration: int, items: List[Dict] = None, 
                         **kwargs) -> Dict[str, Any]:
        """
        添加训练日志
        
        Args:
            user_id: 用户ID
            duration: 训练时长(分钟)
            items: 训练项目详情列表
            **kwargs: 其他可选参数
        
        Returns:
            训练日志信息
        """
        data = {
            "duration": duration,
            "items": items or [],
            **kwargs
        }
        
        response = self.client.post(f"/api/training-logs/user/{user_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_training_logs(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        获取用户训练日志列表
        
        Args:
            user_id: 用户ID
            skip: 跳过数量（分页）
            limit: 限制数量（分页）
        
        Returns:
            训练日志列表
        """
        response = self.client.get(
            f"/api/training-logs/user/{user_id}",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_training_log_by_id(self, log_id: int) -> Dict[str, Any]:
        """
        根据ID获取训练日志详情
        
        Args:
            log_id: 训练日志ID
        
        Returns:
            训练日志详情
        """
        response = self.client.get(f"/api/training-logs/{log_id}")
        response.raise_for_status()
        return response.json()
    
    def get_monthly_stats(self, user_id: int, year: int = None, month: int = None) -> Dict[str, Any]:
        """
        获取用户月度训练统计
        
        Args:
            user_id: 用户ID
            year: 年份，默认当前年
            month: 月份，默认当前月
        
        Returns:
            月度统计数据
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        response = self.client.get(
            f"/api/training-logs/stats/user/{user_id}/monthly",
            params={"year": year, "month": month}
        )
        response.raise_for_status()
        return response.json()
    
    # ==================== 目标设定相关测试方法 ====================
    
    def add_goal(self, user_id: int, goal_type: str, goal_name: str, 
                 target_value: float = None, current_value: float = None,
                 **kwargs) -> Dict[str, Any]:
        """
        添加健身目标
        
        Args:
            user_id: 用户ID
            goal_type: 目标类型 (lose_weight/gain_muscle/shape/endurance)
            goal_name: 目标名称
            target_value: 目标值
            current_value: 当前值
            **kwargs: 其他可选参数
        
        Returns:
            目标信息
        """
        data = {
            "goal_type": goal_type,
            "goal_name": goal_name,
            "target_value": target_value,
            "current_value": current_value,
            **kwargs
        }
        
        response = self.client.post(f"/api/goals/user/{user_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_user_goals(self, user_id: int, status: str = None, 
                        skip: int = 0, limit: int = 100) -> List[Dict]:
        """
        获取用户目标列表
        
        Args:
            user_id: 用户ID
            status: 目标状态筛选 (active/completed/failed)
            skip: 跳过数量（分页）
            limit: 限制数量（分页）
        
        Returns:
            目标列表
        """
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        
        response = self.client.get(
            f"/api/goals/user/{user_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_active_goal(self, user_id: int) -> Optional[Dict]:
        """
        获取用户当前进行中的目标
        
        Args:
            user_id: 用户ID
        
        Returns:
            当前目标信息，如无则返回None
        """
        response = self.client.get(f"/api/goals/active/user/{user_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def add_goal_progress(self, goal_id: int, progress_value: float, 
                          progress_percent: float = None, notes: str = None) -> Dict[str, Any]:
        """
        添加目标进度记录
        
        Args:
            goal_id: 目标ID
            progress_value: 当前进度值
            progress_percent: 进度百分比（可选，自动计算）
            notes: 进度备注
        
        Returns:
            进度记录信息
        """
        data = {
            "progress_value": progress_value
        }
        if progress_percent is not None:
            data["progress_percent"] = progress_percent
        if notes:
            data["notes"] = notes
        
        response = self.client.post(f"/api/goals/{goal_id}/progress", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_goal_progress_records(self, goal_id: int, limit: int = 30) -> List[Dict]:
        """
        获取目标进度记录列表
        
        Args:
            goal_id: 目标ID
            limit: 限制数量
        
        Returns:
            进度记录列表
        """
        response = self.client.get(
            f"/api/goals/{goal_id}/progress",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_goal_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户目标统计
        
        Args:
            user_id: 用户ID
        
        Returns:
            目标统计数据
        """
        response = self.client.get(f"/api/goals/stats/user/{user_id}")
        response.raise_for_status()
        return response.json()
    
    # ==================== 健康检查 ====================
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            服务状态信息
        """
        response = self.client.get("/health")
        response.raise_for_status()
        return response.json()


# ==================== 示例测试数据 ====================

SAMPLE_EXERCISES = [
    {"name": "卧推", "category": "力量训练", "default_calories_per_hour": 300},
    {"name": "深蹲", "category": "力量训练", "default_calories_per_hour": 350},
    {"name": "慢跑", "category": "有氧运动", "default_calories_per_hour": 450},
    {"name": "游泳", "category": "有氧运动", "default_calories_per_hour": 500},
    {"name": "瑜伽", "category": "柔韧训练", "default_calories_per_hour": 200},
]

SAMPLE_GOAL_TYPES = [
    {"type": "lose_weight", "name": "减脂瘦身", "desc": "通过有氧运动和饮食控制减少体脂"},
    {"type": "gain_muscle", "name": "增肌塑形", "desc": "通过力量训练增加肌肉量"},
    {"type": "shape", "name": "体态调整", "desc": "改善身体姿态，塑造完美身形"},
    {"type": "endurance", "name": "耐力提升", "desc": "提高心肺功能和肌肉耐力"},
]


def run_demo_tests():
    """
    运行演示测试
    展示API的基本用法
    """
    print("=" * 60)
    print("健身API演示测试")
    print("=" * 60)
    
    tester = FitnessApiTester()
    
    try:
        # 1. 健康检查
        print("\n1. 健康检查...")
        health = tester.health_check()
        print(f"   状态: {health['status']}")
        
        # 2. 获取训练项目分类
        print("\n2. 获取训练项目分类...")
        categories = tester.get_all_categories()
        print(f"   分类数量: {len(categories)}")
        if categories:
            print(f"   分类列表: {categories}")
        
        # 3. 获取所有训练项目
        print("\n3. 获取训练项目列表...")
        exercises = tester.get_all_exercises(limit=5)
        print(f"   获取到 {len(exercises)} 个训练项目")
        for ex in exercises[:3]:
            print(f"   - {ex['name']} ({ex['category']})")
        
        print("\n" + "=" * 60)
        print("演示测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n测试出错: {e}")
        print("请确保后端服务已启动 (python -m uvicorn app.main:app --reload)")
    finally:
        tester.close()


if __name__ == "__main__":
    run_demo_tests()
