def calculate_temperature(data):
    bytes = bytearray(data)

    Tobj = float( int(bytes[1]) << 8 | int(bytes[0]) )
    Tobj *= 0.02
    Tobj -= 273.15
    
    Tamb = float( int(bytes[3]) << 8 | int(bytes[2]) )
    Tamb *= 0.02
    Tamb -= 273.15
        
    return [Tobj, Tamb]

def calculate_respiration(data):
    # We can resue `calculate_ecg`
    return calculate_ecg(data)

def calculate_ecg(data):
    bytesPerSample = 3
    totalBytes = 18

    ecgs = []
    for i in range(0, totalBytes/bytesPerSample):
        byteA = bytearray(data)[i*bytesPerSample + 2]
        byteB = bytearray(data)[i*bytesPerSample + 1]
        byteC = bytearray(data)[i*bytesPerSample + 0]
        ecgs.append(ecg_sample_from_bytes(byteA, byteB, byteC))
    
    return ecgs

def ecg_sample_from_bytes(byteA, byteB, byteC):

    # First, convert number from U2
    out = 0
    if (byteA & 0x80) == 0x80:  # If negative, we need to extend sign
        out = (0xff << 24) | (byteA << 16) | (byteB << 8) | byteC
    else:
        out = (byteA << 16) | (byteB << 8) | byteC

    # Then, multiple the value by the resolution
    # Where resolution is Vref / Gain / Bit resolution:
    # 2 * 2.42 / 6 / 2^24
    resolution = 0.00000004808108011881510416
    sampleInVolts = out * resolution

    sampleInVolts *= -1

    return sampleInVolts

def q16ToFloat(byteA, byteB, byteC, byteD):
    q16 = (byteA & 0xFF) << 24 | (byteB & 0xFF) << 16 | (
        byteC & 0xFF) << 8 | (byteD & 0xFF)
    return q16 / float(1 << 16)

def toSigned32(n):
    n = n & 0xffffffff
    return n | (-(n & 0x80000000))

def q30ToFloat(byteA, byteB, byteC, byteD):
    q30 = (byteA & 0xFF) << 24 | (byteB & 0xFF) << 16 | (
        byteC & 0xFF) << 8 | (byteD & 0xFF)
    q30 = toSigned32(q30)
    return q30 / float(1 << 30)
    
def calculate_battery(data):
    bytes = bytearray(data)
    return float( int(bytes[1]) << 8 | int(bytes[0]) ) / 10.0

def calculate_motion(data):

    scratchVal = bytearray(data)

    # Quaternion
    qw = q30ToFloat(scratchVal[0], scratchVal[1], 0, 0)
    qx = q30ToFloat(scratchVal[2], scratchVal[3], 0, 0)
    qy = q30ToFloat(scratchVal[4], scratchVal[5], 0, 0)
    qz = q30ToFloat(scratchVal[6], scratchVal[7], 0, 0)

    # Accelerometer
    ax = q16ToFloat(
        scratchVal[8], scratchVal[9], scratchVal[10], scratchVal[11])
    ay = q16ToFloat(
        scratchVal[12], scratchVal[13], scratchVal[14], scratchVal[15])
    az = q16ToFloat(
        scratchVal[16], scratchVal[17], scratchVal[18], scratchVal[19])

    return [qw, qx, qy, qz, ax, ay, az]
