"""
测试数据生成脚本
用于初始化数据库并生成测试数据
运行此脚本将：
1. 创建数据库表（如果不存在）
2. 删除现有数据（可选）
3. 生成测试数据包括：管理员用户、普通用户、产品、服务、案例、文档等
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import User, Product, Service, Case, Document, KeyApplication
from security import get_password_hash, generate_api_key


def init_database():
    """
    初始化数据库，创建所有表
    """
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def clear_database(session):
    """
    清空数据库中的所有数据
    """
    print("正在清空现有数据...")
    session.query(KeyApplication).delete()
    session.query(Document).delete()
    session.query(Case).delete()
    session.query(Service).delete()
    session.query(Product).delete()
    session.query(User).delete()
    session.commit()
    print("现有数据已清空！")


def create_admin_user(session):
    """
    创建管理员用户
    """
    print("正在创建管理员用户...")
    
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        full_name="系统管理员",
        phone="13800138000",
        is_active=True,
        is_admin=True
    )
    
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    print(f"管理员用户创建成功！")
    print(f"  用户名: admin")
    print(f"  密码: admin123")
    print(f"  邮箱: admin@example.com")
    
    return admin


def create_normal_users(session):
    """
    创建普通测试用户
    """
    print("正在创建普通用户...")
    
    users_data = [
        {
            "username": "zhangsan",
            "email": "zhangsan@example.com",
            "password": "123456",
            "full_name": "张三",
            "phone": "13800138001"
        },
        {
            "username": "lisi",
            "email": "lisi@example.com",
            "password": "123456",
            "full_name": "李四",
            "phone": "13800138002"
        },
        {
            "username": "wangwu",
            "email": "wangwu@example.com",
            "password": "123456",
            "full_name": "王五",
            "phone": "13800138003"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            phone=user_data["phone"],
            is_active=True,
            is_admin=False
        )
        session.add(user)
        created_users.append(user)
    
    session.commit()
    
    print(f"成功创建 {len(created_users)} 个普通用户！")
    print("  默认密码: 123456")
    
    return created_users


def create_products(session):
    """
    创建产品测试数据
    """
    print("正在创建产品数据...")
    
    products_data = [
        {
            "name": "企业管理系统",
            "short_desc": "一站式企业管理解决方案，包含OA、CRM、ERP等功能模块",
            "description": "本产品是一套完整的企业管理系统，涵盖人力资源管理、客户关系管理、项目管理、财务管理等多个模块，帮助企业实现数字化转型。系统采用微服务架构，支持灵活扩展，可根据企业需求定制开发。",
            "price": "9999.00",
            "category": "企业软件",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20enterprise%20software%20dashboard%20interface%20with%20charts%20and%20data%20visualization&image_size=landscape_4_3",
            "sort_order": 10,
            "is_active": True
        },
        {
            "name": "智能客服系统",
            "short_desc": "AI驱动的智能客服解决方案，支持多渠道接入",
            "description": "基于大语言模型的智能客服系统，支持文本、语音、视频等多种交互方式。系统具备自然语言理解、意图识别、知识库管理等核心功能，可大幅降低人工客服成本，提升客户满意度。",
            "price": "5999.00",
            "category": "AI应用",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AI%20chatbot%20interface%20with%20robot%20avatar%20and%20conversation%20bubbles&image_size=landscape_4_3",
            "sort_order": 9,
            "is_active": True
        },
        {
            "name": "数据分析平台",
            "short_desc": "专业的大数据分析和可视化平台",
            "description": "强大的数据分析平台，支持多种数据源接入，提供丰富的数据可视化组件。用户可以通过拖拽方式快速构建数据看板，支持实时数据更新和多维度数据分析。",
            "price": "7999.00",
            "category": "数据分析",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=data%20analytics%20dashboard%20with%20colorful%20charts%20graphs%20and%20business%20intelligence%20interface&image_size=landscape_4_3",
            "sort_order": 8,
            "is_active": True
        },
        {
            "name": "云存储服务",
            "short_desc": "安全可靠的企业级云存储解决方案",
            "description": "企业级云存储服务，提供海量存储空间、多重数据备份、高速访问等特性。支持文件同步、版本控制、权限管理等高级功能，是企业数据存储的理想选择。",
            "price": "2999.00/年",
            "category": "云服务",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cloud%20storage%20concept%20with%20digital%20clouds%20files%20and%20servers%20network&image_size=landscape_4_3",
            "sort_order": 7,
            "is_active": True
        },
        {
            "name": "API网关服务",
            "short_desc": "高性能的API管理和网关服务",
            "description": "专业的API网关服务，提供限流、熔断、负载均衡、安全认证等功能。支持多种协议转换，帮助企业构建安全、可靠、高性能的API生态系统。",
            "price": "4999.00",
            "category": "云服务",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=API%20gateway%20architecture%20diagram%20with%20data%20flow%20connections%20and%20servers&image_size=landscape_4_3",
            "sort_order": 6,
            "is_active": True
        },
        {
            "name": "安全扫描工具",
            "short_desc": "自动化的Web应用安全扫描工具",
            "description": "专业的Web安全扫描工具，支持SQL注入、XSS、CSRF等常见漏洞检测。提供详细的漏洞报告和修复建议，帮助企业提前发现和修复安全问题。",
            "price": "3999.00",
            "category": "安全工具",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cybersecurity%20scanning%20interface%20with%20shield%20icon%20and%20security%20reports&image_size=landscape_4_3",
            "sort_order": 5,
            "is_active": True
        }
    ]
    
    for product_data in products_data:
        product = Product(**product_data)
        session.add(product)
    
    session.commit()
    print(f"成功创建 {len(products_data)} 个产品！")


def create_services(session):
    """
    创建服务测试数据
    """
    print("正在创建服务数据...")
    
    services_data = [
        {
            "name": "定制开发服务",
            "short_desc": "根据您的需求，提供专业的软件定制开发服务",
            "description": "我们拥有经验丰富的开发团队，可根据企业的具体业务需求，提供从需求分析到上线运维的全流程定制开发服务。",
            "icon": "bi bi-code-slash",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=software%20development%20team%20working%20on%20code%20with%20multiple%20screens&image_size=landscape_4_3",
            "sort_order": 10,
            "is_active": True
        },
        {
            "name": "系统集成服务",
            "short_desc": "打通系统壁垒，实现数据互联互通",
            "description": "提供企业内部各系统的集成服务，包括ERP、CRM、OA等系统的对接，实现数据的统一管理和流程的自动化。",
            "icon": "bi bi-diagram-3",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=system%20integration%20network%20diagram%20connecting%20different%20business%20systems&image_size=landscape_4_3",
            "sort_order": 9,
            "is_active": True
        },
        {
            "name": "技术咨询服务",
            "short_desc": "专业的技术架构和解决方案咨询",
            "description": "由资深架构师提供技术咨询服务，包括系统架构设计、技术选型、性能优化等方面的专业建议。",
            "icon": "bi bi-lightbulb",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=technology%20consulting%20meeting%20with%20architect%20discussing%20blueprints&image_size=landscape_4_3",
            "sort_order": 8,
            "is_active": True
        },
        {
            "name": "运维支持服务",
            "short_desc": "7x24小时的系统运维和技术支持",
            "description": "提供专业的运维支持服务，包括系统监控、故障排查、性能调优、安全加固等，确保系统稳定运行。",
            "icon": "bi bi-gear-wide-connected",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=data%20center%20operations%20with%20servers%20monitors%20and%20support%20team&image_size=landscape_4_3",
            "sort_order": 7,
            "is_active": True
        },
        {
            "name": "培训服务",
            "short_desc": "专业的技术培训和知识转移",
            "description": "提供各类技术培训服务，包括开发技术培训、系统使用培训、安全意识培训等，帮助企业提升团队能力。",
            "icon": "bi bi-mortarboard",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=professional%20training%20workshop%20with%20instructor%20and%20audience&image_size=landscape_4_3",
            "sort_order": 6,
            "is_active": True
        },
        {
            "name": "云迁移服务",
            "short_desc": "平滑、安全的系统上云迁移服务",
            "description": "提供专业的云迁移服务，包括迁移评估、方案设计、迁移实施、验证优化等全流程服务，确保系统平滑迁移到云端。",
            "icon": "bi bi-cloud-arrow-up",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cloud%20migration%20concept%20with%20data%20flowing%20from%20on-premise%20to%20cloud&image_size=landscape_4_3",
            "sort_order": 5,
            "is_active": True
        }
    ]
    
    for service_data in services_data:
        service = Service(**service_data)
        session.add(service)
    
    session.commit()
    print(f"成功创建 {len(services_data)} 个服务！")


def create_cases(session):
    """
    创建案例测试数据
    """
    print("正在创建案例数据...")
    
    cases_data = [
        {
            "title": "某大型银行数字化转型项目",
            "short_desc": "帮助某大型银行完成核心业务系统的数字化改造",
            "description": "为某国有大型银行提供了完整的数字化转型解决方案，包括核心业务系统重构、数据中台建设、智能客服系统上线等。项目上线后，业务处理效率提升300%，客户满意度显著提升。",
            "content": """## 项目背景

