from time import sleep
import time
from pyble.handlers import PeripheralHandler, ProfileHandler
from .data import calculate_ecg, calculate_motion
import pyble
import uuid
import sys
sys.dont_write_bytecode = True


_callback = None


class UserService(ProfileHandler):
    UUID = "44366E80-CF3A-11E1-9AB4-0002A5D5C51B"
    _AUTOLOAD = True
    names = {
        "45366E80-CF3A-11E1-9AB4-0002A5D5C51B": "Temperature Characteristic",
        "46366E80-CF3A-11E1-9AB4-0002A5D5C51B": "ECG Characteristic",
        "47366E80-CF3A-11E1-9AB4-0002A5D5C51B": "Battery Characteristic",
        "48366E80-CF3A-11E1-9AB4-0002A5D5C51B": "Respiration Characteristic",
        "49366E80-CF3A-11E1-9AB4-0002A5D5C51B": "Motion Characteristic"
    }

    def initialize(self):
        pass

    def on_notify(self, characteristic, data):
        cUUID = characteristic.UUID
        if cUUID == "46366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            ecg = calculate_ecg(data)
            _callback("ecg", ecg)
        elif cUUID == "49366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            motion = calculate_motion(data)
            _callback("motion", motion)


class AidlabPeripheral(PeripheralHandler):

    def initialize(self):
        self.addProfileHandler(UserService)

    def on_connect(self):
        print("on_connect")

    def on_disconnect(self):
        print("on_disconnect")

    def on_rssi(self, value):
        print("on_rssi")


def connect(characteristics, callback, aidlabUUID=None):
    global _callback
    _callback = callback
    cm = pyble.CentralManager()
    if not cm.ready:
        return
    target = None
    while True:
        try:
            target = cm.startScan()
            if target and aidlabUUID and target.UUID == uuid.UUID("{"+aidlabUUID+"}"):
                break
            elif target and target.name == "Aidlab":
                break
        except Exception as e:
            print(e)

        # Aidlab not found? Try again later ...
        sleep(1)

    target.delegate = AidlabPeripheral
    p = cm.connectPeripheral(target)

    for characteristic in characteristics:
        if characteristic == "ecg":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["46366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        elif characteristic == "motion":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["49366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        else:
            print("Characteristic {} not supported".format(characteristic))

    cm.loop()
