import logging
import sys
import requests
from access_token_all import wx_token_mgr

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def send_template_card(touser: str, company: str, tel: str) -> dict:
    token = wx_token_mgr.get_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"

    payload = {
        "touser": touser,
        "msgtype": "template_card",
        "agentid": 1000038,
        "template_card": {
            "card_type": "text_notice",
            "main_title": {
                "title": "CRM分配提醒",
                "desc": "您有新线索已分配，请及时跟进"
            },
            "horizontal_content_list": [
                {
                    "keyname": "公司名称",
                    "value": company
                },
                {
                    "keyname": "电话",
                    "value": tel
                }
            ],
            "card_action": {
                "type": 1,
                "url": "https://work.weixin.qq.com"
            }
        }
    }

    try:
        logging.info(f"📤 正在向 {touser} 发送模板卡片消息...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()

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


if __name__ == "__main__":
    try:
        wx_token_mgr.start_auto_refresh()
        send_template_card(
            touser="Qi",
            company="测试公司",
            tel="13800000000"
        )
    except KeyboardInterrupt:
        pass
    finally:
        wx_token_mgr.stop_auto_refresh()