该银行作为国内领先的金融机构，面临着业务快速发展和技术架构陈旧的矛盾。原有的核心系统已经运行超过10年，难以支撑新业务的快速迭代。

## 解决方案

1. **核心系统重构**：采用微服务架构重构核心业务系统
2. **数据中台建设**：构建统一的数据服务平台
3. **智能客服**：引入AI智能客服系统
4. **移动银行**：全新设计的移动端应用

## 项目成果

- 业务处理效率提升300%
- 系统可用性达到99.99%
- 客户满意度提升45%
- IT运维成本降低40%""",
            "client": "某国有大型银行",
            "category": "金融行业",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=modern%20banking%20digital%20transformation%20project%20with%20futuristic%20interface&image_size=landscape_16_9",
            "is_featured": True,
            "sort_order": 10,
            "is_active": True
        },
        {
            "title": "电商平台高并发架构设计",
            "short_desc": "为某头部电商平台设计支持亿级流量的技术架构",
            "description": "为某知名电商平台进行了全面的架构升级，采用分布式架构设计，支持亿级流量的峰值访问。在双十一等大促期间，系统表现稳定，零故障运行。",
            "content": """## 项目挑战

该电商平台面临的主要挑战：
- 单日订单量突破1000万
- 峰值QPS达到50万
- 需要保证99.99%的系统可用性

