from main.AbstractSystemAdapter import AbstractSystemAdapter


class SystemAdapter(AbstractSystemAdapter):

    def receiveGeneratedTask(self, taskId, data):
        print("ReceiveGeneratedTask(" + taskId + "," + data + "). Sending back to storage")
        self.sendResultToEvalStorage(taskId, data+"_back")