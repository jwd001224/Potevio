import socket
import threading

import HHhdlist
import HStategrid
from HHhdlist import *
import HSyslog


def tpp_init(host, port):
    try:
        while True:
            if not HHhdlist.Device_ready:
                time.sleep(3)
            else:
                break
        while True:
            if HHhdlist.get_ping() == 0:
                time.sleep(5)
            else:
                break
        HStategrid.save_VerInfoEvt(0, HHhdlist.device_ctrl_type.SDK.value, "20.0.2", "A.0.2")
        HStategrid.start_time = HStategrid.get_datetime_timestamp()
        boot_num = HStategrid.get_DeviceInfo("boot_num")
        if boot_num is None:
            HStategrid.boot_num += 1
            HStategrid.save_DeviceInfo("boot_num", HStategrid.DB_Data_Type.DATA_INT.value, "", HStategrid.boot_num)
        else:
            boot_num += 1
            HStategrid.boot_num = boot_num
            HStategrid.save_DeviceInfo("boot_num", HStategrid.DB_Data_Type.DATA_INT.value, "", boot_num)

        client = Client(host, port)
        client.connect()
        do_mqtt_resv_data()
        do_device_platform_data()
        do_mqtt_period()
    except Exception as e:
        HSyslog.log_error(f"tpp_init error. {e}")


class Client:
    def __init__(self, broker_address, broker_port, keepalive=10):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.client = None
        self.connect_thread = None
        self.send_thread = None
        self.receive_thread = None

    def connect(self):
        if not self.connect_thread or not self.connect_thread.is_alive():
            self.connect_thread = threading.Thread(target=self._connect_thread, daemon=True)
            self.connect_thread.start()

    def start_send_thread(self):
        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self._send_messages, daemon=True)
            self.send_thread.start()

    def start_receive_thread(self):
        if not self.receive_thread or not self.receive_thread.is_alive():
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

    def _connect_thread(self, isReady=False):
        """连接到MQTT服务器"""
        while True:
            try:
                if HStategrid.Heartbeat_class.get_heartbeat_timeout_interval() >= 3:
                    HStategrid.hand_status = False
                    HStategrid.connect_status = False
                if HStategrid.hand_status is False and HStategrid.connect_status is False:
                    try:
                        HStategrid.Heartbeat_class.set_send_heartbeat(0)
                        HStategrid.Heartbeat_class.set_receive_heartbeat(0)
                        HStategrid.Heartbeat_class.empty_heartbeat_timeout_interval()
                        self.client = socket.create_connection((self.broker_address, self.broker_port), timeout=15)
                        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, self.keepalive)
                        HStategrid.hand_status = True
                        hhd_to_tpp_10({})
                        isReady = True
                        HSyslog.log_info(f"Connected to TCP broker at {self.broker_address}:{self.broker_port}")
                    except Exception as e:
                        HSyslog.log_error(f"Failed to connect to broker: {e}")

                    if isReady:
                        self.start_send_thread()
                        self.start_receive_thread()
                else:
                    if HStategrid.Heartbeat_class.compare_heartbeat_interval():
                        HStategrid.Heartbeat_class.empty_heartbeat_timeout_interval()
                    else:
                        HStategrid.Heartbeat_class.set_heartbeat_timeout_interval()
                    time.sleep(3)
            except socket.error as e:
                HSyslog.log_error(f"{HStategrid.red_char}connect_tpp: {e}{HStategrid.init_char}")
                time.sleep(5)

    def _receive_messages(self):
        """接收消息时的回调函数"""
        while True:
            if HStategrid.hand_status:
                try:
                    receive_msg = self.client.recv(1024)
                    if receive_msg:
                        # HSyslog.log_info(f"Received message: '{receive_msg}' on ip {self.broker_address}")
                        HStategrid.unpack(receive_msg)
                except Exception as e:
                    HSyslog.log_error(f"Receive_messages: '{receive_msg}': {e}")
            else:
                time.sleep(1)

    def _send_messages(self):
        """向主题发送消息"""
        HSyslog.log_info(f"start send msg")
        while True:
            if HStategrid.hand_status:
                if not HStategrid.tpp_send_data:
                    time.sleep(0.1)
                else:
                    try:
                        if HStategrid.tpp_send_data.empty():
                            time.sleep(0.1)
                        else:
                            msg = HStategrid.tpp_send_data.get()
                            self.client.sendall(msg[0])
                            # HSyslog.log_info(f"Send_to_Platform: {msg[1]}: {msg[0]} to: {self.broker_address}")
                            time.sleep(0.02)
                    except Exception as e:
                        HSyslog.log_error(f"Send_to_Platform: {e}")
            else:
                if not HStategrid.tpp_send_data:
                    time.sleep(0.01)
                else:
                    if HStategrid.tpp_send_data.empty():
                        time.sleep(0.01)
                    else:
                        msg = HStategrid.tpp_send_data.get()
                        HSyslog.log_info(f"Send_to_Platform Faild: {msg}")
                        time.sleep(0.01)


def __mqtt_resv_data():
    while True:
        if HStategrid.hand_status:
            if not HStategrid.tpp_resv_data:
                time.sleep(0.1)
            else:
                try:
                    if HStategrid.tpp_resv_data.empty():
                        time.sleep(0.1)
                    else:
                        msg = HStategrid.tpp_resv_data.get()
                        if msg[0] in tpp_to_hhd.keys():
                            tpp_to_hhd[msg[0]](msg[1])
                        else:
                            HSyslog.log_info(f"__mqtt_resv_data： 参数错误--{msg}")
                except Exception as e:
                    HSyslog.log_error(f"__mqtt_resv_data error: {e}")
        else:
            if not HStategrid.tpp_resv_data:
                time.sleep(0.1)
            else:
                if HStategrid.tpp_resv_data.empty():
                    time.sleep(0.1)
                else:
                    msg = HStategrid.tpp_resv_data.get()
                    HSyslog.log_info(f"__mqtt_resv_data Faild: {msg}")


def do_mqtt_resv_data():
    mqttSendThread = threading.Thread(target=__mqtt_resv_data)
    mqttSendThread.start()
    HSyslog.log_info("do_mqtt_resv_data")


def __device_platform_data():
    while True:
        if HStategrid.hand_status:
            if not HHhdlist.device_platform_data:
                time.sleep(0.1)
            else:
                try:
                    if HHhdlist.device_platform_data.empty():
                        time.sleep(0.1)
                    else:
                        msg = HHhdlist.device_platform_data.get()
                        if msg[0] in hhd_to_tpp.keys():
                            hhd_to_tpp[msg[0]](msg[1])
                        else:
                            HSyslog.log_info(f"__device_platform_data： 参数错误--{msg}")
                except Exception as e:
                    HSyslog.log_error(f"__device_platform_data error: {e}")
        else:
            if not HHhdlist.device_platform_data:
                time.sleep(0.1)
            else:
                if HHhdlist.device_platform_data.empty():
                    time.sleep(0.1)
                else:
                    msg = HHhdlist.device_platform_data.get()
                    HSyslog.log_info(f"__device_platform_data Faild: {msg}")


def do_device_platform_data():
    d_p = threading.Thread(target=__device_platform_data)
    d_p.start()
    HSyslog.log_info("__device_platform_data")


def __mqtt_period_event(report_interval=15, report_mode=0x02, sign_interval=30 * 60):
    report_period_interval = HStategrid.get_datetime_timestamp()
    sign_period_interval = HStategrid.get_datetime_timestamp()
    heart_period_interval = HStategrid.get_datetime_timestamp()
    while True:
        if not HStategrid.connect_status:
            if abs(int(time.time()) - int(sign_period_interval)) >= sign_interval:
                sign_period_interval = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_10({})
        if HStategrid.connect_status and HStategrid.hand_status:
            if abs(int(time.time()) - int(heart_period_interval)) == HStategrid.Heartbeat_class.get_interval():
                heart_period_interval = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_58({})
        if report_mode == 0x02:
            if abs(int(time.time()) - int(sign_period_interval)) >= sign_interval:
                sign_period_interval = HStategrid.get_datetime_timestamp()
                hhd_to_tpp_10({})
            if HStategrid.connect_status and HStategrid.hand_status:
                if abs(int(time.time()) - int(report_period_interval)) >= report_interval:
                    report_period_interval = HStategrid.get_datetime_timestamp()
                    hhd_to_tpp_11({})
                    hhd_to_tpp_17()
                    hhd_to_tpp_31()
                    hhd_to_tpp_34()
                    hhd_to_tpp_35()
                    hhd_to_tpp_3A()
                    hhd_to_tpp_3F()
        time.sleep(0.1)


