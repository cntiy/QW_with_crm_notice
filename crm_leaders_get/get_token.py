import requests
import uuid
jsons={
    "appId": "FSAID_132345a",
    "permanentCode": "71ABD58049D62213E70FA7049D3C2770",
    "appSecret": "79b5c62e73044f8b93ecefd33b393731",
    "grantType": "app_secret"
}

# 最常用：生成随机 UUID (v4)
u = uuid.uuid4()
url=f"https://open.fxiaoke.com/oauth2.0/token?thirdTraceId=${u}"
def get_token():
 response=requests.post(url=url,json=jsons)
 return response.json()
