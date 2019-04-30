from time import sleep
import time
from pyble.handlers import PeripheralHandler, ProfileHandler
from .data import calculate_ecg, calculate_motion, calculate_respiration, calculate_temperature, calculate_battery
import pyble
import uuid
import sys

# Disable logging
import logging
logging.disable(sys.maxsize)

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

        peripheralUUID = characteristic.service.peripheral.UUID
        characteristicUUID = characteristic.UUID

        if characteristicUUID == "45366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            temperature = calculate_temperature(data)
            _callback(peripheralUUID, "temperature", temperature)
        elif characteristicUUID == "46366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            ecg = calculate_ecg(data)
            _callback(peripheralUUID, "ecg", ecg)
        elif characteristicUUID == "47366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            battery = calculate_battery(data)
            _callback(peripheralUUID, "battery", battery)
        elif characteristicUUID == "48366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            respiration = calculate_respiration(data)
            _callback(peripheralUUID, "respiration", respiration)
        elif characteristicUUID == "49366E80-CF3A-11E1-9AB4-0002A5D5C51B":
            motion = calculate_motion(data)
            _callback(peripheralUUID, "motion", motion)


class AidlabPeripheral(PeripheralHandler):

    def initialize(self):
        self.addProfileHandler(UserService)

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_rssi(self, value):
        pass

def connect_to_aidlab(cm, target, characteristics):
    target.delegate = AidlabPeripheral
    p = cm.connectPeripheral(target)
    print("Connected to {}".format(target.UUID))

    for characteristic in characteristics:
        if characteristic == "temperature":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["45366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        elif characteristic == "ecg":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["46366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        elif characteristic == "respiration":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["47366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        elif characteristic == "battery":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["48366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        elif characteristic == "motion":
            p["44366E80-CF3A-11E1-9AB4-0002A5D5C51B"]["49366E80-CF3A-11E1-9AB4-0002A5D5C51B"].notify = True
        else:
            print("Characteristic {} not supported".format(characteristic))

def connect(characteristics, callback, aidlabUUIDs=None):
    global _callback
    _callback = callback
    
    # Init Central Manager
    cm = pyble.CentralManager()
    if not cm.ready:
        print("Central Manager not ready")
        return

    print("Connecting ...")

    target = None

    if aidlabUUIDs: # Connect to every discoverable Aidlab
       
        # Map aidlabUUIDs string to Python's UUID
        uuids = []
        for aidlabUUID in aidlabUUIDs:
            uuids.append(uuid.UUID("{"+aidlabUUID+"}"))
        
        # Iterate till we will connect with all Aidlabs from the list
        while uuids > 0:
            target = cm.startScan()
            if target and target.UUID in uuids:
                
                # We don't that UUID any longer
                uuids.remove(target.UUID)

                # Connect to the target (Aidlab)
                connect_to_aidlab(cm, target, characteristics)

                # Log how many Aidlab left to connect
                connected_count = len(aidlabUUIDs) - len(uuids)
                print("Connection [{}/{}]".format(connected_count, len(aidlabUUIDs)))

    else: # Connect to all Aidlabs from `aidlabUUIDs` list
        while True:
            try:
                target = cm.startScan()
                if target and target.name == "Aidlab":
                    connect_to_aidlab(cm, target, characteristics)
            except Exception as e:
                print(e)