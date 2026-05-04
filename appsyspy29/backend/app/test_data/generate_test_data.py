"""
测试数据生成脚本
用于生成测试数据，辅助功能测试
"""
import sys
import os
from datetime import datetime, timedelta
import random

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import SessionLocal, init_db
from app.models import (
    User, BodyMeasurement, Exercise, TrainingLog, TrainingLogItem,
    Goal, TrainingPlan, DietAdvice, GoalProgress
)


def generate_users(db):
    """
    生成测试用户数据
    """
    users_data = [
        {
            "username": "testuser1",
            "password": "123456",
            "nickname": "健身达人",
            "gender": "male",
            "phone": "13800138001",
            "email": "user1@example.com"
        },
        {
            "username": "testuser2",
            "password": "123456",
            "nickname": "塑形专家",
            "gender": "female",
            "phone": "13800138002",
            "email": "user2@example.com"
        },
        {
            "username": "testuser3",
            "password": "123456",
            "nickname": "增肌狂人",
            "gender": "male",
            "phone": "13800138003",
            "email": "user3@example.com"
        }
    ]
    
    users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"已生成 {len(users)} 个测试用户")
    return users


def generate_exercises(db):
    """
    生成测试训练项目数据
    """
    exercises_data = [
        # 力量训练
        {"name": "卧推", "category": "力量训练", "description": "胸部和三头肌主要训练动作", "default_calories_per_hour": 300},
        {"name": "深蹲", "category": "力量训练", "description": "腿部和臀部主要训练动作", "default_calories_per_hour": 350},
        {"name": "硬拉", "category": "力量训练", "description": "全身综合力量训练", "default_calories_per_hour": 400},
        {"name": "引体向上", "category": "力量训练", "description": "背部和二头肌训练", "default_calories_per_hour": 280},
        {"name": "哑铃弯举", "category": "力量训练", "description": "二头肌孤立训练", "default_calories_per_hour": 200},
        # 有氧运动
        {"name": "慢跑", "category": "有氧运动", "description": "中低强度有氧训练", "default_calories_per_hour": 450},
        {"name": "游泳", "category": "有氧运动", "description": "全身有氧训练", "default_calories_per_hour": 500},
        {"name": "动感单车", "category": "有氧运动", "description": "高强度有氧训练", "default_calories_per_hour": 550},
        {"name": "跳绳", "category": "有氧运动", "description": "高效燃脂训练", "default_calories_per_hour": 600},
        {"name": "椭圆机", "category": "有氧运动", "description": "低冲击有氧训练", "default_calories_per_hour": 400},
        # 柔韧训练
        {"name": "瑜伽", "category": "柔韧训练", "description": "柔韧性和核心训练", "default_calories_per_hour": 200},
        {"name": "普拉提", "category": "柔韧训练", "description": "核心力量和柔韧性", "default_calories_per_hour": 250},
        # HIIT训练
        {"name": "波比跳", "category": "HIIT训练", "description": "高强度间歇训练动作", "default_calories_per_hour": 700},
        {"name": "开合跳", "category": "HIIT训练", "description": "快速燃脂训练", "default_calories_per_hour": 650},
        {"name": "高抬腿", "category": "HIIT训练", "description": "高强度心肺训练", "default_calories_per_hour": 600},
    ]
    
    exercises = []
    for exercise_data in exercises_data:
        exercise = Exercise(**exercise_data)
        db.add(exercise)
        exercises.append(exercise)
    
    db.commit()
    print(f"已生成 {len(exercises)} 个测试训练项目")
    return exercises


def generate_body_measurements(db, users):
    """
    生成测试体测记录数据
    为每个用户生成过去30天的体测数据，模拟变化趋势
    """
    measurements = []
    
    for user in users:
        # 基础数据，每个用户略有不同
        base_weight = random.uniform(60, 85)
        base_body_fat = random.uniform(15, 25)
        base_muscle = random.uniform(30, 45)
        
        # 生成过去30天的数据
        for i in range(30):
            # 模拟数据变化（略有波动，但整体趋势）
            day_offset = 29 - i  # 从30天前到今天
            date = datetime.now() - timedelta(days=day_offset)
            
            # 模拟变化趋势
            weight_change = (random.uniform(-0.3, 0.2) * (day_offset / 30))
            body_fat_change = (random.uniform(-0.5, 0.3) * (day_offset / 30))
            muscle_change = (random.uniform(-0.2, 0.4) * (day_offset / 30))
            
            measurement = BodyMeasurement(
                user_id=user.id,
                weight=round(base_weight + weight_change, 1),
                body_fat_rate=round(base_body_fat + body_fat_change, 1),
                muscle_mass=round(base_muscle + muscle_change, 1),
                bmi=round((base_weight + weight_change) / (1.75 ** 2), 1),
                waist_circumference=round(random.uniform(75, 90), 1),
                hip_circumference=round(random.uniform(90, 105), 1),
                chest_circumference=round(random.uniform(85, 100), 1),
                measurement_date=date,
                source="manual" if random.random() > 0.3 else "gym_sync"
            )
            db.add(measurement)
            measurements.append(measurement)
    
    db.commit()
    print(f"已生成 {len(measurements)} 条测试体测记录")
    return measurements


