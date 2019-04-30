from bluepy.btle import BTLEException, BTLEDisconnectError, Peripheral, Scanner, DefaultDelegate
from .data import calculate_ecg, calculate_motion, calculate_respiration, calculate_temperature, calculate_battery

temperatureHandle = -1
ecgHandle = -1
respirationHandle = -1
batteryHandle = -1
motionHandle = -1
_callback = None

scanner = None

class ScanDelegate(DefaultDelegate):
    def __init(self):
        DefaultDelegate.__init(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device {}".format(dev.addr))
        elif isNewData:
            print("Received new data from {}".format(dev.addr))


class NotificationHandler(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        global _callback

        if temperatureHandle == cHandle:
            temperature = calculate_temperature(data)
            _callback("temperature", temperature)
        elif ecgHandle == cHandle:
            ecg = calculate_ecg(data)
            _callback("ecg", ecg)
        elif batteryHandle == cHandle:
            battery = calculate_battery(data)
            _callback("battery", battery)
        elif respirationHandle == cHandle:
            respiration = calculate_respiration(data)
            _callback("respiration", respiration)
        elif motionHandle == cHandle:
            motion = calculate_motion(data)
            _callback("motion", motion)


def connect(characteristics, callback, aidlabsMAC=None):
    global _callback

    _callback = callback

    if aidlabsMAC is None:
        aidlabsMAC = scan_for_aidlab()

    if aidlabsMAC is None:
        print("Could not find Aidlabs nearby")
        return

    for aidlabMAC in aidlabsMAC:
        connect_to_aidlab(characteristics, aidlabMAC)

def subscribe_to_characteristic(service, peripheral, characteristicUUID):
    characteristic = service.getCharacteristics(characteristicUUID)[0]
    characteristicHandler = characteristic.getHandle()
    peripheral.writeCharacteristic(characteristicHandler+1, b"\x01\x00", True)
    return characteristicHandler

def connect_to_aidlab(characteristics, aidlabMAC):
    global temperatureHandle, ecgHandle, batteryHandle, respirationHandle, motionHandle

    try:
        peripheral = Peripheral(aidlabMAC)
        print("Connected")
    except BTLEException:
        print("Could not connect to Aidlab")
        return

    peripheral.withDelegate(NotificationHandler())
    userServiceUUID = "44366E80-CF3A-11E1-9AB4-0002A5D5C51B"
    userService = peripheral.getServiceByUUID(userServiceUUID)

    for characteristic in characteristics:
        if characteristic == "temperature":
            temperatureHandle = subscribe_to_characteristic(userService, peripheral, "45366E80-CF3A-11E1-9AB4-0002A5D5C51B")
        elif characteristic == "ecg":
            ecgHandle = subscribe_to_characteristic(userService, peripheral, "46366E80-CF3A-11E1-9AB4-0002A5D5C51B")
        elif characteristic == "battery":
            batteryHandle = subscribe_to_characteristic(userService, peripheral, "47366E80-CF3A-11E1-9AB4-0002A5D5C51B")
        elif characteristic == "respiration":
            respirationHandle = subscribe_to_characteristic(userService, peripheral, "48366E80-CF3A-11E1-9AB4-0002A5D5C51B")
        elif characteristic == "motion":
            motionHandle = subscribe_to_characteristic(userService, peripheral, "49366E80-CF3A-11E1-9AB4-0002A5D5C51B")

    while True:
        try:
            if peripheral.waitForNotifications(1.0):
                continue
        except BTLEDisconnectError:
            pass


def scan_for_aidlab():
    scanner = Scanner().withDelegate(ScanDelegate())

    print("Scanning for Aidlab (timeout = 10 seconds) ...")
    devices = scanner.scan(10.0)

    aidlabs = []

    for dev in devices:
        print("Device {}, {}".format(dev.addr, dev.addrType))

        for value in dev.getScanData():
            if value == "Aidlab":
                aidlabs.append(dev.addr)

    return aidlabs
