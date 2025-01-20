#!/bin/python3
import json
import os
import platform
import queue
import re
import subprocess
import time
from datetime import datetime
from enum import Enum

import HSyslog

ota_version = None
config_file = '/opt/hhd/ex_cloud/DeviceCode.json'
config_directory = '/opt/hhd/ex_cloud/'
device_mqtt_status = False
package_num = 0  # 包序号
Device_ready = False
gun_num = 0
qrcode_nums = 0
hd_send_data = queue.Queue()

device_platform_data = queue.Queue()
platform_device_data = queue.Queue()

read_param_is = False
write_param_is = False

net_status = {
    "netType": 6,
    "sigVal": 4,
    "netId": 2,
}

stop_code = {
    1: [0, 5, 6, 12, 14, 33, 34, 35, 36, 37, 57, 141, 191, 227, 228, 229],  # 按照充电策略，充电结束，充电机停止z
    2: [13, 20, 21, 24, 53, 54, 134, 135, 230, ],  # 在不具备充电结束的条件下，充电机停止z
    3: [15],  # 紧急停机按钮停机故障，充电机停止z
    4: [20, 55],  # CC1 故障（连接确认故障）z
    5: [],  # BMS 故障，充电机停止z
    6: [162, 185, 186, 188, 189, 190, 191, 194, 195, 196, 198, 199, 200, 201, 203, 204, 205, 206, 207, 208, 210, 211, 212, 221, 222, 223, 225, 226, 244, 245, 247, 248],  # BMS 错误，充电机停止z
    7: [223],  # 单体电池电压过高，充电机停止z
    8: [212, 221, 222],  # 单体电池温度过高，充电机停止z
    9: [39, 121, 401],  # 输入过压，充电机停止z
    10: [122, 402],  # 输入欠压，充电机停止z
    11: [123, 403],  # 输入缺相，充电机停止z
    12: [],  # 输出短路，充电机停止z
    13: [22],  # 内部故障（充电机自检故障），充电机停止z
    14: [156, 160, 161, 163, 164],  # 输出过压，充电机停止z
    15: [140, 139, 230],  # 直流输出断路，充电机停止z
    16: [],  # 系统发生故障时，充电机停机z
    17: [],  # 充电系统发生故障时，充电机停机z
    18: [],  # 充电模块发生故障时，充电机停机
    19: [],  # 电池发生故障时，充电机停机z

    80: [1, 3, 4],  # 通过平台系统下达停机指令，充电机停止z
    81: [52, ],  # 用户通过刷卡，选择停止充电，充电机停止z
    82: [],  # 用户通过订单号验证，控制充电机停止z
    90: [],  # 客户已通过智能终端权限认证，但因异常情况未开启充电z
    83: [2, 11, 51, 59, 599],  # 用户使用车辆 VIN 即插即充服务开启充电，通过界面“结束充电”按钮，控制充电机停止z
}

system_fault_code = {
    0x00000001: [],  # 读卡器通信故障
    0x00000002: [],  # 读卡器与主控板通信超时故障
    0x00000004: [],  # 显示屏硬件损坏
    0x00000008: [],  # 显示屏与主控板通信超时故障
    0x00000010: [19, 96, 97, 98, 99, 100, 101, 102, 103, 104, 503, 504, 505, 506, 507, 508, ],  # 交流接触器故障z
    0x00000020: [105, 106, 107, 108],  # 交流接触器供电故障
    0x00000040: [95],  # 低压辅助电源异常
    0x00000080: [17, 18, 41, 73, 74, 75, 94, 109, 110, 111, 500, 501, 502, 521],  # 主控板硬件故障z
    0x00000100: [22, 38, 40, 55, 92, 93, 598, 597],  # 主控板程序异常z
    0x00000200: [440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458],  # 主控板与充电模块通讯不稳定
    0x00000400: [28, 29],  # 主控板与充电模块通讯断开
    0x00000800: [],  # 数据传输出现数据丢失（丢包率≥15%）
    0x00001000: [76, 77, 78, 79, ],  # 电子锁故障
    0x00002000: [261],  # 充电连接装置中温度传感器故障
    0x00004000: [],  #
    0x00008000: [],  #
    0x00010000: [],  # 键盘硬件损坏
    0x00020000: [],  # 键盘与主控板通信故障
    0x00040000: [],  # 电磁锁故障
    0x00080000: [50],  # 电表硬件故障
    0x00100000: [45, 58, 91],  # 电表与主控板通信故障z
    0x00200000: [15, 16, 71, 72, ],  # 急停故障z
    0x00400000: [],  # 数据传输出现数据丢失（1%≤丢包率＜15%）
    0x00800000: [47],  # 设备与后台通讯故障
    0x01000000: [],  #
    0x02000000: [],  #
    0x04000000: [],  # 打印机硬件损坏
    0x08000000: [],  # 打印机与主控板通信故障
    0x10000000: [],  # 缺纸状态（新增）
    0x20000000: [],  # 数据传输出现数据丢失（丢包率＜1%）
    0x40000000: [],  #
    0x80000000: [],  #
}

