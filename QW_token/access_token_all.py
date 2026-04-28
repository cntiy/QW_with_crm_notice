import os
from dotenv import load_dotenv
# 假设你之前的 WeChatTokenManager 类保存在这个文件，或从其他模块导入
from get_qiwei_access_token import WeChatTokenManager

load_dotenv()

# 全局单例实例（模块级变量天然单例）
wx_token_mgr = WeChatTokenManager(
    corpid=os.getenv("CORP_id"),
    corpsecret=os.getenv("agent_scret"),
    refresh_interval=7000
)