## 技术方案

1. **多层缓存架构**：Redis + 本地缓存
2. **分布式消息队列**：Kafka异步处理
3. **数据库分库分表**：ShardingSphere
4. **微服务网关**：统一入口和限流
5. **全链路监控**：Prometheus + Grafana

## 项目成果

- 成功支撑双十一1200万订单
- 系统响应时间降低60%
- 故障率降低90%""",
            "client": "某知名电商平台",
            "category": "电商行业",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=ecommerce%20platform%20high%20traffic%20architecture%20with%20shopping%20carts%20and%20data%20flow&image_size=landscape_16_9",
            "is_featured": True,
            "sort_order": 9,
            "is_active": True
        },
        {
            "title": "智慧校园建设项目",
            "short_desc": "为某知名高校打造一体化智慧校园平台",
            "description": "为某985高校建设了完整的智慧校园平台，涵盖教务管理、学生服务、后勤管理、校园安全等多个模块。平台上线后，极大提升了学校的管理效率和师生体验。",
            "content": """## 项目概述

该项目是一个综合性的智慧校园建设项目，旨在通过信息化手段提升学校的管理水平和服务质量。

## 主要功能

1. **教务管理系统**：选课、成绩、排课
2. **学生服务平台**：奖学金、资助、就业
3. **后勤管理系统**：宿舍、餐饮、报修
4. **校园安防系统**：视频监控、门禁管理
5. **移动校园APP**：一站式服务入口

