"""
路由模块
包含所有API路由
"""

from . import auth, device, maintenance, fault, test_helper

__all__ = ['auth', 'device', 'maintenance', 'fault', 'test_helper']
