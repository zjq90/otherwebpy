from app.schemas.member import (
    MemberBase,
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    VerificationRequest,
    StatusChangeRequest,
)
from app.schemas.archive import (
    PhysicalTestBase,
    PhysicalTestCreate,
    PhysicalTestUpdate,
    PhysicalTestResponse,
    FitnessGoalBase,
    FitnessGoalCreate,
    FitnessGoalUpdate,
    FitnessGoalResponse,
    ConsumptionRecordBase,
    ConsumptionRecordCreate,
    ConsumptionRecordResponse,
    CourseParticipationBase,
    CourseParticipationCreate,
    CourseParticipationResponse,
)
from app.schemas.level import (
    MemberLevelBase,
    MemberLevelResponse,
    LevelBenefitBase,
    LevelBenefitResponse,
    MemberLevelInfo,
)
from app.schemas.common import (
    PaginatedResponse,
    ApiResponse,
    SuccessResponse,
    ErrorResponse,
)

__all__ = [
    # Member schemas
    "MemberBase",
    "MemberCreate",
    "MemberUpdate",
    "MemberResponse",
    "MemberListResponse",
    "VerificationRequest",
    "StatusChangeRequest",
    # Archive schemas
    "PhysicalTestBase",
    "PhysicalTestCreate",
    "PhysicalTestUpdate",
    "PhysicalTestResponse",
    "FitnessGoalBase",
    "FitnessGoalCreate",
    "FitnessGoalUpdate",
    "FitnessGoalResponse",
    "ConsumptionRecordBase",
    "ConsumptionRecordCreate",
    "ConsumptionRecordResponse",
    "CourseParticipationBase",
    "CourseParticipationCreate",
    "CourseParticipationResponse",
    # Level schemas
    "MemberLevelBase",
    "MemberLevelResponse",
    "LevelBenefitBase",
    "LevelBenefitResponse",
    "MemberLevelInfo",
    # Common schemas
    "PaginatedResponse",
    "ApiResponse",
    "SuccessResponse",
    "ErrorResponse",
]