device_fault_code = {
    0x00000001: [],  # 绝缘电阻值小于阀值
    0x00000002: [152, 153, 154, 157, 159, 165, 166, 258, 259, 260, 268],  # 绝缘模块故障
    0x00000004: [80, 81, 82, 113, 114, 510, 511, 512, 513, 514, 515, 516, 517, 518, 520, 522, 595],  # 整机内部温度过高（70℃≤温度）
    0x00000008: [42, 121, ],  # 输入过压
    0x00000010: [43, 49, 122, 519],  # 输入欠压
    0x00000020: [112, 123, 509],  # 输入缺相
    0x00000040: [124, 125, 126],  # 输入过流
    0x00000080: [],  # 总谐波含量超限
    0x00000100: [131, 132, 133],  # 输出过压
    0x00000200: [134],  # 输出欠压
    0x00000400: [135],  # 输出过流
    0x00000800: [138, 169, 170, 171],  # 输出短路
    0x00001000: [48, 172, 177],  # 充电模块无输出电压、电流
    0x00002000: [],  #
    0x00004000: [],  #
    0x00008000: [],  #
    0x00010000: [],  # 整机内部温度过高（65≤温度＜70℃）
    0x00020000: [],  #
    0x00040000: [],  #
    0x00080000: [],  #
    0x00100000: [],  #
    0x00200000: [],  #
    0x00400000: [],  #
    0x00800000: [],  #
    0x01000000: [],  # 整机内部温度过高（60≤温度＜65℃）
    0x02000000: [],  #
    0x04000000: [25, 26, 27, 60, ],  # 存储器读取数据失败
    0x08000000: [46],  # 存储器已满
    0x10000000: [],  #
    0x20000000: [],  #
    0x40000000: [],  #
    0x80000000: [],  #
}

power_model_fault_code = {
    0x00000001: [],  # PFC模块母线过压
    0x00000002: [],  # PFC模块母线欠压
    0x00000004: [],  # PFC模块控制电源异常
    0x00000008: [30, 31, 44, 167, 168, 173, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413],  # DC/DC模块控制电源异常
    0x00000010: [],  # IGBT驱动过流
    0x00000020: [],  # IGBT驱动欠压
    0x00000040: [],  # 变压器过热（温升＞80K）
    0x00000080: [],  # PFC模块温度过高（70≤温度＜75℃）
    0x00000100: [],  # PFC模块温度过高（75≤温度＜80℃）
    0x00000200: [],  # PFC模块温度过高（80℃≤温度
    0x00000400: [],  # 软启动功能异常
    0x00000800: [],  # 充电模块内部温度过高（75≤温度＜80℃）
    0x00001000: [32, 411],  # 充电模块内部温度过高（80℃≤温度）
    0x00002000: [],  # 直流输出继电器故障
    0x00004000: [],  # 直流输出继电器无触发信号
    0x00008000: [],  # 充电模块内部温度过高（70＜温度＜75℃）
    0x00010000: [],  #
    0x00020000: [],  #
    0x00040000: [],  #
    0x00080000: [],  #
    0x00100000: [],  #
    0x00200000: [],  #
    0x00400000: [],  #
    0x00800000: [],  #
    0x01000000: [],  #
    0x02000000: [],  #
    0x04000000: [],  #
    0x08000000: [],  #
    0x10000000: [],  #
    0x20000000: [],  #
    0x40000000: [],  #
    0x80000000: [],  #
}