## 应用效果

- 教职工工作效率提升50%
- 学生满意度提升85%
- 管理成本降低30%""",
            "client": "某985高校",
            "category": "教育行业",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=smart%20campus%20digital%20platform%20with%20university%20buildings%20and%20students&image_size=landscape_16_9",
            "is_featured": True,
            "sort_order": 8,
            "is_active": True
        },
        {
            "title": "医疗健康大数据平台",
            "short_desc": "为某三甲医院构建医疗大数据分析平台",
            "description": "为某三甲医院建设了医疗大数据平台，实现了临床数据的整合分析，支持辅助诊断、科研数据分析、质量管理等多种应用场景。",
            "content": """## 项目目标

构建一个统一的医疗大数据平台，实现：
- 多源异构数据的整合
- 临床数据的深度分析
- 辅助决策支持
- 科研数据服务

## 技术架构

- 数据采集层：ETL工具 + 实时接入
- 数据存储层：Hadoop + HBase
- 计算引擎层：Spark + Flink
- 分析服务层：机器学习 + BI报表

## 应用成果

- 实现了5年历史数据的整合分析
- 辅助诊断准确率提升25%
- 科研数据获取效率提升10倍""",
            "client": "某三甲医院",
            "category": "医疗行业",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=healthcare%20big%20data%20analytics%20platform%20with%20medical%20records%20and%20charts&image_size=landscape_16_9",
            "is_featured": False,
            "sort_order": 7,
            "is_active": True
        },
        {
            "title": "智能物流调度系统",
            "short_desc": "为某物流企业打造智能调度平台",
            "description": "为某大型物流企业开发了智能调度系统，采用AI算法进行路径优化和资源调度，大幅提升了配送效率，降低了运营成本。",
            "content": """## 业务痛点

该物流企业面临的问题：
- 人工调度效率低
- 车辆空驶率高
- 配送成本难以控制
- 客户体验有待提升

## 解决方案

1. **智能排单算法**：基于AI的订单分配
2. **路径优化**：TSP问题求解
3. **实时调度**：动态调整配送计划
4. **数据分析**：运营数据可视化

## 项目效果

- 配送效率提升40%
- 车辆空驶率降低35%
- 配送成本降低20%
- 客户满意度提升60%""",
            "client": "某大型物流企业",
            "category": "物流行业",
            "image_url": "https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=smart%20logistics%20dispatching%20system%20with%20delivery%20trucks%20and%20route%20optimization&image_size=landscape_16_9",
            "is_featured": False,
            "sort_order": 6,
            "is_active": True
        }
    ]
    
    for case_data in cases_data:
        case = Case(**case_data)
        session.add(case)
    
    session.commit()
    print(f"成功创建 {len(cases_data)} 个案例！")


def create_documents(session):
    """
    创建文档测试数据
    """
    print("正在创建文档数据...")
    
    documents_data = [
        {
            "title": "快速入门指南",
            "short_desc": "帮助您快速上手使用我们的产品和服务",
            "description": "本指南将帮助您了解如何快速开始使用我们的产品，包括账号注册、系统配置、基础功能使用等内容。",
            "content": """# 快速入门指南

## 1. 账号注册

访问注册页面，填写以下信息：
- 用户名（3-50个字符）
- 邮箱地址（用于接收验证邮件）
- 密码（至少6个字符）
- 真实姓名（可选）

## 2. 系统登录

1. 访问登录页面
2. 输入用户名和密码
3. 点击"登录"按钮

登录成功后，您将被重定向到首页。

## 3. 基础功能介绍

### 3.1 产品浏览

- 点击导航栏的"产品展示"
- 可以按分类筛选产品
- 点击产品卡片查看详情

### 3.2 服务查看

- 点击导航栏的"服务介绍"
- 了解我们提供的各类服务
- 如需咨询可联系客服

### 3.3 案例展示

