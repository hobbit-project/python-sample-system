import io
import json
import os
import signal
import sys

import bitstring

from main.supplementary import RabbitMQUtils
from main.supplementary.AbstractCommandReceivingComponent import AbstractCommandReceivingComponent

DOCKER_CONTAINER_START = 12
DOCKER_CONTAINER_STOP = 13
DOCKER_CONTAINER_TERMINATED = 16
BENCHMARK_FINISHED_SIGNAL = 11

class HobbitCommandsListener(AbstractCommandReceivingComponent):

    imageName=None
    component=None
    benchProc=None

    def __init__(self, component, imageName):
        self.component = component
        self.imageName = imageName


    def commandReceivedCallback(self, ch, method, properties, body):
        buffer = io.BytesIO(body)
        sessionId = RabbitMQUtils.readString(buffer)
        if sessionId==self.sessionId:
            command = RabbitMQUtils.readByte(buffer)
            if command==DOCKER_CONTAINER_START:
                containerStartCommand = RabbitMQUtils.readString(buffer)
                jsonObj = json.loads(containerStartCommand)
                if self.imageName == jsonObj["image"]:

                    for var in jsonObj["environmentVariables"]:
                        splitted = var.split("=")
                        os.environ[splitted[0]] = splitted[1]

                    self.component.init()
                    self.component.run()
                    print("Sending DOCKER_CONTAINER_TERMINATED signal")

                    stream = bitstring.BitStream()
                    stream.append(b"")
                    stream.append("int:32=" + str(len(self.imageName)))
                    stream.append(bytearray(self.imageName, encoding="utf-8"))
                    stream.append("int:8=" + str(0))
                    self.component.terminate()
                    self.sendCmdToQueue(DOCKER_CONTAINER_TERMINATED, stream.bytes)


            if command == BENCHMARK_FINISHED_SIGNAL:
                print("BENCHMARK_FINISHED_SIGNAL signal received")
                self.terminate()


    def on_channels_ready(self, channel):
        super().on_channels_ready(channel)
        # self.component.init()
        # self.component.run()
        print("Waiting commands from benchmark")