battery_fault_code = {
    0x00000001: [],  #
    0x00000002: [],  #
    0x00000004: [176, 213, 215],  # 单体电池电压过高
    0x00000008: [],  # 单体电池温度过高
    0x00000010: [174, 182, 183, 217, 218, 219, 220, 224, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 246, 249, 250, 251, 252, 253, 254, 255, 256, 257],  # BMS错误
    0x00000020: [56, 181, 184, 187, 192, 193, 197, 202, 209, ],  # BMS通信超时
    0x00000040: [151],  # 电池反接
    0x00000080: [],  # 电池未接
    0x00000100: [216],  # 电池总电压过高
    0x00000200: [214],  # 电池总电压过低
    0x00000400: [],  # SOC过高
    0x00000800: [155, 158, ],  # 电池组绝缘故障
    0x00001000: [],  # 电池组输出连接器故障
    0x00002000: [175, ],  # CC1故障（连接确认故障）
    0x00004000: [],  #
    0x00008000: [],  #
    0x00010000: [],  #
    0x00020000: [],  #
    0x00040000: [],  #
    0x00080000: [],  #
    0x00100000: [],  #
    0x00200000: [],  #
    0x00400000: [],  #
    0x00800000: [],  #
    0x01000000: [],  #
    0x02000000: [],  #
    0x04000000: [],  #
    0x08000000: [],  #
    0x10000000: [],  #
    0x20000000: [],  #
    0x40000000: [],  #
    0x80000000: [],  #
}

fault_stop_class = {
    "stop_code": {
        "device_code": [0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 20, 21, 24, 33, 34, 35, 36, 37, 39, 51, 52, 53, 54, 57, 59, 138, 139, 140, 141, 156, 160, 161, 162, 163, 164, 185, 186, 188, 189, 190, 191, 194, 195, 196, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
                        208, 210, 211, 212, 221, 222, 223, 225, 226, 227, 228, 229, 230, 244, 245, 247, 248, 599],
        "platform_code": stop_code,
    },
    "system_fault_code": {
        "device_code": [15, 16, 17, 18, 19, 22, 28, 29, 38, 40, 41, 45, 47, 50, 55, 58, 71, 72, 73, 74, 75, 76, 77, 78, 79, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 261, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451,
                        452, 453, 454, 455, 456, 457, 458, 500, 501, 502, 503, 504, 505, 506, 507, 508, 521, 598, 597],
        "platform_code": system_fault_code,
    },
    "device_fault_code": {
        "device_code": [25, 26, 27, 42, 43, 46, 48, 49, 60, 80, 81, 82, 112, 113, 114, 121, 122, 123, 124, 125, 126, 131, 132, 133, 134, 135, 136, 137, 138, 152, 153, 154, 157, 159, 165, 166, 169, 170, 171, 172, 177, 258, 259, 260, 268, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520,
                        522, 595],
        "platform_code": device_fault_code,
    },
    "power_model_fault_code": {
        "device_code": [30, 31, 32, 44, 167, 168, 173, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413],
        "platform_code": power_model_fault_code,
    },
    "battery_fault_code": {
        "device_code": [56, 151, 155, 158, 174, 175, 176, 181, 182, 183, 184, 187, 192, 193, 197, 202, 209, 213, 214, 215, 216, 217, 218, 219, 220, 224, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 246, 249, 250, 251, 252, 253, 254, 255, 256, 257, ],
        "platform_code": battery_fault_code,
    },
}
chargeSys = {}  # 系统
cabinet = {}  # 主机柜
gun = {}  # 枪
pdu = {}  # 模块控制器
module = {}  # 模块
bms = {}  # bms
meter = {}  # 电表
parkLock = {}  # 地锁

