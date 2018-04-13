import math
import multiprocessing
import os
import subprocess
import time
from threading import Thread
from time import sleep

from main.SystemAdapter import SystemAdapter
from main.supplementary.HobbitCommandsListener import HobbitCommandsListener

# check/change it
workingDir = "/mnt/share/Projects/DEBS-GC-2018/"
jarFile = "target/debs_2018_gc_sample_system-1.0.jar"

systemImageName = "git.project-hobbit.eu:4567/smirnp/sml-benchmark-v2/system-adapter"


runningClass='org.hobbit.debs_2018_gc_samples.System.SampleSystemTestRunner'


sessionId = "session_"+str(math.floor(time.time()))
os.environ["HOBBIT_SESSION_ID"]=sessionId

args = ['java -cp '+jarFile+' '+runningClass+' '+ systemImageName+' '+ sessionId]


def start_benchmark(arg):
    try:
        process = subprocess.Popen(args, cwd=workingDir, shell=True, stdout=subprocess.PIPE)
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



