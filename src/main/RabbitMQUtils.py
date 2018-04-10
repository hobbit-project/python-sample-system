from io import BytesIO

def readInt(buffer):
    return rabbitGetRequired(buffer, 0)[0]

def readByteArray(buffer):
    return rabbitGetRequired(buffer, 0)

def readString(buffer):
    accumulated = list(rabbitGetRequired(buffer, 19))
    ret = "".join(map(chr, accumulated))
    return ret



def rabbitGetRequired(buffer: BytesIO, skip):
    accumulated = []
    #ints = list(buffer.getvalue())

    readed=0
    byte = buffer.read(1)
    while True:
        listed = list(byte)
        if len(listed)>0:
            if (listed[0] > skip):
                #accumulated.append(byte)
                accumulated.append(listed[0])
            elif len(accumulated) > 0 :
                break
        else:
            break
        byte = buffer.read(1)
        readed+=1
    buffer.seek(readed)
    return accumulated