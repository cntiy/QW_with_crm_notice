import logging
import time
import threading
from datetime import datetime, timedelta

from QW_token import wx_token_mgr, send_template_card
from crm_leaders_get import crm_token_mgr, get_leaders
from db_add import save_leads, get_leads, clear_leads, insert_daily_leads, get_yesterday_lead_ids
from config.user_mapping import get_qw_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

_stop = threading.Event()
_is_first_poll = True   # 首次轮询（启动或凌晨清缓存后）只存不通知

# 轮询时间窗口（仅在此时段内执行轮询）
POLL_START_HOUR = 8
POLL_END_HOUR   = 22


# ─── 核心业务 ────────────────────────────────────────────────────────────────

def poll_crm() -> None:
    global _is_first_poll
    try:
        new_leads = get_leaders()
        new_index = {lead["_id"]: lead for lead in new_leads}

        if _is_first_poll:
            redis_leads = get_leads()
            if redis_leads:
                # 中途重启：Redis 有今天的数据，直接用作基准，避免重复通知
                prev_ids = {lead["_id"] for lead in redis_leads}
                added = [lead for lid, lead in new_index.items() if lid not in prev_ids]
                logging.info(f"重启后首次轮询：Redis 已有 {len(redis_leads)} 条，新增 {len(added)} 条")
            else:
                # 全新启动：Redis 为空，与昨天 MySQL 对比过滤旧数据
                yesterday_ids = get_yesterday_lead_ids()
                added = [lead for lid, lead in new_index.items() if lid not in yesterday_ids]
                logging.info(
                    f"首次轮询：CRM 返回 {len(new_leads)} 条，"
                    f"昨日记录 {len(yesterday_ids)} 条，新增 {len(added)} 条"
                )
            _is_first_poll = False
        else:
            prev_ids = {lead["_id"] for lead in get_leads()}
            added = [lead for lid, lead in new_index.items() if lid not in prev_ids]

        if added:
            logging.info(f"检测到 {len(added)} 条新分配线索，开始通知...")
            for lead in added:
                _notify(lead)

        save_leads(new_leads)
        logging.info(f"Redis 已更新，当前共 {len(new_leads)} 条线索")

    except Exception:
        logging.exception("poll_crm 执行失败")


def _notify(lead: dict) -> None:
    owner_raw = lead.get("owner")
    owner_id = owner_raw[0] if isinstance(owner_raw, list) else owner_raw
    qw_user = get_qw_user(owner_id) or "Qi"  # 测试用：未映射时发给 Qi
    if not get_qw_user(owner_id):
        logging.warning(f"未找到 CRM owner={owner_id} 的映射，消息转发至 Qi")
    try:
        send_template_card(
            touser=qw_user,
            company=lead.get("company", "未知"),
            tel=lead.get("tel", "未知"),
        )
    except Exception:
        logging.exception(f"企微通知发送失败，lead_id={lead.get('_id')}")


def midnight_flush() -> None:
    """凌晨执行：当天最终线索写入 MySQL，然后清空 Redis 准备次日。"""
    try:
        leads = get_leads()
        if leads:
            insert_daily_leads(leads)
            logging.info(f"MySQL 落库完成，共 {len(leads)} 条线索，日期={datetime.now().date()}")
        clear_leads()
        global _is_first_poll
        _is_first_poll = True   # 凌晨清缓存后，下次轮询只初始化不通知
        logging.info("Redis 线索缓存已清空，准备记录新一天")
    except Exception:
        logging.exception("midnight_flush 执行失败")


# ─── 调度线程 ─────────────────────────────────────────────────────────────────

def _polling_loop() -> None:
    """每 120 秒轮询一次 CRM。"""
    while not _stop.is_set():
        poll_crm()
        _stop.wait(120)


def _midnight_loop() -> None:
    """精确等到下一个凌晨 00:00 执行落库+清缓存，之后每 24 小时循环。"""
    while not _stop.is_set():
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        wait_secs = (next_midnight - now).total_seconds()
        logging.info(
            f"下次凌晨落库将在 {wait_secs:.0f}s 后执行"
            f"（{next_midnight.strftime('%Y-%m-%d %H:%M:%S')}）"
        )
        _stop.wait(wait_secs)
        if not _stop.is_set():
            midnight_flush()


# ─── 入口 ─────────────────────────────────────────────────────────────────────

def main() -> None:
    wx_token_mgr.start_auto_refresh()    # 企微 token 后台自动刷新
    crm_token_mgr.start_auto_refresh()   # CRM token 后台自动刷新（6600s）

    threads = [
        threading.Thread(target=_polling_loop, name="polling", daemon=True),
        threading.Thread(target=_midnight_loop, name="midnight", daemon=True),
    ]
    for t in threads:
        t.start()

    logging.info("服务已启动：每 120s 轮询 CRM，每天 00:00 落库并清缓存")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("收到中断信号，正在退出...")
    finally:
        _stop.set()
        wx_token_mgr.stop_auto_refresh()
        crm_token_mgr.stop_auto_refresh()
        for t in threads:
            t.join(timeout=5)
        logging.info("服务已停止")


if __name__ == "__main__":
    main()
