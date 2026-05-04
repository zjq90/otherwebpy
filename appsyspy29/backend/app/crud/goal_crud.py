"""
目标设定相关CRUD操作模块
负责目标数据的增删改查和进度管理
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models import Goal, TrainingPlan, DietAdvice, GoalProgress
from ..schemas import (
    GoalCreate, GoalUpdate, TrainingPlanCreate, DietAdviceCreate, GoalProgressCreate
)


def get_goal_by_id(db: Session, goal_id: int) -> Optional[Goal]:
    """
    根据ID获取目标
    """
    return db.query(Goal).filter(Goal.id == goal_id).first()


def get_user_goals(
    db: Session, 
    user_id: int, 
    status: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Goal]:
    """
    获取用户的目标列表
    可按状态过滤
    """
    query = db.query(Goal).filter(Goal.user_id == user_id)
    
    if status:
        query = query.filter(Goal.status == status)
    
    return query.order_by(Goal.created_at.desc()).offset(skip).limit(limit).all()


def get_active_goal(db: Session, user_id: int) -> Optional[Goal]:
    """
    获取用户当前进行中的目标
    """
    return db.query(Goal)\
        .filter(Goal.user_id == user_id, Goal.status == "active")\
        .order_by(Goal.created_at.desc())\
        .first()


def calculate_goal_progress(goal: Goal) -> float:
    """
    计算目标进度百分比
    """
    if goal.target_value is None or goal.current_value is None:
        return 0.0
    
    if goal.target_value == 0:
        return 0.0
    
    # 根据目标类型计算进度
    if goal.goal_type == "lose_weight":
        # 减脂目标：初始值 - 当前值 / (初始值 - 目标值)
        # 假设初始值可以从目标描述或第一次体测记录获取
        # 这里简化处理
        progress = 0.0
    else:
        # 其他目标：当前值 / 目标值
        progress = (goal.current_value / goal.target_value) * 100
    
    return round(min(max(progress, 0.0), 100.0), 1)


def generate_training_plans(goal_type: str) -> List[TrainingPlanCreate]:
    """
    根据目标类型生成推荐训练计划
    """
    plans = []
    
    if goal_type == "lose_weight":
        # 减脂目标训练计划
        plans.append(TrainingPlanCreate(
            plan_name="有氧燃脂计划",
            description="以有氧运动为主，配合力量训练提高基础代谢",
            frequency="每周5次",
            duration=60,
            exercises='[ {"name": "慢跑", "duration": 30}, {"name": "动感单车", "duration": 20}, {"name": "力量训练", "duration": 10} ]'
        ))
        plans.append(TrainingPlanCreate(
            plan_name="HIIT高强度间歇训练",
            description="高强度间歇训练，短时间内高效燃脂",
            frequency="每周3-4次",
            duration=45,
            exercises='[ {"name": "开合跳", "duration": 5}, {"name": "高抬腿", "duration": 5}, {"name": "波比跳", "duration": 5} ]'
        ))
    elif goal_type == "gain_muscle":
        # 增肌目标训练计划
        plans.append(TrainingPlanCreate(
            plan_name="力量增肌计划",
            description="大重量低次数，刺激肌肉生长",
            frequency="每周4-5次",
            duration=90,
            exercises='[ {"name": "卧推", "sets": 4, "reps": 8}, {"name": "深蹲", "sets": 4, "reps": 8}, {"name": "硬拉", "sets": 3, "reps": 6} ]'
        ))
        plans.append(TrainingPlanCreate(
            plan_name="分化训练计划",
            description="按部位分化训练，充分刺激每个肌肉群",
            frequency="每周5次",
            duration=75,
            exercises='[ {"name": "胸部训练日", "exercises": ["卧推", "飞鸟", "夹胸"]}, {"name": "背部训练日", "exercises": ["引体", "划船", "硬拉"]} ]'
        ))
    elif goal_type == "shape":
        # 塑形目标训练计划
        plans.append(TrainingPlanCreate(
            plan_name="综合塑形计划",
            description="有氧与力量结合，塑造完美体态",
            frequency="每周4-5次",
            duration=60,
            exercises='[ {"name": "瑜伽", "duration": 30}, {"name": "普拉提", "duration": 20}, {"name": "轻重量力量", "duration": 10} ]'
        ))
    else:
        # 耐力目标训练计划
        plans.append(TrainingPlanCreate(
            plan_name="耐力提升计划",
            description="逐步提升心肺功能和肌肉耐力",
            frequency="每周4-6次",
            duration=90,
            exercises='[ {"name": "长跑", "duration": 45}, {"name": "游泳", "duration": 30}, {"name": "骑行", "duration": 60} ]'
        ))
    
    return plans


def generate_diet_advices(goal_type: str) -> List[DietAdviceCreate]:
    """
    根据目标类型生成推荐饮食建议
    """
    advices = []
    
    if goal_type == "lose_weight":
        # 减脂饮食建议
        advices.append(DietAdviceCreate(
            advice_type="breakfast",
            title="高蛋白早餐",
            content="建议食用：水煮蛋2个、全麦面包2片、无糖豆浆1杯、蔬菜水果适量。避免高糖、油炸食品。",
            calories_range="300-400卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="lunch",
            title="均衡午餐",
            content="建议食用：鸡胸肉/鱼肉150g、糙米饭/杂粮饭100g、大量蔬菜。烹饪方式以蒸煮为主，少油少盐。",
            calories_range="400-500卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="dinner",
            title="清淡晚餐",
            content="建议食用：鱼类/豆制品100g、大量绿叶蔬菜、少量杂粮。晚餐时间不宜过晚，7点前完成。",
            calories_range="300-400卡路里"
        ))
    elif goal_type == "gain_muscle":
        # 增肌饮食建议
        advices.append(DietAdviceCreate(
            advice_type="breakfast",
            title="增肌早餐",
            content="建议食用：全蛋3个+蛋清2个、全麦面包3片、牛奶1杯、香蕉1根。确保充足的蛋白质和碳水。",
            calories_range="500-600卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="lunch",
            title="高蛋白午餐",
            content="建议食用：鸡胸肉/牛肉200g、糙米饭150g、大量蔬菜。蛋白质是肌肉生长的关键。",
            calories_range="600-700卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="snack",
            title="训练后补给",
            content="训练后30分钟内补充蛋白质：蛋白粉1勺+香蕉1根，或鸡胸肉沙拉。促进肌肉恢复和生长。",
            calories_range="200-300卡路里"
        ))
    elif goal_type == "shape":
        # 塑形饮食建议
        advices.append(DietAdviceCreate(
            advice_type="breakfast",
            title="营养早餐",
            content="建议食用：燕麦粥1碗、水煮蛋1个、酸奶1杯、蓝莓适量。营养均衡，提供持续能量。",
            calories_range="350-450卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="lunch",
            title="均衡午餐",
            content="建议食用：鱼肉/鸡肉150g、红薯100g、各色蔬菜。烹饪方式多样化，保证营养均衡。",
            calories_range="450-550卡路里"
        ))
    else:
        # 耐力饮食建议
        advices.append(DietAdviceCreate(
            advice_type="breakfast",
            title="能量早餐",
            content="建议食用：全麦面包3片、花生酱适量、香蕉1根、运动饮料1杯。为长时间运动储备能量。",
            calories_range="500-600卡路里"
        ))
        advices.append(DietAdviceCreate(
            advice_type="lunch",
            title="高碳水午餐",
            content="建议食用：意面/米饭200g、鸡胸肉150g、蔬菜适量。碳水化合物是耐力运动的主要能量来源。",
            calories_range="600-700卡路里"
        ))
    
    return advices


def create_goal(db: Session, user_id: int, goal: GoalCreate) -> Goal:
    """
    创建新目标
    同时生成推荐训练计划和饮食建议
    """
    db_goal = Goal(
        user_id=user_id,
        goal_type=goal.goal_type.value,
        goal_name=goal.goal_name,
        description=goal.description,
        target_value=goal.target_value,
        current_value=goal.current_value,
        start_date=goal.start_date or datetime.now(),
        end_date=goal.end_date,
        status="active",
        progress=0.0
    )
    db.add(db_goal)
    db.flush()  # 刷新以获取ID
    
    # 生成推荐训练计划
    if not goal.training_plans:
        # 根据目标类型自动生成
        auto_plans = generate_training_plans(goal.goal_type.value)
        for plan in auto_plans:
            db_plan = TrainingPlan(
                goal_id=db_goal.id,
                plan_name=plan.plan_name,
                description=plan.description,
                frequency=plan.frequency,
                duration=plan.duration,
                exercises=plan.exercises
            )
            db.add(db_plan)
    else:
        # 使用用户提供的计划
        for plan in goal.training_plans:
            db_plan = TrainingPlan(
                goal_id=db_goal.id,
                plan_name=plan.plan_name,
                description=plan.description,
                frequency=plan.frequency,
                duration=plan.duration,
                exercises=plan.exercises
            )
            db.add(db_plan)
    
    # 生成推荐饮食建议
    if not goal.diet_advices:
        # 根据目标类型自动生成
        auto_advices = generate_diet_advices(goal.goal_type.value)
        for advice in auto_advices:
            db_advice = DietAdvice(
                goal_id=db_goal.id,
                advice_type=advice.advice_type,
                title=advice.title,
                content=advice.content,
                calories_range=advice.calories_range
            )
            db.add(db_advice)
    else:
        # 使用用户提供的建议
        for advice in goal.diet_advices:
            db_advice = DietAdvice(
                goal_id=db_goal.id,
                advice_type=advice.advice_type,
                title=advice.title,
                content=advice.content,
                calories_range=advice.calories_range
            )
            db.add(db_advice)
    
    db.commit()
    db.refresh(db_goal)
    return db_goal


def update_goal(
    db: Session, 
    goal_id: int, 
    goal: GoalUpdate
) -> Optional[Goal]:
    """
    更新目标信息
    """
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return None
    
    # 更新非空字段
    update_data = goal.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status" and value:
            value = value.value
        setattr(db_goal, key, value)
    
    # 重新计算进度
    if db_goal.target_value is not None and db_goal.current_value is not None:
        db_goal.progress = calculate_goal_progress(db_goal)
    
    db_goal.updated_at = datetime.now()
    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, goal_id: int) -> bool:
    """
    删除目标
    """
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return False
    
    db.delete(db_goal)
    db.commit()
    return True


def add_goal_progress(
    db: Session, 
    goal_id: int, 
    progress: GoalProgressCreate
) -> Optional[GoalProgress]:
    """
    添加目标进度记录
    """
    db_goal = get_goal_by_id(db, goal_id)
    if not db_goal:
        return None
    
    # 计算进度百分比
    progress_percent = progress.progress_percent
    if progress_percent is None and db_goal.target_value:
        progress_percent = (progress.progress_value / db_goal.target_value) * 100
        progress_percent = round(min(max(progress_percent, 0.0), 100.0), 1)
    
    db_progress = GoalProgress(
        goal_id=goal_id,
        progress_value=progress.progress_value,
        progress_percent=progress_percent,
        notes=progress.notes,
        record_date=progress.record_date or datetime.now()
    )
    db.add(db_progress)
    db.flush()
    
    # 更新目标的当前值和进度
    db_goal.current_value = progress.progress_value
    db_goal.progress = progress_percent or 0.0
    db_goal.updated_at = datetime.now()
    
    # 检查是否完成目标
    if db_goal.progress >= 100.0:
        db_goal.status = "completed"
    
    db.commit()
    db.refresh(db_progress)
    return db_progress


def get_goal_progress_records(
    db: Session, 
    goal_id: int, 
    limit: int = 30
) -> List[GoalProgress]:
    """
    获取目标的进度记录列表
    """
    return db.query(GoalProgress)\
        .filter(GoalProgress.goal_id == goal_id)\
        .order_by(GoalProgress.record_date.desc())\
        .limit(limit)\
        .all()


def get_goal_with_details(db: Session, goal_id: int) -> Optional[Goal]:
    """
    获取目标及其详情（训练计划、饮食建议、进度记录）
    """
    return db.query(Goal)\
        .filter(Goal.id == goal_id)\
        .first()
