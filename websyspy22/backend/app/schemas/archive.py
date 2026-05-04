"""
档案管理相关Pydantic模型
定义体测数据、运动目标、消费记录、课程参与的数据格式
"""
from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel, Field
from decimal import Decimal


# ==================== 体测数据模型 ====================

class PhysicalTestBase(BaseModel):
    """
    体测数据基础模型
    """
    test_date: date = Field(description="体测日期")
    height: Optional[Decimal] = Field(default=None, description="身高（cm）")
    weight: Optional[Decimal] = Field(default=None, description="体重（kg）")
    bmi: Optional[Decimal] = Field(default=None, description="BMI指数")
    body_fat: Optional[Decimal] = Field(default=None, description="体脂率（%）")
    muscle_mass: Optional[Decimal] = Field(default=None, description="肌肉量（kg）")
    bone_mass: Optional[Decimal] = Field(default=None, description="骨量（kg）")
    body_water: Optional[Decimal] = Field(default=None, description="体内水分（kg）")
    resting_heart_rate: Optional[int] = Field(default=None, description="静息心率（次/分）")
    blood_pressure_systolic: Optional[int] = Field(default=None, description="收缩压（mmHg）")
    blood_pressure_diastolic: Optional[int] = Field(default=None, description="舒张压（mmHg）")
    vital_capacity: Optional[Decimal] = Field(default=None, description="肺活量（L）")
    grip_strength: Optional[Decimal] = Field(default=None, description="握力（kg）")
    sit_and_reach: Optional[Decimal] = Field(default=None, description="坐位体前屈（cm）")
    tester: Optional[str] = Field(default=None, max_length=100, description="测试员")
    notes: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        from_attributes = True


class PhysicalTestCreate(PhysicalTestBase):
    """
    体测数据创建模型
    """
    pass


class PhysicalTestUpdate(BaseModel):
    """
    体测数据更新模型
    """
    test_date: Optional[date] = Field(default=None, description="体测日期")
    height: Optional[Decimal] = Field(default=None, description="身高（cm）")
    weight: Optional[Decimal] = Field(default=None, description="体重（kg）")
    bmi: Optional[Decimal] = Field(default=None, description="BMI指数")
    body_fat: Optional[Decimal] = Field(default=None, description="体脂率（%）")
    muscle_mass: Optional[Decimal] = Field(default=None, description="肌肉量（kg）")
    bone_mass: Optional[Decimal] = Field(default=None, description="骨量（kg）")
    body_water: Optional[Decimal] = Field(default=None, description="体内水分（kg）")
    resting_heart_rate: Optional[int] = Field(default=None, description="静息心率（次/分）")
    blood_pressure_systolic: Optional[int] = Field(default=None, description="收缩压（mmHg）")
    blood_pressure_diastolic: Optional[int] = Field(default=None, description="舒张压（mmHg）")
    vital_capacity: Optional[Decimal] = Field(default=None, description="肺活量（L）")
    grip_strength: Optional[Decimal] = Field(default=None, description="握力（kg）")
    sit_and_reach: Optional[Decimal] = Field(default=None, description="坐位体前屈（cm）")
    tester: Optional[str] = Field(default=None, max_length=100, description="测试员")
    notes: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        from_attributes = True