topic_hqc_sys_network_state = '/hqc/sys/network-state'  # 网络状态消息
topic_hqc_sys_time_sync = '/hqc/sys/time-sync'  # 时间同步消息
topic_hqc_main_telemetry_notify_fault = '/hqc/main/telemetry-notify/fault'  # 设备故障消息
topic_hqc_cloud_event_notify_fault = '/hqc/cloud/event-notify/fault'  # 设备故障查询消息
topic_hqc_main_telemetry_notify_info = '/hqc/main/telemetry-notify/info'  # 遥测遥信消息
topic_hqc_cloud_event_notify_info = '/hqc/cloud/event-notify/info'  # 遥测遥信查询消息
topic_hqc_main_event_notify_request_charge = '/hqc/main/event-notify/request-charge'  # 充电请求消息
topic_hqc_main_event_reply_request_charge = '/hqc/main/event-reply/request-charge'  # 充电请求应答消息
topic_hqc_main_event_notify_control_charge = '/hqc/main/event-notify/control-charge'  # 充电控制消息
topic_hqc_main_event_reply_control_charge = '/hqc/main/event-reply/control-charge'  # 充电控制应答消息
topic_hqc_ui_event_notify_auth_gun = '/hqc/ui/event-notify/auth-gun'  # 鉴权绑定消息
topic_hqc_main_event_notify_check_vin = '/hqc/main/event-notify/check-vin'  # 车辆VIN鉴权消息
topic_hqc_main_event_reply_check_vin = '/hqc/main/event-reply/check-vin'  # 车辆VIN鉴权应答消息
topic_hqc_main_event_notify_charge_record = '/hqc/main/event-notify/charge-record'  # 充电记录消息
topic_hqc_main_event_reply_charge_record = '/hqc/main/event-reply/charge-record'  # 充电记录应答消息
topic_hqc_main_event_notify_charge_cost = '/hqc/main/event-notify/charge-cost'  # 充电费用消息
topic_hqc_main_event_notify_charge_elec = '/hqc/main/event-notify/charge-elec'  # 充电电量冻结消息
topic_hqc_main_event_notify_charge_account = '/hqc/main/event-notify/charge-account'  # 充电结算消息
topic_hqc_cloud_event_notify_recharge = '/hqc/cloud/event-notify/recharge'  # 账户充值消息
topic_hqc_cloud_event_reply_recharge = '/hqc/cloud/event-reply/recharge'  # 账户充值应答消息
topic_hqc_cloud_event_notify_balance_query = '/hqc/cloud/event-notify/balance-query'  # 账户余额查询消息
topic_hqc_cloud_event_reply_balance_query = '/hqc/cloud/event-reply/balance-query'  # 账户余额查询结果消息
topic_hqc_cloud_event_notify_request_rate = '/hqc/cloud/event-notify/request-rate'  # 充电系统费率请求消息
topic_hqc_cloud_event_reply_request_rate = '/hqc/cloud/event-reply/request-rate'  # 充电系统费率请求应答消息
topic_hqc_cloud_event_notify_query_rate = '/hqc/cloud/event-notify/query-rate'  # 充电系统费率查询消息
topic_hqc_cloud_event_reply_query_rate = '/hqc/cloud/event-reply/query-rate'  # 充电系统费率查询结果消息
topic_hqc_cloud_event_notify_request_gunrate = '/hqc/cloud/event-notify/request-gunrate'  # 充电枪费率请求消息
topic_hqc_cloud_event_reply_request_gunrate = '/hqc/cloud/event-reply/request-gunrate'  # 充电枪费率请求应答消息
topic_hqc_cloud_event_notify_query_gunrate = '/hqc/cloud/event-notify/query-gunrate'  # 充电枪费率查询消息
topic_hqc_cloud_event_reply_query_gunrate = '/hqc/cloud/event-reply/query-gunrate'  # 充电枪费率查询结果消息
topic_hqc_cloud_event_notify_request_startup = '/hqc/cloud/event-notify/request-startup'  # 充电启动策略请求消息
topic_hqc_cloud_event_reply_request_startup = '/hqc/cloud/event-reply/request-startup'  # 充电启动策略请求应答消息
topic_hqc_cloud_event_notify_query_startup = '/hqc/cloud/event-notify/query-startup'  # 充电启动策略查询消息
topic_hqc_cloud_event_reply_query_startup = '/hqc/cloud/event-reply/query-startup'  # 充电启动策略查询结果消息
topic_hqc_cloud_event_notify_request_dispatch = '/hqc/cloud/event-notify/request-dispatch'  # 功率分配策略请求消息
topic_hqc_cloud_event_reply_request_dispatch = '/hqc/cloud/event-reply/request-dispatch'  # 功率分配策略请求应答消息
topic_hqc_cloud_event_notify_query_dispatch = '/hqc/cloud/event-notify/query-dispatch'  # 功率分配策略查询消息
topic_hqc_cloud_event_reply_query_dispatch = '/hqc/cloud/event-reply/query-dispatch'  # 功率分配策略查询结果消息
topic_hqc_cloud_event_notify_request_offlinelist = '/hqc/cloud/event-notify/request-offlinelist'  # 离线名单版本请求消息
topic_hqc_cloud_event_reply_request_offlinelist = '/hqc/cloud/event-reply/request-offlinelist'  # 离线名单版本应答消息
topic_hqc_main_event_notify_charge_session = '/hqc/main/event-notify/charge-session'  # 充电会话消息
topic_hqc_main_event_reply_charge_session = '/hqc/main/event-reply/charge-session'  # 充电会话应答消息
topic_hqc_main_event_notify_update_param = '/hqc/main/event-notify/update-param'  # 设置参数消息
topic_hqc_main_event_reply_update_param = '/hqc/main/event-reply/update-param'  # 设置参数应答消息
topic_hqc_main_event_notify_update_qrcode = '/hqc/main/event-notify/update-qrcode'  # 二维码更新消息
topic_hqc_main_event_notify_reserve_count_down = '/hqc/main/event-notify/reserve-count-down'  # 预约延时启动倒计时消息
topic_hqc_cloud_event_notify_m1_secret = '/hqc/cloud/event-notify/m1-secret'  # M1卡密钥更新消息
topic_hqc_cloud_event_reply_m1_secret = '/hqc/cloud/event-reply/m1-secret'  # M1卡密钥更新结果消息
topic_hqc_main_event_reply_update_qrcode = '/hqc/main/event-reply/update-qrcode'  # 二维码更新应答消息
topic_hqc_cloud_event_notify_pos_pre_transaction = '/hqc/cloud/event-notify/pos-pre-transaction'  # POS机预交易信息消息
topic_hqc_cloud_event_notify_pos_charge_cost = '/hqc/cloud/event-notify/pos-charge-cost'  # POS机扣费消息
topic_hqc_cloud_event_reply_pos_charge_cost = '/hqc/cloud/event-reply/pos-charge-cost'  # POS机扣费结果消息
topic_hqc_cloud_event_notify_update_charge_order_id = '/hqc/cloud/event-notify/update-charge-order-id'  # 充电订单ID更新消息
_hqc_cloud_event_reply_update_charge_order_id = '/hqc/cloud/event-reply/update-charge-order-id'  # 充电订单ID更新结果消息
topic_hqc_main_event_notify_update_rate = '/hqc/main/event-notify/update-rate'  # 充电系统费率同步消息
topic_hqc_main_event_reply_update_rate = '/hqc/main/event-reply/update-rate'  # 充电系统费率同步应答消息
topic_hqc_main_event_notify_update_gunrate = '/hqc/main/event-notify/update-gunrate'  # 充电枪费率同步消息
topic_hqc_main_event_reply_update_gunrate = '/hqc/main/event-reply/update-gunrate'  # 充电枪费率同步应答消息
topic_hqc_main_event_notify_update_startup = '/hqc/main/event-notify/update-startup'  # 充电启动策略同步消息
topic_hqc_main_event_reply_update_startup = '/hqc/main/event-reply/update-startup'  # 充电启动策略同步应答消息
topic_hqc_main_event_notify_update_dispatch = '/hqc/main/event-notify/update-dispatch'  # 功率分配策略同步消息
topic_hqc_main_event_reply_update_dispatch = '/hqc/main/event-reply/update-dispatch'  # 功率分配策略同步应答消息
topic_hqc_main_event_notify_update_offlinelist = '/hqc/main/event-notify/update-offlinelist'  # 离线名单版本同步消息
topic_hqc_main_event_reply_update_offflinelist = '/hqc/main/event-reply/update-offflinelist'  # 离线名单版本同步应答消息
topic_hqc_main_event_notify_offlinelist_log = '/hqc/main/event-notify/offlinelist-log'  # 离线名单项操作日志消息
topic_hqc_main_event_reply_offlinelist_log = '/hqc/main/event-reply/offlinelist-log'  # 离线名单项操作日志应答消息
topic_hqc_main_event_notify_clear = '/hqc/main/event-notify/clear'  # 清除故障、事件消息
topic_hqc_main_event_reply_clear = '/hqc/main/event-reply/clear'  # 清除故障、事件应答消息
topic_hqc_sys_upgrade_notify_notify = '/hqc/sys/upgrade-notify/notify'  # 升级控制消息
topic_hqc_sys_upgrade_reply_notify = '/hqc/sys/upgrade-reply/notify'  # 升级控制应答消息
topic_hqc_sys_upgrade_notify_process = '/hqc/sys/upgrade-notify/process'  # 升级进度消息
topic_hqc_sys_upgrade_notify_result = '/hqc/sys/upgrade-notify/result'  # 升级结果消息
topic_hqc_sys_upload_notify_notify = '/hqc/sys/upload-notify/notify'  # 日志文件上传请求消息
topic_hqc_sys_upload_reply_notify = '/hqc/sys/upload-reply/notify'  # 日志文件上传请求应答消息
topic_hqc_sys_upgrade_notify_version = '/hqc/sys/upgrade-notify/version'  # 读取版本号消息
topic_hqc_sys_upgrade_reply_version = '/hqc/sys/upgrade-reply/version'  # 读取版本号应答消息
topic_hqc_sys_upgrade_notify_process_version = '/hqc/sys/upgrade-notify/process-version'  # 读取进程版本号消息
topic_hqc_sys_upgrade_reply_process_versio = '/hqc/sys/upgrade-reply/process-version'  # 读取进程版本号应答消息
topic_hqc_sys_upgrade_notify_control_command = '/hqc/sys/upgrade-notify/control_command'  # 远程控制命令消息
topic_hqc_sys_upgrade_reply_control_command = '/hqc/sys/upgrade-reply/control_command'  # 远程控制命令应答消息
topic_hqc_main_event_notify_read_param = '/hqc/main/event-notify/read-param'  # 参数读取消息
topic_hqc_main_event_reply_read_param = '/hqc/main/event-reply/read-param'  # 参数读取应答消息
topic_hqc_main_event_notify_read_fault = '/hqc/main/event-notify/read-fault'  # 当前/历史故障读取消息
topic_hqc_main_event_reply_read_fault = '/hqc/main/event-reply/read-fault'  # 当前/历史读取应答消息
topic_hqc_main_event_notify_read_event = '/hqc/main/event-notify/read-event'  # 事件读取消息
topic_hqc_main_event_reply_read_event = '/hqc/main/event-reply/read-event'  # 事件读取应答消息