def generate_training_logs(db, users, exercises):
    """
    生成测试训练日志数据
    为每个用户生成过去30天的训练记录
    """
    training_logs = []
    training_items = []
    
    # 按分类分组训练项目
    exercises_by_category = {}
    for ex in exercises:
        if ex.category not in exercises_by_category:
            exercises_by_category[ex.category] = []
        exercises_by_category[ex.category].append(ex)
    
    for user in users:
        # 生成过去30天的数据，大约每2天训练一次
        for i in range(15):
            day_offset = random.randint(0, 29)
            date = datetime.now() - timedelta(days=day_offset)
            
            # 随机选择训练类型
            categories = list(exercises_by_category.keys())
            selected_category = random.choice(categories)
            category_exercises = exercises_by_category[selected_category]
            
            # 创建训练日志
            training_log = TrainingLog(
                user_id=user.id,
                training_date=date,
                duration=random.randint(45, 90),
                total_calories=0,  # 后续计算
                notes=random.choice([
                    "今天训练感觉很好！",
                    "状态一般，勉强完成",
                    "突破了个人记录！",
                    "休息日恢复训练",
                    "专注于核心力量训练"
                ]) if random.random() > 0.5 else None,
                mood=random.choice(["好", "一般", "差"])
            )
            db.add(training_log)
            db.flush()  # 获取ID
            
            # 创建训练日志详情（2-4个训练项目）
            num_exercises = random.randint(2, 4)
            selected_exercises = random.sample(category_exercises, min(num_exercises, len(category_exercises)))
            
            total_calories = 0
            for ex in selected_exercises:
                sets = random.randint(3, 5)
                reps = random.randint(8, 15)
                weight = random.uniform(10, 50) if "力量" in ex.category else 0
                duration = random.randint(10, 30) if "有氧" in ex.category or "HIIT" in ex.category else 0
                
                # 计算卡路里
                if ex.default_calories_per_hour and duration > 0:
                    calories = ex.default_calories_per_hour * (duration / 60)
                else:
                    calories = sets * 5 * (1 + weight / 100)
                
                item = TrainingLogItem(
                    training_log_id=training_log.id,
                    exercise_id=ex.id,
                    sets=sets,
                    reps=reps,
                    weight=round(weight, 1),
                    duration=duration,
                    calories=round(calories, 1),
                    notes=f"{ex.name}训练" if random.random() > 0.7 else None
                )
                db.add(item)
                training_items.append(item)
                total_calories += calories
            
            # 更新训练日志总卡路里
            training_log.total_calories = round(total_calories, 1)
            training_logs.append(training_log)
    
    db.commit()
    print(f"已生成 {len(training_logs)} 条测试训练日志，{len(training_items)} 条训练详情")
    return training_logs