class PhysicalTestResponse(PhysicalTestBase):
    """
    体测数据响应模型
    """
    id: int = Field(description="体测记录ID")
    member_id: int = Field(description="会员ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 运动目标模型 ====================

class FitnessGoalBase(BaseModel):
    """
    运动目标基础模型
    """
    goal_type: str = Field(..., min_length=1, max_length=50, description="目标类型: 减肥/增肌/塑形/康复/其他")
    target_value: Optional[Decimal] = Field(default=None, description="目标值")
    current_value: Optional[Decimal] = Field(default=None, description="当前值")
    unit: Optional[str] = Field(default=None, max_length=20, description="单位")
    start_date: date = Field(description="开始日期")
    target_date: Optional[date] = Field(default=None, description="目标完成日期")
    actual_completion_date: Optional[date] = Field(default=None, description="实际完成日期")
    status: str = Field(default="active", max_length=20, description="目标状态: active/achieved/cancelled")
    progress: int = Field(default=0, description="进度百分比")
    description: Optional[str] = Field(default=None, description="目标描述")
    notes: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        from_attributes = True


class FitnessGoalCreate(FitnessGoalBase):
    """
    运动目标创建模型
    """
    pass


class FitnessGoalUpdate(BaseModel):
    """
    运动目标更新模型
    """
    goal_type: Optional[str] = Field(default=None, min_length=1, max_length=50, description="目标类型")
    target_value: Optional[Decimal] = Field(default=None, description="目标值")
    current_value: Optional[Decimal] = Field(default=None, description="当前值")
    unit: Optional[str] = Field(default=None, max_length=20, description="单位")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    target_date: Optional[date] = Field(default=None, description="目标完成日期")
    actual_completion_date: Optional[date] = Field(default=None, description="实际完成日期")
    status: Optional[str] = Field(default=None, max_length=20, description="目标状态")
    progress: Optional[int] = Field(default=None, description="进度百分比")
    description: Optional[str] = Field(default=None, description="目标描述")
    notes: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        from_attributes = True


class FitnessGoalResponse(FitnessGoalBase):
    """
    运动目标响应模型
    """
    id: int = Field(description="目标ID")
    member_id: int = Field(description="会员ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True


# ==================== 消费记录模型 ====================

class ConsumptionRecordBase(BaseModel):
    """
    消费记录基础模型
    """
    consumption_type: str = Field(..., min_length=1, max_length=50, description="消费类型: 办卡/续卡/私教/团课/商品/其他")
    item_name: str = Field(..., min_length=1, max_length=200, description="消费项目名称")
    amount: int = Field(..., description="消费金额（分）")
    discount_amount: int = Field(default=0, description="优惠金额（分）")
    actual_amount: int = Field(..., description="实付金额（分）")
    payment_method: Optional[str] = Field(default=None, max_length=50, description="支付方式: 现金/微信/支付宝/刷卡/其他")
    transaction_no: Optional[str] = Field(default=None, max_length=100, description="交易流水号")
    operator: Optional[str] = Field(default=None, max_length=100, description="操作人")
    notes: Optional[str] = Field(default=None, description="备注")
    
    class Config:
        from_attributes = True


class ConsumptionRecordCreate(ConsumptionRecordBase):
    """
    消费记录创建模型
    """
    pass


class ConsumptionRecordResponse(ConsumptionRecordBase):
    """
    消费记录响应模型
    """
    id: int = Field(description="消费记录ID")
    member_id: int = Field(description="会员ID")
    consumption_time: datetime = Field(description="消费时间")
    created_at: datetime = Field(description="创建时间")
    
    class Config:
        from_attributes = True


# ==================== 课程参与模型 ====================

class CourseParticipationBase(BaseModel):
    """
    课程参与基础模型
    """
    course_name: str = Field(..., min_length=1, max_length=200, description="课程名称")
    course_type: Optional[str] = Field(default=None, max_length=50, description="课程类型: 私教/团课/公开课")
    coach_name: Optional[str] = Field(default=None, max_length=100, description="教练姓名")
    participation_date: date = Field(description="参与日期")
    start_time: Optional[str] = Field(default=None, max_length=20, description="开始时间")
    end_time: Optional[str] = Field(default=None, max_length=20, description="结束时间")
    duration_minutes: Optional[int] = Field(default=None, description="时长（分钟）")
    status: str = Field(default="attended", max_length=20, description="参与状态: attended/absent/cancelled")
    rating: Optional[int] = Field(default=None, description="评分（1-5星）")
    feedback: Optional[str] = Field(default=None, description="反馈意见")
    
    class Config:
        from_attributes = True


class CourseParticipationCreate(CourseParticipationBase):
    """
    课程参与创建模型
    """
    pass


class CourseParticipationResponse(CourseParticipationBase):
    """
    课程参与响应模型
    """
    id: int = Field(description="参与记录ID")
    member_id: int = Field(description="会员ID")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")
    
    class Config:
        from_attributes = True