- 点击导航栏的"案例展示"
- 查看我们的成功案例
- 了解项目实施效果

## 4. 下一步

- 了解详细功能请查看《用户手册》
- 如需API访问请申请秘钥
- 如有问题请查看《常见问题》
""",
            "category": "入门指南",
            "tags": "入门,快速开始,指南",
            "sort_order": 10,
            "view_count": 1256,
            "is_active": True
        },
        {
            "title": "API接口文档",
            "short_desc": "完整的API接口参考文档",
            "description": "本文档详细介绍了所有可用的API接口，包括接口说明、请求参数、响应格式等信息。",
            "content": """# API接口文档

## 概述

本API采用RESTful设计风格，所有接口返回JSON格式数据。

### 基础URL

```
https://api.example.com/v1
```

### 认证方式

除登录注册接口外，其他接口需要在请求头中携带认证令牌：

```
Authorization: Bearer <your_token>
```

## 用户认证接口

### 1. 用户登录

**POST** `/auth/login`

请求参数：
```json
{
    "username": "用户名",
    "password": "密码"
}
```

响应示例：
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

### 2. 用户注册

**POST** `/auth/register`

请求参数：
```json
{
    "username": "用户名",
    "email": "邮箱地址",
    "password": "密码",
    "full_name": "真实姓名（可选）"
}
```

## 产品接口

### 获取产品列表

**GET** `/products`

查询参数：
- `category` (可选): 产品分类
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认10

### 获取产品详情

**GET** `/products/{id}`

## 公共响应码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
""",
            "category": "API文档",
            "tags": "API,接口,开发文档",
            "sort_order": 9,
            "view_count": 3420,
            "is_active": True
        },
        {
            "title": "用户手册",
            "short_desc": "详细的系统功能使用说明",
            "description": "本手册详细介绍了系统各功能模块的使用方法，帮助您充分利用系统的各项功能。",
            "content": """# 用户手册

## 第一章 系统概述

### 1.1 系统简介

本系统是一个综合性的企业展示平台，包含产品展示、服务介绍、案例展示、文档中心等功能模块。

### 1.2 主要功能

- **产品展示**：展示企业产品信息
- **服务介绍**：介绍企业提供的服务
- **案例展示**：展示成功案例
- **文档中心**：提供技术文档
- **用户中心**：个人信息和秘钥管理

## 第二章 用户管理

### 2.1 用户注册

1. 点击右上角"注册"按钮
2. 填写注册信息
3. 点击"提交"完成注册

### 2.2 用户登录

1. 点击右上角"登录"按钮
2. 输入用户名和密码
3. 点击"登录"

### 2.3 密码找回

如忘记密码，请联系系统管理员重置密码。

## 第三章 个人中心

### 3.1 查看个人信息

登录后，点击右上角用户名，选择"个人中心"可查看个人信息。

### 3.2 秘钥申请

1. 进入个人中心
2. 点击"秘钥申请"
3. 填写申请信息
4. 提交申请等待审核

### 3.3 查看申请记录

在个人中心页面可查看所有秘钥申请记录及其状态。

## 第四章 系统功能

### 4.1 产品浏览

- 列表页支持分类筛选
- 产品详情页展示详细信息

### 4.2 案例查看

- 推荐案例展示在首页
- 支持按行业分类筛选

### 4.3 文档阅读

- 文档按分类组织
- 支持内容搜索

## 第五章 常见问题

请查看《常见问题》文档。
""",
            "category": "用户手册",
            "tags": "用户手册,功能说明,操作指南",
            "sort_order": 8,
            "view_count": 890,
            "is_active": True
        },
        {
            "title": "常见问题",
            "short_desc": "解答用户常见的问题",
            "description": "本文档收集了用户最常提出的问题，并给出详细解答，帮助您快速解决使用中遇到的问题。",
            "content": """# 常见问题

## 账号相关

### Q1: 如何注册账号？

A: 点击网站右上角的"注册"按钮，填写用户名、邮箱、密码等信息，点击提交即可完成注册。