class device_system_mode(Enum):
    Windows = 1
    Linux = 2
    Darwin = 3


system_mode = device_system_mode.Linux.value


class net_type(Enum):  # 网络状态
    no_net = 0
    other_net = 1
    net_4G = 2
    net_5G = 3
    NB_IOT = 4
    WIFI = 5
    wired_net = 6


class net_id(Enum):  # 网络运营商
    unknow = 0
    id_4G = 1
    id_cable = 2
    id_WIFI = 3


class control_charge(Enum):  # 充电控制
    start_charge = 1
    stop_charge = 2
    rev_charge = 3
    rev_not_charge = 4


class device_param_type(Enum):  # 设备分类
    chargeSys = 0x00
    cabinet = 0x01
    gun = 0x02
    pdu = 0x03
    module = 0x04
    bms = 0x05
    meter = 0x06
    parkLock = 0x07


class device_ctrl_type(Enum):  # 设备硬件分类
    TIU = 0x00
    GCU = 0x01
    PDU = 0x02
    CCU = 0x03
    DTU = 0x04
    ACU = 0x05
    UI = 0x1A
    SDK = 0x1B
    Protocol = 0x1C
    Advertisement = 0x1D
    Main = 0x1E


#  充电枪遥测


def do_start_source(i):
    if i == 10:
        return 0x01
    elif i == 11:
        return 0x07
    elif i == 12:
        return 0x3F
    elif i == 13:
        return 0x01
    elif i == 14:
        return 0x3F
    elif i == 15:
        return 0x04


