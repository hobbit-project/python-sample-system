import math
import multiprocessing
import os
import subprocess
import time
from threading import Thread
from time import sleep

from main.SystemAdapter import SystemAdapter
from main.supplementary.HobbitCommandsListener import HobbitCommandsListener

cwd = "/mnt/share/Projects/hobbit-java-sdk/target/"
systemImageName = "dummybenchmark/system-adapter"

sessionId = "session_"+str(math.floor(time.time()))
os.environ["HOBBIT_SESSION_ID"]=sessionId

args = ['java -cp hobbit-java-sdk-1.1.5.jar org.hobbit.sdk.DummyBenchmarkTest2 '+ systemImageName+' '+ sessionId]


def start_benchmark(arg):
    try:
        process = subprocess.Popen(args, cwd=cwd, shell=True, stdout=subprocess.PIPE)
        pid = process.pid
        for line in iter(process.stdout.readline, ''):
            print(line)
            if "[org.hobbit.sdk.utils.CommandQueueListener] - <Terminated>" in str(line):
                break
        process.kill()
    except Exception as e:
        print(e)



thread = Thread(target = start_benchmark, args = (10,))
thread.start()

commandsListener = HobbitCommandsListener(SystemAdapter(), systemImageName)
commandsListener.init()
commandsListener.run()