def generate_goals(db, users):
    """
    生成测试目标数据
    为每个用户生成1-2个目标
    """
    goals = []
    training_plans = []
    diet_advices = []
    progress_records = []
    
    goal_types = [
        {"type": "lose_weight", "name": "减脂瘦身", "target": 5, "current": 0},
        {"type": "gain_muscle", "name": "增肌塑形", "target": 3, "current": 0},
        {"type": "shape", "name": "体态调整", "target": 100, "current": 0},
        {"type": "endurance", "name": "耐力提升", "target": 60, "current": 0}
    ]
    
    for user in users:
        # 为每个用户生成1-2个目标
        num_goals = random.randint(1, 2)
        selected_goals = random.sample(goal_types, num_goals)
        
        for goal_data in selected_goals:
            # 随机生成进度
            progress_percent = random.uniform(0, 100)
            current_value = goal_data["current"] + (goal_data["target"] * progress_percent / 100)
            
            # 确定目标状态
            if progress_percent >= 100:
                status = "completed"
            elif progress_percent >= 80 and random.random() > 0.7:
                status = "completed"
            else:
                status = "active"
            
            goal = Goal(
                user_id=user.id,
                goal_type=goal_data["type"],
                goal_name=goal_data["name"],
                description=f"目标是{goal_data['name']}，坚持就是胜利！",
                target_value=goal_data["target"],
                current_value=round(current_value, 1),
                start_date=datetime.now() - timedelta(days=random.randint(10, 60)),
                end_date=datetime.now() + timedelta(days=random.randint(30, 90)),
                status=status,
                progress=round(min(progress_percent, 100), 1)
            )
            db.add(goal)
            db.flush()  # 获取ID
            
            # 生成训练计划
            plan_names = {
                "lose_weight": ["有氧燃脂计划", "HIIT高强度训练"],
                "gain_muscle": ["力量增肌计划", "分化训练计划"],
                "shape": ["综合塑形计划", "瑜伽普拉提计划"],
                "endurance": ["耐力提升计划", "长跑训练计划"]
            }
            
            for plan_name in plan_names.get(goal_data["type"], ["基础训练计划"]):
                plan = TrainingPlan(
                    goal_id=goal.id,
                    plan_name=plan_name,
                    description=f"针对{goal_data['name']}的专业训练计划",
                    frequency=f"每周{random.randint(3, 5)}次",
                    duration=random.randint(45, 90),
                    exercises='[ {"name": "示例训练", "duration": 30} ]'
                )
                db.add(plan)
                training_plans.append(plan)
            
            # 生成饮食建议
            advice_types = ["breakfast", "lunch", "dinner"]
            advice_titles = {
                "breakfast": "高蛋白早餐",
                "lunch": "均衡午餐",
                "dinner": "清淡晚餐"
            }
            
            for advice_type in advice_types:
                advice = DietAdvice(
                    goal_id=goal.id,
                    advice_type=advice_type,
                    title=advice_titles[advice_type],
                    content=f"针对{goal_data['name']}目标的{advice_titles[advice_type]}建议：合理搭配营养，控制热量摄入。",
                    calories_range=f"{random.randint(300, 500)}-{random.randint(400, 600)}卡路里"
                )
                db.add(advice)
                diet_advices.append(advice)
            
            # 生成进度记录（3-5条）
            num_progress = random.randint(3, 5)
            for i in range(num_progress):
                day_offset = (num_progress - i) * 5
                record_date = datetime.now() - timedelta(days=day_offset)
                
                # 模拟进度递增
                progress_value = goal_data["current"] + (goal_data["target"] * (i + 1) / (num_progress + 1) * (progress_percent / 100))
                
                progress = GoalProgress(
                    goal_id=goal.id,
                    progress_value=round(progress_value, 1),
                    progress_percent=round((i + 1) / (num_progress + 1) * progress_percent, 1),
                    notes=f"第{i + 1}次进度记录，继续加油！",
                    record_date=record_date
                )
                db.add(progress)
                progress_records.append(progress)
            
            goals.append(goal)
    
    db.commit()
    print(f"已生成 {len(goals)} 个测试目标，{len(training_plans)} 个训练计划，{len(diet_advices)} 条饮食建议，{len(progress_records)} 条进度记录")
    return goals


def generate_all_test_data():
    """
    生成所有测试数据
    """
    print("=" * 50)
    print("开始生成测试数据...")
    print("=" * 50)
    
    # 初始化数据库
    init_db()
    
    # 创建会话
    db = SessionLocal()
    
    try:
        # 生成用户数据
        users = generate_users(db)
        
        # 生成训练项目数据
        exercises = generate_exercises(db)
        
        # 生成体测记录数据
        generate_body_measurements(db, users)
        
        # 生成训练日志数据
        generate_training_logs(db, users, exercises)
        
        # 生成目标数据
        generate_goals(db, users)
        
        print("=" * 50)
        print("测试数据生成完成！")
        print("=" * 50)
        print("\n测试账号信息：")
        print("用户名: testuser1, 密码: 123456")
        print("用户名: testuser2, 密码: 123456")
        print("用户名: testuser3, 密码: 123456")
        print("\nAPI文档地址: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"生成测试数据时出错: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_test_data()
