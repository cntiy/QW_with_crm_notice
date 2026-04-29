# CRM 员工ID -> 企微 userid 映射表
# 来源：CRM 人员导出 × 企微通讯录 取交集（共 17 人）
# 注：郑荣胜企微有两个账号，当前使用 ZhengRongSheng，备选 zhengrongsheng@slemon.com
CRM_TO_QW: dict[str, str] = {
    "1099": "QUDAO",                            # 张本
    "1062": "qy012b73853c6740002b0d00a851",      # 黄玉梅
    "1025": "ZHANLUEKEHUFUWU2",                  # 闫小永
    "1016": "anna-qeejoysterilizer",             # 金永娜
    "1008": "qy016d73493cee40002ba60518b8",      # 张宇
    "1007": "QiZheWoNiuQuBiaoChe",               # 王攀飞
    "1186": "ShiJiaQi",                          # 史佳奇
    "1185": "JinChenYu",                         # 金晨宇
    "1179": "HuJie01",                           # 胡洁
    "1177": "ZhangWenBo",                        # 张文博
    "1174": "FengGuanWu01",                      # 冯观武
    "1172": "LiuJiaWen",                         # 张宇豪
    "1166": "ShenZhenShiSiLiMingKeJiYangYiMing", # 杨乙明
    "1153": "yanghao",                           # 杨豪
    "1122": "ZhengRongSheng",                    # 郑荣胜
    "1119": "CaiShuangWu",                       # 杨晶晶
    "1116": "cindy",                             # 杨丹
}


def get_qw_user(crm_owner_id: str) -> str | None:
    return CRM_TO_QW.get(str(crm_owner_id))
