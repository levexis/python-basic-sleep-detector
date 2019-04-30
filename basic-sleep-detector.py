from Aidlab import AidlabBLECommunication as aidlab
from time import sleep, time
from datetime import datetime


def onReceivedCharacteristic(aidlab, name, value):
    if name == "motion":
        naiveSleepDetector(value)


def naiveSleepDetector(value):

    quaternion = value[0:4]

    verticalOrientation = determineVerticalOrientation(
        quaternion[0], quaternion[1], quaternion[2], quaternion[3])

    # Sleep detection heuristic
    basicSleepDetector(verticalOrientation)


def determineVerticalOrientation(qW, qX, qY, qZ):

    normalVec = normalVectorToUp(qW, qX, qY, qZ)

    if normalVec[2] >= 0.5:
        return "OrientationDown"
    elif normalVec[2] <= -0.5:
        return "OrientationUp"
    else:
        return "OrientationFront"


def normalVectorToUp(qW, qX, qY, qZ):

    quat = multQuat(qW, qX, qY, qZ, 0, 0, 0, 1)
    quat = multQuat(quat[0], quat[1], quat[2], quat[3], qW, -qX, -qY, -qZ)

    return [quat[1], quat[2], quat[3]]


def multQuat(w, x, y, z, qW, qX, qY, qZ):

    newW = w * qW - x * qX - y * qY - z * qZ
    newX = w * qX + x * qW + y * qZ - z * qY
    newY = w * qY + y * qW + z * qX - x * qZ
    newZ = w * qZ + z * qW + x * qY - y * qX

    return [newW, newX, newY, newZ]


startTimeOfSleepingPosition = 0
isInSleepingPosition = False


def basicSleepDetector(verticalOrientation):
    global startTimeOfSleepingPosition, isInSleepingPosition

    if (verticalOrientation == 'OrientationUp' or verticalOrientation == 'OrientationDown') and isInSleepingPosition == False:
        isInSleepingPosition = True
        startTimeOfSleepingPosition = time()

    elif verticalOrientation == 'OrientationFront' and isInSleepingPosition:
        startTimeOfSleepingPosition = 0
        isInSleepingPosition = False

    # Sleep detection heuristic:
    # We are sleeping if we are in sleeping position for longer than 10 minutes
    if isInSleepingPosition and (time() - startTimeOfSleepingPosition > 10 * 60):
        print("I am sleeping")


aidlab.connect(["motion"], onReceivedCharacteristic)
