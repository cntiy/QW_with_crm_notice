import logging
import sys
import requests
from access_token_all import wx_token_mgr

# 1️⃣ 统一日志配置（替代 print，便于排查和线上监控）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


# 2️⃣ 封装发送逻辑（参数化 + 避免覆盖内置 json 模块 + 业务状态码校验）
def send_template_card(touser: str, title: str, desc: str) -> dict:
    # 自动获取有效凭证（内部处理过期/刷新/并发锁）
    token = wx_token_mgr.get_token()

    # ⚠️ 企微消息接口官方规范要求 token 必须放在 URL 参数中
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

    payload = {
        "touser": touser,
        "msgtype": "template_card",
        "agentid": 1000038,
        "template_card": {
            "card_type": "text_notice",
            "main_title": {"title": title, "desc": desc},
            "quote_area": {
                "type": 1,
                "url": "https://work.weixin.qq.com",
                "title": "企业微信的引用样式",
                "quote_text": "企业微信真好用呀真好用"
            },
            "emphasis_content": {"title": "100", "desc": "核心数据"},
            "sub_title_text": "下载企业微信还能抢红包！",
            "card_action": {"type": 1, "url": "https://work.weixin.qq.com"}
        }
    }

    try:
        logging.info(f"📤 正在向 {touser} 发送模板卡片消息...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # 检查 HTTP 状态码（如 400/500）
        result = response.json()

        # 企微 API 特性：HTTP 200 不代表业务成功，必须校验 errcode
        if result.get("errcode") != 0:
            logging.error(f"❌ 企微业务返回错误: {result}")
            return result

        logging.info("✅ 消息发送成功！")
        return result

    except requests.RequestException as e:
        logging.error(f"❌ 网络请求失败: {e}")
        raise
    except Exception as e:
        logging.error(f"❌ 未知异常: {e}")
        raise


# 3️⃣ 主入口（严格管理生命周期）
if __name__ == "__main__":
    try:
        # 启动后台自动刷新线程（全进程仅调用一次）
        wx_token_mgr.start_auto_refresh()
        logging.info("🚀 凭证管理器已启动，准备发送消息...")

        # 执行业务调用
        send_template_card(
            touser="Qi",  # 支持: 用户ID、部门ID、"@all"
            title="欢迎使用企业微信",
            desc="您的好友正在邀请您加入企业微信"
        )

    except KeyboardInterrupt:
        logging.info("\n👋 收到中断信号，正在安全退出...")
    finally:
        # 优雅停止后台刷新线程，防止僵尸进程
        wx_token_mgr.stop_auto_refresh()
        logging.info("🛑 程序已退出。")