def unix_time(unix_t):
    dt_time = datetime.fromtimestamp(unix_t)
    return dt_time.strftime("%y%m%d")


def unix_time_14(unix_t):
    dt_time = datetime.fromtimestamp(unix_t)
    return dt_time.strftime("%Y%m%d%H%M%S")


def get_unix_time():
    return int(time.time())


def get_auxiliary_power_options(auxiliary_power_options):
    if auxiliary_power_options == 0:
        return 0x5A
    if auxiliary_power_options == 1:
        return 0xA5


def get_reservation_status(reservation_status):
    if reservation_status == 0x0A:
        return 1
    else:
        return 0


def get_control_reason(control_reason):
    if control_reason == 0:
        return 0x00
    if control_reason == 1:
        return 0x08
    if control_reason == 2:
        return 0x05
    if control_reason == 3:
        return 0x01
    if control_reason == 4:
        return 0x02


def get_reply_check_vin_result(result):
    if result == 0x01:
        return 0x00
    if result == 0x00:
        return 0x01


def get_reply_check_vin_reason(reason):
    if reason == 0x00:
        return 0x00
    if reason == 0x01:
        return 0x01
    if reason == 0x02:
        return 0x02
    if reason == 0x03:
        return 0x03
    if reason == 0x04:
        return 0x03


