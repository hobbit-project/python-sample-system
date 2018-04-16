# python-sample-system
A sample python-based implementation of system adapter.

The actions below will allow you to run a target benchmark locally and you may debug your system fully the same way, as it is executed in the online platform. But you may test/debug your system without running benchmark if find the procedure too complicated.

The [standard dockerfile-based image building procedure](https://github.com/hobbit-project/platform/wiki/Upload-a-system) will be required to upload a python system into the online platform. 

# Local debugging under a target benchmark

1. Clone the target benchmark repository (e.g. [DEBS-GC-2018](https://github.com/hobbit-project/DEBS-GC-2018)) as well as this one. The benchmark should be runnable locally (contain [SDK-based](https://github.com/hobbit-project/java-sdk-example) tests).
2. Make sure that `checkHealth()` from the `DEBS-GC-2018` executes without errors (see instructions in [Readme](https://github.com/hobbit-project/DEBS-GC-2018)). 
3. Comment the submission of java-based sample system (line ` .systemAdapter(systemAdapter)` in [SampleSystemTestRunner.java](https://github.com/hobbit-project/DEBS-GC-2018/blob/master/src/main/java/org/hobbit/debs_2018_gc_samples/System/SampleSystemTestRunner.java)) and make sure, that `check_health()` test is not finishing anymore (hangs up after taskGenetator ready signal or something like that. This means waiting of system Adapter, which you excluded from the execution by commenting the line.
4. Package the java code (`mvn package -DskipTests=true`).
5. Open python code and modify the paths to jar file in [SystemAdapterTest.py](https://github.com/hobbit-project/python-sample-system/blob/master/src/test/SystemAdapterTest.py). You may also modify the name of the future docker image of your system.
6. Run the SystemAdapterTest.py from your IDE (running under sudo probably might be requred) and you may debug it.
