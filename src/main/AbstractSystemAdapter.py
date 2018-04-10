import io
from abc import abstractmethod

import bitstring
import pika

from main import RabbitMQUtils
from main.AbstractCommandReceivingComponent import AbstractCommandReceivingComponent

SYSTEM_READY_SIGNAL = 1
TASK_GENERATION_FINISHED = 15
DOCKER_CONTAINER_TERMINATED = 16

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

    def __init__(self):
        test="123"

    def init(self):
        super.__init__()
        parameters = pika.ConnectionParameters(host='192.168.56.20')
        self.connection = pika.SelectConnection(parameters, self.on_connection_open)

    def on_connection_open(self, connection):
        self.commandChannel = connection.channel(self.on_command_channel_open)
        self.dataGenChannel = connection.channel(self.on_dataGen_channel_open)
        self.taskGenChannel = connection.channel(self.on_taskGen_channel_open)
        self.evalStorageChannel = connection.channel(self.on_evalStorage_channel_open)

    def on_command_channel_open(self, channel):
        channel.exchange_declare(exchange=self.commandExchangeName, exchange_type="fanout", callback=self.on_command_exchange_declared, durable=False, auto_delete=True)

    def on_command_exchange_declared(self, result):
        self.commandChannel.queue_declare(callback=self.on_command_queue_declared, exclusive=True)

    def on_command_queue_declared(self, result):
        self.commandQueue = result.method.queue
        self.commandChannel.queue_bind(queue=self.commandQueue, exchange=self.commandExchangeName, callback=self.on_command_queue_bound)

    def on_command_queue_bound(self, result):
        self.commandChannel.basic_consume(self.commandReceivedCallback, queue=self.commandQueue, no_ack=True)
        self.on_channels_ready(self.commandChannel)

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
        self.readyChannels+=1
        if self.readyChannels==4:
            print("Sending SYSTEM_READY_SIGNAL signal")
            self.sendCmdToQueue(SYSTEM_READY_SIGNAL, None)
        # if self.readyChannels > 4:
        #     for data in self.delayedSend:
        #         self.evalStorageChannel.basic_publish(exchange="", routing_key=self.evalStorageQueueName, body=data)

    def sendCmdToQueue(self, command: bytes, data: bytes):

        attachData = None
        if data is not None and len(data) > 0:
            attachData = True

        stream = bitstring.BitStream()
        stream.append("int:32=" + str(len(self.sessionId)))
        stream.append(bytearray(self.sessionId, encoding="utf-8"))
        stream.append("int:8=" + str(command))

        if attachData is not None:
            stream.append(data)

        self.commandChannel.basic_publish(exchange=self.commandExchangeName, routing_key="", body=stream.bytes)

    def commandReceivedCallback(self, ch, method, properties, body):
        buffer = io.BytesIO(body)
        sessionId = RabbitMQUtils.readString(buffer)
        command = RabbitMQUtils.readInt(buffer)
        print(" [x] Command received %r" % command)

        if command==TASK_GENERATION_FINISHED:
            self.sendCmdToQueue()
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

    def run(self):
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.terminate()

    def terminate(self):
        print("Terminating")
        self.connection.close()