def do_mqtt_period():
    report_interval = HStategrid.get_DeviceInfo("report_interval")
    report_mode = HStategrid.get_DeviceInfo("report_mode")
    sign_interval = HStategrid.get_DeviceInfo("sign_interval") * 60
    if report_interval is None or report_interval == 0:
        report_interval = 15
    if report_mode is None:
        report_mode = 0x02
    if sign_interval is None or sign_interval == 0:
        sign_interval = 30 * 60
    mqttPeriodThread = threading.Thread(target=__mqtt_period_event, args=(report_interval, report_mode, sign_interval,))
    mqttPeriodThread.start()
    HSyslog.log_info("do_mqtt_period")


'''################################################### 接收数据处理 ####################################################'''


def tpp_to_hhd_41(msg):
    try:
        HStategrid.save_DeviceInfo("storage_cap_limit", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("storage_cap_limit"))
        HStategrid.save_DeviceInfo("param_cap_limit", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("param_cap_limit"))
        HStategrid.save_DeviceInfo("battery_cap_limit", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("battery_cap_limit"))
        HStategrid.save_DeviceInfo("charge_cap_limit", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("charge_cap_limit"))
        HStategrid.save_DeviceInfo("sign_interval", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("sign_interval", 30 * 60))

        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
        }
        hhd_to_tpp_51(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_41'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_42(msg):
    try:
        system_time = msg.get("system_time")
        charging = True
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge() != {}:
                charging = False
                break
        if charging:
            time_info = {
                "unix_time": system_time
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_sys_time_sync, time_info])
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "system_time": system_time
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "system_time": HStategrid.get_datetime_timestamp()
            }
        hhd_to_tpp_52(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_42'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_46(msg):
    try:
        HStategrid.save_DeviceInfo("device_id", HStategrid.DB_Data_Type.DATA_STR.value, msg.get("device_id"), 0)
        HStategrid.save_DeviceInfo("device_type", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("device_type"))
        HStategrid.save_DeviceInfo("battery_type", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("battery_type"))
        HStategrid.save_DeviceInfo("gun_num", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("gun_num"))
        HStategrid.save_DeviceInfo("server_host", HStategrid.DB_Data_Type.DATA_STR.value, msg.get("server_host"), 0)
        HStategrid.save_DeviceInfo("server_port", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("server_port"))
        HHhdlist.save_json_config({"deviceName": msg.get("device_id")})
        charging = True
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge() != {}:
                charging = False
                break
        if charging:
            subprocess.run(['supervisorctl', 'restart', 'internal_ui'])
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
            }
        hhd_to_tpp_56(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_46'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_48(msg):
    try:
        heart_index = msg.get("heart_index")
        HStategrid.Heartbeat_class.set_receive_heartbeat()
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_48'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_49(msg):
    try:
        HStategrid.Heartbeat_class.set_interval(msg.get("heart_interval"))
        HStategrid.Heartbeat_class.set_timeout_interval(msg.get("heart_timeout_num"))
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
        }
        hhd_to_tpp_59(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_49'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_40(msg):
    try:
        HStategrid.save_DeviceInfo("input_card", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("input_card"))
        HStategrid.save_DeviceInfo("input_password", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("input_password"))
        HStategrid.save_DeviceInfo("charge_inquiry_service", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("charge_inquiry_service"))
        HStategrid.save_DeviceInfo("input_car_card", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("input_car_card"))
        HStategrid.save_DeviceInfo("door_unlock", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("door_unlock"))
        HStategrid.save_DeviceInfo("connect_charge", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("connect_charge"))
        HStategrid.save_DeviceInfo("charge_mode", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("charge_mode"))
        HStategrid.save_DeviceInfo("start_charge", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("start_charge"))
        HStategrid.save_DeviceInfo("stop_charge_card", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("stop_charge_card"))
        HStategrid.save_DeviceInfo("unconnect_charge", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("unconnect_charge"))
        HStategrid.save_DeviceInfo("door_lock", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("door_lock"))
        HStategrid.save_DeviceInfo("charge_cost_account", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("charge_cost_account"))
        HStategrid.save_DeviceInfo("print_receipt", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("print_receipt"))
        HStategrid.save_DeviceInfo("query", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("query"))
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
        }
        hhd_to_tpp_50(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_40'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_43(msg):
    try:
        charging = True
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge() != {}:
                charging = False
                break
        if charging:
            subprocess.run(['supervisorctl', 'restart', 'internal_ui'])
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
            }
        hhd_to_tpp_53(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_43'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_01(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
        }
        hhd_to_tpp_10(info)
        HStategrid.sign_time = HStategrid.get_datetime_timestamp()
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_01'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_05(msg):
    try:
        param_list = msg.get("param_list")
        param_type = msg.get("param_type")
        param_num = msg.get("param_num")
        if param_type == 2:
            for param_info in param_list:
                if param_info.get("param_no") != 0:
                    info = {
                        "gun_id": param_info.get("param_no") - 1,
                        "control_type": HHhdlist.control_charge.stop_charge.value
                    }
                    HStategrid.Gun_list[info.get("gun_id")].set_gun_charge({"cmd_id_stop": msg.get("cmd_id", 0)})
                    HStategrid.Gun_list[info.get("gun_id")].set_gun_charge({"cmd_nums_stop": msg.get("cmd_nums", 0)})
                    HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_control_charge, info])
                else:
                    for gun_info in HStategrid.Gun_list:
                        info = {
                            "gun_id": gun_info.gun_id,
                            "control_type": HHhdlist.control_charge.stop_charge.value
                        }
                        HStategrid.Gun_list[info.get("gun_id")].set_gun_charge({"cmd_id_stop": msg.get("cmd_id", 0)})
                        HStategrid.Gun_list[info.get("gun_id")].set_gun_charge({"cmd_nums_stop": msg.get("cmd_nums", 0)})
                        HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_control_charge, info])
        elif param_type == 3:
            for param_info in param_list:
                param_no = param_info.get("param_no")
                HStategrid.save_DeviceInfo(f"{param_type}_{param_no}", HStategrid.DB_Data_Type.DATA_INT.value, "", param_info.get("param"))
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "param_type": param_type,
                "param_num": param_num,
                "param_list": param_list,
            }
            hhd_to_tpp_15(info)
        elif param_type == 7:
            for param_info in param_list:
                if param_info.get("param") == 1:
                    update_param = {
                        "device_type": HHhdlist.device_param_type.chargeSys.value,
                        "param_list": [{"param_id": 169, "param_value": 0xFF}],
                    }
                else:
                    update_param = {
                        "device_type": HHhdlist.device_param_type.chargeSys.value,
                        "param_list": [{"param_id": 169, "param_value": 0x00}],
                    }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_param, update_param])
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "param_type": param_type,
                "param_num": param_num,
                "param_list": param_list,
            }
            hhd_to_tpp_15(info)
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "param_type": param_type,
                "param_num": param_num,
                "param_list": param_list,
            }
            hhd_to_tpp_15(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_05'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_07(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_17(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_07'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_08(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_18(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_08'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_09(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "device_id": msg.get("device_id")
        }
        HStategrid.Device_class.set_work_status(HStategrid.Device_Work_Status.Service.value)
        HStategrid.connect_status = True
        hhd_to_tpp_79({})
        if HHhdlist.qrcode_nums <= 5:
            HHhdlist.qrcode_nums += 1
            update_qrcode = {
                "gun_id": [],
                "qrcode": []
            }
            for gun_info in HStategrid.Gun_list:
                if isinstance(gun_info.get_gun_qr(), str):
                    update_qrcode["gun_id"].append(gun_info.gun_id)
                    update_qrcode["qrcode"].append(gun_info.get_gun_qr())
                else:
                    return
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_update_qrcode, update_qrcode])
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_09'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_0A(msg):
    try:
        cmd_param = msg.get("cmd_param")
        cmd_data = msg.get("cmd_data")
        if cmd_param in HStategrid.cleck_code.keys():
            HStategrid.save_DeviceInfo(HStategrid.cleck_code.get(cmd_param).get("param_id"), HStategrid.cleck_code.get(cmd_param).get("param_type"), cmd_data, 0)
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "cmd_param": cmd_param,
            "cmd_data": cmd_data,
        }
        hhd_to_tpp_1A(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_0A'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_E0(msg):
    try:
        HStategrid.save_DeviceInfo("report_mode", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("report_mode"))
        HStategrid.save_DeviceInfo("report_interval", HStategrid.DB_Data_Type.DATA_INT.value, "", msg.get("report_interval", 15))
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "report_mode": msg.get("report_mode"),
            "report_interval": msg.get("report_interval"),
        }
        hhd_to_tpp_F0(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_E0'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_21(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
        }
        hhd_to_tpp_31(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_21'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_22(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_3A(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_22'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_23(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_33(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_23'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_24(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_34(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_24'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_25(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "gun_num": msg.get("gun_num"),
            "charge_mode": msg.get("charge_mode"),
        }
        hhd_to_tpp_35(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_25'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_26(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_26'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_2B(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_2B'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_60(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_60'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_61(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_61'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_62(msg):
    try:
        gun_id = msg.get("gun_id")
        device_id = msg.get("device_id")
        charge_id = msg.get("charge_id")
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_309'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_63(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_311'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_64(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        user_card_id = msg.get("user_card_id")
        order_info = HStategrid.get_DeviceOrder_pa_id(user_card_id)
        if order_info.get("device_session_id") is None or order_info.get("device_session_id") == "":
            device_session_id = ""
        else:
            device_session_id = order_info.get("device_session_id")
        info = {
            "gun_id": gun_id,
            "cloud_session_id": user_card_id,
            "device_session_id": device_session_id,
            "result": 0
        }
        HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_201'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_65(msg):
    try:
        gun_id = msg.get("gun_id") - 1
        user_card_id = msg.get("user_card_id")
        if user_card_id == HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"):
            info = {
                "gun_id": gun_id,
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("charge_id"),
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge("device_session_id"),
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_205'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_68(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_401'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_69(msg):
    try:
        user_card_id = msg.get("user_card_id")
        user_name = msg.get("user_name")
        cmd_code = msg.get("cmd_code")
        cmd_code_desc = msg.get("cmd_code_desc")
        user_code = msg.get("user_code")
        electricity_balance = msg.get("electricity_balance")
        electricity_available_balance = msg.get("electricity_available_balance")
        server_balance = msg.get("server_balance")
        server_available_balance = msg.get("server_available_balance")
        charge_id = msg.get("charge_id")
        BOSS_id = msg.get("BOSS_id")
        charge_allow_power_kw = msg.get("charge_allow_power_kw")
        charge_allow_time = msg.get("charge_allow_time")
        charge_date = msg.get("charge_date")
        gun_id = None
        for gun_info in HStategrid.Gun_list:
            if user_card_id == gun_info.get_gun_charge("card_id"):
                gun_id = gun_info.gun_id
                break
            else:
                continue
        if gun_id is None:
            pass
        else:
            info = {
                "gun_id": gun_id,
                "result": 1
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_69'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_6A(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_1303'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_6C(msg):
    try:
        cmd_id = msg.get("cmd_id", 0)
        cmd_nums = msg.get("cmd_nums", 0)
        user_card_id = msg.get("user_card_id")
        charge_nums = msg.get("charge_nums")
        user_code = msg.get("user_code")
        electricity_balance = msg.get("electricity_balance")
        electricity_available_balance = msg.get("electricity_available_balance")
        server_balance = msg.get("server_balance")
        server_available_balance = msg.get("server_available_balance")
        charge_id = msg.get("charge_id")
        BOSS_id = msg.get("BOSS_id")
        charge_date = msg.get("charge_date")
        gun_id = msg.get("gun_id") - 1
        charge_policy_mode = msg.get("charge_policy_mode")
        charge_policy_plan_time = msg.get("charge_policy_plan_time")
        charge_policy_plan_kw = msg.get("charge_policy_plan_kw")
        msg_code = msg.get("msg_code")

        if HStategrid.Gun_list[gun_id].get_gun_charge() == {} and HStategrid.Gun_list[gun_id].get_gun_charge_order() == {}:
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_id_start": cmd_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_nums_start": cmd_nums})
            HStategrid.Gun_list[gun_id].set_gun_charge({"msg_code_start": msg_code})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_card_id": user_card_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_nums": charge_nums})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_code": user_code})
            if user_code == '0':
                HStategrid.Gun_list[gun_id].set_gun_charge({"car_card": ""})
            else:
                HStategrid.Gun_list[gun_id].set_gun_charge({"car_card": user_code.split(',')[1]})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electricity_balance": electricity_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electricity_available_balance": electricity_available_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"server_balance": server_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"server_available_balance": server_available_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_id": charge_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"BOSS_id": BOSS_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_date": charge_date})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_mode": charge_policy_mode})
            HStategrid.Gun_list[gun_id].set_gun_charge({
                "stop_type": {
                    0x20: [0x00, 0],
                    0x30: [0x03, charge_policy_plan_time * 60],
                    0x40: [0x01, charge_policy_plan_kw * 1000]
                }.get(charge_policy_mode)[0]})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_plan_time": charge_policy_plan_time})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_plan_kw": charge_policy_plan_kw})
            HStategrid.Gun_list[gun_id].set_gun_charge({
                "stop_condition": {
                    0x20: [0x00, 0],
                    0x30: [0x03, charge_policy_plan_time * 60],
                    0x40: [0x01, charge_policy_plan_kw * 1000]
                }.get(charge_policy_mode)[1]})
            HStategrid.Gun_list[gun_id].set_gun_charge({
                "charge_policy": {
                    0x20: [4, 0],
                    0x30: [1, charge_policy_plan_time],
                    0x40: [2, charge_policy_plan_kw]
                }.get(charge_policy_mode)[0]})

            HStategrid.Gun_list[gun_id].set_gun_charge({
                "charge_policy_param": {
                    0x20: [4, 0],
                    0x30: [1, charge_policy_plan_time],
                    0x40: [2, charge_policy_plan_kw]
                }.get(charge_policy_mode)[1]})

            if HStategrid.Gun_list[gun_id].get_gun_charge("start_source") is None:
                HStategrid.Gun_list[gun_id].set_gun_charge({"start_source": 4})
                info = {
                    "gun_id": gun_id,
                    "control_type": HHhdlist.control_charge.start_charge.value
                }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_control_charge, info])
                info = {
                    "gun_id": gun_id,
                    "result": 1,
                }
                hhd_to_tpp_7A(info)
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "user_card_id": msg.get("user_card_id"),
                "charge_date": msg.get("charge_date"),
                "msg_code": msg.get("msg_code"),
                "gun_id": gun_id,
                "result": 2,
            }
            hhd_to_tpp_7A(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_6C'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_6B(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_6B'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_6F(msg):
    try:
        cmd_id = msg.get("cmd_id")
        cmd_nums = msg.get("cmd_nums")
        charge_mode = msg.get("charge_mode")
        user_card_id = msg.get("user_card_id")
        user_code = msg.get("user_code")
        charge_info = msg.get("charge_info")
        charge_electricity_cost = msg.get("charge_electricity_cost")
        charge_server_cost = msg.get("charge_server_cost")
        charge_cost = msg.get("charge_cost")
        charge_id = msg.get("charge_id")
        BOSS_id = msg.get("BOSS_id"),
        charge_date = msg.get("charge_date")
        gun_id = None
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge_reserve("cloud_session_id") == charge_id:
                gun_id = gun_info.gun_id
                break
        if gun_id is None:
            if charge_id != "":
                info = {
                    "gun_id": gun_id,
                    "charge_id": charge_id,
                    "confirm_is": 1
                }
                HStategrid.set_HistoryOrder(info)
        else:
            HStategrid.Gun_list[gun_id].set_gun_charge_reserve({"charge_electricity_cost": charge_electricity_cost})
            HStategrid.Gun_list[gun_id].set_gun_charge_reserve({"charge_server_cost": charge_server_cost})
            HStategrid.Gun_list[gun_id].set_gun_charge_reserve({"charge_cost": charge_cost})

            info = {
                "gun_id": gun_id,
                "cloud_session_id": charge_id,
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_notify_charge_account, info])

            if charge_id != "" and charge_id == HStategrid.Gun_list[gun_id].get_gun_charge_reserve("charge_id"):
                info = {
                    "gun_id": gun_id,
                    "charge_id": charge_id,
                    "confirm_is": 1
                }
                HStategrid.set_HistoryOrder(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_6F'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_6D(msg):
    try:
        cmd_id = msg.get("cmd_id")
        cmd_nums = msg.get("cmd_nums")
        user_card_id = msg.get("user_card_id")
        cmd_code = msg.get("cmd_code")
        cmd_code_desc = msg.get("cmd_code_desc")
        electricity_balance = msg.get("electricity_balance")
        electricity_available_balance = msg.get("electricity_available_balance")
        server_balance = msg.get("server_balance")
        server_available_balance = msg.get("server_available_balance")
        charge_id = msg.get("charge_id")
        charge_date = msg.get("charge_date")
        msg_code = msg.get("msg_code")
        is_stop_code = msg.get("is_stop_code")
        stop_code = msg.get("stop_code")

        gun_id = None
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge("cmd_nums_check") == cmd_nums:
                gun_id = gun_info.gun_id
                break
        if gun_id is not None:
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_id_start": cmd_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_nums_start": cmd_nums})
            HStategrid.Gun_list[gun_id].set_gun_charge({"msg_code_start": msg_code})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_card_id": user_card_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_code": cmd_code})
            HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_code_desc": cmd_code_desc})
            HStategrid.Gun_list[gun_id].set_gun_charge({"car_card": ""})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electricity_balance": electricity_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electricity_available_balance": electricity_available_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"server_balance": server_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"server_available_balance": server_available_balance})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_id": charge_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_date": charge_date})

            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy": 4})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_policy_param": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"charge_date": charge_date})

            HStategrid.Gun_list[gun_id].set_gun_charge({"aux_power_type": 0xFF})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_mode": 0xFF})
            HStategrid.Gun_list[gun_id].set_gun_charge({"user_id": user_card_id})
            HStategrid.Gun_list[gun_id].set_gun_charge({"appointment_time": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"balance": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"billing": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"overdraft_limit": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"electric_discount": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"service_discount": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"multi_charge": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"delay_time": -1})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_type": 0})
            HStategrid.Gun_list[gun_id].set_gun_charge({"stop_condition": 0})
            if is_stop_code == 1:
                HStategrid.Gun_list[gun_id].set_gun_charge({"is_stop_code": is_stop_code})
                HStategrid.Gun_list[gun_id].set_gun_charge({"stop_code": stop_code})
            else:
                HStategrid.Gun_list[gun_id].set_gun_charge({"is_stop_code": is_stop_code})
                HStategrid.Gun_list[gun_id].set_gun_charge({"stop_code": "000000"})

            if cmd_code == "000000":
                info = {
                    "gun_id": gun_id,
                    "result": 1,
                    "reason": 0x04,
                }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
            else:
                info = {
                    "gun_id": gun_id,
                    "result": 0,
                    "reason": 0x00,
                }
                HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_check_vin, info])
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_6D'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_80(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id"),
            "cmd_nums": msg.get("cmd_nums"),
            "charge_record_start": msg.get("charge_record_start") - 1,
            "charge_record_num": msg.get("charge_record_num"),
        }
        hhd_to_tpp_94(info)
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_80'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_86(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_86'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_87(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_87'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_88(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_88'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_E1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_801'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_E2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_509'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_C1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_C1'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_C2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_C2'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_C3(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_C3'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_A3(msg):
    try:
        ota_host = msg.get("ota_host")
        ota_port = msg.get("ota_port")
        log_host = msg.get("log_host")
        log_port = msg.get("log_port")

        ota_user_id = msg.get("ota_user_id")
        ota_password = msg.get("ota_password")
        ota_device_version = msg.get("ota_device_version")
        ota_ctrl = msg.get("ota_ctrl")

        # try:
        #     # 连接到 FTP 服务器
        #     ftp = FTP()
        #     ftp.connect(ota_host, int(ota_port))
        #     ftp.login(user=ota_user_id, passwd=ota_password)
        #
        #     # 下载文件
        #     with open(HStategrid.ota_path, 'wb') as file:
        #         ftp.retrbinary(f"RETR {HStategrid.ota_path}", file.write)
        #
        #     HSyslog.log_info(f"固件升级包已成功下载到 {HStategrid.ota_path}")
        #
        #     # 关闭连接
        #     ftp.quit()
        # except Exception as e:
        #     HSyslog.log_info(f"发生错误: {e}")

        charging = True
        for gun_info in HStategrid.Gun_list:
            if gun_info.get_gun_charge() != {}:
                charging = False
                break
        if charging:
            HStategrid.save_DeviceInfo("ota_device_version", HStategrid.DB_Data_Type.DATA_STR.value, ota_device_version, 0)
            if ota_ctrl == 1:
                info = {
                    "cmd_id": msg.get("cmd_id", 0),
                    "cmd_nums": msg.get("cmd_nums", 0),
                    "ota_result": 0,
                }
            elif ota_ctrl == 2:
                info = {
                    "cmd_id": msg.get("cmd_id", 0),
                    "cmd_nums": msg.get("cmd_nums", 0),
                    "ota_result": 0,
                }
            else:
                info = {
                    "cmd_id": msg.get("cmd_id", 0),
                    "cmd_nums": msg.get("cmd_nums", 0),
                    "ota_result": 0,
                }
            hhd_to_tpp_B3(info)
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "ota_result": 1,
            }
            hhd_to_tpp_B3(info)
            hhd_to_tpp_10({})
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_A3'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_A1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_43'msg error: {msg}. {e}")
        return False


def tpp_to_hhd_A2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"tpp_to_hhd_45'msg error: {msg}. {e}")
        return False


