import io
from abc import abstractmethod

import bitstring
import pika

from main import RabbitMQUtils
from main.AbstractCommandReceivingComponent import AbstractCommandReceivingComponent

SYSTEM_READY_SIGNAL = 1
TASK_GENERATION_FINISHED = 15

class AbstractSystemAdapter(AbstractCommandReceivingComponent):
    connection = None
    commandChannel=None
    datagenChannel=None
    taskgenChannel = None
    readyChannels = 0

    delayedSend=[]

    commandExchangeName = 'hobbit.command'

    sessionId = 'session_4'
    #sessionIdB = b"session_1"

    commandQueue = None
    dataGenQueueName = 'hobbit.datagen-system.' + sessionId
    taskGenQueueName = 'hobbit.taskgen-system.' + sessionId
    evalStorageQueueName = 'hobbit.system-evalstore.' + sessionId

    def init(self):
        super().init()

    def on_connection_open(self, connection):
        super().on_connection_open(connection)

        self.dataGenChannel = connection.channel(self.on_dataGen_channel_open)
        self.taskGenChannel = connection.channel(self.on_taskGen_channel_open)
        self.evalStorageChannel = connection.channel(self.on_evalStorage_channel_open)

    def on_dataGen_channel_open(self, channel):
        self.dataGenChannel.queue_declare(queue=self.dataGenQueueName, callback=self.on_dataGen_queue_declared, auto_delete=True)

    def on_dataGen_queue_declared(self, result):
        self.dataGenChannel.basic_consume(self.dataGenCallback, queue=self.dataGenQueueName, no_ack=True)
        self.on_channels_ready(self.dataGenChannel)

    def on_taskGen_channel_open(self, channel):
        self.taskGenChannel.queue_declare(queue=self.taskGenQueueName, callback=self.on_taskGen_queue_declared, auto_delete=True)

    def on_taskGen_queue_declared(self, result):
        self.taskGenChannel.basic_consume(self.taskGenCallback, queue=self.taskGenQueueName, no_ack=True)
        self.on_channels_ready(self.taskGenChannel)

    def on_evalStorage_channel_open(self, channel):
        self.evalStorageChannel.queue_declare(queue=self.evalStorageQueueName, callback=self.on_evalStorage_queue_declared, auto_delete=True)

    def on_evalStorage_queue_declared(self, result):
        self.on_channels_ready(self.evalStorageChannel)

    def on_channels_ready(self, channel):
        super().on_channels_ready(channel)
        if self.readyChannels==4:
            print("Sending SYSTEM_READY_SIGNAL signal")
            self.sendCmdToQueue(SYSTEM_READY_SIGNAL, None)
        # if self.readyChannels > 4:
        #     for data in self.delayedSend:
        #         self.evalStorageChannel.basic_publish(exchange="", routing_key=self.evalStorageQueueName, body=data)

    def commandReceivedCallback(self, ch, method, properties, body):
        command = super().commandReceivedCallback(ch, method, properties, body)

        if command==TASK_GENERATION_FINISHED:
            self.terminate()

    def taskGenCallback(self, ch, method, properties, body):
        buffer = io.BytesIO(body)
        taskId = RabbitMQUtils.readString(buffer)
        taskData = RabbitMQUtils.readString(buffer)
        self.receiveGeneratedTask(taskId, taskData)

    @abstractmethod
    def receiveGeneratedTask(self, taskId, data):
        raise NotImplementedError

    def dataGenCallback(self, ch, method, properties, body):
        print(" [x] DataGen Received %r" % body)

    def sendResultToEvalStorage(self,taskIdString, data):
        stream = bitstring.BitStream()
        stream.append("int:32=" + str(len(taskIdString)))
        stream.append(bytearray(taskIdString, encoding="utf-8"))
        stream.append("int:32=" + str(len(data)))
        stream.append(bytearray(data, encoding="utf-8"))

        try:
            self.evalStorageChannel.basic_publish(exchange="", routing_key=self.evalStorageQueueName, body=stream.bytes)
        except Exception as e:
            print(" Sending failed: ")

    # def run(self):
    #     super().run()
    #     # try:
    #     #     self.connection.ioloop.start()
    #     # except KeyboardInterrupt:
    #     #     self.terminate()


