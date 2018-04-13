import io
import os

import bitstring
import pika

from main.supplementary import RabbitMQUtils


class AbstractCommandReceivingComponent:
    connection = None
    commandChannel=None
    datagenChannel=None
    taskgenChannel = None
    readyChannels = 0

    delayedSend=[]

    commandExchangeName = 'hobbit.command'

    sessionId = None

    commandQueue = None

    def init(self):
        parameters = pika.ConnectionParameters(host='rabbit')
        self.sessionId = os.environ["HOBBIT_SESSION_ID"]
        self.connection = pika.SelectConnection(parameters, self.on_connection_open)

    def on_connection_open(self, connection):
        self.commandChannel = connection.channel(self.on_command_channel_open)

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

    def on_channels_ready(self, channel):
        self.readyChannels+=1

    def sendCmdToQueue(self, command: bytes, data: bytes):

        # attachData = None
        # if data is not None and len(data) > 0:
        #     attachData = True

        stream = bitstring.BitStream()
        stream.append("int:32=" + str(len(self.sessionId)))
        stream.append(bytearray(self.sessionId, encoding="utf-8"))
        stream.append("int:8=" + str(command))

        if data is not None:
            stream.append(data)

        self.commandChannel.basic_publish(exchange=self.commandExchangeName, routing_key="", body=stream.bytes)

    def commandReceivedCallback(self, ch, method, properties, body):
        buffer = io.BytesIO(body)
        sessionId = RabbitMQUtils.readString(buffer)
        if sessionId == self.sessionId:
            command = RabbitMQUtils.readByte(buffer)
        #containerStartCommand = RabbitMQUtils.readString(buffer)
        #print(" [x] Command received %r" % command)
        return command

    def run(self):
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.terminate()

    def terminate(self):
        print("Terminating")
        self.connection.close()
