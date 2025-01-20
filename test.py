# import HStategrid
#
# for gun in range(0,2):
#     gun_id = str("{:03}".format(gun + 1))
#     qrcode_list = HStategrid.gun_qrcode.split('.')
#     qrcode_active_verification = HStategrid.get_DeviceInfo("qrcode_active_verification")
#     if qrcode_active_verification is None or qrcode_active_verification == "":
#         qrcode = f"{qrcode_list[0]}{gun_id}.{qrcode_list[1]}000000"
#     else:
#         qrcode = f"{qrcode_list[0]}{gun_id}.{qrcode_list[1]}{qrcode_active_verification}"
#     HStategrid.save_DeviceInfo(f"qrcode_{gun + 1}", HStategrid.DB_Data_Type.DATA_STR.value, qrcode, 0)
#     print(qrcode)
import HHhdlist
import HStategrid

HStategrid.delete_DeviceOrder()
