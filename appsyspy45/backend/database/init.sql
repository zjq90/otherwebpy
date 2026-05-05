-- 旧衣物回收App数据库初始化脚本
-- 数据库: SQLite
-- 版本: 1.0

-- ==================== 1. 用户相关表 ====================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255),
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    email VARCHAR(100),
    gender TINYINT DEFAULT 0,  -- 0: 未知, 1: 男, 2: 女
    register_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_time DATETIME,
    status TINYINT DEFAULT 1,  -- 0: 禁用, 1: 正常
    points INTEGER DEFAULT 0,   -- 积分余额
    total_points INTEGER DEFAULT 0,  -- 累计积分
    recycle_count INTEGER DEFAULT 0,  -- 回收次数
    carbon_reduction REAL DEFAULT 0.0,  -- 累计减碳量(kg)
    invite_code VARCHAR(20) UNIQUE,  -- 邀请码
    invited_by INTEGER,  -- 被谁邀请
    UNIQUE(phone)
);

-- 登录方式表（支持多种登录方式）
CREATE TABLE IF NOT EXISTS login_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    login_type VARCHAR(20) NOT NULL,  -- phone, wechat, alipay
    openid VARCHAR(100),  -- 第三方登录的唯一标识
    unionid VARCHAR(100),
    extra_info TEXT,  -- 额外信息(JSON)
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(login_type, openid)
);

-- 收货地址表
CREATE TABLE IF NOT EXISTS user_addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,  -- 收货人姓名
    phone VARCHAR(20) NOT NULL,  -- 收货人电话
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    address VARCHAR(255) NOT NULL,  -- 详细地址
    is_default TINYINT DEFAULT 0,  -- 是否默认地址
    status TINYINT DEFAULT 1,  -- 0: 已删除, 1: 正常
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== 2. 衣物类型和积分配置表 ====================

-- 衣物类型表
CREATE TABLE IF NOT EXISTS clothing_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,  -- 类型名称，如T恤、毛衣、羽绒服
    code VARCHAR(50) UNIQUE NOT NULL,  -- 类型代码
    description TEXT,  -- 描述
    icon VARCHAR(255),  -- 图标
    points_per_unit INTEGER DEFAULT 10,  -- 每件积分
    carbon_per_unit REAL DEFAULT 0.5,  -- 每件减碳量(kg)
    sort_order INTEGER DEFAULT 0,  -- 排序
    status TINYINT DEFAULT 1  -- 0: 禁用, 1: 启用
);

-- 积分配置表
CREATE TABLE IF NOT EXISTS points_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,  -- 配置键
    config_value VARCHAR(255) NOT NULL,  -- 配置值
    description TEXT,  -- 描述
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 3. 订单相关表 ====================

-- 回收人员表
CREATE TABLE IF NOT EXISTS collectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  -- 关联用户表，如果回收员也是用户
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    avatar VARCHAR(255),
    id_card VARCHAR(50),  -- 身份证号
    work_status TINYINT DEFAULT 0,  -- 0: 休息, 1: 工作中, 2: 忙碌
    latitude REAL,  -- 当前纬度
    longitude REAL,  -- 当前经度
    location_update_time DATETIME,  -- 位置更新时间
    rating REAL DEFAULT 5.0,  -- 评分
    total_orders INTEGER DEFAULT 0,  -- 完成订单数
    status TINYINT DEFAULT 1,  -- 0: 禁用, 1: 正常
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 回收订单表
CREATE TABLE IF NOT EXISTS recycle_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(50) UNIQUE NOT NULL,  -- 订单号
    user_id INTEGER NOT NULL,
    collector_id INTEGER,  -- 回收员ID
    clothing_type_id INTEGER NOT NULL,  -- 衣物类型ID
    clothing_name VARCHAR(50),  -- 衣物类型名称（冗余）
    quantity INTEGER NOT NULL,  -- 数量
    unit VARCHAR(20) DEFAULT '件',  -- 单位
    quality VARCHAR(20) DEFAULT '普通',  -- 品质：优质、普通、较差
    province VARCHAR(50),
    city VARCHAR(50),
    district VARCHAR(50),
    address VARCHAR(255) NOT NULL,  -- 详细地址
    contact_name VARCHAR(50) NOT NULL,  -- 联系人
    contact_phone VARCHAR(20) NOT NULL,  -- 联系电话
    scheduled_date DATE NOT NULL,  -- 预约日期
    scheduled_time_slot VARCHAR(50) NOT NULL,  -- 预约时间段
    estimated_arrival VARCHAR(50),  -- 预计上门时段
    actual_arrival_time DATETIME,  -- 实际上门时间
    complete_time DATETIME,  -- 完成时间
    cancel_time DATETIME,  -- 取消时间
    cancel_reason TEXT,  -- 取消原因
    status TINYINT DEFAULT 1,  -- 1:待接单, 2:待上门, 3:回收中, 4:已完成, 5:已取消
    status_text VARCHAR(50) DEFAULT '待接单',
    points_earned INTEGER DEFAULT 0,  -- 获得的积分
    carbon_earned REAL DEFAULT 0.0,  -- 获得的减碳量
    remark TEXT,  -- 备注
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (collector_id) REFERENCES collectors(id),
    FOREIGN KEY (clothing_type_id) REFERENCES clothing_types(id)
);