### Q2: 忘记密码怎么办？

A: 目前系统暂不支持自助找回密码功能，请联系系统管理员进行密码重置。

### Q3: 如何修改个人信息？

A: 登录后，进入"个人中心"页面，可以查看和修改个人信息。

## 秘钥申请相关

### Q4: 为什么需要申请API秘钥？

A: API秘钥用于访问我们的开放接口，只有获得秘钥才能调用API服务。

### Q5: 如何申请API秘钥？

A: 1. 登录账号
   2. 进入个人中心
   3. 点击"秘钥申请"
   4. 填写申请信息并提交
   5. 等待管理员审核

### Q6: 审核需要多长时间？

A: 通常审核时间为1-3个工作日，审核结果将通过邮件通知您。

### Q7: 秘钥有效期是多久？

A: 试用版秘钥有效期为30天，其他版本秘钥有效期为1年。

## 系统使用相关

### Q8: 如何查看产品详情？

A: 在产品列表页面，点击任意产品卡片或产品名称，即可进入产品详情页面。

### Q9: 如何搜索文档？

A: 在文档中心页面，可以使用搜索框按关键词搜索文档，也可以按分类进行筛选。

### Q10: 系统支持哪些浏览器？

A: 系统支持主流现代浏览器，包括：
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

建议使用最新版本的Chrome浏览器以获得最佳体验。

## 联系我们

如以上解答未能解决您的问题，请通过以下方式联系我们：

- 客服电话：400-123-4567
- 客服邮箱：support@example.com
- 工作时间：周一至周五 9:00-18:00
""",
            "category": "帮助文档",
            "tags": "FAQ,常见问题,帮助",
            "sort_order": 7,
            "view_count": 2100,
            "is_active": True
        },
        {
            "title": "系统架构说明",
            "short_desc": "详细介绍系统的技术架构设计",
            "description": "本文档面向技术人员，详细介绍了系统的整体架构、技术选型、模块划分等技术细节。",
            "content": """# 系统架构说明

## 1. 整体架构

本系统采用前后端分离的架构设计，后端使用FastAPI框架，前端使用Bootstrap 5进行页面渲染。

### 1.1 技术栈

**后端技术：**
- Python 3.9+
- FastAPI 0.109+
- SQLAlchemy 2.0+
- Pydantic 2.5+
- SQLite（数据库）

**前端技术：**
- HTML5
- Bootstrap 5.3
- JavaScript (ES6+)
- Jinja2（模板引擎）

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      客户端层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   浏览器    │  │  移动设备   │  │  API客户端  │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      应用层                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              FastAPI Application                 │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │   │
│  │  │  路由层 │ │  服务层 │ │  数据访问层    │   │   │
│  │  └─────────┘ └─────────┘ └─────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      数据层                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │              SQLite Database                      │   │
│  │  users │ products │ services │ cases │ documents │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2. 模块设计

### 2.1 目录结构

```
websyspy1/
├── main.py              # 应用入口
├── config.py            # 配置文件
├── database.py          # 数据库连接
├── models.py            # 数据模型
├── schemas.py           # Pydantic模型
├── security.py          # 安全认证
├── requirements.txt     # 依赖清单
├── routers/             # 路由模块
│   ├── __init__.py
│   ├── auth.py          # 认证路由
│   ├── users.py         # 用户路由
│   ├── products.py      # 产品路由
│   ├── services.py      # 服务路由
│   ├── cases.py         # 案例路由
│   ├── documents.py     # 文档路由
│   ├── key_applications.py  # 秘钥申请路由
│   └── pages.py         # 页面路由
├── templates/           # 模板文件
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── ...
├── static/              # 静态文件
└── data/                # 数据库文件
```

### 2.2 核心模块说明

**路由模块 (routers/)：**
- `auth.py`：用户认证相关接口
- `users.py`：用户管理接口（管理员专用）
- `products.py`：产品管理接口
- `services.py`：服务管理接口
- `cases.py`：案例管理接口
- `documents.py`：文档管理接口
- `key_applications.py`：秘钥申请管理接口
- `pages.py`：页面渲染路由

