from main.supplementary.AbstractSystemAdapter import AbstractSystemAdapter


class SystemAdapter(AbstractSystemAdapter):

    def init(self):
        super().init()
        print("ParametersModel: "+self.systemParamModel)

    def receiveGeneratedTask(self, taskId, data):
        print("ReceiveGeneratedTask(" + taskId + "," + data + "). Sending back to storage")
        self.sendResultToEvalStorage(taskId, data+"_back")