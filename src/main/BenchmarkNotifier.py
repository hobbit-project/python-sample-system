import bitstring

from main.AbstractCommandReceivingComponent import AbstractCommandReceivingComponent

DOCKER_CONTAINER_TERMINATED = 16

class BenchmarkNotifier(AbstractCommandReceivingComponent):

    imageName=None
    def __init__(self, imageName):
        self.imageName = imageName

    def on_channels_ready(self, channel):
        super().on_channels_ready(channel)
        if self.readyChannels==1:
            print("Sending DOCKER_CONTAINER_TERMINATED signal")

            stream = bitstring.BitStream()
            stream.append(b"")
            stream.append("int:32=" + str(len(self.imageName)))
            stream.append(bytearray(self.imageName, encoding="utf-8"))
            stream.append("int:8=" + str(0))
            self.sendCmdToQueue(DOCKER_CONTAINER_TERMINATED, stream.bytes)
            self.terminate()


