import copy
import hashlib
import struct
import threading
from datetime import datetime
import datetime
import queue
import sqlite3
import time
from enum import Enum

import HSyslog


class tpp_mqtt_cmd_enum(Enum):
    tpp_cmd_type_41 = 0x41
    tpp_cmd_type_51 = 0x51
    tpp_cmd_type_42 = 0x42
    tpp_cmd_type_52 = 0x52
    tpp_cmd_type_46 = 0x46
    tpp_cmd_type_56 = 0x56
    tpp_cmd_type_48 = 0x48
    tpp_cmd_type_58 = 0x58
    tpp_cmd_type_49 = 0x49
    tpp_cmd_type_59 = 0x59
    tpp_cmd_type_40 = 0x40
    tpp_cmd_type_50 = 0x50
    tpp_cmd_type_43 = 0x43
    tpp_cmd_type_53 = 0x53

    tpp_cmd_type_01 = 0x01
    tpp_cmd_type_10 = 0x10
    tpp_cmd_type_11 = 0x11
    tpp_cmd_type_05 = 0x05
    tpp_cmd_type_15 = 0x15
    tpp_cmd_type_07 = 0x07
    tpp_cmd_type_17 = 0x17
    tpp_cmd_type_08 = 0x08
    tpp_cmd_type_18 = 0x18
    tpp_cmd_type_09 = 0x09
    tpp_cmd_type_0A = 0x0A
    tpp_cmd_type_1A = 0x1A

    tpp_cmd_type_E0 = 0xE0
    tpp_cmd_type_F0 = 0xF0
    tpp_cmd_type_21 = 0x21
    tpp_cmd_type_31 = 0x31
    tpp_cmd_type_22 = 0x22
    tpp_cmd_type_32 = 0x32
    tpp_cmd_type_23 = 0x23
    tpp_cmd_type_33 = 0x33
    tpp_cmd_type_24 = 0x24
    tpp_cmd_type_34 = 0x34
    tpp_cmd_type_25 = 0x25
    tpp_cmd_type_35 = 0x35
    tpp_cmd_type_26 = 0x26
    tpp_cmd_type_36 = 0x36
    tpp_cmd_type_2B = 0x2B
    tpp_cmd_type_3B = 0x3B
    tpp_cmd_type_39 = 0x39
    tpp_cmd_type_3A = 0x3A
    tpp_cmd_type_3F = 0x3F

    tpp_cmd_type_70 = 0x70
    tpp_cmd_type_60 = 0x60
    tpp_cmd_type_71 = 0x71
    tpp_cmd_type_61 = 0x61
    tpp_cmd_type_72 = 0x72
    tpp_cmd_type_62 = 0x62
    tpp_cmd_type_73 = 0x73
    tpp_cmd_type_63 = 0x63
    tpp_cmd_type_74 = 0x74
    tpp_cmd_type_64 = 0x64
    tpp_cmd_type_75 = 0x75
    tpp_cmd_type_65 = 0x65
    tpp_cmd_type_78 = 0x78
    tpp_cmd_type_68 = 0x68
    tpp_cmd_type_69 = 0x69
    tpp_cmd_type_7A = 0x7A
    tpp_cmd_type_6A = 0x6A
    tpp_cmd_type_6C = 0x6C
    tpp_cmd_type_6B = 0x6B
    tpp_cmd_type_7B = 0x7B
    tpp_cmd_type_79 = 0x79
    tpp_cmd_type_6F = 0x6F
    tpp_cmd_type_7F = 0x7F
    tpp_cmd_type_7D = 0x7D
    tpp_cmd_type_6D = 0x6D

    tpp_cmd_type_80 = 0x80
    tpp_cmd_type_90 = 0x90
    tpp_cmd_type_92 = 0x92
    tpp_cmd_type_93 = 0x93
    tpp_cmd_type_94 = 0x94
    tpp_cmd_type_86 = 0x86
    tpp_cmd_type_96 = 0x96
    tpp_cmd_type_87 = 0x87
    tpp_cmd_type_97 = 0x97
    tpp_cmd_type_88 = 0x88
    tpp_cmd_type_98 = 0x98
    tpp_cmd_type_E1 = 0xE1
    tpp_cmd_type_F1 = 0xF1
    tpp_cmd_type_E2 = 0xE2
    tpp_cmd_type_F2 = 0xF2

    tpp_cmd_type_C1 = 0xC1
    tpp_cmd_type_D1 = 0xD1
    tpp_cmd_type_C2 = 0xC2
    tpp_cmd_type_D2 = 0xD2
    tpp_cmd_type_C3 = 0xC3
    tpp_cmd_type_D3 = 0xD3

    tpp_cmd_type_A3 = 0xA3
    tpp_cmd_type_B3 = 0xB3

    tpp_cmd_type_A1 = 0xA1
    tpp_cmd_type_B1 = 0xB1
    tpp_cmd_type_A2 = 0xA2
    tpp_cmd_type_B2 = 0xB2
    tpp_cmd_type_B9 = 0xB9