-- 订单状态历史表
CREATE TABLE IF NOT EXISTS order_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    order_no VARCHAR(50),
    status TINYINT NOT NULL,  -- 状态值
    status_text VARCHAR(50),  -- 状态文本
    operator_type VARCHAR(20),  -- 操作者类型：user, collector, system
    operator_id INTEGER,  -- 操作者ID
    remark TEXT,  -- 备注
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES recycle_orders(id)
);

-- ==================== 4. 积分相关表 ====================

-- 积分记录表
CREATE TABLE IF NOT EXISTS points_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,  -- 类型：recycle(回收), invite(邀请), exchange(兑换), adjust(调整)
    transaction_type_text VARCHAR(50),
    points INTEGER NOT NULL,  -- 积分数量（正为增加，负为减少）
    balance_after INTEGER NOT NULL,  -- 变动后余额
    reference_type VARCHAR(50),  -- 关联类型：order, exchange_order, invite
    reference_id INTEGER,  -- 关联ID
    description TEXT,  -- 描述
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 邀请记录表
CREATE TABLE IF NOT EXISTS invites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inviter_id INTEGER NOT NULL,  -- 邀请人ID
    invitee_id INTEGER NOT NULL,  -- 被邀请人ID
    invite_code VARCHAR(20),  -- 使用的邀请码
    inviter_points_earned INTEGER DEFAULT 0,  -- 邀请人获得的积分
    invitee_points_earned INTEGER DEFAULT 0,  -- 被邀请人获得的积分
    status TINYINT DEFAULT 0,  -- 0: 待确认, 1: 已确认, 2: 已发放积分
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (inviter_id) REFERENCES users(id),
    FOREIGN KEY (invitee_id) REFERENCES users(id),
    UNIQUE(invitee_id)
);

-- ==================== 5. 兑换相关表 ====================

-- 商品表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,  -- 商品名称
    code VARCHAR(50) UNIQUE,  -- 商品编码
    description TEXT,  -- 描述
    image VARCHAR(255),  -- 主图
    images TEXT,  -- 轮播图(JSON数组)
    category_id INTEGER,  -- 分类ID
    price REAL DEFAULT 0.0,  -- 现金价格
    points_price INTEGER DEFAULT 0,  -- 积分价格
    exchange_type VARCHAR(20) DEFAULT 'points',  -- 兑换类型：points(纯积分), points_cash(积分+现金), clothing(旧衣兑换)
    required_clothing_quantity INTEGER DEFAULT 0,  -- 所需旧衣数量
    stock INTEGER DEFAULT 0,  -- 库存
    sales INTEGER DEFAULT 0,  -- 销量
    sort_order INTEGER DEFAULT 0,  -- 排序
    is_hot TINYINT DEFAULT 0,  -- 是否热门
    is_new TINYINT DEFAULT 0,  -- 是否新品
    status TINYINT DEFAULT 1,  -- 0: 下架, 1: 上架
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 商品分类表
CREATE TABLE IF NOT EXISTS product_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(50) UNIQUE,
    icon VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    status TINYINT DEFAULT 1
);

