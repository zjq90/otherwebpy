"""
权限配置模块
定义系统中所有可用的权限和角色
"""

# ==================== 权限定义 ====================

# 权限模块定义
PERMISSION_MODULES = {
    "farm": {
        "name": "农场管理",
        "icon": "fa-building",
        "permissions": [
            {
                "code": "farm:read",
                "name": "查看农场",
                "description": "查看农场列表和详情"
            },
            {
                "code": "farm:create",
                "name": "创建农场",
                "description": "添加新农场"
            },
            {
                "code": "farm:update",
                "name": "更新农场",
                "description": "修改农场信息"
            },
            {
                "code": "farm:delete",
                "name": "删除农场",
                "description": "删除农场数据"
            }
        ]
    },
    "plot": {
        "name": "地块管理",
        "icon": "fa-map-marker",
        "permissions": [
            {
                "code": "plot:read",
                "name": "查看地块",
                "description": "查看地块列表和详情"
            },
            {
                "code": "plot:create",
                "name": "创建地块",
                "description": "添加新地块"
            },
            {
                "code": "plot:update",
                "name": "更新地块",
                "description": "修改地块信息"
            },
            {
                "code": "plot:delete",
                "name": "删除地块",
                "description": "删除地块数据"
            }
        ]
    },
    "crop": {
        "name": "作物档案",
        "icon": "fa-tree",
        "permissions": [
            {
                "code": "crop:read",
                "name": "查看作物",
                "description": "查看作物列表和详情"
            },
            {
                "code": "crop:create",
                "name": "创建作物",
                "description": "添加新作物"
            },
            {
                "code": "crop:update",
                "name": "更新作物",
                "description": "修改作物信息"
            },
            {
                "code": "crop:delete",
                "name": "删除作物",
                "description": "删除作物数据"
            }
        ]
    },
    "staff": {
        "name": "人员管理",
        "icon": "fa-users",
        "permissions": [
            {
                "code": "staff:read",
                "name": "查看人员",
                "description": "查看员工列表和详情"
            },
            {
                "code": "staff:create",
                "name": "创建人员",
                "description": "添加新员工"
            },
            {
                "code": "staff:update",
                "name": "更新人员",
                "description": "修改员工信息"
            },
            {
                "code": "staff:delete",
                "name": "删除人员",
                "description": "删除员工数据"
            }
        ]
    },
    "system": {
        "name": "系统管理",
        "icon": "fa-cog",
        "permissions": [
            {
                "code": "system:admin",
                "name": "系统管理员",
                "description": "拥有系统所有权限"
            },
            {
                "code": "system:test",
                "name": "测试数据管理",
                "description": "管理测试数据生成和清除"
            }
        ]
    }
}


# ==================== 角色定义 ====================

# 预设角色
PREDEFINED_ROLES = [
    {
        "name": "超级管理员",
        "code": "super_admin",
        "description": "拥有系统所有权限",
        "permissions": [],
        "is_system": True,
        "is_default": False
    },
    {
        "name": "农场经理",
        "code": "farm_manager",
        "description": "管理农场和所有业务数据",
        "permissions": [
            "farm:read", "farm:create", "farm:update", "farm:delete",
            "plot:read", "plot:create", "plot:update", "plot:delete",
            "crop:read", "crop:create", "crop:update", "crop:delete",
            "staff:read"
        ],
        "is_system": True,
        "is_default": False
    },
    {
        "name": "技术人员",
        "code": "technician",
        "description": "查看农场数据，管理作物档案",
        "permissions": [
            "farm:read",
            "plot:read",
            "crop:read", "crop:create", "crop:update",
            "staff:read"
        ],
        "is_system": True,
        "is_default": True
    },
    {
        "name": "普通员工",
        "code": "employee",
        "description": "仅能查看基础数据",
        "permissions": [
            "farm:read",
            "plot:read",
            "crop:read"
        ],
        "is_system": True,
        "is_default": False
    }
]


# ==================== 辅助函数 ====================

def get_all_permissions():
    """
    获取所有权限列表
    """
    permissions = []
    for module_code, module_info in PERMISSION_MODULES.items():
        for perm in module_info["permissions"]:
            permissions.append({
                "module_code": module_code,
                "module_name": module_info["name"],
                "module_icon": module_info["icon"],
                **perm
            })
    return permissions


def get_permission_modules():
    """
    获取所有权限模块（带权限列表）
    """
    return PERMISSION_MODULES


def get_permissions_by_module(module_code):
    """
    根据模块代码获取权限列表
    """
    module = PERMISSION_MODULES.get(module_code)
    if module:
        return module["permissions"]
    return []


def has_permission(user_permissions, required_permission):
    """
    检查用户是否拥有指定权限
    
    :param user_permissions: 用户权限列表（逗号分隔的字符串或列表）
    :param required_permission: 需要检查的权限代码
    :return: 是否拥有权限
    """
    if not user_permissions:
        return False
    
    # 转换为列表
    if isinstance(user_permissions, str):
        user_permission_list = [p.strip() for p in user_permissions.split(",") if p.strip()]
    else:
        user_permission_list = list(user_permissions)
    
    # 检查是否有通配符权限
    for perm in user_permission_list:
        if perm == "*":
            return True
        if perm == "system:admin":
            return True
        if ":" in perm:
            module, action = perm.split(":", 1)
            # 检查通配符，如 "farm:*" 匹配所有农场权限
            if action == "*":
                req_module = required_permission.split(":")[0]
                if module == req_module:
                    return True
    
    # 直接检查是否存在
    return required_permission in user_permission_list


def parse_permissions(permission_str):
    """
    解析权限字符串为列表
    
    :param permission_str: 逗号分隔的权限字符串
    :return: 权限列表
    """
    if not permission_str:
        return []
    return [p.strip() for p in permission_str.split(",") if p.strip()]


def serialize_permissions(permission_list):
    """
    序列化权限列表为字符串
    
    :param permission_list: 权限列表
    :return: 逗号分隔的权限字符串
    """
    if not permission_list:
        return None
    return ",".join(permission_list)
