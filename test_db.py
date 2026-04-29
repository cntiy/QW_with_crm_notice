import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_add"))

from redis_insert import save_leads, get_leads, clear_leads
from mysql_insert import insert_daily_leads

MOCK_LEADS = [
    {"_id": "lead_001", "tel": "13800000001", "owner": "crm_uid_001", "company": "测试公司A"},
    {"_id": "lead_002", "tel": "13800000002", "owner": "crm_uid_002", "company": "测试公司B"},
]


def test_redis():
    print("\n===== Redis 测试 =====")

    clear_leads()
    print("[1] 清空后读取:", get_leads())

    save_leads(MOCK_LEADS)
    result = get_leads()
    print("[2] 写入后读取:", result)
    assert len(result) == 2, "写入条数不符"
    assert result[0]["_id"] == "lead_001"
    print("[3] 断言通过 ✓")

    print("[4] 数据保留，可去 Redis 客户端查看 key: crm:leads:today")
    print("Redis 测试完成 ✓")


def test_mysql():
    print("\n===== MySQL 测试 =====")
    try:
        insert_daily_leads(MOCK_LEADS)
        print("写入成功 ✓（请去数据库确认 crm_notice 最新一行）")
    except Exception as e:
        print(f"写入失败 ✗: {e}")


if __name__ == "__main__":
    test_redis()
    test_mysql()
