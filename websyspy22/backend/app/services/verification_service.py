"""
实名认证服务模块
提供手机号验证和人脸识别验证功能
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.member import Member, VerificationMethod
from app.services.sms_service import sms_service
from app.config import settings
import logging
import base64

logger = logging.getLogger(__name__)


class VerificationService:
    """
    实名认证服务类
    提供手机号验证和人脸识别验证功能
    """
    
    def verify_phone(
        self, 
        db: Session, 
        member: Member, 
        verification_code: str
    ) -> dict:
        """
        手机号验证
        Args:
            db: 数据库会话
            member: 会员对象
            verification_code: 验证码
        Returns:
            包含验证结果的字典
        """
        # 验证短信验证码
        if not sms_service.verify_code(member.phone, verification_code, "verification"):
            return {
                "success": False,
                "message": "验证码错误或已过期"
            }
        
        # 更新会员认证状态
        member.is_verified = 1
        member.verification_method = VerificationMethod.PHONE
        db.commit()
        db.refresh(member)
        
        logger.info(f"会员 {member.id} ({member.name}) 已通过手机号实名认证")
        
        return {
            "success": True,
            "message": "实名认证成功",
            "member_id": member.id,
            "verification_method": "phone"
        }
    
    def verify_face(
        self, 
        db: Session, 
        member: Member, 
        face_image_data: str
    ) -> dict:
        """
        人脸识别验证
        Args:
            db: 数据库会话
            member: 会员对象
            face_image_data: 人脸图像数据（base64编码）
        Returns:
            包含验证结果的字典
        """
        # 测试环境：模拟人脸识别
        if not settings.FACE_RECOGNITION_ENABLED:
            # 简单验证：检查是否有图像数据
            if not face_image_data or len(face_image_data) < 100:
                return {
                    "success": False,
                    "message": "人脸图像数据不完整"
                }
            
            # 模拟验证成功
            logger.info(f"[模拟人脸识别] 会员 {member.id} ({member.name}) 人脸识别验证通过")
            
            # 更新会员认证状态
            member.is_verified = 1
            member.verification_method = VerificationMethod.FACE_RECOGNITION
            db.commit()
            db.refresh(member)
            
            return {
                "success": True,
                "message": "人脸识别认证成功（测试环境）",
                "member_id": member.id,
                "verification_method": "face"
            }
        
        # 生产环境：调用实际人脸识别API
        return self._call_face_recognition_api(db, member, face_image_data)
    
    def _call_face_recognition_api(
        self, 
        db: Session, 
        member: Member, 
        face_image_data: str
    ) -> dict:
        """
        调用实际人脸识别API（生产环境）
        Args:
            db: 数据库会话
            member: 会员对象
            face_image_data: 人脸图像数据
        Returns:
            包含验证结果的字典
        """
        # TODO: 集成实际的人脸识别服务（如阿里云人脸核身、腾讯云人脸核身等）
        # 这里是占位实现，实际项目中需要替换为真实的API调用
        try:
            # 示例：调用第三方人脸核身API
            # response = httpx.post(
            #     "https://face-api.example.com/verify",
            #     json={
            #         "image": face_image_data,
            #         "id_card": member.id_card,
            #         "name": member.name,
            #         "api_key": settings.FACE_API_KEY
            #     }
            # )
            # result = response.json()
            # if result.get("success"):
            #     member.is_verified = 1
            #     member.verification_method = VerificationMethod.FACE_RECOGNITION
            #     db.commit()
            #     return {"success": True, "message": "人脸识别认证成功"}
            
            return {
                "success": False,
                "message": "人脸识别服务未配置"
            }
        except Exception as e:
            logger.error(f"人脸识别验证失败: {str(e)}")
            return {
                "success": False,
                "message": f"人脸识别验证失败: {str(e)}"
            }
    
    def send_verification_code(self, phone: str) -> dict:
        """
        发送实名认证验证码
        Args:
            phone: 手机号
        Returns:
            包含发送状态的字典
        """
        return sms_service.send_verification_code(phone, "verification")
    
    def check_verification_status(self, member: Member) -> dict:
        """
        检查会员实名认证状态
        Args:
            member: 会员对象
        Returns:
            包含认证状态的字典
        """
        status_map = {
            0: "未认证",
            1: "已认证"
        }
        
        method_map = {
            None: "未选择认证方式",
            VerificationMethod.PHONE: "手机号验证",
            VerificationMethod.FACE_RECOGNITION: "人脸识别"
        }
        
        return {
            "member_id": member.id,
            "is_verified": member.is_verified == 1,
            "status_text": status_map.get(member.is_verified, "未知状态"),
            "verification_method": member.verification_method,
            "verification_method_text": method_map.get(member.verification_method, "未知方式")
        }


# 创建全局服务实例
verification_service = VerificationService()