-- 兑换订单表
CREATE TABLE IF NOT EXISTS exchange_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_no VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(100),  -- 商品名称（冗余）
    product_image VARCHAR(255),  -- 商品图片（冗余）
    quantity INTEGER DEFAULT 1,  -- 数量
    exchange_type VARCHAR(20),  -- 兑换类型
    points_spent INTEGER DEFAULT 0,  -- 消耗积分
    cash_spent REAL DEFAULT 0.0,  -- 支付现金
    clothing_spent INTEGER DEFAULT 0,  -- 消耗旧衣数量
    -- 收货地址信息
    receiver_name VARCHAR(50),
    receiver_phone VARCHAR(20),
    receiver_province VARCHAR(50),
    receiver_city VARCHAR(50),
    receiver_district VARCHAR(50),
    receiver_address VARCHAR(255),
    -- 物流信息
    express_company VARCHAR(50),
    express_no VARCHAR(50),
    -- 订单状态
    status TINYINT DEFAULT 1,  -- 1:待发货, 2:已发货, 3:已签收, 4:已取消
    status_text VARCHAR(50) DEFAULT '待发货',
    remark TEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ==================== 6. 资讯和客服相关表 ====================

-- 环保资讯表
CREATE TABLE IF NOT EXISTS eco_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,  -- 标题
    summary VARCHAR(500),  -- 摘要
    content TEXT,  -- 内容
    cover_image VARCHAR(255),  -- 封面图
    category VARCHAR(50) DEFAULT '环保资讯',  -- 分类
    author VARCHAR(50),  -- 作者
    source VARCHAR(100),  -- 来源
    view_count INTEGER DEFAULT 0,  -- 浏览量
    like_count INTEGER DEFAULT 0,  -- 点赞数
    is_top TINYINT DEFAULT 0,  -- 是否置顶
    is_hot TINYINT DEFAULT 0,  -- 是否热门
    status TINYINT DEFAULT 1,  -- 0: 下架, 1: 发布
    publish_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 旧衣回收流程表
CREATE TABLE IF NOT EXISTS recycle_process (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step INTEGER NOT NULL,  -- 步骤序号
    title VARCHAR(100) NOT NULL,  -- 步骤标题
    description TEXT,  -- 步骤描述
    icon VARCHAR(255),  -- 图标
    image VARCHAR(255),  -- 图片
    sort_order INTEGER DEFAULT 0,
    status TINYINT DEFAULT 1
);

-- 客服消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(50) NOT NULL,  -- 会话ID
    user_id INTEGER NOT NULL,  -- 用户ID
    message_type VARCHAR(20) NOT NULL,  -- 消息类型：text, image, voice, system
    content TEXT,  -- 消息内容
    media_url VARCHAR(255),  -- 媒体文件URL
    sender_type VARCHAR(20) NOT NULL,  -- 发送者类型：user, customer_service, system
    sender_id INTEGER,  -- 发送者ID
    is_read TINYINT DEFAULT 0,  -- 是否已读
    read_time DATETIME,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 客服会话表
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    customer_service_id INTEGER,  -- 客服ID
    last_message TEXT,  -- 最后一条消息
    last_message_time DATETIME,  -- 最后消息时间
    unread_count INTEGER DEFAULT 0,  -- 未读消息数
    status TINYINT DEFAULT 1,  -- 0: 已结束, 1: 进行中
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ==================== 7. 系统配置和管理员表 ====================

-- 管理员表
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    role VARCHAR(20) DEFAULT 'admin',  -- 角色：admin, super_admin, customer_service
    status TINYINT DEFAULT 1,
    last_login_time DATETIME,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==================== 创建索引 ====================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_invite_code ON users(invite_code);

-- 订单表索引
CREATE INDEX IF NOT EXISTS idx_recycle_orders_user_id ON recycle_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_recycle_orders_collector_id ON recycle_orders(collector_id);
CREATE INDEX IF NOT EXISTS idx_recycle_orders_status ON recycle_orders(status);
CREATE INDEX IF NOT EXISTS idx_recycle_orders_order_no ON recycle_orders(order_no);

-- 积分记录表索引
CREATE INDEX IF NOT EXISTS idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_create_time ON points_transactions(create_time);

-- 消息表索引
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);

-- ==================== 插入基础数据 ====================

-- 插入衣物类型数据
INSERT INTO clothing_types (name, code, description, points_per_unit, carbon_per_unit, sort_order, status) VALUES
('T恤', 'tshirt', '各类T恤、短袖衫等', 10, 0.3, 1, 1),
('衬衫', 'shirt', '衬衫、衬衣等', 12, 0.4, 2, 1),
('毛衣', 'sweater', '毛衣、针织衫等', 20, 0.6, 3, 1),
('外套', 'coat', '夹克、风衣、西装等', 25, 0.8, 4, 1),
('羽绒服', 'down_jacket', '羽绒服、羽绒马甲等', 35, 1.2, 5, 1),
('裤子', 'pants', '裤子、牛仔裤、运动裤等', 15, 0.5, 6, 1),
('裙子', 'skirt', '裙子、连衣裙等', 12, 0.4, 7, 1),
('家纺用品', 'home_textile', '床单、被套、毛巾、窗帘等', 20, 0.7, 8, 1),
('鞋子', 'shoes', '各类鞋子，需干净无破损', 15, 0.5, 9, 1),
('包包', 'bags', '包包、背包等', 18, 0.6, 10, 1);