**数据模型 (models.py)：**
- `User`：用户表
- `Product`：产品表
- `Service`：服务表
- `Case`：案例表
- `Document`：文档表
- `KeyApplication`：秘钥申请表

## 3. 数据库设计

### 3.1 表结构

详见 `models.py` 文件中的定义。

### 3.2 关系说明

- User 与 KeyApplication：一对多关系
- 其他表为独立实体

## 4. 安全设计

### 4.1 密码安全

- 使用 bcrypt 算法进行密码哈希
- 密码以哈希形式存储，不可逆

### 4.2 认证机制

- 使用 JWT (JSON Web Token) 进行身份认证
- Token 有效期可配置，默认30分钟

### 4.3 权限控制

- 普通用户：只能访问公开资源和自己的信息
- 管理员：拥有所有权限，可管理用户和内容

## 5. 部署说明

详见部署相关文档。
""",
            "category": "技术文档",
            "tags": "架构,技术,设计",
            "sort_order": 6,
            "view_count": 560,
            "is_active": True
        }
    ]
    
    for doc_data in documents_data:
        document = Document(**doc_data)
        session.add(document)
    
    session.commit()
    print(f"成功创建 {len(documents_data)} 个文档！")


def create_key_applications(session, users):
    """
    创建秘钥申请测试数据
    """
    print("正在创建秘钥申请数据...")
    
    if len(users) < 2:
        print("用户数量不足，跳过秘钥申请数据创建")
        return
    
    applications_data = [
        {
            "user_id": users[0].id,
            "application_type": "trial",
            "company_name": "测试科技有限公司",
            "website": "https://test.example.com",
            "use_case": "用于公司内部系统集成测试，需要调用产品查询API和文档查询API。预计日均调用量约1000次。",
            "expected_calls": "<1000",
            "status": "pending"
        },
        {
            "user_id": users[1].id,
            "application_type": "pro",
            "company_name": "创新软件公司",
            "website": "https://innovation.example.com",
            "use_case": "我们正在开发一个企业级SaaS平台，需要集成您的API网关和数据分析服务。预计日均调用量约50000次，高峰期可能达到100000次/天。",
            "expected_calls": "10000-100000",
            "status": "approved",
            "api_key": generate_api_key(),
            "valid_until": datetime.now() + timedelta(days=365),
            "review_notes": "申请通过，已分配专业版秘钥。"
        }
    ]
    
    for app_data in applications_data:
        application = KeyApplication(**app_data)
        session.add(application)
    
    session.commit()
    print(f"成功创建 {len(applications_data)} 个秘钥申请！")


def main():
    """
    主函数
    """
    print("=" * 60)
    print("      测试数据生成脚本")
    print("=" * 60)
    print()
    
    import argparse
    parser = argparse.ArgumentParser(description="测试数据生成脚本")
    parser.add_argument("--clear", action="store_true", help="清空现有数据")
    parser.add_argument("--no-clear", action="store_true", help="不清空现有数据")
    args = parser.parse_args()
    
    session = SessionLocal()
    
    try:
        init_database()
        
        if args.clear or (not args.no_clear and input("\n是否清空现有数据？(y/n): ").lower() == 'y'):
            clear_database(session)
        
        admin = create_admin_user(session)
        users = create_normal_users(session)
        all_users = [admin] + users
        
        create_products(session)
        create_services(session)
        create_cases(session)
        create_documents(session)
        create_key_applications(session, users)
        
        print()
        print("=" * 60)
        print("      测试数据生成完成！")
        print("=" * 60)
        print()
        print("测试账号信息：")
        print("-" * 40)
        print(f"管理员账号:")
        print(f"  用户名: admin")
        print(f"  密码: admin123")
        print(f"  邮箱: admin@example.com")
        print()
        print(f"普通用户账号 (密码均为 123456):")
        for user in users:
            print(f"  - {user.username} ({user.email})")
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