def tpp_cmd_41(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  # 保留字节
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  # 类型：设置
            "storage_cap_limit": hex_to_info(data[4:8], Encode_type.BIN.value),  # 设置参数启始地址
            "param_cap_limit": hex_to_info(data[8:12], Encode_type.BIN.value),  # 设置参数的个数
            "battery_cap_limit": hex_to_info(data[12:16], Encode_type.BIN.value),  # 设置参数的字节数
            "charge_cap_limit": hex_to_info(data[16:20], Encode_type.BIN.value),  # 设置参数的数据
            "sign_interval": hex_to_info(data[20:24], Encode_type.BIN.value),  # 设置参数的数据
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_41.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_41: {data}")
            HSyslog.log_info(f"tpp_cmd_41: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_41 error: .{data} .{e}")
        return {}


def tpp_cmd_51(data: dict):
    cmd_id = data.get("cmd_id", 0)  #
    cmd_nums = data.get("cmd_nums", 0)
    result = data.get("result")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_51: {data}")
            HSyslog.log_info(f"tpp_cmd_51: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_51.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_51 error: .{data} .{e}")
        return []


def tpp_cmd_42(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "system_time": hex_to_info(data[4:12], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_42.value, info])
        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_42: {data}")
            HSyslog.log_info(f"tpp_cmd_42: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_42 error: .{data} .{e}")
        return {}


def tpp_cmd_52(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    system_time = data.get("system_time")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(system_time, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_52: {data}")
            HSyslog.log_info(f"tpp_cmd_52: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_52.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_52 error: .{data} .{e}")
        return []


def tpp_cmd_46(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:12], Encode_type.BCD.value),
            "device_type": hex_to_info(data[12], Encode_type.BIN.value),  #
            "battery_type": hex_to_info(data[13], Encode_type.BIN.value),
            "gun_num": hex_to_info(data[14], Encode_type.BIN.value),  #
            "server_host": hex_to_info(data[15:19], Encode_type.IP.value),
            "server_port": hex_to_info(data[19:21], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_46.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_46: {data}")
            HSyslog.log_info(f"tpp_cmd_46: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_46 error: .{data} .{e}")
        return {}


def tpp_cmd_56(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    result = data.get("result")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_56: {data}")
            HSyslog.log_info(f"tpp_cmd_56: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_56.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_56 error: .{data} .{e}")
        return []


def tpp_cmd_48(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "heart_index": hex_to_info(data[4:6], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_48.value, info])

        if IS_DEBUG:
            pass
            # HSyslog.log_info(f"tpp_cmd_48: {data}")
            # HSyslog.log_info(f"tpp_cmd_48: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_48 error: .{data} .{e}")
        return {}


def tpp_cmd_58(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    heart_index = data.get("heart_index")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(heart_index, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            pass
            # HSyslog.log_info(f"tpp_cmd_58: {data}")
            # HSyslog.log_info(f"tpp_cmd_58: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_58.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_58 error: .{data} .{e}")
        return []


def tpp_cmd_49(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "heart_interval": hex_to_info(data[4], Encode_type.BIN.value),
            "heart_timeout_num": hex_to_info(data[5], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_49.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_49: {data}")
            HSyslog.log_info(f"tpp_cmd_49: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_49 error: .{data} .{e}")
        return {}


def tpp_cmd_59(data: dict):
    reserved = data.get("reserved", 0)
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    heart_interval = data.get("heart_interval")
    heart_timeout_num = data.get("heart_timeout_num")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(heart_interval, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(heart_timeout_num, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_59: {data}")
            HSyslog.log_info(f"tpp_cmd_59: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_59.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_59 error: .{data} .{e}")
        return []


def tpp_cmd_40(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "input_card": hex_to_info(data[4], Encode_type.BIN.value),
            "input_password": hex_to_info(data[5], Encode_type.BIN.value),
            "charge_inquiry_service": hex_to_info(data[6], Encode_type.BIN.value),
            "input_car_card": hex_to_info(data[7], Encode_type.BIN.value),
            "door_unlock": hex_to_info(data[8], Encode_type.BIN.value),
            "connect_charge": hex_to_info(data[9], Encode_type.BIN.value),
            "charge_mode": hex_to_info(data[10], Encode_type.BIN.value),
            "start_charge": hex_to_info(data[11], Encode_type.BIN.value),
            "stop_charge_card": hex_to_info(data[12], Encode_type.BIN.value),
            "unconnect_charge": hex_to_info(data[13], Encode_type.BIN.value),
            "door_lock": hex_to_info(data[14], Encode_type.BIN.value),
            "charge_cost_account": hex_to_info(data[15], Encode_type.BIN.value),
            "print_receipt": hex_to_info(data[16], Encode_type.BIN.value),
            "query": hex_to_info(data[17], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_40.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_40: {data}")
            HSyslog.log_info(f"tpp_cmd_40: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_40 error: .{data} .{e}")
        return {}


def tpp_cmd_50(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    result = data.get("result")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_50: {data}")
            HSyslog.log_info(f"tpp_cmd_50: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_50.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_50 error: .{data} .{e}")
        return []


def tpp_cmd_43(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "reboot": hex_to_info(data[4], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_43.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_43: {data}")
            HSyslog.log_info(f"tpp_cmd_43: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_43 error: .{data} .{e}")
        return {}


def tpp_cmd_53(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    reboot = data.get("reboot")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(reboot, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_53: {data}")
            HSyslog.log_info(f"tpp_cmd_53: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_53.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_53 error: .{data} .{e}")
        return []


def tpp_cmd_01(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_01.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_01: {data}")
            HSyslog.log_info(f"tpp_cmd_01: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_01 error: .{data} .{e}")
        return {}


def tpp_cmd_10(data: dict):
    device_id = data.get("device_id")
    device_sn = data.get("device_sn")
    device_version = data.get("device_version")
    boot_num = data.get("boot_num")
    flash_room = data.get("flash_room")
    device_run_time = data.get("device_run_time")
    start_date = data.get("start_time")
    sign_date = data.get("sign_time")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(device_sn, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(device_version, 4, Encode_type.VERSION.value)
        tpp_cmd_msg += info_to_hex(boot_num, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(flash_room, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_run_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(sign_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_10: {data}")
            HSyslog.log_info(f"tpp_cmd_10: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_10.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_10 error: .{data} .{e}")
        return []


def tpp_cmd_11(data: dict):
    device_id = data.get("device_id")
    work_status = data.get("work_status")
    system_fault_code = data.get("system_fault_code")
    device_1 = data.get("device_1")
    device_2 = data.get("device_2")
    device_3 = data.get("device_3")
    device_4 = data.get("device_4")
    device_5 = data.get("device_5")
    device_6 = data.get("device_6")
    device_7 = data.get("device_7")
    device_8 = data.get("device_8")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(work_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(system_fault_code, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_1, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_2, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_3, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_4, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_5, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_6, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_7, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_8, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_11: {data}")
            HSyslog.log_info(f"tpp_cmd_11: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_11.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_11 error: .{data} .{e}")
        return []


def tpp_cmd_05(data: list):
    try:
        param_num = hex_to_info(data[5], Encode_type.BIN.value)
        param_list = []
        for i in range(0, param_num * 3, 3):
            param_info = {
                "param_no": hex_to_info(data[6 + i], Encode_type.BIN.value),
                "param": hex_to_info(data[6 + i + 1:6 + i + 3], Encode_type.BIN.value)
            }
            param_list.append(param_info)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "param_type": hex_to_info(data[4], Encode_type.BIN.value),
            "param_num": param_num,
            "param_list": param_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_05.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_05: {data}")
            HSyslog.log_info(f"tpp_cmd_05: {info}")
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_05 error: .{data} .{e}")
        return {}


def tpp_cmd_15(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    param_type = data.get("param_type")
    param_num = data.get("param_num")
    param_list = data.get("param_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(param_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(param_num, 1, Encode_type.BIN.value)
        for param_info in param_list:
            tpp_cmd_msg += info_to_hex(param_info.get("param_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(param_info.get("param"), 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_15: {data}")
            HSyslog.log_info(f"tpp_cmd_15: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_15.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_15 error: .{data} .{e}")
        return []


def tpp_cmd_07(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        charge_mode = []
        for i in range(0, gun_num):
            charge_mode.append(hex_to_info(data[5 + i], Encode_type.BIN.value))
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "charge_mode": charge_mode,  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_07.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_07: {data}")
            HSyslog.log_info(f"tpp_cmd_07: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_07 error: .{data} .{e}")
        return {}


def tpp_cmd_17(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    power_model_list = data.get("power_model_list")
    reserved = data.get("reserved", 0)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for power_model_info in power_model_list:
            tpp_cmd_msg += info_to_hex(power_model_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("gun_max_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("gun_min_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("gun_max_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("gun_max_single_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_max_temperature"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_allow_charge"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_need_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_need_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_need_single_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_max_battery_temperature"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_sdk_version"), 3, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_battery_num"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_battery_series"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_battery_parallel"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_info.get("bms_battery_cap"), 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_17: {data}")
            HSyslog.log_info(f"tpp_cmd_17: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_17.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_17 error: .{data} .{e}")
        return []


def tpp_cmd_08(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        charge_mode = []
        for i in range(0, gun_num):
            charge_mode.append(hex_to_info(data[5 + i], Encode_type.BIN.value))
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,
            "charge_mode": charge_mode
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_08.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_08: {data}")
            HSyslog.log_info(f"tpp_cmd_08: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_08 error: .{data} .{e}")
        return {}


def tpp_cmd_18(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    battery_list = data.get("param_list")
    reserved = data.get("reserved", 0x0F)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for battery_info in battery_list:
            tpp_cmd_msg += info_to_hex(battery_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(battery_info.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(battery_info.get("bms_id"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(battery_info.get("bms_battery_num"), 1, Encode_type.BIN.value)
            bms_battery_list = battery_info.get("bms_battery_list")
            for bms_battery_info in bms_battery_list:
                tpp_cmd_msg += info_to_hex(bms_battery_info.get("battery_id"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_18: {data}")
            HSyslog.log_info(f"tpp_cmd_18: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_18.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_18 error: .{data} .{e}")
        return []


def tpp_cmd_09(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:12], Encode_type.BCD.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_09.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_09: {data}")
            HSyslog.log_info(f"tpp_cmd_09: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_09 error: .{data} .{e}")
        return {}


def tpp_cmd_0A(data: list):
    try:
        cmd_param = hex_to_info(data[4], Encode_type.BIN.value)
        if cmd_param in [1, 4, 5, 6]:
            info = {
                "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
                "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
                "cmd_param": cmd_param,  #
                "cmd_data": hex_to_info(data[5:105], Encode_type.GB2312.value),  #
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_0A.value, info])
        elif cmd_param in [2, 3, 7, 8]:
            info = {
                "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
                "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
                "cmd_param": cmd_param,  #
                "cmd_data": hex_to_info(data[5:105], Encode_type.ASCII.value),  #
            }
            tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_0A.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_0A: {data}")
            HSyslog.log_info(f"tpp_cmd_0A: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_0A error: .{data} .{e}")
        return {}


def tpp_cmd_1A(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    cmd_param = data.get("cmd_param")
    cmd_data = data.get("cmd_data")
    result = data.get("result")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_param, 1, Encode_type.BIN.value)
        if cmd_param in [1, 4, 5, 6]:
            tpp_cmd_msg += info_to_hex(cmd_data, 100, Encode_type.GB2312.value)
        elif cmd_param in [2, 3, 7, 8]:
            tpp_cmd_msg += info_to_hex(cmd_data, 100, Encode_type.ASCII.value)
        else:
            tpp_cmd_msg += info_to_hex(0x00, 100, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_1A: {data}")
            HSyslog.log_info(f"tpp_cmd_1A: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_1A.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_1A error: .{data} .{e}")
        return []


def tpp_cmd_E0(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "report_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "report_interval": hex_to_info(data[5], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_E0.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_E0: {data}")
            HSyslog.log_info(f"tpp_cmd_E0: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_E0 error: .{data} .{e}")
        return {}


def tpp_cmd_F0(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    report_mode = data.get("report_mode")
    report_interval = data.get("report_interval")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(report_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(report_interval, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_F0: {data}")
            HSyslog.log_info(f"tpp_cmd_F0: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_F0.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_F0 error: .{data} .{e}")
        return []


def tpp_cmd_21(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_21.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_21: {data}")
            HSyslog.log_info(f"tpp_cmd_21: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_21 error: .{data} .{e}")
        return {}


def tpp_cmd_31(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    input_power = data.get("input_power")
    average_temperature = data.get("average_temperature")
    out_temperature = data.get("out_temperature")
    work_status = data.get("work_status")
    power_model_num = data.get("power_model_num")
    output_active_power = data.get("output_active_power")
    output_wattless_power = data.get("output_wattless_power")
    device_status = data.get("device_status")
    device_fault_code = data.get("device_fault_code")
    model_fault_status = data.get("model_fault_status")
    fan_status = data.get("fan_status")
    air_status = data.get("air_status")
    heater_status = data.get("heater_status")
    smoke_status = data.get("smoke_status")
    shake_status = data.get("shake_status")
    gun_num = data.get("gun_num")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(input_power, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(average_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(out_temperature, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(work_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(power_model_num, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(output_active_power, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(output_wattless_power, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_fault_code, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(model_fault_status, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(fan_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(air_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(heater_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(smoke_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(shake_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_31: {data}")
            HSyslog.log_info(f"tpp_cmd_31: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_31.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_31 error: .{data} .{e}")
        return []


def tpp_cmd_22(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        charge_mode = []
        for i in range(0, gun_num):
            gun_status = hex_to_info(data[5 + i], Encode_type.BIN.value)
            charge_mode.append(gun_status)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "charge_mode": charge_mode,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_22.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_22: {data}")
            HSyslog.log_info(f"tpp_cmd_22: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_22 error: .{data} .{e}")
        return {}


def tpp_cmd_32(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status_info in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("gun_status"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("bms_id"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("max_single_vol"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("min_single_vol"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("max_temperature"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("min_temperature"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("max_single_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("min_single_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("max_temperature_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("min_temperature_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("SOH1"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("SOC1"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("gun_work_status"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_32: {data}")
            HSyslog.log_info(f"tpp_cmd_32: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_32.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_32 error: .{data} .{e}")
        return []


def tpp_cmd_23(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        charge_mode = []
        for i in range(0, gun_num):
            gun_status = hex_to_info(data[5 + i], Encode_type.BIN.value)
            charge_mode.append(gun_status)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "charge_mode": charge_mode,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_23.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_23: {data}")
            HSyslog.log_info(f"tpp_cmd_23: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_23 error: .{data} .{e}")
        return {}


def tpp_cmd_33(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status_info in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_time"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_now_soc"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_33: {data}")
            HSyslog.log_info(f"tpp_cmd_33: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_33.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_33 error: .{data} .{e}")
        return []


def tpp_cmd_24(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        charge_mode = []
        for i in range(0, gun_num):
            gun_status = hex_to_info(data[5 + i], Encode_type.BIN.value)
            charge_mode.append(gun_status)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "charge_mode": charge_mode,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_24.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_24: {data}")
            HSyslog.log_info(f"tpp_cmd_24: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_24 error: .{data} .{e}")
        return {}


def tpp_cmd_34(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status_info in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_carry_status"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("power_model_id"), 8, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("bms_id"), 8, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_power_kw"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("power_model_fault_code"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_status"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_34: {data}")
            HSyslog.log_info(f"tpp_cmd_34: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_34.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_34 error: .{data} .{e}")
        return []


def tpp_cmd_25(data: list):
    try:
        gun_num = hex_to_info(data[4], Encode_type.BIN.value)
        gun_status_list = []
        for i in range(0, gun_num):
            gun_status = hex_to_info(data[5 + i], Encode_type.BIN.value)
            gun_status_list.append(gun_status)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "gun_status_list": gun_status_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_25.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_25: {data}")
            HSyslog.log_info(f"tpp_cmd_25: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_25 error: .{data} .{e}")
        return {}


def tpp_cmd_35(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status_info in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_fault_group_id"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_fault_grade"), 1, Encode_type.BIN.value)
            for battery_fault_info in gun_status_info.get("battery_fault_list"):
                tpp_cmd_msg += info_to_hex(battery_fault_info.get("battery_fault_code"), 2, Encode_type.BIN.value)
                tpp_cmd_msg += info_to_hex(battery_fault_info.get("battery_fault_num"), 1, Encode_type.BIN.value)
                for battery_fault_location in battery_fault_info.get("battery_fault_location_list"):
                    tpp_cmd_msg += info_to_hex(battery_fault_location, 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(0xFF, 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_system_fault_group_id"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_system_fault_grade"), 1, Encode_type.BIN.value)
            for battery_system_fault_info in gun_status_info.get("battery_system_fault_list"):
                tpp_cmd_msg += info_to_hex(battery_system_fault_info.get("battery_system_fault_code"), 2, Encode_type.BIN.value)
                tpp_cmd_msg += info_to_hex(battery_system_fault_info.get("battery_system_fault_num"), 1, Encode_type.BIN.value)
                for battery_system_fault_location in battery_system_fault_info.get("battery_system_fault_location_list"):
                    tpp_cmd_msg += info_to_hex(battery_system_fault_location, 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(0xFF, 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("bms_fault_group_id"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("bms_fault_grade"), 1, Encode_type.BIN.value)
            for bms_fault_info in gun_status_info.get("bms_fault_list"):
                tpp_cmd_msg += info_to_hex(bms_fault_info.get("bms_fault_code"), 2, Encode_type.BIN.value)
                tpp_cmd_msg += info_to_hex(bms_fault_info.get("bms_fault_num"), 1, Encode_type.BIN.value)
                for bms_fault_location in bms_fault_info.get("bms_fault_location_list"):
                    tpp_cmd_msg += info_to_hex(bms_fault_location, 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(0xFF, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_35: {data}")
            HSyslog.log_info(f"tpp_cmd_35: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_35.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_35 error: .{data} .{e}")
        return []


def tpp_cmd_26(data: list):
    try:
        gun_num = hex_to_info(data[5], Encode_type.BIN.value)
        battery_status_list = []
        for i in range(0, gun_num, 2):
            battery_status = {
                "charge_mode": hex_to_info(data[6 + i], Encode_type.BIN.value),
                "battery_no": hex_to_info(data[6 + i + 1], Encode_type.BIN.value),
            }
            battery_status_list.append(battery_status)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "cmd_type": hex_to_info(data[4], Encode_type.BIN.value),  #
            "gun_num": gun_num,  #
            "gun_status_list": battery_status_list,
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_26.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_26: {data}")
            HSyslog.log_info(f"tpp_cmd_26: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_26 error: .{data} .{e}")
        return {}


def tpp_cmd_36(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    cmd_type = data.get("cmd_type")
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status_info in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_id"), 8, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status_info.get("battery_num"), 1, Encode_type.BIN.value)
            for battery_no in gun_status_info.get("battery_list"):
                tpp_cmd_msg += info_to_hex(battery_no, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_36: {data}")
            HSyslog.log_info(f"tpp_cmd_36: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_36.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_36 error: .{data} .{e}")
        return []


def tpp_cmd_2B(data: list):
    try:
        power_model_num = hex_to_info(data[4], Encode_type.BIN.value)
        power_model_list = []
        for i in range(0, power_model_num):
            power_model_list.append(hex_to_info(data[4 + i], Encode_type.BIN.value))
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "power_model_num": power_model_num,
            "power_model_list": power_model_list,
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_2B: {data}")
            HSyslog.log_info(f"tpp_cmd_2B: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_2B.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_2B error: .{data} .{e}")
        return {}


def tpp_cmd_3B(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    power_model_num = data.get("power_model_num")
    power_model_list = data.get("power_model_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(power_model_num, 1, Encode_type.BIN.value)
        for power_model_status in power_model_list:
            tpp_cmd_msg += info_to_hex(power_model_status.get("power_model_no"), 1, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("meter_no"), 50, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("meter_num"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_active_power"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_wattless_power"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_power_factor"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_harmonic_factor"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_fault_status"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_distribution_fault_status"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_distribution_switch"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(power_model_status.get("input_distribution_insurance"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_3B: {data}")
            HSyslog.log_info(f"tpp_cmd_3B: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_3B.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_3B error: .{data} .{e}")
        return []


def tpp_cmd_39(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_time"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_now_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_meter"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_39: {data}")
            HSyslog.log_info(f"tpp_cmd_39: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_39.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_39 error: .{data} .{e}")
        return []


def tpp_cmd_3A(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_lock_status"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("bms_id"), 8, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("battery_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("battery_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("max_battery_single_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("min_battery_single_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("max_battery_temperature"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("min_battery_temperature"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("max_battery_single_no"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("min_battery_single_no"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("max_battery_temperature_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("min_battery_temperature_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("gun_temperature"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("SOC1"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("work_status"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_last_time"), 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_3A: {data}")
            HSyslog.log_info(f"tpp_cmd_3A: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_3A.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_3A error: .{data} .{e}")
        return []


def tpp_cmd_3F(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    gun_num = data.get("gun_num")
    gun_status_list = data.get("gun_status_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_num, 1, Encode_type.BIN.value)
        for gun_status in gun_status_list:
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_kwh_add"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_time"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_now_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_meter_num"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(gun_status.get("charge_meter_num_add"), 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_3F: {data}")
            HSyslog.log_info(f"tpp_cmd_3F: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_3F.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_3F error: .{data} .{e}")
        return []


def tpp_cmd_70(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    user_card_id = data.get("user_card_id")
    user_certificate_type = data.get("user_certificate_type")
    user_certificate_id = data.get("user_certificate_id")
    acceptance_channel = data.get("acceptance_channel")
    agency_id = data.get("agency_id")
    agency_code = data.get("agency_code")
    acceptance_operator_nums = data.get("acceptance_operator_nums")
    charge_date = data.get("charge_date")
    pay_password = data.get("pay_password")
    gun_id = data.get("gun_id")
    server_fee = data.get("server_fee")
    msg_code = data.get("msg_code")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(user_certificate_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_certificate_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_channel, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(agency_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(agency_code, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_operator_nums, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(pay_password, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(server_fee, 12, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(msg_code, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_70: {data}")
            HSyslog.log_info(f"tpp_cmd_70: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_70.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_70 error: .{data} .{e}")
        return []


def tpp_cmd_60(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "cmd_code": hex_to_info(data[4:10], Encode_type.ASCII.value),  #
            "cmd_code_decs": hex_to_info(data[10:110], Encode_type.GB2312.value),  #
            "user_code": hex_to_info(data[110:140], Encode_type.GB2312.value),  #
            "electricity_balance": hex_to_info(data[140:152], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[152:164], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[164:176], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[176:188], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[188:203], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[203:223], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[223:231], Encode_type.TIME.value),  #
            "msg_code": hex_to_info(data[231:239], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_60.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_60: {data}")
            HSyslog.log_info(f"tpp_cmd_60: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_60 error: .{data} .{e}")
        return {}


def tpp_cmd_71(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    user_card_id = data.get("user_card_id")
    charge_type = data.get("charge_type")
    charge_date = data.get("charge_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_71: {data}")
            HSyslog.log_info(f"tpp_cmd_71: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_71.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_71 error: .{data} .{e}")
        return []


def tpp_cmd_61(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[4:20], Encode_type.ASCII.value),  #
            "charge_type": hex_to_info(data[20], Encode_type.BIN.value),  #
            "charge_date": hex_to_info(data[21:29], Encode_type.TIME.value),  #
            "charge_id": hex_to_info(data[29:44], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[44:64], Encode_type.ASCII.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_61.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_61: {data}")
            HSyslog.log_info(f"tpp_cmd_61: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_61 error: .{data} .{e}")
        return {}


def tpp_cmd_72(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    power_model_num = data.get("power_model_num")
    charge_mode = data.get("charge_mode")
    battery_num = data.get("battery_num")
    battery_list = data.get("battery_list")
    charge_date = data.get("charge_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(power_model_num, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(battery_num, 1, Encode_type.BIN.value)
        for battery_id in battery_list:
            tpp_cmd_msg += info_to_hex(battery_id, 8, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_72: {data}")
            HSyslog.log_info(f"tpp_cmd_72: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_72.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_72 error: .{data} .{e}")
        return []


def tpp_cmd_62(data: list):
    try:
        battery_num = hex_to_info(data[6], Encode_type.BIN.value)
        battery_list = []
        for i in range(0, battery_num, 9):
            battery_info = {
                "battery_id": hex_to_info(data[7 + i: 7 + i + 8], Encode_type.BIN.value),
                "battery_type": hex_to_info(data[7 + i + 8], Encode_type.BIN.value),
            }
            battery_list.append(battery_info)
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "power_model_num": hex_to_info(data[4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[5], Encode_type.BIN.value),  #
            "battery_num": battery_num,  #
            "battery_list": battery_list,  #
            "charge_date": hex_to_info(data[battery_num * 9:battery_num * 9 + 8], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_62.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_62: {data}")
            HSyslog.log_info(f"tpp_cmd_62: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_62 error: .{data} .{e}")
        return {}


def tpp_cmd_73(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_mode = data.get("charge_mode")
    user_card_id = data.get("user_card_id")
    bms_id = data.get("bms_id")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_power_ah = data.get("charge_power_ah")
    charge_power_kwh = data.get("charge_power_kwh")
    charge_time = data.get("charge_time")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    is_normal_stop = data.get("is_normal_stop")
    charge_start_date = data.get("charge_start_date")
    charge_stop_date = data.get("charge_stop_date")
    charge_date = data.get("charge_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(bms_id, 8, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_ah, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy_param, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(is_normal_stop, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_stop_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_73: {data}")
            HSyslog.log_info(f"tpp_cmd_73: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_73.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_73 error: .{data} .{e}")
        return []


def tpp_cmd_63(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "user_code": hex_to_info(data[21:51], Encode_type.GB2312.value),  #
            "charge_time_balance": hex_to_info(data[51:63], Encode_type.ASCII.value),  #
            "electricity_balance": hex_to_info(data[63:75], Encode_type.ASCII.value),  #
            "server_cost": hex_to_info(data[75:87], Encode_type.BIN.value),  #
            "server_balance": hex_to_info(data[87:99], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[99:114], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[114:134], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[134:142], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_63.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_63: {data}")
            HSyslog.log_info(f"tpp_cmd_63: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_63 error: .{data} .{e}")
        return {}


def tpp_cmd_74(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    reserved = data.get("reserved", 0)
    user_card_id = data.get("user_card_id")
    query_record_num = data.get("query_record_num")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(query_record_num, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_74: {data}")
            HSyslog.log_info(f"tpp_cmd_74: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_74.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_74 error: .{data} .{e}")
        return []


def tpp_cmd_64(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "record_num": hex_to_info(data[21], Encode_type.BIN.value),  #
            "bms_id": hex_to_info(data[22:30], Encode_type.BIN.value),  #
            "charge_start_soc": hex_to_info(data[55], Encode_type.BIN.value),  #
            "charge_stop_soc": hex_to_info(data[56], Encode_type.BIN.value),  #
            "charge_power_ah": hex_to_info(data[57:59], Encode_type.BIN.value),  #
            "charge_power_kwh": hex_to_info(data[59:61], Encode_type.BIN.value),  #
            "charge_time": hex_to_info(data[61:65], Encode_type.BIN.value),  #
            "charge_policy": hex_to_info(data[65], Encode_type.BIN.value),  #
            "charge_policy_param": hex_to_info(data[66:68], Encode_type.BIN.value),  #
            "is_normal_stop": hex_to_info(data[68], Encode_type.BIN.value),  #
            "charge_start_date": hex_to_info(data[69:77], Encode_type.TIME.value),  #
            "charge_stop_date": hex_to_info(data[77:85], Encode_type.TIME.value),  #
            "charge_date": hex_to_info(data[93:101], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_64.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_64: {data}")
            HSyslog.log_info(f"tpp_cmd_64: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_64 error: .{data} .{e}")
        return {}


def tpp_cmd_75(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_mode = data.get("charge_mode")
    car_card = data.get("car_card")
    charge_date = data.get("charge_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_75: {data}")
            HSyslog.log_info(f"tpp_cmd_75: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_75.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_75 error: .{data} .{e}")
        return []


def tpp_cmd_65(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "car_card": hex_to_info(data[5:13], Encode_type.GB2312.value),  #
            "charge_date": hex_to_info(data[13:21], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_65.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_65: {data}")
            HSyslog.log_info(f"tpp_cmd_65: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_65 error: .{data} .{e}")
        return {}


def tpp_cmd_78(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_mode = data.get("charge_mode")
    user_card_id = data.get("user_card_id")
    device_id = data.get("device_id")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_power_ah = data.get("charge_power_ah")
    charge_power_kwh = data.get("charge_power_kwh")
    charge_time = data.get("charge_time")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    is_normal_stop = data.get("is_normal_stop")
    charge_start_date = data.get("charge_start_date")
    charge_stop_date = data.get("charge_stop_date")
    charge_date = data.get("charge_date")
    charge_start_meter = data.get("charge_start_meter")
    charge_stop_meter = data.get("charge_stop_meter")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_ah, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy_param, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(is_normal_stop, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_stop_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_start_meter, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_meter, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_78: {data}")
            HSyslog.log_info(f"tpp_cmd_78: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_78.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_78 error: .{data} .{e}")
        return []


def tpp_cmd_68(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "user_code": hex_to_info(data[21:51], Encode_type.GB2312.value),  #
            "charge_info": hex_to_info(data[51:63], Encode_type.BIN.value),  #
            "charge_electricity_cost": hex_to_info(data[63:75], Encode_type.BIN.value),  #
            "charge_server_cost": hex_to_info(data[75:87], Encode_type.BIN.value),  #
            "charge_cost": hex_to_info(data[87:99], Encode_type.BIN.value),  #
            "charge_id": hex_to_info(data[99:114], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[114:134], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[134:142], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_68.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_68: {data}")
            HSyslog.log_info(f"tpp_cmd_68: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_68 error: .{data} .{e}")
        return {}


def tpp_cmd_69(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "user_name": hex_to_info(data[21:41], Encode_type.GB2312.value),  #
            "cmd_code": hex_to_info(data[41:71], Encode_type.BIN.value),  #
            "cmd_code_desc": hex_to_info(data[71:135], Encode_type.GB2312.value),  #
            "user_code": hex_to_info(data[135:165], Encode_type.GB2312.value),  #
            "electricity_balance": hex_to_info(data[165:177], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[177:189], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[189:201], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[201:213], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[213:228], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[228:248], Encode_type.ASCII.value),  #
            "charge_allow_power_kw": hex_to_info(data[248:252], Encode_type.BIN.value),  #
            "charge_allow_time": hex_to_info(data[252:256], Encode_type.BIN.value),  #
            "charge_date": hex_to_info(data[256:264], Encode_type.TIME.value),  #
            "msg_code": hex_to_info(data[264:272], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_69.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_69: {data}")
            HSyslog.log_info(f"tpp_cmd_69: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_69 error: .{data} .{e}")
        return {}


def tpp_cmd_7A(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    user_card_id = data.get("user_card_id")
    user_certificate_type = data.get("user_certificate_type")
    user_certificate_id = data.get("user_certificate_id")
    acceptance_channel = data.get("acceptance_channel")
    agency_id = data.get("agency_id")
    agency_code = data.get("agency_code")
    acceptance_operator_nums = data.get("acceptance_operator_nums")
    charge_date = data.get("charge_date")
    gun_id = data.get("gun_id")
    result = data.get("result")
    msg_code = data.get("msg_code")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(user_certificate_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_certificate_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_channel, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(agency_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(agency_code, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_operator_nums, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(msg_code, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_7A: {data}")
            HSyslog.log_info(f"tpp_cmd_7A: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_7A.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_7A error: .{data} .{e}")
        return []


def tpp_cmd_6A(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "user_code": hex_to_info(data[21:51], Encode_type.GB2312.value),  #
            "electricity_balance": hex_to_info(data[51:63], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[63:75], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[75:87], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[87:99], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[99:114], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[114:134], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[134:142], Encode_type.TIME.value),  #
            "gun_id": hex_to_info(data[142], Encode_type.BIN.value),  #
            "charge_policy": hex_to_info(data[143], Encode_type.BIN.value),  #
            "charge_policy_plan_time": hex_to_info(data[144:148], Encode_type.BIN.value),  #
            "charge_policy_plan_kw": hex_to_info(data[148:152], Encode_type.BIN.value),  #
            "msg_code": hex_to_info(data[152:160], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_6A.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6A: {data}")
            HSyslog.log_info(f"tpp_cmd_6A: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_6A error: .{data} .{e}")
        return {}


def tpp_cmd_6C(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[4:20], Encode_type.ASCII.value),  #
            "charge_nums": hex_to_info(data[20:28], Encode_type.BIN.value),  #
            "user_code": hex_to_info(data[28:58], Encode_type.GB2312.value),  #
            "electricity_balance": hex_to_info(data[58:70], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[70:82], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[82:94], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[94:106], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[106:121], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[121:141], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[141:149], Encode_type.TIME.value),  #
            "gun_id": hex_to_info(data[149], Encode_type.BIN.value),  #
            "charge_policy_mode": hex_to_info(data[150], Encode_type.BIN.value),  #
            "charge_policy_plan_time": hex_to_info(data[151:155], Encode_type.BIN.value),  #
            "charge_policy_plan_kw": hex_to_info(data[155:159], Encode_type.BIN.value),  #
            "msg_code": hex_to_info(data[159:167], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_6C.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6C: {data}")
            HSyslog.log_info(f"tpp_cmd_6C: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_6C error: .{data} .{e}")
        return {}


def tpp_cmd_6B(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "charge_nums": hex_to_info(data[21:29], Encode_type.BIN.value),  #
            "charge_date": hex_to_info(data[29:37], Encode_type.TIME.value),  #
            "msg_code": hex_to_info(data[37:45], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_6B.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6B: {data}")
            HSyslog.log_info(f"tpp_cmd_6B: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_6C error: .{data} .{e}")
        return {}


def tpp_cmd_7B(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    user_card_id = data.get("user_card_id")
    device_id = data.get("device_id")
    charge_date = data.get("charge_date")
    msg_code = data.get("msg_code")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(msg_code, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_7B: {data}")
            HSyslog.log_info(f"tpp_cmd_7B: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_7B.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_7B error: .{data} .{e}")
        return []


def tpp_cmd_79(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_mode = data.get("charge_mode")
    user_card_id = data.get("user_card_id")
    charge_id = data.get("charge_id")
    charge_book_id = data.get("charge_book_id")
    device_id = data.get("device_id")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_power_ah = data.get("charge_power_ah")
    charge_power_kwh = data.get("charge_power_kwh")
    charge_power_kwh_add = data.get("charge_power_kwh_add")
    charge_time = data.get("charge_time")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    is_normal_stop = data.get("is_normal_stop")
    charge_start_date = data.get("charge_start_date")
    charge_stop_date = data.get("charge_stop_date")
    charge_date = data.get("charge_date")
    charge_start_meter = data.get("charge_start_meter")
    charge_start_meter_add = data.get("charge_start_meter_add")
    charge_stop_meter = data.get("charge_stop_meter")
    charge_stop_meter_add = data.get("charge_stop_meter_add")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_id, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_book_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_ah, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh_add, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy_param, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(is_normal_stop, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_stop_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_start_meter, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_meter_add, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_meter, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_meter_add, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_79: {data}")
            HSyslog.log_info(f"tpp_cmd_79: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_7F.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_79 error: .{data} .{e}")
        return []


def tpp_cmd_6F(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "charge_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "user_code": hex_to_info(data[21:51], Encode_type.GB2312.value),  #
            "charge_info": hex_to_info(data[51:69], Encode_type.GB2312.value),  #
            "charge_electricity_cost": hex_to_info(data[69:81], Encode_type.ASCII.value),  #
            "charge_server_cost": hex_to_info(data[81:93], Encode_type.ASCII.value),  #
            "charge_cost": hex_to_info(data[93:105], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[105:120], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[120:140], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[140:148], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_6F.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6F: {data}")
            HSyslog.log_info(f"tpp_cmd_6F: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_6F error: .{data} .{e}")
        return {}


def tpp_cmd_7F(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_mode = data.get("charge_mode")
    user_card_id = data.get("user_card_id")
    charge_id = data.get("charge_id")
    charge_book_id = data.get("charge_book_id")
    device_id = data.get("device_id")
    car_vin = data.get("car_vin")
    car_card = data.get("car_card")
    charge_start_soc = data.get("charge_start_soc")
    charge_stop_soc = data.get("charge_stop_soc")
    charge_power_ah = data.get("charge_power_ah")
    charge_power_kwh = data.get("charge_power_kwh")
    charge_power_kwh_add = data.get("charge_power_kwh_add")
    charge_time = data.get("charge_time")
    charge_policy = data.get("charge_policy")
    charge_policy_param = data.get("charge_policy_param")
    is_normal_stop = data.get("is_normal_stop")
    charge_start_date = data.get("charge_start_date")
    charge_stop_date = data.get("charge_stop_date")
    charge_date = data.get("charge_date")
    charge_start_meter = data.get("charge_start_meter")
    charge_start_meter_add = data.get("charge_start_meter_add")
    charge_stop_meter = data.get("charge_stop_meter")
    charge_stop_meter_add = data.get("charge_stop_meter_add")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_id, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_book_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(charge_start_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_ah, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_power_kwh_add, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_policy_param, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(is_normal_stop, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_stop_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_start_meter, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_start_meter_add, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_meter, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_stop_meter_add, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_7F: {data}")
            HSyslog.log_info(f"tpp_cmd_7F: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_7F.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_7F error: .{data} .{e}")
        return []


def tpp_cmd_7D(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    work_status = data.get("work_status")
    gun_id = data.get("gun_id")
    car_vin = data.get("car_vin")
    charge_date = data.get("charge_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(work_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(gun_id, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_vin, 17, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(charge_date, 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_7D: {data}")
            HSyslog.log_info(f"tpp_cmd_7D: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_7D.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_7D error: .{data} .{e}")
        return []


def tpp_cmd_6D(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "user_card_id": hex_to_info(data[4:20], Encode_type.ASCII.value),
            "cmd_code": hex_to_info(data[20:26], Encode_type.ASCII.value),
            "cmd_code_desc": hex_to_info(data[26:90], Encode_type.GB2312.value),
            "electricity_balance": hex_to_info(data[90:102], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[102:114], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[114:126], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[126:138], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[138: 153], Encode_type.ASCII.value),
            "charge_date": hex_to_info(data[153:161], Encode_type.TIME.value),
            "msg_code": hex_to_info(data[161:169], Encode_type.BIN.value),
            "is_stop_code": hex_to_info(data[169], Encode_type.BIN.value),
            "stop_code": hex_to_info(data[170:176], Encode_type.ASCII.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_6D.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_6D: {data}")
            HSyslog.log_info(f"tpp_cmd_6D: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_6D error: .{data} .{e}")
        return {}


def tpp_cmd_80(data: dict):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "charge_record_start": hex_to_info(data[4: 6], Encode_type.BIN.value),
            "charge_record_num": hex_to_info(data[6], Encode_type.BIN.value),
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_80.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_80: {data}")
            HSyslog.log_info(f"tpp_cmd_80: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_80 error: .{data} .{e}")
        return {}


def tpp_cmd_90(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_record_num = data.get("charge_record_num")
    charge_record_list = data.get("charge_record_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_record_num, 1, Encode_type.BIN.value)
        for charge_record_info in charge_record_list:
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_record_no"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("device_id"), 8, Encode_type.BCD.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("user_card_id"), 16, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_card"), 8, Encode_type.GB2312.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_time"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_policy"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("is_normal_stop"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_date"), 8, Encode_type.TIME.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_90: {data}")
            HSyslog.log_info(f"tpp_cmd_90: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_90.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_90 error: .{data} .{e}")
        return []


def tpp_cmd_92(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_record_num = data.get("charge_record_num")
    charge_record_list = data.get("charge_record_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_record_num, 1, Encode_type.BIN.value)
        for charge_record_info in charge_record_list:
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_record_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("device_id"), 8, Encode_type.BCD.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("user_card_id"), 16, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_card"), 8, Encode_type.GB2312.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_time"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_policy"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("is_normal_stop"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_meter"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_meter"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_92: {data}")
            HSyslog.log_info(f"tpp_cmd_92: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_92.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_92 error: .{data} .{e}")
        return []


def tpp_cmd_93(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_record_num = data.get("charge_record_num")
    charge_record_list = data.get("charge_record_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_record_num, 1, Encode_type.BIN.value)
        for charge_record_info in charge_record_list:
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_record_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("device_id"), 8, Encode_type.BCD.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("user_card_id"), 16, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_id"), 15, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_book_id"), 20, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_card"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_time"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_policy"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("is_normal_stop"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_meter"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_meter"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_93: {data}")
            HSyslog.log_info(f"tpp_cmd_93: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_93.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_93 error: .{data} .{e}")
        return []


def tpp_cmd_94(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    charge_record_num = data.get("charge_record_num")
    charge_record_list = data.get("charge_record_list")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_record_num, 1, Encode_type.BIN.value)
        for charge_record_info in charge_record_list:
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_record_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("device_id"), 8, Encode_type.BCD.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("user_card_id"), 16, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_id"), 15, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_book_id"), 20, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_vin"), 17, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("car_card"), 8, Encode_type.GB2312.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_ah"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_power_kwh_add"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_time"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_policy"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("is_normal_stop"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_date"), 8, Encode_type.TIME.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_meter"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_start_meter_add"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_meter"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(charge_record_info.get("charge_stop_meter_add"), 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_94: {data}")
            HSyslog.log_info(f"tpp_cmd_94: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_94.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_94 error: .{data} .{e}")
        return []


def tpp_cmd_86(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "start_date": hex_to_info(data[4:12], Encode_type.TIME.value),
            "stop_date": hex_to_info(data[12:20], Encode_type.TIME.value),
            "query_type": hex_to_info(data[20], Encode_type.BIN.value),
            "query_num": hex_to_info(data[21:23], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_86: {data}")
            HSyslog.log_info(f"tpp_cmd_86: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_86.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_86 error: .{data} .{e}")
        return {}


def tpp_cmd_96(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    query_type = data.get("query_type")
    query_num = data.get("query_num")
    query_list = data.get("query_list")
    reserved = data.get("reserved", 0xFF)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(query_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_num, 1, Encode_type.BIN.value)
        for query_info in query_list:
            tpp_cmd_msg += info_to_hex(query_info.get("query_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("year"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("mouth"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("day"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("hour"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("minute"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("seconds"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("type_code"), 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_96: {data}")
            HSyslog.log_info(f"tpp_cmd_96: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_96.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_96 error: .{data} .{e}")
        return []


def tpp_cmd_87(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "start_date": hex_to_info(data[4:12], Encode_type.TIME.value),
            "stop_date": hex_to_info(data[12:20], Encode_type.TIME.value),
            "query_type": hex_to_info(data[20], Encode_type.BIN.value),
            "query_num": hex_to_info(data[21:23], Encode_type.BIN.value),
        }
        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_87: {data}")
            HSyslog.log_info(f"tpp_cmd_87: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_87.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_87 error: .{data} .{e}")
        return {}


def tpp_cmd_97(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    query_type = data.get("query_type")
    query_num = data.get("query_num")
    query_list = data.get("query_list")
    reserved = data.get("reserved", 0xFF)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(query_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_num, 1, Encode_type.BIN.value)
        for query_info in query_list:
            tpp_cmd_msg += info_to_hex(query_info.get("query_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("year"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("mouth"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("day"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("hour"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("minute"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("seconds"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("power_mode_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("fault_code"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_97: {data}")
            HSyslog.log_info(f"tpp_cmd_97: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_97.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_97 error: .{data} .{e}")
        return []


def tpp_cmd_88(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "start_date": hex_to_info(data[4:12], Encode_type.TIME.value),
            "stop_date": hex_to_info(data[12:20], Encode_type.TIME.value),
            "query_type": hex_to_info(data[20], Encode_type.BIN.value),
            "query_num": hex_to_info(data[21:23], Encode_type.BIN.value),
        }
        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_88: {data}")
            HSyslog.log_info(f"tpp_cmd_88: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_88.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_88 error: .{data} .{e}")
        return {}


def tpp_cmd_98(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    query_type = data.get("query_type")
    query_num = data.get("query_num")
    query_list = data.get("query_list")
    reserved = data.get("reserved", 0xFF)

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(query_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_num, 1, Encode_type.BIN.value)
        for query_info in query_list:
            tpp_cmd_msg += info_to_hex(query_info.get("query_no"), 4, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("year"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("mouth"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("day"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("hour"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("minute"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("seconds"), 1, Encode_type.BIN.value)

            tpp_cmd_msg += info_to_hex(query_info.get("device_id"), 8, Encode_type.BCD.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_mode"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("max_charge_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("min_charge_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("max_charge_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("power_kwh"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("power_ah"), 2, Encode_type.BIN.value)

            tpp_cmd_msg += info_to_hex(query_info.get("charge_time"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_start_soc"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_now_soc"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("gun_connect_status"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_cur"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("charge_output_power_kw"), 2, Encode_type.BIN.value)

            tpp_cmd_msg += info_to_hex(query_info.get("sdk_version"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(query_info.get("potevio_sdk_versoin"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_cap"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_num"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_parallel"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_series"), 2, Encode_type.BIN.value)

            tpp_cmd_msg += info_to_hex(query_info.get("sdk_version"), 8, Encode_type.ASCII.value)
            tpp_cmd_msg += info_to_hex(query_info.get("potevio_sdk_versoin"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_cap"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_vol"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_num"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_parallel"), 2, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("battery_series"), 2, Encode_type.BIN.value)

            tpp_cmd_msg += info_to_hex(reserved, 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("power_mode_no"), 1, Encode_type.BIN.value)
            tpp_cmd_msg += info_to_hex(query_info.get("fault_code"), 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_98: {data}")
            HSyslog.log_info(f"tpp_cmd_98: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_98.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_98 error: .{data} .{e}")
        return []


def tpp_cmd_E1(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "ctrl_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "data_type": hex_to_info(data[5], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_E1.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_E1: {data}")
            HSyslog.log_info(f"tpp_cmd_E1: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_E1 error: .{data} .{e}")
        return {}


def tpp_cmd_F1(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    ctrl_mode = data.get("ctrl_mode")
    data_type = data.get("data_type")
    record_num = data.get("record_num")
    record_max_nums = data.get("record_max_nums")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(data_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(record_num, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(record_max_nums, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_F1: {data}")
            HSyslog.log_info(f"tpp_cmd_F1: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_F1.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_F1 error: .{data} .{e}")
        return []


def tpp_cmd_E2(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "ctrl_mode": hex_to_info(data[4], Encode_type.BIN.value),  #
            "data_type": hex_to_info(data[5], Encode_type.BIN.value),  #
            "data_ctrl_mode": hex_to_info(data[6], Encode_type.BIN.value),  #
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_E2: {data}")
            HSyslog.log_info(f"tpp_cmd_E2: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_E2.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_E2 error: .{data} .{e}")
        return {}


def tpp_cmd_F2(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    ctrl_mode = data.get("ctrl_mode")
    data_type = data.get("data_type")
    data_ctrl_mode = data.get("data_ctrl_mode")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(data_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(data_ctrl_mode, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_F2: {data}")
            HSyslog.log_info(f"tpp_cmd_F2: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_F2.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_F2 error: .{data} .{e}")
        return []


def tpp_cmd_C1(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
            "charge_book_id": hex_to_info(data[4:24], Encode_type.ASCII.value),
            "book_date": hex_to_info(data[24:32], Encode_type.TIME.value),
            "book_start_date": hex_to_info(data[32:40], Encode_type.TIME.value),
            "book_ctrl": hex_to_info(data[40], Encode_type.BIN.value),
            "book_time": hex_to_info(data[41:43], Encode_type.BIN.value),
            "book_car_card": hex_to_info(data[43:51], Encode_type.GB2312.value),
            "book_card_id": hex_to_info(data[51:67], Encode_type.ASCII.value),
            "book_mode": hex_to_info(data[67], Encode_type.BIN.value),
            "user_name": hex_to_info(data[68:88], Encode_type.GB2312.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_C1: {data}")
            HSyslog.log_info(f"tpp_cmd_C1: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_C1.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_C1 error: .{data} .{e}")
        return {}


def tpp_cmd_D1(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    book_date = data.get("book_date")
    book_start_date = data.get("book_start_date")
    book_ctrl = data.get("book_ctrl")
    book_time = data.get("book_time")
    book_car_card = data.get("book_car_card")
    book_card_id = data.get("book_card_id")
    book_mode = data.get("book_mode")
    user_name = data.get("user_name")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(book_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(book_ctrl, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_time, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_car_card, 8, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(book_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(book_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_name, 20, Encode_type.GB2312.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_D1: {data}")
            HSyslog.log_info(f"tpp_cmd_D1: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_D1.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_D1 error: .{data} .{e}")
        return []


def tpp_cmd_C2(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_C2: {data}")
            HSyslog.log_info(f"tpp_cmd_C2: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_C2.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_C2 error: .{data} .{e}")
        return {}


def tpp_cmd_D2(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    book_date = data.get("book_date")
    book_start_date = data.get("book_start_date")
    book_ctrl = data.get("book_ctrl")
    book_time = data.get("book_time")
    book_car_card = data.get("book_car_card")
    book_card_id = data.get("book_card_id")
    book_mode = data.get("book_mode")
    user_name = data.get("user_name")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(book_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(book_ctrl, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_time, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(book_car_card, 8, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(book_card_id, 16, Encode_type.GB2312.value)
        tpp_cmd_msg += info_to_hex(book_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_name, 20, Encode_type.GB2312.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_D2: {data}")
            HSyslog.log_info(f"tpp_cmd_D2: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_D2.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_D2 error: .{data} .{e}")
        return []


def tpp_cmd_C3(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),
        }

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_C3: {data}")
            HSyslog.log_info(f"tpp_cmd_C3: {info}")

        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_C3.value, info])
        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_C3 error: .{data} .{e}")
        return {}


def tpp_cmd_D3(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    system_date = data.get("system_date")
    query_mode = data.get("query_mode")
    query_time = data.get("query_time")
    query_status = data.get("query_status")
    query_param_type = data.get("query_param_type")
    car_long = data.get("car_long")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(system_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(query_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_time, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(query_param_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_long, 4, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_D3: {data}")
            HSyslog.log_info(f"tpp_cmd_D3: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_D3.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_D3 error: .{data} .{e}")
        return []


def tpp_cmd_A3(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "ota_host": hex_to_info(data[4:24], Encode_type.ASCII.value),  #
            "ota_port": hex_to_info(data[24:29], Encode_type.ASCII.value),  #
            "log_host": hex_to_info(data[29:49], Encode_type.ASCII.value),  #
            "log_port": hex_to_info(data[49:54], Encode_type.ASCII.value),  #
            "ota_user_id": hex_to_info(data[54:74], Encode_type.ASCII.value),  #
            "ota_password": hex_to_info(data[74:94], Encode_type.ASCII.value),  #
            "ota_device_mode": hex_to_info(data[94:114], Encode_type.ASCII.value),  #
            "ota_device_version": hex_to_info(data[114:164], Encode_type.ASCII.value),  #
            "ota_ctrl": hex_to_info(data[164], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_A3.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_A3: {data}")
            HSyslog.log_info(f"tpp_cmd_A3: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_A3 error: .{data} .{e}")
        return {}


def tpp_cmd_B3(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    ota_result = data.get("ota_result")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ota_result, 1, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_B3: {data}")
            HSyslog.log_info(f"tpp_cmd_B3: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_B3.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_B3 error: .{data} .{e}")
        return []


def tpp_cmd_A1(data: list):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "device_id": hex_to_info(data[4:12], Encode_type.BCD.value),  #
            "gun_id": hex_to_info(data[12:14], Encode_type.BIN.value),  #
            "car_nums": hex_to_info(data[14:18], Encode_type.BIN.value),  #
            "ctrl_date": hex_to_info(data[18:26], Encode_type.TIME.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_A1.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_A1: {data}")
            HSyslog.log_info(f"tpp_cmd_A1: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_A1 error: .{data} .{e}")
        return {}


def tpp_cmd_B1(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    gun_id = data.get("gun_id")
    car_nums = data.get("car_nums")
    ctrl_date = data.get("ctrl_date")
    ctrl_result = data.get("ctrl_result")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 32, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 1, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_nums, 32, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_date, 1, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(ctrl_result, 2, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_B1: {data}")
            HSyslog.log_info(f"tpp_cmd_B1: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_B1.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_B1 error: .{data} .{e}")
        return []


def tpp_cmd_A2(data: dict):
    try:
        info = {
            "cmd_id": hex_to_info(data[0:2], Encode_type.BIN.value),  #
            "cmd_nums": hex_to_info(data[2:4], Encode_type.BIN.value),  #
            "user_card_id": hex_to_info(data[5:21], Encode_type.ASCII.value),  #
            "charge_nums": hex_to_info(data[21:29], Encode_type.BIN.value),  #
            "user_code": hex_to_info(data[29:59], Encode_type.GB2312.value),  #
            "electricity_balance": hex_to_info(data[59:71], Encode_type.ASCII.value),  #
            "electricity_available_balance": hex_to_info(data[71:83], Encode_type.ASCII.value),  #
            "server_balance": hex_to_info(data[83:95], Encode_type.ASCII.value),  #
            "server_available_balance": hex_to_info(data[95:107], Encode_type.ASCII.value),  #
            "charge_id": hex_to_info(data[107:122], Encode_type.ASCII.value),  #
            "BOSS_id": hex_to_info(data[122:142], Encode_type.ASCII.value),  #
            "charge_date": hex_to_info(data[142:150], Encode_type.TIME.value),  #
            "device_id": hex_to_info(data[150:158], Encode_type.BCD.value),  #
            "gun_id": hex_to_info(data[158], Encode_type.BIN.value),  #
            "ctrl_type": hex_to_info(data[159], Encode_type.BIN.value),  #
            "ctrl_mode": hex_to_info(data[160], Encode_type.BIN.value),  #
            "charge_policy": hex_to_info(data[161], Encode_type.BIN.value),  #
            "charge_policy_plan_time": hex_to_info(data[162:166], Encode_type.BIN.value),  #
            "charge_policy_plan_kw": hex_to_info(data[166:170], Encode_type.BIN.value),  #
            "msg_code": hex_to_info(data[170:178], Encode_type.BIN.value),  #
        }
        tpp_resv_data.put([tpp_mqtt_cmd_enum.tpp_cmd_type_A2.value, info])

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_A2: {data}")
            HSyslog.log_info(f"tpp_cmd_A2: {info}")

        return info
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_A2 error: .{data} .{e}")
        return {}


def tpp_cmd_B2(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    user_card_id = data.get("user_card_id")
    user_certificate_type = data.get("user_certificate_type")
    user_certificate_id = data.get("user_certificate_id")
    acceptance_channel = data.get("acceptance_channel")
    agency_id = data.get("agency_id")
    agency_code = data.get("agency_code")
    acceptance_operator_nums = data.get("acceptance_operator_nums")
    ctrl_start_date = data.get("ctrl_start_date")
    device_id = data.get("device_id")
    gun_id = data.get("gun_id")
    ctrl_type = data.get("ctrl_type")
    car_nums = data.get("car_nums")
    arm_id = data.get("arm_id")
    arm_ctrl_mode = data.get("arm_ctrl_mode")
    ctrl_mode = data.get("ctrl_mode")
    result = data.get("result")
    ctrl_stop_date = data.get("ctrl_stop_date")
    msg_code = data.get("msg_code")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_card_id, 16, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(user_certificate_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(user_certificate_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_channel, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(agency_id, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(agency_code, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(acceptance_operator_nums, 20, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(ctrl_start_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_nums, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(arm_id, 32, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(arm_ctrl_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_mode, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(result, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(ctrl_stop_date, 8, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(msg_code, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_B2: {data}")
            HSyslog.log_info(f"tpp_cmd_B2: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_B2.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_B2 error: .{data} .{e}")
        return []


def tpp_cmd_B9(data: dict):
    cmd_id = data.get("cmd_id", 0)
    cmd_nums = data.get("cmd_nums", 0)
    device_id = data.get("device_id")
    gun_id = data.get("gun_id")
    car_nums = data.get("car_nums")
    charge_id = data.get("charge_id")
    cmd_type = data.get("cmd_type")
    arm_id = data.get("arm_id")
    arm_status = data.get("arm_status")
    is_car_suitable = data.get("is_car_suitable")
    arm_battery_vol = data.get("arm_battery_vol")
    fault_code1 = data.get("fault_code1")
    fault_code2 = data.get("fault_code2")
    charge_vol = data.get("charge_vol")
    charge_cur = data.get("charge_cur")
    charge_soc = data.get("charge_soc")
    report_date = data.get("report_date")

    try:
        tpp_cmd_msg = []
        tpp_cmd_msg += info_to_hex(cmd_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(cmd_nums, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(device_id, 8, Encode_type.BCD.value)
        tpp_cmd_msg += info_to_hex(gun_id, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(car_nums, 4, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_id, 15, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(cmd_type, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(arm_id, 32, Encode_type.ASCII.value)
        tpp_cmd_msg += info_to_hex(arm_status, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(is_car_suitable, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(arm_battery_vol, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(fault_code1, 2, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(fault_code2, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(charge_vol, 2, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_cur, 2, Encode_type.TIME.value)
        tpp_cmd_msg += info_to_hex(charge_soc, 1, Encode_type.BIN.value)
        tpp_cmd_msg += info_to_hex(report_date, 8, Encode_type.BIN.value)

        if IS_DEBUG:
            HSyslog.log_info(f"tpp_cmd_B9: {data}")
            HSyslog.log_info(f"tpp_cmd_B9: {tpp_cmd_msg}")

        return pack(tpp_cmd_msg, tpp_mqtt_cmd_enum.tpp_cmd_type_B9.value)
    except Exception as e:
        HSyslog.log_error(f"tpp_cmd_B9 error: .{data} .{e}")
        return []


tpp_mqtt_cmd_type = {
    tpp_mqtt_cmd_enum.tpp_cmd_type_41.value: {"func": tpp_cmd_41, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_51.value: {"func": tpp_cmd_51, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_42.value: {"func": tpp_cmd_42, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_52.value: {"func": tpp_cmd_52, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_46.value: {"func": tpp_cmd_46, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_56.value: {"func": tpp_cmd_56, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_48.value: {"func": tpp_cmd_48, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_58.value: {"func": tpp_cmd_58, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_49.value: {"func": tpp_cmd_49, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_59.value: {"func": tpp_cmd_59, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_40.value: {"func": tpp_cmd_40, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_50.value: {"func": tpp_cmd_50, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_43.value: {"func": tpp_cmd_43, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_53.value: {"func": tpp_cmd_53, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_01.value: {"func": tpp_cmd_01, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_10.value: {"func": tpp_cmd_10, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_11.value: {"func": tpp_cmd_11, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_05.value: {"func": tpp_cmd_05, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_15.value: {"func": tpp_cmd_15, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_07.value: {"func": tpp_cmd_07, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_17.value: {"func": tpp_cmd_17, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_08.value: {"func": tpp_cmd_08, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_18.value: {"func": tpp_cmd_18, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_09.value: {"func": tpp_cmd_09, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_0A.value: {"func": tpp_cmd_0A, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_1A.value: {"func": tpp_cmd_1A, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_E0.value: {"func": tpp_cmd_E0, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_F0.value: {"func": tpp_cmd_F0, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_21.value: {"func": tpp_cmd_21, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_31.value: {"func": tpp_cmd_31, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_22.value: {"func": tpp_cmd_22, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_32.value: {"func": tpp_cmd_32, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_23.value: {"func": tpp_cmd_23, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_33.value: {"func": tpp_cmd_33, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_24.value: {"func": tpp_cmd_24, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_34.value: {"func": tpp_cmd_34, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_25.value: {"func": tpp_cmd_25, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_35.value: {"func": tpp_cmd_35, "qos": 0},
    tpp_mqtt_cmd_enum.tpp_cmd_type_26.value: {"func": tpp_cmd_26, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_36.value: {"func": tpp_cmd_36, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_2B.value: {"func": tpp_cmd_2B, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_3B.value: {"func": tpp_cmd_3B, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_39.value: {"func": tpp_cmd_39, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_3A.value: {"func": tpp_cmd_3A, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_3F.value: {"func": tpp_cmd_3F, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_70.value: {"func": tpp_cmd_70, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_60.value: {"func": tpp_cmd_60, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_71.value: {"func": tpp_cmd_71, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_61.value: {"func": tpp_cmd_61, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_72.value: {"func": tpp_cmd_72, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_62.value: {"func": tpp_cmd_62, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_73.value: {"func": tpp_cmd_73, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_63.value: {"func": tpp_cmd_63, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_74.value: {"func": tpp_cmd_74, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_64.value: {"func": tpp_cmd_64, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_75.value: {"func": tpp_cmd_75, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_65.value: {"func": tpp_cmd_65, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_78.value: {"func": tpp_cmd_78, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_68.value: {"func": tpp_cmd_68, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_69.value: {"func": tpp_cmd_69, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_7A.value: {"func": tpp_cmd_7A, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6A.value: {"func": tpp_cmd_6A, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6C.value: {"func": tpp_cmd_6C, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6B.value: {"func": tpp_cmd_6B, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_7B.value: {"func": tpp_cmd_7B, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_79.value: {"func": tpp_cmd_79, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6F.value: {"func": tpp_cmd_6F, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_7F.value: {"func": tpp_cmd_7F, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_7D.value: {"func": tpp_cmd_7D, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_6D.value: {"func": tpp_cmd_6D, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_80.value: {"func": tpp_cmd_80, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_90.value: {"func": tpp_cmd_90, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_92.value: {"func": tpp_cmd_92, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_93.value: {"func": tpp_cmd_93, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_94.value: {"func": tpp_cmd_94, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_86.value: {"func": tpp_cmd_86, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_96.value: {"func": tpp_cmd_96, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_87.value: {"func": tpp_cmd_87, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_97.value: {"func": tpp_cmd_97, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_88.value: {"func": tpp_cmd_88, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_98.value: {"func": tpp_cmd_98, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_E1.value: {"func": tpp_cmd_E1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_F1.value: {"func": tpp_cmd_F1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_E2.value: {"func": tpp_cmd_E2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_F2.value: {"func": tpp_cmd_F2, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_C1.value: {"func": tpp_cmd_C1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_D1.value: {"func": tpp_cmd_D1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_C2.value: {"func": tpp_cmd_C2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_D2.value: {"func": tpp_cmd_D2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_C3.value: {"func": tpp_cmd_C3, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_D3.value: {"func": tpp_cmd_D3, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_A3.value: {"func": tpp_cmd_A3, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_B3.value: {"func": tpp_cmd_B3, "qos": 1},

    tpp_mqtt_cmd_enum.tpp_cmd_type_A1.value: {"func": tpp_cmd_A1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_B1.value: {"func": tpp_cmd_B1, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_A2.value: {"func": tpp_cmd_A2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_B2.value: {"func": tpp_cmd_B2, "qos": 1},
    tpp_mqtt_cmd_enum.tpp_cmd_type_B9.value: {"func": tpp_cmd_B9, "qos": 1},
}

"""
/* #################################################### 数据信息 #######################################################*/
"""
User_Name = None
User_Password = None  # 用户密码
Enterprise_Code = None  # 生产厂商代码
Msg_Header = 0xF5FA  # 数据包头
SDK_Info = 0x80

serial_code = 0x01
End_Service_Code = 0xFF  # 消息最大序列号
Start_Service_Code = 0x00  # 消息最小序列号
Device_ID = "1031241203010001"  # 设备ID（桩编码，资产编码）
Encryption_Flag = None  # 是否加密
connect_status = False  # 连接状态
hand_status = False  # 握手状态
platform_host = "49.7.211.152"  # 平台IP
platform_port = 19688  # 平台端口号
data_path = "/opt/hhd/Platform.db"
ota_path = "/opt/hhd/dtu20.tar.gz"
syslog_path = '/var/log'  # 替换为实际路径
IS_DEBUG = True
boot_num = 0
start_time = 0
sign_time = 0
gun_qrcode = f"hlht://{Device_ID}.565843400/"

red_char = "\033[91m"
green_char = "\033[92m"
init_char = "\033[0m"

Gun_list = []
Device_class = None
Heartbeat_class = None


class Encode_type(Enum):
    BIN = 1
    TIME = 2
    ASCII = 3
    VERSION = 4
    MD5 = 5
    IP = 6
    MAC = 7
    ENCRYPT_VERSION = 8
    GB2312 = 9
    BCD = 10


class Big_Little(Enum):
    BIG = 1
    LITTLE = 2


class DB_Data_Type(Enum):
    DATA_STR = 1
    DATA_INT = 2


class Gun_DC_AC(Enum):
    DC_gun = 0x01
    AC_gun = 0x02
    Discharge_gun = 0x11


tpp_send_data = queue.Queue()
tpp_resv_data = queue.Queue()


class Gun_Status(Enum):
    Charging = 1  # 充电
    Stop_charge = 0  # 充电停止
    Server_preparation = 2  # 服务准备
    Server_end = 3  # 服务结束
    Charge_preparation = 4  # 充电准备
    Charge_end = 5  # 充电结束
    Reservation = 9  # 预约锁定


class Gun_Work_Status(Enum):
    Charging = 1  # 充电中
    Idle = 2  # 静置
    Dormancy = 3  # 休眠
    Fault = 4  # 故障
    Default = 0xFF  # 缺省


class Device_Work_Status(Enum):
    Manage = 1  # 管理
    Service = 2  # 服务
    Fault = 3  # 故障
    Init = 9  # 初始化


class Device_Status(Enum):
    Fault = 0x01
    Server = 0x00
    Idle = 0x00
    Occupy = 0x04
    One_Gun = 0x00
    Two_Gun = 0x10
    Other_Gun = 0x30


class Gun_Connect_Status(Enum):
    Connect = 0x02
    Not_Connect = 0x01


class Gun_Charge_Mode(Enum):
    One_Gun = 0x00
    Two_Gun = 0x80


class Heartbeat_info:
    def __init__(self, interval=3, timeout_interval=3):
        self._send_heartbeat = 0
        self._receive_heartbeat = 0
        self._heartbeat_timeout_interval = 0
        self._interval = interval
        self._timeout_interval = timeout_interval

    def set_send_heartbeat(self, send_heartbeat=None):
        if send_heartbeat is None:
            if self._send_heartbeat >= 0xFFFF:
                self._send_heartbeat = 0
            self._send_heartbeat += 1
        else:
            self._send_heartbeat = send_heartbeat

    def get_send_heartbeat(self):
        return self._send_heartbeat

    def set_receive_heartbeat(self, receive_heartbeat=None):
        if receive_heartbeat is None:
            if self._receive_heartbeat >= 0xFFFF:
                self._receive_heartbeat = 0
            self._receive_heartbeat += 1
        else:
            self._receive_heartbeat = receive_heartbeat

    def get_receive_heartbeat(self):
        return self._receive_heartbeat

    def set_heartbeat_timeout_interval(self):
        self._heartbeat_timeout_interval += 1

    def get_heartbeat_timeout_interval(self):
        return self._heartbeat_timeout_interval

    def compare_heartbeat_interval(self):
        if abs(self._send_heartbeat - self._receive_heartbeat) <= 3:
            return True
        else:
            HSyslog.log_info(f"{self._send_heartbeat}------{self._receive_heartbeat}")
            return False

    def empty_heartbeat_timeout_interval(self):
        self._heartbeat_timeout_interval = 0

    def set_interval(self, interval):
        self._interval = interval
        save_DeviceInfo("heart_interval", DB_Data_Type.DATA_INT.value, "", interval)

    def set_timeout_interval(self, timeout_interval):
        self._timeout_interval = timeout_interval
        save_DeviceInfo("heart_timeout_num", DB_Data_Type.DATA_INT.value, "", timeout_interval)

    def get_interval(self):
        return self._interval

    def get_timeout_interval(self):
        return self._timeout_interval


class Device_info:
    def __init__(self, device_id=Device_ID):
        self._device_id = device_id
        self._system_fault_code = [0x00]
        self._device_fault_code = [0x00]
        self._power_model_fault_code = [0x00]
        self._battery_fault_code = [0x00]
        self._work_status = Device_Work_Status.Init.value
        self._device_status = 0

    def set_system_fault_code(self, system_fault_code):
        self._system_fault_code = [0x00]
        if system_fault_code != 0x00:
            if system_fault_code not in self._system_fault_code:
                self._system_fault_code.append(system_fault_code)
        else:
            self._system_fault_code = [0x00]
        return self._system_fault_code

    def set_device_fault_code(self, device_fault_code):
        self._device_fault_code = [0x00]
        if device_fault_code != 0x00:
            if device_fault_code not in self._device_fault_code:
                self._device_fault_code.append(device_fault_code)
        else:
            self._device_fault_code = [0x00]
        return self._device_fault_code

    def set_work_status(self, work_status):
        self._work_status = work_status
        return self._work_status

    def set_power_model_fault_code(self, power_model_fault_code):
        self._power_model_fault_code = [0x00]
        if power_model_fault_code != 0x00:
            if power_model_fault_code not in self._power_model_fault_code:
                self._power_model_fault_code.append(power_model_fault_code)
        else:
            self._power_model_fault_code = [0x00]
        return self._power_model_fault_code

    def set_battery_fault_code(self, battery_fault_code):
        self._battery_fault_code = [0x00]
        if battery_fault_code != 0x00:
            if battery_fault_code not in self._battery_fault_code:
                self._battery_fault_code.append(battery_fault_code)
        else:
            self._battery_fault_code = [0x00]
        return self._battery_fault_code

    def set_device_status(self, device_status):
        self._device_status += device_status
        return self._device_status

    def get_system_fault_code(self):
        return sum(set(self._system_fault_code))

    def get_work_status(self):
        return self._work_status

    def get_device_fault_code(self):
        return sum(set(self._device_fault_code))

    def get_power_model_fault_code(self):
        return sum(set(self._power_model_fault_code))

    def get_battery_fault_code(self):
        return sum(set(self._battery_fault_code))

    def get_device_status(self):
        return self._device_status


class Gun_info:
    def __init__(self, gun_id):
        self.gun_id = gun_id
        self.gun_charge_cost = False
        self.gun_charge_session = False

        self._gun_type = 1
        self._gun_status = Gun_Status.Server_preparation.value
        self._gun_connect_status = Gun_Connect_Status.Not_Connect.value
        self._gun_charge_mode = Gun_Charge_Mode.One_Gun.value + (gun_id + 1) * 4 + Gun_DC_AC.DC_gun.value
        self._gun_work_status = Gun_Work_Status.Idle.value
        self._gun_charge = {}
        self._gun_charge_order = {}
        self._gun_charge_reserve = {}
        self._gun_fault = {}
        self._gun_warn = {}
        self._gun_qr = None
        self._gun_charge_gun_id = [gun_id]

    # 写入
    def set_gun_status(self, gun_status):
        self._gun_status = gun_status
        return self._gun_status

    def set_gun_connect_status(self, gun_connect_status):
        self._gun_connect_status = gun_connect_status
        return self._gun_connect_status

    def set_gun_charge_mode(self, gun_charge_mode):
        self._gun_charge_mode = gun_charge_mode + (self.gun_id + 1) * 4 + Gun_DC_AC.DC_gun.value
        return self._gun_connect_status

    def set_gun_work_status(self, gun_work_status):
        self._gun_work_status = gun_work_status
        return self._gun_work_status

    def set_gun_type(self, gun_type):
        self._gun_type = gun_type
        return self._gun_type

    def set_gun_charge(self, charge_info):
        self._gun_charge.update(charge_info)
        return True

    def empty_gun_charge(self):
        self._gun_charge = {}
        HSyslog.log_info("empty_gun_charge")
        return self._gun_charge

    def copy_gun_charge(self, gun_id):
        gun_charge = Gun_list[gun_id].get_gun_charge()
        self._gun_charge = copy.copy(gun_charge)
        return self._gun_charge

    def set_gun_charge_order(self, charge_info):
        self._gun_charge_order = charge_info
        HSyslog.log_info(self._gun_charge_order)
        return True

    def empty_gun_charge_order(self):
        self._gun_charge_order = {}
        HSyslog.log_info("empty_gun_charge_order")
        return self._gun_charge_order

    def set_gun_charge_reserve(self, gun_charge_reserve=None):
        if gun_charge_reserve is None:
            self._gun_charge_reserve = copy.copy(self._gun_charge_order)
        else:
            self._gun_charge_reserve.update(gun_charge_reserve)
        return self._gun_charge_reserve

    def empty_gun_charge__reserve(self):
        self._gun_charge_reserve = {}
        HSyslog.log_info("empty_gun_charge_reserve")
        return self._gun_charge_reserve

    def set_gun_fault(self, fault_info):
        if self._gun_fault != {}:
            for fault_id in self._gun_fault.keys():
                self._gun_fault[fault_id]["status"] = 1
        self._gun_fault.update(fault_info)
        return True

    def set_gun_warn(self, warn_info):
        if self._gun_warn != {}:
            for fault_id in self._gun_warn.keys():
                self._gun_warn[fault_id]["status"] = 1
        self._gun_warn.update(warn_info)
        return True

    def set_gun_qr(self, qr):
        self._gun_qr = qr
        return self._gun_qr

    def set_gun_charge_gun_id(self, gun_list: list):
        self._gun_charge_gun_id = gun_list
        return self._gun_charge_gun_id

    def get_gun_type(self):
        return self._gun_type

    # 获取
    def get_gun_status(self):
        return self._gun_status

    def get_gun_connect_status(self):
        return self._gun_connect_status

    def get_gun_charge_mode(self):
        return self._gun_charge_mode

    def get_gun_work_status(self):
        return self._gun_work_status

    def get_gun_charge(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge

    def get_gun_charge_order(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge_order.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge_order

    def get_gun_charge_reserve(self, charge_info=None):
        if charge_info is not None:
            if not isinstance(charge_info, str):
                return None
            data = self._gun_charge_reserve.get(charge_info, -1)
            if data == -1:
                return None
            return data
        else:
            return self._gun_charge_reserve

    def get_gun_fault(self, fault_id=None):
        if fault_id is None:
            return self._gun_fault
        else:
            return self._gun_fault.get(fault_id, {})

    def get_gun_warn(self, warn_id=None):
        if warn_id is None:
            return self._gun_warn
        else:
            return self._gun_warn.get(warn_id, {})

    def get_gun_qr(self):
        return self._gun_qr

    def get_gun_charge_gun_id(self):
        return self._gun_charge_gun_id


INFO_MODEL = Big_Little.LITTLE.value
Gun_Type = Gun_DC_AC.DC_gun.value


def get_datatime_YYMMDDHHMMSS(timestamp=""):
    if timestamp == "":
        current_time = datetime.now()
        formatted_time = current_time.strftime("%y%m%d%H%M%S")
    else:
        datetime_obj = datetime.utcfromtimestamp(int(timestamp))
        formatted_time = datetime_obj.strftime('%y%m%d%H%M%S')
    return formatted_time


def get_datetime_timestamp():
    datetime_obj = time.time()
    return int(datetime_obj)


def get_mac_address(interface):
    try:
        mac_bytes = get_DeviceInfo("mac_bytes")
        if mac_bytes is None:
            mac_bytes = open(f"/sys/class/net/{interface}/address").read().strip()
            save_DeviceInfo("mac_bytes", 1, mac_bytes, 0)
        # mac = ":".join([mac_bytes[i:i+2] for i in range(0, 12, 2)])
        return mac_bytes
    except FileNotFoundError:
        return None


def kwh_to_ah(kwh, voltage):
    if voltage <= 0:
        return 0
    return kwh * 1000 / voltage


cleck_code = {
    1: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "company_name", "param_type": DB_Data_Type.DATA_STR.value},
    2: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "website_info", "param_type": DB_Data_Type.DATA_STR.value},
    3: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "customer_service_telephone_number", "param_type": DB_Data_Type.DATA_STR.value},
    4: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "website_charge_info", "param_type": DB_Data_Type.DATA_STR.value},
    5: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_type", "param_type": DB_Data_Type.DATA_STR.value},
    6: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "matters_need_attention", "param_type": DB_Data_Type.DATA_STR.value},
    7: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "qrcode_active_field", "param_type": DB_Data_Type.DATA_STR.value},
    8: {"encode": [100, Encode_type.BIN.value], "is_save_device": None, "param_id": "qrcode_active_verification", "param_type": DB_Data_Type.DATA_STR.value},
}

cleck_code_3 = {
    1: {"encode": [32, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_id", "param_type": DB_Data_Type.DATA_STR.value},
    2: {"encode": [8, Encode_type.TIME.value], "is_save_device": None, "param_id": "system_time", "param_type": DB_Data_Type.DATA_STR.value},
    3: {"encode": [8, Encode_type.ASCII.value], "is_save_device": None, "param_id": "admin_password", "param_type": DB_Data_Type.DATA_STR.value},
    4: {"encode": [8, Encode_type.ASCII.value], "is_save_device": None, "param_id": "user_password", "param_type": DB_Data_Type.DATA_STR.value},
    5: {"encode": [6, Encode_type.ASCII.value], "is_save_device": None, "param_id": "mac_addr", "param_type": DB_Data_Type.DATA_STR.value},
    6: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "Box_transformer_id", "param_type": DB_Data_Type.DATA_STR.value},
    7: {"encode": [1, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_id", "param_type": DB_Data_Type.DATA_STR.value},
    8: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    9: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_llogo", "param_type": DB_Data_Type.DATA_STR.value},
    10: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_STR.value},
    11: {"encode": [16, Encode_type.ASCII.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_STR.value},
    12: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "user_cost_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    13: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_com", "param_type": DB_Data_Type.DATA_STR.value},
    14: {"encode": [4, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_port", "param_type": DB_Data_Type.DATA_STR.value},
    15: {"encode": [256, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_hlogo", "param_type": DB_Data_Type.DATA_STR.value},
    16: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "left_qr_word", "param_type": DB_Data_Type.DATA_STR.value},
    17: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "left_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    18: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "right_qr_word", "param_type": DB_Data_Type.DATA_STR.value},
    19: {"encode": [128, Encode_type.ASCII.value], "is_save_device": None, "param_id": "right_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
}

cleck_code_5 = {
    1: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "power_model_start", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_stop", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_ctrl_type", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    6: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reserve", "param_type": DB_Data_Type.DATA_INT.value},
    7: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "res_out_vol", "param_type": DB_Data_Type.DATA_INT.value},
    8: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "res_out_cur", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "charge_mode", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "rev_charge", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "device_reboot", "param_type": DB_Data_Type.DATA_INT.value},
    12: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "update_mode", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_lock_up", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "gun_lock_down", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "update_start", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "use_start", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_106", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_104", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "cost_suss", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "reconnect", "param_type": DB_Data_Type.DATA_INT.value},
}

cleck_code_501 = {
    1: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_106_interval", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_104_interval", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "report_102_interval", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "heart_timeout_num", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [32, Encode_type.ASCII.value], "is_save_device": None, "param_id": "device_id", "param_type": DB_Data_Type.DATA_STR.value},
    6: {"encode": [130, Encode_type.ASCII.value], "is_save_device": None, "param_id": "gun_id_qrcode", "param_type": DB_Data_Type.DATA_STR.value},
    7: {"encode": [64, Encode_type.ASCII.value], "is_save_device": None, "param_id": "server_ip", "param_type": DB_Data_Type.DATA_STR.value},
    8: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "server_port", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_level", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_policy", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "TCU_log_interval", "param_type": DB_Data_Type.DATA_INT.value},

    12: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_12", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_13", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_14", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_15", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_16", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_17", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_18", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_19", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_20", "param_type": DB_Data_Type.DATA_INT.value},
    21: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_21", "param_type": DB_Data_Type.DATA_INT.value},
    22: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_22", "param_type": DB_Data_Type.DATA_INT.value},
    23: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_23", "param_type": DB_Data_Type.DATA_INT.value},
    24: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_24", "param_type": DB_Data_Type.DATA_INT.value},
    25: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_25", "param_type": DB_Data_Type.DATA_INT.value},
    26: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_26", "param_type": DB_Data_Type.DATA_INT.value},
    27: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_27", "param_type": DB_Data_Type.DATA_INT.value},
    28: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_28", "param_type": DB_Data_Type.DATA_INT.value},
    29: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_29", "param_type": DB_Data_Type.DATA_INT.value},
    30: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_30", "param_type": DB_Data_Type.DATA_INT.value},
    31: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_31", "param_type": DB_Data_Type.DATA_INT.value},
    32: {"encode": [4, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_32", "param_type": DB_Data_Type.DATA_INT.value},
    33: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_33", "param_type": DB_Data_Type.DATA_INT.value},
    34: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_34", "param_type": DB_Data_Type.DATA_INT.value},
    35: {"encode": [2, Encode_type.BIN.value], "is_save_device": None, "param_id": "501_35", "param_type": DB_Data_Type.DATA_INT.value},
}

cleck_code_507 = {
    0: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "third_platform_is", "param_type": DB_Data_Type.DATA_INT.value},
    1: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "Three_electric_display_is", "param_type": DB_Data_Type.DATA_INT.value},
    2: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "plug_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    3: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "card_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    4: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "insulation_inspection_is", "param_type": DB_Data_Type.DATA_INT.value},
    5: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BSM_failure_stop_charge_is", "param_type": DB_Data_Type.DATA_INT.value},
    6: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "lock_failure_detection_is", "param_type": DB_Data_Type.DATA_INT.value},
    7: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "guard_detection_is", "param_type": DB_Data_Type.DATA_INT.value},
    8: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "auxiliary_power_is", "param_type": DB_Data_Type.DATA_INT.value},
    9: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BHM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    10: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    11: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCP_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    12: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRO_00_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    13: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BRO_AA_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    14: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCL_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    15: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BCS_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    16: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "BSM_timeout", "param_type": DB_Data_Type.DATA_INT.value},
    17: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "out_vol_threshold", "param_type": DB_Data_Type.DATA_INT.value},
    18: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "start_charging_limit_time_param", "param_type": DB_Data_Type.DATA_INT.value},
    19: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_reboot", "param_type": DB_Data_Type.DATA_INT.value},
    20: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_power_control", "param_type": DB_Data_Type.DATA_INT.value},
    21: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_double_gun_charge", "param_type": DB_Data_Type.DATA_INT.value},
    22: {"encode": [1, Encode_type.BIN.value], "is_save_device": None, "param_id": "function_offline_charhe", "param_type": DB_Data_Type.DATA_INT.value},
}


def get_datatime():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d-%H:%M:%S")
    return formatted_time


"""
/* #################################################### 数据信息 #######################################################*/
"""

"""
/* ##################################################### 组码 #########################################################*/
"""


def pack(msg, cmd):
    try:
        protocol = Protocol_Decode(msg, cmd)
        return protocol.protocol_message()
    except Exception as e:
        HSyslog.log_error(f"pack error: {msg} {cmd} {e}")


class Protocol_Decode:
    def __init__(self, msg: list, cmd: int):
        self.msg = msg
        self.header_code = info_to_hex(Msg_Header, 2, Encode_type.BIN.value)
        self.length_code = None
        self.info_code = info_to_hex(SDK_Info, 1, Encode_type.BIN.value)
        self.serial_code = None
        self.cmd_code = info_to_hex(cmd, 1, Encode_type.BIN.value)
        self.datas = msg
        self.check_code = None

    def Pprint(self):
        HSyslog.log_info(f"msg: {self.msg}")
        HSyslog.log_info(f"header_code: {self.header_code}")
        HSyslog.log_info(f"length_code: {self.length_code}")
        HSyslog.log_info(f"info_code: {self.info_code}")
        HSyslog.log_info(f"serial_code: {self.serial_code}")
        HSyslog.log_info(f"cmd_code: {self.cmd_code}")
        HSyslog.log_info(f"datas: {self.datas}")
        HSyslog.log_info(f"check_code: {self.check_code}")

    def list_to_bytes(self, msg):
        return bytes(msg)

    def get_serial_code(self):
        global serial_code
        self.serial_code = info_to_hex(serial_code, 1, Encode_type.BIN.value)
        if serial_code >= End_Service_Code:
            serial_code = Start_Service_Code
        else:
            serial_code += 1
        return True

    def get_length_code(self):
        length_code = 1 + 1 + 1 + len(self.datas)
        self.length_code = info_to_hex(length_code, 1, Encode_type.BIN.value)
        return True

    def get_check_code(self):
        if not self.datas:
            self.check_code = 0
            return False
        check_code = 0
        for data in self.datas + self.cmd_code:
            check_code += data
        self.check_code = info_to_hex(check_code & 0xFF, 1, Encode_type.BIN.value)
        return True

    def protocol_message(self):
        self.get_serial_code()
        self.get_length_code()
        self.get_check_code()

        msg = []
        msg += self.header_code
        msg += self.length_code
        msg += self.info_code
        msg += self.serial_code
        msg += self.cmd_code
        msg += self.datas
        msg += self.check_code
        # msg_list = " ".join([f"{x:02X}" for x in msg])
        # HSyslog.log_info(f"protocol_message_list: [{msg_list}]")
        msg = self.list_to_bytes(msg)
        tpp_send_data.put([msg, self.cmd_code])
        return msg


def info_to_ascii(info, info_len, info_mode):
    if not isinstance(info, str):  # 如果是整数，转换为单元素列表
        info = str(info)

    info_byte = info.encode('utf-8')
    padding_needed = max(0, info_len - len(info_byte))
    padded_bytes = info_byte + b'\x00' * padding_needed

    if info_mode == Big_Little.BIG.value:
        format_str = f'>{info_len}s'
        info_byte = struct.pack(format_str, padded_bytes)
        info_list = list(info_byte)
        return info_list
    if info_mode == Big_Little.LITTLE.value:
        format_str = f'<{info_len}s'
        info_byte = struct.pack(format_str, padded_bytes)
        info_list = list(info_byte)
        return info_list


def info_to_bin(info, info_len, info_mode):
    if not isinstance(info, int):
        return []
    if info_len < 1:
        raise ValueError("info_len must be greater than 0.")

    byte_length = (info.bit_length() + 7) // 8  # 计算 info 所需的字节数
    if byte_length > info_len:
        raise ValueError(f"info is too large to fit in {info_len} bytes.")

    if info_mode == Big_Little.BIG.value:
        info_bytes = info.to_bytes(info_len, byteorder='big')  # 大端
    elif info_mode == Big_Little.LITTLE.value:
        info_bytes = info.to_bytes(info_len, byteorder='little')  # 小端
    else:
        raise ValueError(f"Invalid info_mode: {info_mode}. Expected 1 (BIG) or 2 (LITTLE).")

    return list(info_bytes)


def info_to_version(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)

    version_list = info[2:].split('.')
    # 处理每个版本号部分并转换为对应的十六进制表示
    if len(version_list) != 3:
        for i in range(0, 3 - len(version_list)):
            version_list.append('0')
    version_array = []

    # 处理第一个部分，分高低字节
    first_part = int(version_list[0])
    high_byte = (first_part >> 8) & 0xFF  # 取高字节
    low_byte = first_part & 0xFF  # 取低字节
    version_array.extend([high_byte, low_byte])

    # 处理剩余的部分，不分高低字节
    for part in version_list[1:]:
        version_array.append(int(part))

    # 根据端模式调整顺序
    if info_mode == Big_Little.BIG.value:
        version_array = version_array[::-1]

    return version_array


def info_to_time(info, info_len, info_mode):
    # 转换为 datetime 对象
    dt = datetime.datetime.fromtimestamp(info)

    # 分别提取年、月、日、时、分、秒
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = dt.second

    if info_mode == Big_Little.LITTLE.value:
        # 小端序表示年份
        year_bytes = [year & 0xFF, (year >> 8) & 0xFF]
    else:
        # 大端序表示年份
        year_bytes = [(year >> 8) & 0xFF, year & 0xFF]

    # 构造字节数组
    time_bytes = year_bytes + [month, day, hour, minute, second, 0xFF]

    return time_bytes


def info_to_md5(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)
    if len(info) < 6:
        md5_hash = [0x00] * 32
    elif len(info) > 6:
        md5_hash = [0xFF] * 32
    else:
        md5_hash = []
        info_bytes = hashlib.md5(info.encode()).hexdigest()
        for i in range(0, len(info_bytes), 2):
            md5_hash.append(int(f"0x{info_bytes[i:i + 2]}", 16))
    return md5_hash


def info_to_mac(info, info_len, info_mode):
    if not isinstance(info, str):
        info = str(info)

    # 将MAC地址字符串拆分为字节列表
    mac_bytes = [int(byte, 16) for byte in info.split(':')]

    # 将MAC字节填入到列表并在末尾补零到32字节
    byte_array = mac_bytes + [0] * (32 - len(mac_bytes))

    # 根据端模式调整每6字节的顺序
    if info_mode == Big_Little.LITTLE.value:
        # 对前面的MAC字节部分每6字节块反转
        byte_array[:len(mac_bytes)] = [byte for i in range(0, len(mac_bytes), 6)
                                       for byte in reversed(byte_array[i:i + 6])]

    return byte_array


def info_to_encrypt_version(info, info_len, info_mode):
    if not isinstance(info, int):
        return []
    if info_len < 1:
        raise ValueError("info_len must be greater than 0.")

    byte_length = (info.bit_length() + 7) // 8  # 计算 info 所需的字节数
    if byte_length > info_len:
        raise ValueError(f"info is too large to fit in {info_len} bytes.")

    info_year = info // 10000
    info_mou = info % 10000 // 100
    info_day = info % 100

    info_bytes = []
    info_bytes += info_year.to_bytes(2, byteorder='big')  # 大端
    info_bytes += info_mou.to_bytes(1, byteorder='big')  # 大端
    info_bytes += info_day.to_bytes(1, byteorder='big')  # 大端

    return info_bytes


def info_to_chinese(info, info_len, info_mode):
    if not isinstance(info, str):
        return []
    # 按 GB2312 编码
    encoded = info.encode('gb2312')
    # 转换为数字列表
    number_list = [byte for byte in encoded]
    # 如果长度不足，补零；如果超出，截断
    if len(number_list) < info_len:
        number_list.extend([0] * (info_len - len(number_list)))
    else:
        number_list = number_list[:info_len]
    return number_list


def info_to_bcd(info, info_len, info_mode):
    if not isinstance(info, str):
        return str(info)
    # 补零使字符串长度为偶数
    if len(info) % 2 != 0:
        info += "0"

    # 将字符串转为压缩BCD
    bcd_bytes = []
    for i in range(0, len(info), 2):
        bcd_byte = int(info[i]) << 4 | int(info[i + 1])
        bcd_bytes.append(bcd_byte)

    # 不足指定长度时补零
    while len(bcd_bytes) < info_len:
        bcd_bytes.append(0x00)

    # 截断为指定长度
    return bcd_bytes[:info_len]


def info_to_hex(info, info_len, info_type, info_mode=INFO_MODEL):
    result = None
    try:
        if info_type == Encode_type.ASCII.value:
            result = info_to_ascii(info, info_len, info_mode)
        if info_type == Encode_type.BIN.value:
            result = info_to_bin(info, info_len, info_mode)
        if info_type == Encode_type.TIME.value:
            result = info_to_time(info, info_len, info_mode)
        if info_type == Encode_type.VERSION.value:
            result = info_to_version(info, info_len, info_mode)
        if info_type == Encode_type.MD5.value:
            result = info_to_md5(info, info_len, info_mode)
        if info_type == Encode_type.MAC.value:
            result = info_to_mac(info, info_len, info_mode)
        if info_type == Encode_type.ENCRYPT_VERSION.value:
            result = info_to_encrypt_version(info, info_len, info_mode)
        if info_type == Encode_type.GB2312.value:
            result = info_to_chinese(info, info_len, info_mode)
        if info_type == Encode_type.BCD.value:
            result = info_to_bcd(info, info_len, info_mode)

        if result is None:
            HSyslog.log_info(f"{info} --- {info_len} --- {info_type}")
            return [0x00] * info_len
        else:
            # HSyslog.log_info(result)
            return result
    except Exception as e:
        HSyslog.log_error(f"input_data: .{info} .{e}")
        return None


"""
/* ##################################################### 组码 #########################################################*/
"""

"""
/* ##################################################### 解码 #########################################################*/
"""


def unpack(msg):
    try:
        protocol = Protocol_Encode(msg)
        # protocol.Pprint()
        return protocol.protocol_message()
    except Exception as e:
        HSyslog.log_error(f"unpack error: {msg} {e}")


class Protocol_Encode:
    def __init__(self, msg):
        self.msg = self.bytes_to_hex_list(msg)
        self.header_code = hex_to_info(self.msg[0:2], Encode_type.BIN.value)
        self.length_code = hex_to_info(self.msg[2], Encode_type.BIN.value)
        self.info_code = hex_to_info(self.msg[3], Encode_type.BIN.value)
        self.serial_code = hex_to_info(self.msg[4], Encode_type.BIN.value)
        self.cmd_code = hex_to_info(self.msg[5], Encode_type.BIN.value)
        self.datas = self.msg[6:-1]
        self.check_code = hex_to_info(self.msg[-1:], Encode_type.BIN.value)
        self.callback_func = None

    def Pprint(self):
        HSyslog.log_info(f"msg: {self.msg}")
        HSyslog.log_info(f"header_code: {self.header_code}")
        HSyslog.log_info(f"length_code: {self.length_code}")
        HSyslog.log_info(f"info_code: {self.info_code}")
        HSyslog.log_info(f"serial_code: {self.serial_code}")
        HSyslog.log_info(f"cmd_code: {self.cmd_code}")
        HSyslog.log_info(f"datas: {self.datas}")
        HSyslog.log_info(f"check_code: {self.check_code}")

    def bytes_to_hex_list(self, msg):
        bytecode_list = list(msg)
        return bytecode_list

    def cleck_header_code(self):
        if self.header_code == Msg_Header:
            return True
        else:
            HSyslog.log_info(f"cleck_header_code error: {self.header_code} -- {Msg_Header}")
            return False

    def cleck_length_code(self):
        if self.length_code == len(self.msg) - 4:
            return True
        else:
            HSyslog.log_info(f"cleck_length_code error: {self.length_code} -- {len(self.msg) - 4}")
            return False

    def cleck_info_code(self):
        if self.info_code == SDK_Info:
            return True
        else:
            return False

    def cleck_serial_code(self):
        return self.serial_code

    def cleck_cmd_code(self):
        self.cmd_code = hex_to_info(self.cmd_code, Encode_type.BIN.value)
        if self.cmd_code in tpp_mqtt_cmd_type.keys():
            return True
        else:
            HSyslog.log_info(f"cleck_cmd_code error: {self.cmd_code} -- {self.cmd_code}")
            return False

    def cleck_check_code(self):
        if not self.datas:
            return False
        check_code = 0
        for data in self.datas:
            check_code += data
        check_code += self.cmd_code
        if self.check_code == check_code & 0xFF:
            return True
        else:
            HSyslog.log_info(f"cleck_check_code error: {self.check_code} -- {check_code & 0xFF}")
            return False

    def cleck_func(self):
        if self.cleck_header_code() and self.cleck_length_code() and self.cleck_info_code() and self.cleck_check_code() and self.cleck_cmd_code():
            self.callback_func = tpp_mqtt_cmd_type.get(self.cmd_code).get("func")
            return True
        else:
            HSyslog.log_info(f"cleck_func error")
            return False

    def protocol_message(self):
        if not self.cleck_func():
            return False
        if not isinstance(self.datas, list):  # 如果是整数，转换为单元素列表
            self.datas = [self.datas]
        # msg_list = " ".join([f"{x:02X}" for x in self.msg])
        # HSyslog.log_info(f"protocol_message_list: [{msg_list}]")
        result = self.callback_func(self.datas)
        if result == {}:
            return False
        else:
            return True


def ascii_list_to_info(hex_list, hex_mode):
    if not isinstance(hex_list, list):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]

    packed_bytes = bytes(hex_list)
    result_str = ""
    index = 0
    while index < len(packed_bytes):
        byte = packed_bytes[index]
        if byte == 0:
            break
        result_str += chr(byte)
        index += 1

    return result_str.rstrip()


def bin_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte = bytes(hex_list)
    format_str = {
        1: 'B',  # 1字节无符号整数
        2: 'H',  # 2字节无符号整数
        4: 'I',  # 4字节无符号整数
        8: 'Q'  # 8字节无符号整数
    }.get(len(hex_list), 'H')  # 默认为8字节

    if hex_mode == Big_Little.BIG.value:
        hex_int = struct.unpack(f">{format_str}", hex_byte)[0]
        return hex_int
    if hex_mode == Big_Little.LITTLE.value:
        hex_int = struct.unpack(f"<{format_str}", hex_byte)[0]
        return hex_int


def time_list_to_info(hex_list: list, hex_mode):
    year = hex_list[1] << 8 | hex_list[0]
    month = hex_list[2]
    day = hex_list[3]
    hour = hex_list[4]
    minute = hex_list[5]
    second = hex_list[6]

    # 创建时间对象
    timestamp = datetime.datetime(year, month, day, hour, minute, second)

    # 转换为 UNIX 时间戳
    unix_timestamp = int(timestamp.timestamp())

    return unix_timestamp


def version_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte = bytes(hex_list)
    format_str = {
        1: 'B',  # 1字节无符号整数
        2: 'H',  # 2字节无符号整数
        4: 'I',  # 4字节无符号整数
        8: 'Q'  # 8字节无符号整数
    }.get(len(hex_list), 'H')  # 默认为8字节

    if hex_mode == Big_Little.BIG.value:
        hex_int = struct.unpack(f">{format_str}", hex_byte)[0]
        if 9999 < hex_int < 100000:
            hex_str = f"0{str(hex_int)}"
        elif 999 < hex_int < 10000:
            hex_str = f"00{str(hex_int)}"
        elif 99 < hex_int < 1000:
            hex_str = f"000{str(hex_int)}"
        elif 9 < hex_int < 100:
            hex_str = f"0000{str(hex_int)}"
        elif 0 < hex_int < 10:
            hex_str = f"00000{str(hex_int)}"
        elif 0 == hex_int:
            hex_str = f"000000"
        else:
            hex_str = f"{str(hex_int)}"
        hex_str = f"A{hex_str[0:2]}.{hex_str[2:4]}.{hex_str[4:6]}"
        return hex_str
    if hex_mode == Big_Little.LITTLE.value:
        hex_int = struct.unpack(f"<{format_str}", hex_byte)[0]
        if 9999 < hex_int < 100000:
            hex_str = f"0{str(hex_int)}"
        elif 999 < hex_int < 10000:
            hex_str = f"00{str(hex_int)}"
        elif 99 < hex_int < 1000:
            hex_str = f"000{str(hex_int)}"
        elif 9 < hex_int < 100:
            hex_str = f"0000{str(hex_int)}"
        elif 0 < hex_int < 10:
            hex_str = f"00000{str(hex_int)}"
        elif 0 == hex_int:
            hex_str = f"000000"
        else:
            hex_str = f"{str(hex_int)}"
        hex_str = f"A{hex_str[0:2]}.{hex_str[2:4]}.{hex_str[4:6]}"

        return hex_str


def ip_list_to_info(hex_list, hex_mode):
    ip = ""
    for i in range(0, len(hex_list)):
        ip += str(hex_list[i])
        if i == len(hex_list) - 1:
            break
        ip += "."
    return ip


def encrypt_version_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    hex_byte_year = bytes(hex_list[0:2])
    hex_byte_mou = bytes([hex_list[2]])
    hex_byte_day = bytes([hex_list[3]])

    hex_int_year = struct.unpack(">H", hex_byte_year)[0]
    hex_int_mou = struct.unpack(">B", hex_byte_mou)[0]
    hex_int_day = struct.unpack(">B", hex_byte_day)[0]

    return hex_int_year * 10000 + hex_int_mou * 100 + hex_int_day


def chinese_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    # 将数字列表转为字节数组
    byte_array = bytearray(hex_list)
    # 解码为字符串
    try:
        text = byte_array.decode('gb2312').rstrip('\x00')  # 去掉补的零
    except UnicodeDecodeError:
        text = "解码失败: 无效的 GB2312 编码"
    return text.rstrip()


def bcd_list_to_info(hex_list, hex_mode):
    if isinstance(hex_list, int):  # 如果是整数，转换为单元素列表
        hex_list = [hex_list]
    result = []
    for byte in hex_list:
        high = (byte >> 4) & 0x0F  # 高4位
        low = byte & 0x0F  # 低4位
        result.append(str(high))
        result.append(str(low))

    # 拼接字符串，并移除末尾多余的0
    return ''.join(result).rstrip('0')


def hex_to_info(hex_list, hex_type, hex_mode=INFO_MODEL):
    if hex_type == Encode_type.ASCII.value:
        info = ascii_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.BIN.value:
        info = bin_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.TIME.value:
        info = time_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.VERSION.value:
        info = version_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.IP.value:
        info = ip_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.ENCRYPT_VERSION.value:
        info = encrypt_version_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.GB2312.value:
        info = chinese_list_to_info(hex_list, hex_mode)
        return info
    if hex_type == Encode_type.BCD.value:
        info = bcd_list_to_info(hex_list, hex_mode)
        return info


"""
/* ##################################################### 解码 #########################################################*/
"""

"""
/* ##################################################### 数据库 ########################################################*/
"""


def datadb_init():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS VerInfoEvt (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            device_type INTEGER,
            hard_version TEXT,
            soft_version TEXT
        )
    ''')  # 版本号
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_id TEXT,
            data_type INTEGER,
            data_str TEXT,
            data_int INTEGER
        )
    ''')  # 参数
    cur.execute('''
        CREATE TABLE IF NOT EXISTS HistoryOrder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gun_id INTEGER,
            charge_id TEXT,
            device_session_id TEXT,
            cloud_session_id TEXT,
            confirm_is INTEGER
        )
    ''')  # 历史记录
    cur.execute('''
        CREATE TABLE IF NOT EXISTS DeviceOrder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cmd_id INTEGER,
            cmd_nums INTEGER,
            charge_mode INTEGER,
            user_card_id TEXT,
            charge_id TEXT,
            charge_book_id TEXT,
            device_id TEXT,
            car_vin TEXT,
            car_card TEXT,
            charge_start_soc INTEGER,
            charge_stop_soc INTEGER,
            charge_power_ah INTEGER,
            charge_power_kwh INTEGER,
            charge_power_kwh_add INTEGER,
            charge_time INTEGER,
            charge_policy INTEGER,
            charge_policy_param INTEGER,
            is_normal_stop INTEGER,
            charge_start_date INTEGER,
            charge_stop_date INTEGER,
            charge_date INTEGER,
            charge_start_meter INTEGER,
            charge_start_meter_add INTEGER,
            charge_stop_meter INTEGER,
            charge_stop_meter_add INTEGER,
            device_session_id TEXT,
            cloud_session_id TEXT
        )
    ''')  # 记录

    conn.commit()
    conn.close()
    db_delete = threading.Thread(target=delete_db)
    db_delete.start()
    HSyslog.log_info("db_delete")


def save_DeviceInfo(data_id, data_type, data_str, data_int):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_DeviceInfo(data_id) is None:
        cur.execute('''INSERT INTO DeviceInfo (data_id, data_type, data_str, data_int) VALUES (?, ?, ?, ?)''',
                    (data_id, data_type, data_str, data_int))
    else:
        cur.execute('''UPDATE DeviceInfo SET data_type = ?, data_str = ?, data_int = ? WHERE data_id = ?''',
                    (data_type, data_str, data_int, data_id))
    conn.commit()
    conn.close()


def get_DeviceInfo(data_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceInfo WHERE data_id = ?', (data_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if not result:
        return None
    else:
        if result[2] == DB_Data_Type.DATA_STR.value:
            return result[3]
        if result[2] == DB_Data_Type.DATA_INT.value:
            return result[4]


def save_VerInfoEvt(device_id, device_type, hard_version, soft_version):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if get_VerInfoEvt(device_type)[1] is None:
        cur.execute(
            '''INSERT INTO VerInfoEvt (device_id, device_type, hard_version, soft_version) VALUES (?, ?, ?, ?)''',
            (device_id, device_type, hard_version, soft_version))
    else:
        cur.execute(
            '''UPDATE VerInfoEvt SET device_id = ?, hard_version = ?, soft_version = ? WHERE device_type = ?''',
            (device_id, hard_version, soft_version, device_type))
    conn.commit()
    conn.close()


def get_VerInfoEvt(device_type):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM VerInfoEvt WHERE device_type = ?', (device_type,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if not result:
        return None, None
    else:
        return result[3], result[4]


def save_DeviceOrder(dict_order: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if not get_DeviceOrder_pa_id(dict_order.get("cloud_session_id")):
        cur.execute(
            '''INSERT INTO DeviceOrder (cmd_id, cmd_nums, charge_mode, user_card_id, charge_id, charge_book_id, device_id, car_vin, car_card, 
            charge_start_soc, charge_stop_soc, charge_power_ah, charge_power_kwh, charge_power_kwh_add, charge_time, charge_policy, charge_policy_param, is_normal_stop, 
            charge_start_date, charge_stop_date, charge_date, charge_start_meter, charge_start_meter_add, charge_stop_meter, charge_stop_meter_add, device_session_id, cloud_session_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (dict_order.get("cmd_id"), dict_order.get("cmd_nums"), dict_order.get("charge_mode"), dict_order.get("user_card_id"),
             dict_order.get("charge_id"), dict_order.get("charge_book_id"), dict_order.get("device_id"), dict_order.get("car_vin"),
             dict_order.get("car_card"), dict_order.get("charge_start_soc"), dict_order.get("charge_stop_soc"), dict_order.get("charge_power_ah"),
             dict_order.get("charge_power_kwh"), dict_order.get("charge_power_kwh_add"), dict_order.get("charge_time"), dict_order.get("charge_policy"), dict_order.get("charge_policy_param"),
             dict_order.get("is_normal_stop"), dict_order.get("charge_start_date"), dict_order.get("charge_stop_date"), dict_order.get("charge_date"),
             dict_order.get("charge_start_meter"), dict_order.get("charge_start_meter_add"), dict_order.get("charge_stop_meter"), dict_order.get("charge_stop_meter_add"),
             dict_order.get("device_session_id"), dict_order.get("cloud_session_id")))
    else:
        cur.execute(
            '''UPDATE DeviceOrder SET cmd_id = ?, cmd_nums = ?, charge_mode = ?, user_card_id = ?, charge_id = ?, 
            charge_book_id = ?, device_id = ?, car_vin = ?, car_card = ?, charge_start_soc = ?, charge_stop_soc = ?, 
            charge_power_ah = ?, charge_power_kwh = ?, charge_power_kwh_add = ?, charge_time = ?, charge_policy = ?, charge_policy_param = ?, is_normal_stop = ?, charge_start_date = ?, 
            charge_stop_date = ?, charge_date = ?, charge_start_meter = ?, charge_start_meter_add = ?, charge_stop_meter = ?, charge_stop_meter_add = ?, device_session_id = ?
            WHERE cloud_session_id = ? ''',
            (dict_order.get("cmd_id"), dict_order.get("cmd_nums"), dict_order.get("charge_mode"), dict_order.get("user_card_id"), dict_order.get("charge_id"),
             dict_order.get("charge_book_id"), dict_order.get("device_id"), dict_order.get("car_vin"), dict_order.get("car_card"), dict_order.get("charge_start_soc"),
             dict_order.get("charge_stop_soc"), dict_order.get("charge_power_ah"), dict_order.get("charge_power_kwh"), dict_order.get("charge_power_kwh_add"),
             dict_order.get("charge_time"), dict_order.get("charge_policy"), dict_order.get("charge_policy_param"), dict_order.get("is_normal_stop"),
             dict_order.get("charge_start_date"), dict_order.get("charge_stop_date"), dict_order.get("charge_date"), dict_order.get("charge_start_meter"),
             dict_order.get("charge_start_meter_add"), dict_order.get("charge_stop_meter"), dict_order.get("charge_stop_meter_add"), dict_order.get("device_session_id"),
             dict_order.get("cloud_session_id")))
    conn.commit()
    conn.close()


def get_DeviceOrder_pa_id(cloud_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE cloud_session_id = ?', (cloud_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return {}
    else:
        info = {
            "cmd_id": result[1],
            "cmd_nums": result[2],
            "charge_mode": result[3],
            "user_card_id": result[4],
            "charge_id": result[5],
            "charge_book_id": result[6],
            "device_id": result[7],
            "car_vin": result[8],
            "car_card": result[9],
            "charge_start_soc": result[10],
            "charge_stop_soc": result[11],
            "charge_power_ah": result[12],
            "charge_power_kwh": result[13],
            "charge_power_kwh_add": result[14],
            "charge_time": result[15],
            "charge_policy": result[16],
            "charge_policy_param": result[17],
            "is_normal_stop": result[18],
            "charge_start_date": result[19],
            "charge_stop_date": result[20],
            "charge_date": result[21],
            "charge_start_meter": result[22],
            "charge_start_meter_add": result[23],
            "charge_stop_meter": result[24],
            "charge_stop_meter_add": result[25],
            "device_session_id": result[26],
            "cloud_session_id": result[27],
        }
        return info


def get_DeviceOrder_de_id(device_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder WHERE device_session_id = ?', (device_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return {}
    else:
        info = {
            "cmd_id": result[1],
            "cmd_nums": result[2],
            "charge_mode": result[3],
            "user_card_id": result[4],
            "charge_id": result[5],
            "charge_book_id": result[6],
            "device_id": result[7],
            "car_vin": result[8],
            "car_card": result[9],
            "charge_start_soc": result[10],
            "charge_stop_soc": result[11],
            "charge_power_ah": result[12],
            "charge_power_kwh": result[13],
            "charge_power_kwh_add": result[14],
            "charge_time": result[15],
            "charge_policy": result[16],
            "charge_policy_param": result[17],
            "is_normal_stop": result[18],
            "charge_start_date": result[19],
            "charge_stop_date": result[20],
            "charge_date": result[21],
            "charge_start_meter": result[22],
            "charge_start_meter_add": result[23],
            "charge_stop_meter": result[24],
            "charge_stop_meter_add": result[25],
            "device_session_id": result[26],
            "cloud_session_id": result[27],
        }
        return info


def get_DeviceOrder():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    order_list = []
    cur.execute('SELECT * FROM DeviceOrder')
    result = cur.fetchall()
    conn.commit()
    conn.close()
    if result is None:
        return {}
    else:
        for order in result:
            info = {
                "cmd_id": order[1],
                "cmd_nums": order[2],
                "charge_mode": order[3],
                "user_card_id": order[4],
                "charge_id": order[5],
                "charge_book_id": order[6],
                "device_id": order[7],
                "car_vin": order[8],
                "car_card": order[9],
                "charge_start_soc": order[10],
                "charge_stop_soc": order[11],
                "charge_power_ah": order[12],
                "charge_power_kwh": order[13],
                "charge_power_kwh_add": order[14],
                "charge_time": order[15],
                "charge_policy": order[16],
                "charge_policy_param": order[17],
                "is_normal_stop": order[18],
                "charge_start_date": order[19],
                "charge_stop_date": order[20],
                "charge_date": order[21],
                "charge_start_meter": order[22],
                "charge_start_meter_add": order[23],
                "charge_stop_meter": order[24],
                "charge_stop_meter_add": order[25],
                "device_session_id": order[26],
                "cloud_session_id": order[27],
            }
            order_list.append(info)
    return order_list


def save_HistoryOrder(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if not get_HistoryOrder_pa_id(dict_info.get("charge_id")):
        cur.execute(
            '''INSERT INTO HistoryOrder (gun_id, charge_id, device_session_id, cloud_session_id, confirm_is) 
            VALUES (?, ?, ?, ?, ?)''',
            (dict_info.get("gun_id"), dict_info.get("charge_id"), dict_info.get("device_session_id"), dict_info.get("cloud_session_id"), dict_info.get("confirm_is")))
    else:
        cur.execute(
            '''UPDATE HistoryOrder SET gun_id = ?, device_session_id = ?, cloud_session_id = ?, confirm_is = ? WHERE charge_id = ? ''',
            (dict_info.get("gun_id"), dict_info.get("device_session_id"), dict_info.get("cloud_session_id"), dict_info.get("confirm_is"), dict_info.get("charge_id")))
    conn.commit()
    conn.close()


def get_HistoryOrder_pa_id(cloud_session_id):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM HistoryOrder WHERE charge_id = ?', (cloud_session_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    if result is None:
        return False
    else:
        return True


def get_HistoryOrder(cloud_session_id=None):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    if cloud_session_id is None:
        order_list = []
        cur.execute('SELECT * FROM HistoryOrder')
        result = cur.fetchall()
        conn.commit()
        conn.close()
        for order in result:
            if order[5] == 0:
                info = {
                    "gun_id": order[1],
                    "charge_id": order[2],
                    "device_session_id": order[3],
                    "cloud_session_id": order[4],
                    "confirm_is": order[5],
                }
                order_list.append(info)
        return order_list
    else:
        cur.execute('SELECT * FROM HistoryOrder WHERE cloud_session_id = ?', (cloud_session_id,))
        result = cur.fetchone()
        conn.commit()
        conn.close()
        if result is None:
            return False
        else:
            if result[5] == 1:
                return True
            else:
                return False


def set_HistoryOrder(dict_info: dict):
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    gun_id = dict_info.get("gun_id")
    charge_id = dict_info.get("charge_id")
    confirm_is = dict_info.get("confirm_is")
    cur.execute('SELECT * FROM HistoryOrder WHERE charge_id = ?', (charge_id,))
    result = cur.fetchone()
    if result is None:
        conn.commit()
        conn.close()
        return False
    else:
        if confirm_is == 1:
            cur.execute('''UPDATE HistoryOrder SET confirm_is = ? WHERE charge_id = ?''', (confirm_is, charge_id))
            HSyslog.log_info(f"{charge_id} confirm: {confirm_is}")
            conn.commit()
            conn.close()
            return True
        else:
            conn.commit()
            conn.close()
            return False


def delete_db():
    delete_time = get_DeviceInfo("delete_time")
    if delete_time is None or delete_time == 0:
        save_DeviceInfo("delete_time", 2, "", int(time.time()))
    elif int(time.time()) - delete_time >= 86400 * 15:
        delete_DeviceOrder()
    else:
        time.sleep(86400)


def delete_DeviceOrder():
    conn = sqlite3.connect(data_path)
    cur = conn.cursor()
    cur.execute('SELECT * FROM DeviceOrder')
    result = cur.fetchall()
    for info in result:
        if get_HistoryOrder(info[-1]):
            if int(time.time()) - info[20] >= 86400 * 180:
                cur.execute("DELETE FROM DeviceOrder WHERE charge_stop_date=?", (info[20],))
                cur.execute("DELETE FROM HistoryOrder WHERE cloud_session_id=?", (info[-1],))
        else:
            pass
    conn.commit()
    conn.close()
    return result



"""
/* #################################################### 数据库 #########################################################*/
"""