-- 插入积分配置数据
INSERT INTO points_config (config_key, config_value, description) VALUES
('invite_inviter_bonus', '100', '邀请人积分奖励'),
('invite_invitee_bonus', '50', '被邀请人积分奖励'),
('daily_checkin_points', '5', '每日签到积分'),
('new_user_bonus', '100', '新用户注册积分奖励'),
('order_complete_extra', '10', '订单完成额外积分'),
('min_points_exchange', '100', '最低兑换积分');

-- 插入回收流程数据
INSERT INTO recycle_process (step, title, description, sort_order, status) VALUES
(1, '在线预约', '用户通过App选择衣物类型，填写地址和预约时间', 1, 1),
(2, '系统派单', '系统根据位置和时间自动匹配合适的回收人员', 2, 1),
(3, '上门回收', '回收人员按约定时间上门，验收衣物并称重', 3, 1),
(4, '积分到账', '衣物验收合格后，积分自动发放到用户账户', 4, 1),
(5, '分类处理', '回收衣物将进行消毒、分类、再利用或环保处理', 5, 1);

-- 插入环保资讯分类配置
INSERT INTO system_config (config_key, config_value, description) VALUES
('eco_categories', '["环保资讯","旧衣知识","公益活动","环保政策"]', '环保资讯分类'),
('time_slots', '["09:00-11:00","11:00-13:00","13:00-15:00","15:00-17:00","17:00-19:00","19:00-21:00"]', '可预约时间段');

-- 插入商品分类
INSERT INTO product_categories (name, code, sort_order, status) VALUES
('家居用品', 'home', 1, 1),
('生活用品', 'daily', 2, 1),
('电子产品', 'electronics', 3, 1),
('服饰配件', 'accessories', 4, 1),
('优惠券', 'coupons', 5, 1);