def get_stop_reason(device_stop_code):
    stop_fault_code = 0
    if stop_fault_code == 0:
        for code_type, code_info in fault_stop_class.items():
            # print(code_type)
            # print(code_info)
            if device_stop_code in code_info.get("device_code"):
                if code_type == "stop_code":
                    for device_code, code_list in code_info.get("platform_code").items():
                        print(device_code)
                        print(code_list)
                        if device_stop_code in code_list:
                            stop_fault_code = device_code
                            break
                elif code_type == "system_fault_code":
                    stop_fault_code = 16
                elif code_type == "device_fault_code":
                    stop_fault_code = 17
                elif code_type == "power_model_fault_code":
                    stop_fault_code = 18
                elif code_type == "battery_fault_code":
                    stop_fault_code = 19
        return stop_fault_code
    else:
        return 1


def get_fault_reason(device_stop_code):
    stop_fault_code = 0
    if stop_fault_code == 0:
        for code_type, code_info in fault_stop_class.items():
            if code_type != "stop_code":
                if device_stop_code in code_info.get("device_code"):
                    for device_code, code_list in code_info.get("platform_code").items():
                        print(device_code)
                        print(code_list)
                        if device_stop_code in code_list:
                            stop_fault_code = device_code
                            break
        return stop_fault_code
    else:
        return 0


def get_ip_from_resolv():
    if system_mode == device_system_mode.Linux.value:
        if os.path.getsize("/etc/resolv.conf") == 0:
            with open("/etc/resolv.conf", 'a') as file:
                file.write("nameserver 8.8.8.8\n")
            return "8.8.8.8"
        else:
            with open("/etc/resolv.conf", 'r') as file:
                lines = file.readlines()
                # 提取最后一行中的 IP 地址
                for line in lines:
                    if line.startswith("nameserver"):
                        return "8.8.8.8"
    else:
        return "8.8.8.8"


