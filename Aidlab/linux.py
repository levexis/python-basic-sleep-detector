from bluepy.btle import BTLEException, BTLEDisconnectError, Peripheral, Scanner, DefaultDelegate
from .data import calculate_ecg, calculate_motion

ecgHandle = -1
motionHandle = -1
_callback = None


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

        if ecgHandle == cHandle:
            ecg = calculate_ecg(data)
            _callback("ecg", ecg)
        elif motionHandle == cHandle:
            motion = calculate_motion(data)
            _callback("motion", motion)


def connect(characteristics, callback, aidlabMAC=None):
    global _callback

    _callback = callback

    if aidlabMAC is None:
        aidlabMAC = scan_for_aidlab()

    if aidlabMAC is None:
        print("Could not find Aidlab with MAC: {}".format(aidlabMAC))
        return

    connect_to_aidlab(characteristics, aidlabMAC)


def connect_to_aidlab(characteristics, aidlabMAC):
    global motionHandle, ecgHandle

    try:
        peripheral = Peripheral(aidlabMAC)
        print("Connected")
    except BTLEException:
        print("Could not connect to Aidlab")
        return

    peripheral.withDelegate(NotificationHandler())
    svc = peripheral.getServiceByUUID("44366E80-CF3A-11E1-9AB4-0002A5D5C51B")

    for characteristic in characteristics:
        if characteristic == "ecg":
            ch = svc.getCharacteristics(
                "46366E80-CF3A-11E1-9AB4-0002A5D5C51B")[0]
            ecgHandle = ch.getHandle()
            peripheral.writeCharacteristic(motionHandle+1, b"\x01\x00", True)
        elif characteristic == "motion":
            ch = svc.getCharacteristics(
                "49366E80-CF3A-11E1-9AB4-0002A5D5C51B")[0]
            motionHandle = ch.getHandle()
            peripheral.writeCharacteristic(motionHandle+1, b"\x01\x00", True)

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

    for dev in devices:
        print("Device {}, {}".format(dev.addr, dev.addrType))

        for value in dev.getScanData():
            if value == "Aidlab":
                return dev.addr