-- 插入测试商品
INSERT INTO products (name, code, description, image, category_id, price, points_price, exchange_type, stock, sort_order, is_hot, status) VALUES
('环保袋', 'eco_bag_001', '可重复使用的环保购物袋，采用优质帆布材质', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=环保%20帆布%20购物袋%20绿色%20简约&image_size=square', 1, 0.0, 200, 'points', 100, 1, 1, 1),
('竹纤维毛巾', 'towel_001', '天然竹纤维毛巾，柔软吸水，抗菌防螨', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=竹纤维%20毛巾%20柔软%20白色%20简约&image_size=square', 2, 9.9, 300, 'points_cash', 200, 2, 1, 1),
('手机支架', 'stand_001', '多功能手机支架，可调节角度，适合桌面使用', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=手机%20支架%20黑色%20简约%20桌面&image_size=square', 3, 19.9, 500, 'points_cash', 50, 3, 0, 1),
('时尚围巾', 'scarf_001', '柔软舒适的时尚围巾，多种颜色可选', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=围巾%20时尚%20红色%20柔软%20简约&image_size=square', 4, 0.0, 0, 'clothing', 30, 4, 0, 1),
('10元优惠券', 'coupon_001', '全场通用10元优惠券，无门槛使用', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=优惠券%20红色%2010元%20简约&image_size=square', 5, 0.0, 500, 'points', 1000, 5, 1, 1);

-- 插入测试回收人员
INSERT INTO collectors (name, phone, avatar, work_status, rating, total_orders, status) VALUES
('张师傅', '13800138001', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=中年%20男性%20工人%20制服%20微笑&image_size=square', 1, 4.8, 156, 1),
('李师傅', '13800138002', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=中年%20男性%20工人%20制服%20专业&image_size=square', 1, 4.9, 234, 1),
('王师傅', '13800138003', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=中年%20女性%20工人%20制服%20友善&image_size=square', 0, 4.7, 89, 1);

-- 插入测试管理员
INSERT INTO admins (username, password, nickname, role, status) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', '超级管理员', 'super_admin', 1),
('cs001', 'e10adc3949ba59abbe56e057f20f883e', '客服小美', 'customer_service', 1);

-- 插入测试环保资讯
INSERT INTO eco_articles (title, summary, content, cover_image, category, author, view_count, is_top, status) VALUES
('旧衣回收的环保意义', '了解旧衣回收对环境保护的重要性，每一件旧衣的回收都是对地球的贡献。', '随着生活水平的提高，人们购买衣物的频率越来越高，但很多衣物只穿了几次就被闲置或丢弃。据统计，我国每年产生的废旧纺织品约2600万吨，如果这些纺织品能够得到有效回收利用，将极大减少对环境的压力。

旧衣回收的环保意义主要体现在以下几个方面：
1. 减少填埋：纺织品在填埋场中需要数百年才能降解，还可能释放有害物质。
2. 节约资源：生产一件新T恤需要约2700升水，回收一件旧衣相当于节约这些资源。
3. 减少碳排放：纺织品生产是高碳排放行业，回收利用可以显著减少碳排放。
4. 帮助他人：状况良好的旧衣经过消毒处理后，可以捐赠给需要的人。', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=环保%20回收%20绿色%20地球%20衣物&image_size=landscape_16_9', '环保资讯', '环保小编', 1568, 1, 1),
('旧衣如何分类回收', '学会正确分类旧衣，让回收更加高效，不同类型的衣物有不同的处理方式。', '旧衣回收不仅仅是把旧衣打包送走，正确的分类可以让回收更加高效，也能让每件旧衣找到最合适的归宿。

### 衣物分类指南

**1. 可直接捐赠的衣物**
- 干净整洁，无明显破损
- 款式不过于老旧
- 适合捐赠的季节

**2. 可回收再利用的衣物**
- 有轻微破损但材质完好
- 款式老旧但面料优质
- 家纺用品如床单、被套等

**3. 不可回收的衣物**
- 严重破损、发霉、有异味
- 医疗用衣物（如病号服）
- 含有害物质的特殊衣物

### 回收前准备
- 清洗干净，晒干
- 按材质或类型分类打包
- 去除个人物品（如口袋里的东西）', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=分类%20衣物%20整理%20整齐%20环保&image_size=landscape_16_9', '旧衣知识', '回收专家', 986, 0, 1),
('公益捐赠活动启动', '旧衣回收公益捐赠活动正式启动，您的每一件旧衣都将温暖需要帮助的人。', '为了让更多旧衣发挥价值，我们与多家公益机构合作，启动旧衣回收公益捐赠活动。

### 活动说明
- 所有回收的旧衣中，状况良好的将经过专业消毒处理后捐赠给贫困地区。
- 捐赠过程全程透明，用户可以在App中查看自己捐赠的衣物去向。
- 参与捐赠的用户将获得额外的公益积分奖励。

### 合作伙伴
- 中国红十字基金会
- 壹基金
- 当地慈善机构

### 活动时间
长期有效

让我们一起行动，用旧衣传递温暖，让爱心循环。', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=公益%20捐赠%20爱心%20温暖%20帮助&image_size=landscape_16_9', '公益活动', '公益部', 2345, 1, 1);

-- 插入测试环保政策资讯
INSERT INTO eco_articles (title, summary, content, cover_image, category, author, view_count, is_hot, status) VALUES
('国家废旧纺织品循环利用政策解读', '了解国家最新的废旧纺织品循环利用政策，把握环保新趋势。', '近年来，国家高度重视废旧纺织品的循环利用工作，出台了一系列政策文件，推动行业健康发展。

### 主要政策要点

**1. 《关于加快推进废旧纺织品循环利用的实施意见》**
- 到2025年，废旧纺织品循环利用率达到25%
- 建立健全回收体系
- 推动再生纤维高值化利用

**2. 税收优惠政策**
- 对从事废旧纺织品回收利用的企业给予税收优惠
- 再生纤维产品享受增值税即征即退政策

**3. 标准规范建设**
- 制定废旧纺织品分类标准
- 建立再生纤维质量认证体系

### 对普通用户的影响
- 回收渠道更加便捷
- 回收价格更加透明
- 环保意识逐步提升

让我们一起响应国家号召，积极参与旧衣回收，为建设资源节约型社会贡献力量。', 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=政策%20文件%20绿色%20环保%20政府&image_size=landscape_16_9', '环保政策', '政策研究室', 1234, 0, 1);