'''################################################### 发送数据处理 ####################################################'''


def hhd_to_tpp_51(msg):
    try:
        if HStategrid.get_DeviceInfo("storage_cap_limit") is not None and HStategrid.get_DeviceInfo("storage_cap_limit") != 0:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 0
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 1
            }
        HStategrid.tpp_cmd_51(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_51'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_52(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "system_time": msg.get("system_time")
        }
        HStategrid.tpp_cmd_52(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_52'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_56(msg):
    try:
        if HStategrid.get_DeviceInfo("server_host") is not None and HStategrid.get_DeviceInfo("server_host") != "":
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 0
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 1
            }
        HStategrid.tpp_cmd_56(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_56'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_58(msg):
    try:
        HStategrid.Heartbeat_class.set_send_heartbeat()
        info = {
            "cmd_id": 0,
            "cmd_nums": 0,
            "heart_index": HStategrid.Heartbeat_class.get_send_heartbeat(),
        }
        HStategrid.tpp_cmd_58(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_58'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_59(msg):
    try:
        if HStategrid.get_DeviceInfo("heart_interval") is not None and HStategrid.get_DeviceInfo("heart_interval") != 0:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "heart_interval": HStategrid.get_DeviceInfo("heart_interval"),
                "heart_timeout_num": HStategrid.get_DeviceInfo("heart_timeout_num"),
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "heart_interval": 3,
                "heart_timeout_num": 3,
            }
        HStategrid.tpp_cmd_59(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_59'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_50(msg):
    try:
        if HStategrid.get_DeviceInfo("heart_interval") is not None and HStategrid.get_DeviceInfo("heart_interval") != 0:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 0,
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "result": 1,
            }
        HStategrid.tpp_cmd_50(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_50'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_53(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "reboot": 1
        }
        HStategrid.tpp_cmd_53(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_53'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_10(msg):
    try:
        if HStategrid.get_DeviceInfo("ota_device_version") is None or HStategrid.get_DeviceInfo("ota_device_version") == "":
            info = {
                "device_id": HStategrid.Device_ID,
                "device_sn": "",
                "device_version": HStategrid.get_VerInfoEvt(HHhdlist.device_ctrl_type.DTU.value)[1],
                "boot_num": HStategrid.boot_num,
                "flash_room": 100,
                "device_run_time": (HStategrid.get_datetime_timestamp() - HStategrid.start_time) // 60,
                "start_time": HStategrid.start_time,
                "sign_time": HStategrid.get_datetime_timestamp(),
            }
        else:
            info = {
                "device_id": HStategrid.Device_ID,
                "device_sn": "",
                "device_version": HStategrid.get_DeviceInfo("ota_device_version"),
                "boot_num": HStategrid.boot_num,
                "flash_room": 100,
                "device_run_time": (HStategrid.get_datetime_timestamp() - HStategrid.start_time) // 60,
                "start_time": HStategrid.start_time,
                "sign_time": HStategrid.get_datetime_timestamp(),
            }
        HStategrid.tpp_cmd_10(info)
        for gun_info in HStategrid.Gun_list:
            gun_id = str("{:03}".format(gun_info.gun_id + 1))
            qrcode_list = HStategrid.gun_qrcode.split('.')
            qrcode_active_verification = HStategrid.get_DeviceInfo("qrcode_active_verification")
            if qrcode_active_verification is None or qrcode_active_verification == "":
                qrcode = f"{qrcode_list[0]}{gun_id}.{qrcode_list[1]}000000"
            else:
                qrcode = f"{qrcode_list[0]}{gun_id}.{qrcode_list[1]}{qrcode_active_verification}"
            gun_info.set_gun_qr(qrcode)
            HStategrid.save_DeviceInfo(f"qrcode_{gun_info.gun_id + 1}", HStategrid.DB_Data_Type.DATA_STR.value, qrcode, 0)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_10'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_11(msg):
    try:
        info = {
            "device_id": HStategrid.Device_ID,
            "work_status": HStategrid.Device_class.get_work_status(),
            "system_fault_code": HStategrid.Device_class.get_system_fault_code(),
            # "system_fault_code": 0x00000400,
            "device_1": 1,
            "device_2": 1,
            "device_3": 3,
            "device_4": 1,
            "device_5": 3,
            "device_6": 3,
            "device_7": 1,
            "device_8": 1,
        }
        HStategrid.tpp_cmd_11(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_11'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_15(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "param_type": msg.get("param_type"),
            "param_num": msg.get("param_num"),
            "param_list": msg.get("param_list"),
        }
        HStategrid.tpp_cmd_15(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_15'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_17(msg=None):
    try:
        if msg is None:
            power_model_list = []
            for gun_info in HStategrid.Gun_list:
                power_model_info = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "gun_max_vol": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}222") * 10,
                    "gun_min_vol": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}223") * 10,
                    "gun_max_cur": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}224") * 10 + 3200,
                    "gun_max_single_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(11, 0),
                    "bms_max_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(15, 0),
                    "bms_allow_charge": HHhdlist.bms.get(gun_info.gun_id, {}).get(113, 0),
                    "bms_need_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(100, 0),
                    "bms_need_cur": HHhdlist.bms.get(gun_info.gun_id, {}).get(101, 0) + 3200,
                    "bms_need_single_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(11, 0),
                    "bms_max_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(15, 0),
                    "bms_sdk_version": HHhdlist.bms.get(gun_info.gun_id, {}).get(0, 0),
                    "bms_battery_num": 0,
                    "bms_battery_series": 0,
                    "bms_battery_parallel": 0,
                    "bms_battery_cap": HHhdlist.bms.get(gun_info.gun_id, {}).get(2, 0) // 10,
                }
                power_model_list.append(power_model_info)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "power_model_list": power_model_list,
            }
            HStategrid.tpp_cmd_17(info)
        else:
            power_model_list = []
            for gun_info in HStategrid.Gun_list:
                power_model_info = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "gun_max_vol": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}222") * 10,
                    "gun_min_vol": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}223") * 10,
                    "gun_max_cur": HStategrid.get_DeviceInfo(f"2{gun_info.gun_id}224") * 10 + 3200,
                    "gun_max_single_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(11, 0),
                    "bms_max_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(15, 0),
                    "bms_allow_charge": HHhdlist.bms.get(gun_info.gun_id, {}).get(113, 0),
                    "bms_need_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(100, 0),
                    "bms_need_cur": HHhdlist.bms.get(gun_info.gun_id, {}).get(101, 0) + 3200,
                    "bms_need_single_vol": HHhdlist.bms.get(gun_info.gun_id, {}).get(11, 0),
                    "bms_max_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(15, 0),
                    "bms_sdk_version": HHhdlist.bms.get(gun_info.gun_id, {}).get(0, 0),
                    "bms_battery_num": 0,
                    "bms_battery_series": 0,
                    "bms_battery_parallel": 0,
                    "bms_battery_cap": HHhdlist.bms.get(gun_info.gun_id, {}).get(2, 0) // 10,
                }
                power_model_list.append(power_model_info)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": msg.get("gun_num"),
                "power_model_list": power_model_list,
            }
            HStategrid.tpp_cmd_17(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_17'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_18(msg=None):
    try:
        if msg is None:
            battery_list = []
            for gun_info in HStategrid.Gun_list:
                battery_info = {
                    "car_vin": gun_info.get_gun_charge_mode(),
                    "bms_id": 0,
                    "bms_battery_num": 0,
                    "bms_battery_list": [],
                }
                battery_list.append(battery_info)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "battery_list": battery_list,
            }
            HStategrid.tpp_cmd_18(info)
        else:
            battery_list = []
            for gun_info in HStategrid.Gun_list:
                battery_info = {
                    "car_vin": gun_info.get_gun_charge_mode(),
                    "bms_id": 0,
                    "bms_battery_num": 0,
                    "bms_battery_list": [],
                }
                battery_list.append(battery_info)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": msg.get("gun_num"),
                "battery_list": battery_list,
            }
            HStategrid.tpp_cmd_18(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_18'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_1A(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "cmd_param": msg.get("cmd_param"),
            "cmd_data": msg.get("cmd_data"),
            "result": 0,
        }
        HStategrid.tpp_cmd_1A(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_1A'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_F0(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "report_mode": msg.get("report_mode"),
            "report_interval": msg.get("report_interval"),
        }
        HStategrid.tpp_cmd_F0(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_F0'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_31(msg=None):
    try:
        if msg is None:
            output_wattless_power = 0
            output_active_power = 0
            for gun_info in HStategrid.Gun_list:
                output_wattless_power += HHhdlist.meter.get(gun_info.gun_id, {}).get(3, 0)
            for gun_info in HStategrid.Gun_list:
                output_active_power += HHhdlist.meter.get(gun_info.gun_id, {}).get(1, 0)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "input_power": 1,
                "average_temperature": 90,
                "out_temperature": 90,
                "work_status": HStategrid.Device_class.get_work_status(),
                # "work_status": 3,
                "power_model_num": HStategrid.get_DeviceInfo("00111"),
                "output_active_power": output_active_power // 100,
                "output_wattless_power": output_wattless_power // 100,
                "device_status": HStategrid.Device_class.get_device_status(),
                "device_fault_code": HStategrid.Device_class.get_device_fault_code(),
                # "device_fault_code": 0x00000020,
                "model_fault_status": HStategrid.Device_class.get_power_model_fault_code(),
                "fan_status": 2,
                "air_status": 2,
                "heater_status": 2,
                "smoke_status": 2,
                "shake_status": 2,
                "gun_num": HStategrid.get_DeviceInfo("00110"),
            }
            HStategrid.tpp_cmd_31(info)
        else:
            output_wattless_power = 0
            output_active_power = 0
            for gun_info in HStategrid.Gun_list:
                output_wattless_power += HHhdlist.meter.get(gun_info.gun_id, {}).get(3, 0)
            for gun_info in HStategrid.Gun_list:
                output_active_power += HHhdlist.meter.get(gun_info.gun_id, {}).get(1, 0)
            info = {
                "cmd_id": msg.get("cmd_id"),
                "cmd_nums": msg.get("cmd_nums"),
                "input_power": 1,
                "average_temperature": 90,
                "out_temperature": 90,
                "work_status": HStategrid.Device_class.get_work_status(),
                # "work_status": 3,
                "power_model_num": HStategrid.get_DeviceInfo("00111"),
                "output_active_power": output_active_power // 100,
                "output_wattless_power": output_wattless_power // 100,
                "device_status": HStategrid.Device_class.get_device_status(),
                "device_fault_code": HStategrid.Device_class.get_device_fault_code(),
                "model_fault_status": HStategrid.Device_class.get_power_model_fault_code(),
                "fan_status": 2,
                "air_status": 2,
                "heater_status": 2,
                "smoke_status": 2,
                "shake_status": 2,
                "gun_num": HStategrid.get_DeviceInfo("00110"),
            }
            HStategrid.tpp_cmd_31(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_31'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_32(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_32'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_33(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_33'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_34(msg=None):
    try:
        if msg is None:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "charge_carry_status": gun_info.get_gun_connect_status(),
                    "power_model_id": 0,
                    "bms_id": 0,
                    "charge_vol": HHhdlist.gun.get(gun_info.gun_id, {}).get(112, 0),
                    "charge_cur": HHhdlist.gun.get(gun_info.gun_id, {}).get(113, 0) + 3200,
                    "charge_power_kw": HHhdlist.gun.get(gun_info.gun_id, {}).get(115, 0) // 100,
                    "power_model_fault_code": HStategrid.Device_class.get_power_model_fault_code(),
                    # "power_model_fault_code": 0x00001000,
                    "charge_status": gun_info.get_gun_status(),
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_34(info)
        else:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "charge_carry_status": gun_info.get_gun_connect_status(),
                    "power_model_id": 0,
                    "bms_id": 0,
                    "charge_vol": HHhdlist.gun.get(gun_info.gun_id, {}).get(112, 0),
                    "charge_cur": HHhdlist.gun.get(gun_info.gun_id, {}).get(113, 0) + 3200,
                    "charge_power_kw": HHhdlist.gun.get(gun_info.gun_id, {}).get(115, 0) // 100,
                    "power_model_fault_code": HStategrid.Device_class.get_power_model_fault_code(),
                    "charge_status": gun_info.get_gun_status(),
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_34(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_34'msg error: {e}")
        return False


def hhd_to_tpp_35(msg=None):
    try:
        if msg is None:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "battery_fault_group_id": 0x55,
                    "battery_fault_grade": 0,
                    "battery_fault_list": [{
                        "battery_fault_code": 0,
                        # "battery_fault_code": 0x00000020,
                        "battery_fault_num": 0,
                        "battery_fault_location_list": []
                    }],
                    "battery_system_fault_group_id": 0x66,
                    "battery_system_fault_grade": 0,
                    "battery_system_fault_list": [{
                        "battery_system_fault_code": 0,
                        "battery_system_fault_num": 0,
                        "battery_system_fault_location_list": []
                    }],
                    "bms_fault_group_id": 0x77,
                    "bms_fault_grade": 0,
                    "bms_fault_list": [{
                        "bms_fault_code": 0,
                        "bms_fault_num": 0,
                        "bms_fault_location_list": []
                    }],
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_35(info)
        else:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "battery_fault_group_id": 0x55,
                    "battery_fault_grade": 0,
                    "battery_fault_list": [{
                        "battery_fault_code": 0,
                        "battery_fault_num": 0,
                        "battery_fault_location_list": []
                    }],
                    "battery_system_fault_group_id": 0x66,
                    "battery_system_fault_grade": 0,
                    "battery_system_fault_list": [{
                        "battery_system_fault_code": 0,
                        "battery_system_fault_num": 0,
                        "battery_system_fault_location_list": []
                    }],
                    "bms_fault_group_id": 0x77,
                    "bms_fault_grade": 0,
                    "bms_fault_list": [{
                        "bms_fault_code": 0,
                        "bms_fault_num": 0,
                        "bms_fault_location_list": []
                    }],
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_35(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_35'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_36(msg=None):
    try:
        if msg is None:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "battery_no": 0,
                    "battery_id": 0,
                    "battery_num": 0,
                    "battery_list": [],
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "cmd_type": 1,
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_36(info)
        else:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "battery_no": 0,
                    "battery_id": 0,
                    "battery_num": 0,
                    "battery_list": [],
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "cmd_type": msg.get("cmd_type", 1),
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_36(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_36'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_3B(msg=None):
    try:
        info = {
            "cmd_id": HStategrid.Device_ID,
            "cmd_nums": msg.get("cmd_nums", 0),
            "power_model_num": 0,
            "power_model_list": [{
                "power_model_no": 0,
                "meter_no": "",
                "meter_num": 0,
                "input_active_power": 0,
                "input_wattless_power": 0,
                "input_vol": 0,
                "input_cur": 0,
                "input_power_factor": 0,
                "input_harmonic_factor": 0,
                "input_fault_status": HStategrid.Device_class.get_device_fault_code(),
                "input_distribution_fault_status": 0,
                "input_distribution_switch": 2,
                "input_distribution_insurance": 2,
            }
            ]
        }
        HStategrid.tpp_cmd_3B(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_3B'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_39(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_39'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_3A(msg=None):
    try:
        if msg is None:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                if HStategrid.Gun_list[gun_info.gun_id].get_gun_status() in [1, 0, 4, 5]:
                    charge_lock_status = 2
                else:
                    charge_lock_status = 1
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "charge_lock_status": charge_lock_status,
                    "bms_id": 0,
                    "battery_vol": HHhdlist.gun.get(gun_info.gun_id, {}).get(112, 0),
                    "battery_cur": HHhdlist.gun.get(gun_info.gun_id, {}).get(113, 0) + 3200,
                    "max_battery_single_vol": 2000,
                    "min_battery_single_vol": 1200,
                    "max_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(109, 0),
                    "min_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(111, 0),
                    "max_battery_single_no": 10,
                    "min_battery_single_no": 5,
                    "max_battery_temperature_no": HHhdlist.bms.get(gun_info.gun_id, {}).get(110, 0),
                    "min_battery_temperature_no": HHhdlist.bms.get(gun_info.gun_id, {}).get(111, 0),
                    "gun_temperature": HHhdlist.gun.get(gun_info.gun_id, {}).get(122, 0),
                    "SOC1": HHhdlist.bms.get(gun_info.gun_id, {}).get(106, 0),
                    "work_status": HStategrid.Gun_list[gun_info.gun_id].get_gun_work_status(),
                    "charge_last_time": HHhdlist.bms.get(gun_info.gun_id, {}).get(107, 0),
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_3A(info)
        else:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                if HStategrid.Gun_list[gun_info.gun_id].get_gun_status() in [1, 0, 4, 5]:
                    charge_lock_status = 2
                else:
                    charge_lock_status = 1
                gun_status = {
                    "charge_mode": gun_info.get_gun_charge_mode(),
                    "charge_lock_status": charge_lock_status,
                    "bms_id": 0,
                    "battery_vol": HHhdlist.gun.get(gun_info.gun_id, {}).get(112, 0),
                    "battery_cur": HHhdlist.gun.get(gun_info.gun_id, {}).get(113, 0) + 3200,
                    "max_battery_single_vol": 2000,
                    "min_battery_single_vol": 1200,
                    "max_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(109, 0),
                    "min_battery_temperature": HHhdlist.bms.get(gun_info.gun_id, {}).get(111, 0),
                    "max_battery_single_no": 10,
                    "min_battery_single_no": 5,
                    "max_battery_temperature_no": HHhdlist.bms.get(gun_info.gun_id, {}).get(110, 0),
                    "min_battery_temperature_no": HHhdlist.bms.get(gun_info.gun_id, {}).get(111, 0),
                    "gun_temperature": HHhdlist.gun.get(gun_info.gun_id, {}).get(122, 0),
                    "SOC1": HHhdlist.bms.get(gun_info.gun_id, {}).get(106, 0),
                    "work_status": HStategrid.Gun_list[gun_info.gun_id].get_gun_work_status(),
                    "charge_last_time": HHhdlist.bms.get(gun_info.gun_id, {}).get(107, 0),
                }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_3A(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_3A'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_3F(msg=None):
    try:
        if msg is None:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                if gun_info.gun_charge_cost is False or gun_info.gun_charge_session is False:
                    gun_status = {
                        "charge_mode": gun_info.get_gun_charge_mode(),
                        "charge_power_kwh": 0,
                        "charge_power_kwh_add": 0,
                        "charge_power_ah": 0,
                        "charge_time": 0,
                        "charge_start_soc": 0,
                        "charge_now_soc": 0,
                        "charge_meter_num": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) // 10,
                        "charge_meter_num_add": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) % 10 * 10,
                    }
                else:
                    gun_status = {
                        "charge_mode": gun_info.get_gun_charge_mode(),
                        "charge_power_kwh": gun_info.get_gun_charge("total_energy") // 10,
                        "charge_power_kwh_add": gun_info.get_gun_charge("total_energy") % 10 * 10,
                        "charge_power_ah": 0,
                        "charge_time": gun_info.get_gun_charge("charge_time"),
                        "charge_start_soc": gun_info.get_gun_charge("start_soc"),
                        "charge_now_soc": HHhdlist.bms.get(gun_info.gun_id, {}).get(106, 0),
                        "charge_meter_num": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) // 10,
                        "charge_meter_num_add": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) % 10 * 10,
                    }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_3F(info)
        else:
            gun_status_list = []
            for gun_info in HStategrid.Gun_list:
                if gun_info.gun_charge_cost is False or gun_info.gun_charge_session is False:
                    gun_status = {
                        "charge_mode": gun_info.get_gun_charge_mode(),
                        "charge_power_kwh": 0,
                        "charge_power_kwh_add": 0,
                        "charge_power_ah": 0,
                        "charge_time": 0,
                        "charge_start_soc": 0,
                        "charge_now_soc": 0,
                        "charge_meter_num": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) // 10,
                        "charge_meter_num_add": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) % 10 * 10,
                    }
                else:
                    gun_status = {
                        "charge_mode": gun_info.get_gun_charge_mode(),
                        "charge_power_kwh": gun_info.get_gun_charge("total_energy") // 10,
                        "charge_power_kwh_add": gun_info.get_gun_charge("total_energy") % 10 * 10,
                        "charge_power_ah": 0,
                        "charge_time": gun_info.get_gun_charge("charge_time"),
                        "charge_start_soc": gun_info.get_gun_charge("start_soc"),
                        "charge_now_soc": HHhdlist.bms.get(gun_info.gun_id, {}).get(106, 0),
                        "charge_meter_num": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) // 10,
                        "charge_meter_num_add": HHhdlist.meter.get(gun_info.gun_id, {}).get(0, 0) % 10 * 10,
                    }
                gun_status_list.append(gun_status)
            info = {
                "cmd_id": msg.get("cmd_id", 0),
                "cmd_nums": msg.get("cmd_nums", 0),
                "gun_num": HHhdlist.gun_num,
                "gun_status_list": gun_status_list
            }
            HStategrid.tpp_cmd_3F(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_3F'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_70(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "cmd_id": 0,
            "cmd_nums": 0,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("card_id"),
            "user_certificate_type": 0,
            "user_certificate_id": "",
            "acceptance_channel": 0,
            "agency_id": "",
            "agency_code": "",
            "acceptance_operator_nums": "",
            "charge_date": HStategrid.get_datetime_timestamp(),
            "pay_password": HStategrid.Gun_list[gun_id].get_gun_charge("pay_password"),
            "gun_id": gun_id + 1,
            "server_fee": 0,
            "msg_code": 0,
        }
        HStategrid.tpp_cmd_70(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_70'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_71(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "cmd_id": 0,
            "cmd_nums": 0,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("user_card_id"),
            "charge_type": 0x20,
            "charge_date": HStategrid.get_datetime_timestamp(),
        }
        HStategrid.tpp_cmd_71(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_71'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_72(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "cmd_id": 0,
            "cmd_nums": 0,
            "power_model_num": 0,
            "charge_mode": HStategrid.Gun_list[gun_id].get_gun_charge_mode(),
            "battery_num": 0,
            "battery_list": [],
            "charge_date": HStategrid.get_datetime_timestamp(),
        }
        HStategrid.tpp_cmd_71(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_72'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_73(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_73'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_74(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "cmd_id": 0,
            "cmd_nums": 0,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("user_card_id"),
            "query_record_num": 10,
            "battery_num": 0,
            "battery_list": [],
            "charge_date": HStategrid.get_datetime_timestamp(),
        }
        HStategrid.tpp_cmd_74(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_74'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_75(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_75'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_78(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_78'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_7A(msg):
    try:
        gun_id = msg.get("gun_id")
        result = msg.get("result")
        if result == 1:
            info = {
                "cmd_id": HStategrid.Gun_list[gun_id].get_gun_charge("cmd_id_start"),
                "cmd_nums": HStategrid.Gun_list[gun_id].get_gun_charge("cmd_nums_start"),
                "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("user_card_id"),
                "user_certificate_type": 0,
                "user_certificate_id": "",
                "acceptance_channel": 0,
                "agency_id": "",
                "agency_code": "",
                "acceptance_operator_nums": "",
                "charge_date": HStategrid.Gun_list[gun_id].get_gun_charge("charge_date"),
                "gun_id": gun_id + 1,
                "result": msg.get("result"),
                "msg_code": HStategrid.Gun_list[gun_id].get_gun_charge("msg_code_start"),
            }
        else:
            info = {
                "cmd_id": msg.get("cmd_id"),
                "cmd_nums": msg.get("cmd_nums"),
                "user_card_id": msg.get("user_card_id"),
                "user_certificate_type": 0,
                "user_certificate_id": "",
                "acceptance_channel": 0,
                "agency_id": "",
                "agency_code": "",
                "acceptance_operator_nums": "",
                "charge_date": msg.get("charge_date"),
                "gun_id": msg.get("gun_id") + 1,
                "result": msg.get("result"),
                "msg_code": msg.get("msg_code"),
            }
        HStategrid.tpp_cmd_7A(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_7A'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_7B(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_7B'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_79(msg):
    try:
        order_list = HStategrid.get_HistoryOrder()
        for order_info in order_list:
            charge_id = order_info.get("charge_id")
            order = HStategrid.get_DeviceOrder_pa_id(charge_id)
            HStategrid.tpp_cmd_79(order)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_79'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_7F(msg):
    try:
        gun_id = msg.get("gun_id")
        gun_list = HStategrid.Gun_list[gun_id].get_gun_charge_gun_id()
        if len(gun_list) > 1:
            for gun_id in gun_list:
                if HStategrid.Gun_list[gun_id].get_gun_charge_order() == {}:
                    return False
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "charge_mode": HStategrid.Gun_list[gun_id].get_gun_charge_mode(),
                "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("user_card_id"),
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "charge_book_id": "",
                "device_id": HStategrid.Device_ID,
                "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge_order("vin"),
                "car_card": HStategrid.Gun_list[gun_id].get_gun_charge("car_card"),
                "charge_start_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_soc"),
                "charge_stop_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_soc"),
                "charge_power_ah": 0,
                "charge_power_kwh": 0,
                "charge_power_kwh_add": 0,
                "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_order("charge_time"),
                "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                "is_normal_stop": HHhdlist.get_stop_reason(HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_reason")),
                "charge_start_date": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_time"),
                "charge_stop_date": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_time"),
                "charge_date": HStategrid.Gun_list[gun_id].get_gun_charge("charge_date"),
                "charge_start_meter": 0,
                "charge_start_meter_add": 0,
                "charge_stop_meter": 0,
                "charge_stop_meter_add": 0,
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            }
            for gun_id in gun_list:
                info["charge_power_kwh"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy") // 10
                info["charge_power_kwh_add"] += HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy") % 10 * 10
        else:
            is_normal_stop = int(HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id")[-4:])
            info = {
                "cmd_id": 0,
                "cmd_nums": 0,
                "charge_mode": HStategrid.Gun_list[gun_id].get_gun_charge_mode(),
                "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("user_card_id"),
                "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
                "charge_book_id": "",
                "device_id": HStategrid.Device_ID,
                "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge_order("vin"),
                "car_card": HStategrid.Gun_list[gun_id].get_gun_charge("car_card"),
                "charge_start_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_soc"),
                "charge_stop_soc": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_soc"),
                "charge_power_ah": 0,
                "charge_power_kwh": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy") // 10,
                "charge_power_kwh_add": HStategrid.Gun_list[gun_id].get_gun_charge_order("total_energy") % 10 * 10,
                "charge_time": HStategrid.Gun_list[gun_id].get_gun_charge_order("charge_time"),
                "charge_policy": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy"),
                "charge_policy_param": HStategrid.Gun_list[gun_id].get_gun_charge("charge_policy_param"),
                "is_normal_stop": HHhdlist.get_stop_reason(HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_reason")),
                # "is_normal_stop": 18,
                "charge_start_date": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_time"),
                "charge_stop_date": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_time"),
                # "charge_date": HStategrid.Gun_list[gun_id].get_gun_charge("charge_date"),
                "charge_date": HStategrid.get_datetime_timestamp(),
                "charge_start_meter": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_meter_value") // 10,
                "charge_start_meter_add": HStategrid.Gun_list[gun_id].get_gun_charge_order("start_meter_value") % 10 * 10,
                "charge_stop_meter": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_meter_value") // 10,
                "charge_stop_meter_add": HStategrid.Gun_list[gun_id].get_gun_charge_order("stop_meter_value") % 10 * 10,
                "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
                "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            }
        HStategrid.tpp_cmd_7F(info)
        HStategrid.save_DeviceOrder(info)
        HStategrid.Gun_list[gun_id].set_gun_status(HStategrid.Gun_Status.Charge_end.value)

        order_confirm_is = {
            "gun_id": gun_id,
            "charge_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            "device_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("device_session_id"),
            "cloud_session_id": HStategrid.Gun_list[gun_id].get_gun_charge_order("cloud_session_id"),
            "confirm_is": 0,
        }
        HStategrid.save_HistoryOrder(order_confirm_is)
        for gun in gun_list:
            info = {
                "gun_id": gun,
                "cloud_session_id": HStategrid.Gun_list[gun].get_gun_charge("cloud_session_id"),
                "device_session_id": HStategrid.Gun_list[gun].get_gun_charge("device_session_id"),
                "result": 0
            }
            HHhdlist.platform_device_data.put([HHhdlist.topic_hqc_main_event_reply_charge_record, info])
            HStategrid.Gun_list[gun].empty_gun_charge()
            HStategrid.Gun_list[gun].empty_gun_charge_order()
            HStategrid.Gun_list[gun].gun_charge_cost = False
            HStategrid.Gun_list[gun].gun_charge_session = False
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_7F'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_7D(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "cmd_id": 0,
            "cmd_nums": gun_id + 100,
            "device_id": HStategrid.Device_ID,
            "work_status": HStategrid.Gun_list[gun_id].get_gun_charge("gun_charge_mode"),
            "gun_id": gun_id + 1,
            "car_vin": HStategrid.Gun_list[gun_id].get_gun_charge("car_vin"),
            "charge_date": HStategrid.get_datetime_timestamp(),
        }
        HStategrid.Gun_list[gun_id].set_gun_charge({"cmd_nums_check": info.get("cmd_nums")})
        HStategrid.tpp_cmd_7D(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_7D'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_90(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_90'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_92(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_92'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_93(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_93'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_94(msg):
    try:
        charge_record_start = msg.get("charge_record_start")
        charge_record_num = msg.get("charge_record_num")
        info_list = HStategrid.get_DeviceOrder()
        if len(info_list) < charge_record_num:
            for order in range(charge_record_start, len(info_list)):
                info_list[order].update({"charge_record_no": order + 1})
                info = {
                    "cmd_id": msg.get("cmd_id"),
                    "cmd_nums": msg.get("cmd_nums"),
                    "charge_record_num": len(info_list),
                    "charge_record_list": [info_list[order]],
                }
                HStategrid.tpp_cmd_94(info)
        else:
            for order in range(charge_record_start, charge_record_num):
                info_list[order].update({"charge_record_no": order + 1})
                info = {
                    "cmd_id": msg.get("cmd_id"),
                    "cmd_nums": msg.get("cmd_nums"),
                    "charge_record_num": charge_record_num,
                    "charge_record_list": [info_list[order]],
                }
                HStategrid.tpp_cmd_94(info)

    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_94'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_96(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_96'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_97(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": gun_id + 1,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("card_id"),
            "charge_random": "",
            "physical_cord_id": ""
        }
        HStategrid.tpp_cmd_97(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_97'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_98(msg):
    try:
        gun_id = msg.get("gun_id")
        info = {
            "device_id": HStategrid.Device_ID,
            "gun_id": msg.get("gun_id") + 1,
            "user_card_id": HStategrid.Gun_list[gun_id].get_gun_charge("card_id"),
        }
        HStategrid.tpp_cmd_36(info)
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_98'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_F1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_F1'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_F2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_F2'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_D1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_D1'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_D2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_D2'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_D3(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_D3'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_B3(msg):
    try:
        info = {
            "cmd_id": msg.get("cmd_id", 0),
            "cmd_nums": msg.get("cmd_nums", 0),
            "ota_result": msg.get("ota_result"),
        }
        HStategrid.tpp_cmd_B3(info)
        if msg.get("ota_result") == 0:
            time.sleep(3)
            subprocess.run(['supervisorctl', 'restart', 'internal_ocpp'])
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_B3'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_B1(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_B1'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_B2(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_B2'msg error: {msg}. {e}")
        return False


def hhd_to_tpp_B9(msg):
    try:
        pass
    except Exception as e:
        HSyslog.log_error(f"hhd_to_tpp_B9'msg error: {msg}. {e}")
        return False


'''################################################# 数据处理函数索引 ##################################################'''

hhd_to_tpp = {
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_51.value: hhd_to_tpp_51,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_52.value: hhd_to_tpp_52,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_56.value: hhd_to_tpp_56,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_58.value: hhd_to_tpp_58,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_59.value: hhd_to_tpp_59,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_50.value: hhd_to_tpp_50,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_53.value: hhd_to_tpp_53,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_10.value: hhd_to_tpp_10,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_11.value: hhd_to_tpp_11,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_15.value: hhd_to_tpp_15,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_17.value: hhd_to_tpp_17,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_18.value: hhd_to_tpp_18,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_1A.value: hhd_to_tpp_1A,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_F0.value: hhd_to_tpp_F0,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_31.value: hhd_to_tpp_31,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_32.value: hhd_to_tpp_32,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_33.value: hhd_to_tpp_33,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_34.value: hhd_to_tpp_34,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_35.value: hhd_to_tpp_35,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_36.value: hhd_to_tpp_36,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_3B.value: hhd_to_tpp_3B,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_39.value: hhd_to_tpp_39,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_3A.value: hhd_to_tpp_3A,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_3F.value: hhd_to_tpp_3F,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_70.value: hhd_to_tpp_70,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_71.value: hhd_to_tpp_71,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_72.value: hhd_to_tpp_72,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_73.value: hhd_to_tpp_73,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_74.value: hhd_to_tpp_74,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_75.value: hhd_to_tpp_75,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_78.value: hhd_to_tpp_78,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_7A.value: hhd_to_tpp_7A,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_7B.value: hhd_to_tpp_7B,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_79.value: hhd_to_tpp_79,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_7F.value: hhd_to_tpp_7F,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_7D.value: hhd_to_tpp_7D,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_90.value: hhd_to_tpp_90,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_92.value: hhd_to_tpp_92,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_93.value: hhd_to_tpp_93,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_94.value: hhd_to_tpp_94,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_96.value: hhd_to_tpp_96,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_97.value: hhd_to_tpp_97,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_98.value: hhd_to_tpp_98,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_F1.value: hhd_to_tpp_F1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_F2.value: hhd_to_tpp_F2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_D1.value: hhd_to_tpp_D1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_D2.value: hhd_to_tpp_D2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_D3.value: hhd_to_tpp_D3,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_B3.value: hhd_to_tpp_B3,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_B1.value: hhd_to_tpp_B1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_B2.value: hhd_to_tpp_B2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_B9.value: hhd_to_tpp_B9,
}

tpp_to_hhd = {
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_41.value: tpp_to_hhd_41,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_42.value: tpp_to_hhd_42,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_46.value: tpp_to_hhd_46,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_48.value: tpp_to_hhd_48,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_49.value: tpp_to_hhd_49,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_40.value: tpp_to_hhd_40,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_43.value: tpp_to_hhd_43,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_01.value: tpp_to_hhd_01,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_05.value: tpp_to_hhd_05,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_07.value: tpp_to_hhd_07,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_08.value: tpp_to_hhd_08,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_09.value: tpp_to_hhd_09,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_0A.value: tpp_to_hhd_0A,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_E0.value: tpp_to_hhd_E0,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_21.value: tpp_to_hhd_21,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_22.value: tpp_to_hhd_22,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_23.value: tpp_to_hhd_23,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_24.value: tpp_to_hhd_24,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_25.value: tpp_to_hhd_25,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_26.value: tpp_to_hhd_26,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_2B.value: tpp_to_hhd_2B,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_60.value: tpp_to_hhd_60,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_61.value: tpp_to_hhd_61,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_62.value: tpp_to_hhd_62,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_63.value: tpp_to_hhd_63,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_64.value: tpp_to_hhd_64,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_65.value: tpp_to_hhd_65,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_68.value: tpp_to_hhd_68,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_69.value: tpp_to_hhd_69,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6A.value: tpp_to_hhd_6A,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6C.value: tpp_to_hhd_6C,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6B.value: tpp_to_hhd_6B,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6F.value: tpp_to_hhd_6F,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_6D.value: tpp_to_hhd_6D,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_80.value: tpp_to_hhd_80,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_86.value: tpp_to_hhd_86,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_87.value: tpp_to_hhd_87,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_88.value: tpp_to_hhd_88,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_E1.value: tpp_to_hhd_E1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_E2.value: tpp_to_hhd_E2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_C1.value: tpp_to_hhd_C1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_C2.value: tpp_to_hhd_C2,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_C3.value: tpp_to_hhd_C3,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_A3.value: tpp_to_hhd_A3,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_A1.value: tpp_to_hhd_A1,
    HStategrid.tpp_mqtt_cmd_enum.tpp_cmd_type_A2.value: tpp_to_hhd_A2,
}
