"""
API功能测试脚本
用于测试后端API接口功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx
import json
from typing import Optional, Dict, Any


class APIClient:
    """API测试客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        self.access_token: Optional[str] = None
        self.current_user: Optional[Dict] = None
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = self._get_headers()
        
        try:
            with httpx.Client() as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = client.post(url, headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = client.put(url, headers=headers, json=data)
                elif method.upper() == "DELETE":
                    response = client.delete(url, headers=headers)
                else:
                    return {"error": f"不支持的HTTP方法: {method}"}
                
                if response.status_code in [200, 201]:
                    return {"success": True, "data": response.json(), "status_code": response.status_code}
                else:
                    try:
                        error_data = response.json()
                    except:
                        error_data = response.text
                    return {
                        "success": False, 
                        "error": error_data, 
                        "status_code": response.status_code
                    }
        except Exception as e:
            return {"success": False, "error": str(e), "status_code": 0}
    
    # ==================== 认证相关 ====================
    
    def register(self, username: str, email: str, password: str, invite_code: Optional[str] = None) -> Dict:
        """用户注册"""
        data = {
            "username": username,
            "email": email,
            "password": password,
            "nickname": username
        }
        if invite_code:
            data["invite_code"] = invite_code
        
        result = self._make_request("POST", "/auth/register", data)
        
        if result["success"]:
            self.access_token = result["data"].get("access_token")
            self.current_user = result["data"].get("user")
        
        return result
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        data = {
            "username": username,
            "password": password
        }
        
        result = self._make_request("POST", "/auth/login", data)
        
        if result["success"]:
            self.access_token = result["data"].get("access_token")
            self.current_user = result["data"].get("user")
        
        return result
    
    def get_current_user(self) -> Dict:
        """获取当前用户信息"""
        return self._make_request("GET", "/auth/me")
    
    def logout(self) -> Dict:
        """用户登出"""
        result = self._make_request("POST", "/auth/logout")
        if result["success"]:
            self.access_token = None
            self.current_user = None
        return result
    
    # ==================== 动态广场相关 ====================
    
    def create_post(self, content: str, post_type: str = "training", images: str = "") -> Dict:
        """发布动态"""
        data = {
            "content": content,
            "post_type": post_type,
            "images": images,
            "is_public": True
        }
        return self._make_request("POST", "/posts", data)
    
    def get_posts(self, post_type: Optional[str] = None, user_id: Optional[int] = None, page: int = 1, page_size: int = 10) -> Dict:
        """获取动态列表"""
        params = {"page": page, "page_size": page_size}
        if post_type:
            params["post_type"] = post_type
        if user_id:
            params["user_id"] = user_id
        return self._make_request("GET", "/posts", params=params)
    
    def get_post(self, post_id: int) -> Dict:
        """获取动态详情"""
        return self._make_request("GET", f"/posts/{post_id}")
    
    def like_post(self, post_id: int) -> Dict:
        """点赞/取消点赞"""
        return self._make_request("POST", f"/posts/{post_id}/like")
    
    def create_comment(self, post_id: int, content: str, parent_id: Optional[int] = None) -> Dict:
        """发表评论"""
        data = {
            "post_id": post_id,
            "content": content
        }
        if parent_id:
            data["parent_id"] = parent_id
        return self._make_request("POST", "/posts/comments", data)
    
    def get_comments(self, post_id: int, page: int = 1, page_size: int = 20) -> Dict:
        """获取动态评论"""
        params = {"page": page, "page_size": page_size}
        return self._make_request("GET", f"/posts/{post_id}/comments", params=params)
    
    def share_post(self, post_id: int, platform: Optional[str] = None) -> Dict:
        """分享动态"""
        return self._make_request("POST", f"/posts/{post_id}/share")
    
    # ==================== 好友系统相关 ====================
    
    def search_users(self, keyword: str, page: int = 1, page_size: int = 20) -> Dict:
        """搜索用户"""
        params = {"keyword": keyword, "page": page, "page_size": page_size}
        return self._make_request("GET", "/friends/search", params=params)
    
    def get_user_profile(self, user_id: int) -> Dict:
        """查看用户公开资料"""
        return self._make_request("GET", f"/friends/profile/{user_id}")
    
    def add_friend(self, user_id: int) -> Dict:
        """添加好友"""
        data = {"user_id_2": user_id}
        return self._make_request("POST", "/friends/add", data)
    
    def get_friend_requests(self, status: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict:
        """获取收到的好友请求"""
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        return self._make_request("GET", "/friends/requests", params=params)
    
    def accept_friend_request(self, friendship_id: int) -> Dict:
        """接受好友请求"""
        return self._make_request("POST", f"/friends/requests/{friendship_id}/accept")
    
    def reject_friend_request(self, friendship_id: int) -> Dict:
        """拒绝好友请求"""
        return self._make_request("POST", f"/friends/requests/{friendship_id}/reject")
    
    def get_friends(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取好友列表"""
        params = {"page": page, "page_size": page_size}
        return self._make_request("GET", "/friends", params=params)
    
    def send_message(self, receiver_id: int, content: str) -> Dict:
        """发送私信"""
        data = {
            "receiver_id": receiver_id,
            "content": content
        }
        return self._make_request("POST", "/friends/messages", data)
    
    def get_conversations(self) -> Dict:
        """获取会话列表"""
        return self._make_request("GET", "/friends/messages/conversations")
    
    def get_messages_with_user(self, user_id: int, page: int = 1, page_size: int = 50) -> Dict:
        """获取与指定用户的消息记录"""
        params = {"page": page, "page_size": page_size}
        return self._make_request("GET", f"/friends/messages/{user_id}", params=params)
    
    # ==================== 挑战活动相关 ====================
    
    def get_challenges(self, challenge_type: Optional[str] = None, page: int = 1, page_size: int = 10) -> Dict:
        """获取挑战活动列表"""
        params = {"page": page, "page_size": page_size}
        if challenge_type:
            params["challenge_type"] = challenge_type
        return self._make_request("GET", "/challenges", params=params)
    
    def get_challenge(self, challenge_id: int) -> Dict:
        """获取挑战活动详情"""
        return self._make_request("GET", f"/challenges/{challenge_id}")
    
    def join_challenge(self, challenge_id: int) -> Dict:
        """参与挑战活动"""
        data = {"challenge_id": challenge_id}
        return self._make_request("POST", "/challenges/join", data)
    
    def get_my_challenges(self, is_completed: Optional[bool] = None, page: int = 1, page_size: int = 10) -> Dict:
        """获取我参与的挑战"""
        params = {"page": page, "page_size": page_size}
        if is_completed is not None:
            params["is_completed"] = is_completed
        return self._make_request("GET", "/challenges/my/participating", params=params)
    
    def update_challenge_progress(self, user_challenge_id: int, progress: float, daily_data: Optional[str] = None) -> Dict:
        """更新挑战进度"""
        data = {"progress": progress}
        if daily_data:
            data["daily_data"] = daily_data
        return self._make_request("PUT", f"/challenges/progress/{user_challenge_id}", data)
    
    def claim_challenge_reward(self, user_challenge_id: int) -> Dict:
        """领取挑战奖励"""
        return self._make_request("POST", f"/challenges/claim-reward/{user_challenge_id}")
    
    # ==================== 邀请有礼相关 ====================
    
    def get_my_invite_code(self) -> Dict:
        """获取我的邀请码"""
        return self._make_request("GET", "/invitations/my-code")
    
    def create_invitation(self, phone: Optional[str] = None, email: Optional[str] = None) -> Dict:
        """发起邀请"""
        data = {}
        if phone:
            data["invitee_phone"] = phone
        if email:
            data["invitee_email"] = email
        return self._make_request("POST", "/invitations/create", data)
    
    def get_sent_invitations(self, status: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict:
        """获取我发出的邀请记录"""
        params = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        return self._make_request("GET", "/invitations/sent", params=params)
    
    def verify_invite_code(self, invite_code: str) -> Dict:
        """验证邀请码"""
        return self._make_request("POST", f"/invitations/verify/{invite_code}")
    
    def get_invitation_stats(self) -> Dict:
        """获取邀请统计"""
        return self._make_request("GET", "/invitations/stats/overview")


def run_tests():
    """运行API测试"""
    print("=" * 60)
    print("开始API功能测试")
    print("=" * 60)
    
    client = APIClient()
    
    test_results = []
    
    def test_step(name: str, func):
        """执行测试步骤"""
        print(f"\n【测试】{name}...")
        try:
            result = func()
            if result.get("success"):
                print(f"  ✓ 成功")
                test_results.append({"name": name, "success": True})
                return result
            else:
                print(f"  ✗ 失败: {result.get('error')}")
                test_results.append({"name": name, "success": False, "error": result.get('error')})
                return result
        except Exception as e:
            print(f"  ✗ 异常: {str(e)}")
            test_results.append({"name": name, "success": False, "error": str(e)})
            return None
    
    # 1. 健康检查
    print("\n" + "=" * 60)
    print("1. 健康检查")
    print("=" * 60)
    
    try:
        with httpx.Client() as http_client:
            response = http_client.get("http://localhost:8000/")
            if response.status_code == 200:
                print("  ✓ 服务运行正常")
                test_results.append({"name": "健康检查", "success": True})
            else:
                print("  ✗ 服务响应异常")
                test_results.append({"name": "健康检查", "success": False})
    except Exception as e:
        print(f"  ✗ 无法连接到服务器: {e}")
        print("\n请先启动后端服务:")
        print("  cd backend")
        print("  pip install -r requirements.txt")
        print("  python main.py")
        return
    
    # 2. 用户注册测试
    print("\n" + "=" * 60)
    print("2. 用户注册与登录测试")
    print("=" * 60)
    
    # 测试登录（使用测试数据中的用户）
    result = test_step("用户登录 (user1/123456)", 
        lambda: client.login("user1", "123456"))
    
    if result and result.get("success"):
        test_step("获取当前用户信息", lambda: client.get_current_user())
    else:
        # 如果测试用户不存在，尝试注册
        test_step("注册新用户", 
            lambda: client.register("testuser001", "test001@test.com", "123456"))
        
        test_step("获取当前用户信息", lambda: client.get_current_user())
    
    # 3. 动态广场测试
    print("\n" + "=" * 60)
    print("3. 动态广场测试")
    print("=" * 60)
    
    test_step("获取动态列表", lambda: client.get_posts(page=1, page_size=5))
    
    test_step("发布动态", 
        lambda: client.create_post("今天完成了5公里跑步，感觉很棒！", "training"))
    
    test_step("获取训练类动态", 
        lambda: client.get_posts(post_type="training", page=1, page_size=5))
    
    # 4. 好友系统测试
    print("\n" + "=" * 60)
    print("4. 好友系统测试")
    print("=" * 60)
    
    test_step("搜索用户", lambda: client.search_users("user", page=1, page_size=5))
    
    test_step("获取好友列表", lambda: client.get_friends(page=1, page_size=10))
    
    test_step("获取好友请求", lambda: client.get_friend_requests(page=1, page_size=10))
    
    test_step("获取会话列表", lambda: client.get_conversations())
    
    # 5. 挑战活动测试
    print("\n" + "=" * 60)
    print("5. 挑战活动测试")
    print("=" * 60)
    
    test_step("获取挑战活动列表", lambda: client.get_challenges(page=1, page_size=5))
    
    test_step("获取我参与的挑战", lambda: client.get_my_challenges(page=1, page_size=5))
    
    # 6. 邀请有礼测试
    print("\n" + "=" * 60)
    print("6. 邀请有礼测试")
    print("=" * 60)
    
    test_step("获取我的邀请码", lambda: client.get_my_invite_code())
    
    test_step("获取我发出的邀请记录", 
        lambda: client.get_sent_invitations(page=1, page_size=10))
    
    test_step("获取邀请统计", lambda: client.get_invitation_stats())
    
    # 7. 用户登出
    print("\n" + "=" * 60)
    print("7. 用户登出")
    print("=" * 60)
    
    test_step("用户登出", lambda: client.logout())
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    success_count = sum(1 for r in test_results if r.get("success"))
    total_count = len(test_results)
    
    print(f"\n总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    
    if success_count == total_count:
        print("\n✓ 所有测试通过！")
    else:
        print("\n✗ 部分测试失败，详细信息：")
        for r in test_results:
            if not r.get("success"):
                print(f"  - {r['name']}: {r.get('error', '未知错误')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
