import json
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def _connect():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def insert_daily_leads(leads: list[dict]) -> None:
    # 落库时已过凌晨，CURDATE() 是新的一天，用 -1 DAY 记录为昨天的数据
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO crm_notice (notice_collection, record_date) VALUES (%s, CURDATE() - INTERVAL 1 DAY)",
            (json.dumps(leads, ensure_ascii=False),),
        )
        conn.commit()
    finally:
        conn.close()


def get_yesterday_lead_ids() -> set:
    """返回昨天 MySQL 记录中所有线索的 _id 集合，用于首次轮询去重。"""
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT notice_collection FROM crm_notice "
            "WHERE record_date = CURDATE() - INTERVAL 1 DAY "
            "ORDER BY id DESC LIMIT 1"
        )
        row = cursor.fetchone()
        if not row:
            return set()
        leads = json.loads(row[0])
        return {lead["_id"] for lead in leads if "_id" in lead}
    finally:
        conn.close()
