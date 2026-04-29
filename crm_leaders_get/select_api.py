import uuid
import requests
from crm_token_manager import crm_token_mgr


def get_leaders() -> list[dict]:
    token_data = crm_token_mgr.get_token_data()
    access_token = token_data["accessToken"]
    x_fs_ea = token_data["ea"]
    x_fs_userid = "1171"

    uuids = uuid.uuid4()
    url = f"https://open.fxiaoke.com/cgi/crm/v2/data/query?thirdTraceId=${uuids}"
    headers = {
        "authorization": f"Bearer {access_token}",
        "x-fs-userid": x_fs_userid,
        "x-fs-ea": x_fs_ea,
    }
    payload = {
        "data": {
            "search_query_info": {
                "limit": 100,
                "offset": 0,
                "fieldProjection": ["_id", "tel", "owner","company"],
                "filters": [
                    {
                        "field_name": "assigned_time",
                        "field_values": [11],
                        "operator": "BETWEEN",
                        "value_type": 3,
                    },
                    {
                        "field_name": "plain_content",
                        "field_values": ["分配"],
                        "operator": "MATCH",
                        "value_type": 22,
                    },
                ],
            },
            "dataObjectApiName": "LeadsObj",
        }
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()["data"]["dataList"]
