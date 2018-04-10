from main.SystemAdapter import SystemAdapter

containerTerminatedCommand = b'\x00\x00\x00\tsession_1\x10\x00\x00\x00\x16dummybenchmark/datagen\x00'
systemReadyCommand = b'\x00\x00\x00\tsession_1\x01'
containerStartCommand = b'\x00\x00\x00\tsession_1\x0c{"image":"dummybenchmark/datagen","type":"benchmark","environmentVariables":["http://project-hobbit.eu/dummybenchmark/benchmarkParam2\\u003d456","http://project-hobbit.eu/dummybenchmark/benchmarkParam1\\u003d123","HOBBIT_GENERATOR_COUNT\\u003d1","HOBBIT_GENERATOR_ID\\u003d0","HOBBIT_RABBIT_HOST\\u003drabbit","HOBBIT_SESSION_ID\\u003dsession_1"]}'
benchmarkFinishedSignal = b'\x00\x00\x00\tsession_1\x11dummybenchmark/system-adapter'
taskGeneratorStartCommand=b'\x00\x00\x00\tsession_1\x08'

taskCommand=b'\x00\x00\x00\x010\x00\x00\x00\rtask_0_data_1'

adapter = SystemAdapter()
#adapter.commandReceivedCallback(None,None,None, systemReadyCommand)
#adapter.taskGenCallback(None,None,None, taskCommand)

adapter.init()
adapter.run()
test="123"