def ping_ip(IP):
    if system_mode == device_system_mode.Linux.value:
        ping_process = subprocess.Popen(
            ['ping', '-c', '4', IP],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ping_output, ping_error = ping_process.communicate()
        return ping_output.decode('utf-8'), ping_process.returncode
    else:
        # Windows 的 ping 命令
        ping_process = subprocess.Popen(
            ['ping', '-n', '4', IP],  # '-n 4' 表示发送 4 个包
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ping_output, ping_error = ping_process.communicate()
        return ping_output.decode('gbk'), ping_process.returncode


def parse_ping_output(output):
    try:
        if system_mode == device_system_mode.Linux.value:
            loss_match = re.search(r'(\d+)% packet loss', output)
            rtt_match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', output)

            if loss_match:
                packet_loss = int(loss_match.group(1))
            else:
                packet_loss = 100  # 如果没有找到丢包率信息，则认为是100%丢包

            if rtt_match:
                average_latency = float(rtt_match.group(1))
            else:
                average_latency = None

            return packet_loss, average_latency
        else:
            loss_match = re.search(r"丢失 = \d+ \((\d+)% 丢失\)", output)
            rtt_match = re.search(r"平均 = (\d+)ms", output)
            # 提取丢包率
            if loss_match:
                packet_loss = int(loss_match.group(1))
            else:
                packet_loss = 100  # 如果没有找到丢包率信息，则认为是100%丢包

            # 提取平均延迟
            if rtt_match:
                average_latency = float(rtt_match.group(1))
            else:
                average_latency = None

            return packet_loss, average_latency
    except Exception as e:
        HSyslog.log_error(f"Error parsing ping output: {e}")
        return None, None


def calculate_sigval(packet_loss, latency):
    if latency is None:
        return 0

    if packet_loss < 100:
        if 0 <= latency < 50:
            sigVal = 4
        elif 50 <= latency < 120:
            sigVal = 3
        elif 120 <= latency < 200:
            sigVal = 2
        elif 200 <= latency < 300:
            sigVal = 1
        else:
            sigVal = 0
        return sigVal
    else:
        return 0


def get_balance(balance):
    if isinstance(balance, str):
        if "." in balance:
            return int(balance.split('.')[0]) * 1000 + int(balance.split('.')[1]) * 10
        else:
            return int(balance.split('.')[0]) * 1000
    else:
        return 0


def get_ping():
    IP = get_ip_from_resolv()
    ping_output, return_code = ping_ip(IP)
    if return_code == 0:
        try:
            packet_loss, average_latency = parse_ping_output(ping_output)
            if packet_loss is not None and average_latency is not None:
                if packet_loss <= 100:
                    return 1
                else:
                    return 0
        except Exception as e:
            HSyslog.log_error(f"Error calculating sigVal: {e}")
            return 0
    else:
        return 0


def get_net():
    IP = get_ip_from_resolv()
    ping_output, return_code = ping_ip(IP)
    try:
        if return_code == 0:
            try:
                packet_loss, average_latency = parse_ping_output(ping_output)
                # 检查丢包率
                if packet_loss is not None and average_latency is not None:
                    if packet_loss <= 90:
                        net_status["sigVal"] = calculate_sigval(packet_loss, average_latency)
                    else:
                        net_status["sigVal"] = calculate_sigval(packet_loss, average_latency)
            except Exception as e:
                HSyslog.log_error(f"Error calculating sigVal: {e}")
                return 0
        else:
            net_status["sigVal"] = 0
    except Exception as e:
        HSyslog.log_error(f"get_net: {return_code} . {ping_output} .{e}")

    try:
        if system_mode == device_system_mode.Linux.value:
            # 获取网络接口信息
            ifconfig_process = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ifconfig_output, _ = ifconfig_process.communicate()
            # 检查网络接口类型
            if 'wlan' in str(ifconfig_output):
                net_status["netType"] = 5
                net_status["netId"] = 3
            elif 'eth' in str(ifconfig_output):
                net_status["netType"] = 6
                net_status["netId"] = 2
            elif 'ppp0' in str(ifconfig_output):
                net_status["netType"] = 2
                net_status["netId"] = 1
            else:
                net_status["netType"] = 6
                net_status["netId"] = 2
        else:
            # Windows 使用 `ipconfig`
            net_cmd = ['ipconfig']
            net_process = subprocess.Popen(net_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            net_output, net_error = net_process.communicate()

            # 解码输出为 GBK 编码（适用于简体中文系统）
            net_output = net_output.decode('gbk', errors='ignore')

            # 检查接口类型
            if "无线局域网适配器" in net_output or "Wireless" in net_output:
                net_status["netType"] = 5  # 无线网络
                net_status["netId"] = 3
            elif "以太网适配器" in net_output or "Ethernet" in net_output:
                net_status["netType"] = 6  # 有线网络
                net_status["netId"] = 2
            elif "PPP" in net_output:
                net_status["netType"] = 2  # PPP 网络
                net_status["netId"] = 1
            else:
                net_status["netType"] = 6
                net_status["netId"] = 2
    except Exception as e:
        HSyslog.log_error(f"get_net: {ifconfig_process} . {ifconfig_output} .{e}")


def get_sysytem_mode():
    global system_mode
    os_name = platform.system()
    if os_name == "Windows":
        system_mode = device_system_mode.Windows.value
        return device_system_mode.Windows.value
    elif os_name == "Linux":
        system_mode = device_system_mode.Linux.value
        return device_system_mode.Linux.value
    elif os_name == "Darwin":
        system_mode = device_system_mode.Darwin.value
        return device_system_mode.Darwin.value
    else:
        system_mode = device_system_mode.Linux.value
        return device_system_mode.Linux.value


def read_json_config(config_type, file_path=config_file):
    try:
        with open(file_path, 'r') as config_file:
            config_data = json.load(config_file)
            if config_data:
                return config_data.get(config_type)
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    except json.JSONDecodeError:
        print(f"无法解析文件 {file_path}。")
    return None


def save_json_config(config_data, file_path=config_file, directory_path=config_directory):
    # 如果文件存在，先读取现有的配置
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as config_file:
                existing_config = json.load(config_file)
        except json.JSONDecodeError:
            HSyslog.log_error(f"无法解析文件 {file_path} 使用空配置")
            existing_config = {}
    else:
        # 如果文件不存在，初始化为空配置
        os.makedirs(directory_path)
        existing_config = {}

    # 更新现有配置
    existing_config.update(config_data)

    # 保存更新后的配置
    try:
        with open(file_path, 'w') as config_file:
            json.dump(existing_config, config_file, indent=4)
        print(f"配置成功更新并保存到 {file_path}")
    except Exception as e:
        print(f"保存配置文件失败: {e}")
