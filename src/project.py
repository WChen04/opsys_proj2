import sys
import math
from RandomNumberGenerator import RandomNumberGenerator
from Process import Process
from PriorityQueue import PriorityQueue

'''
Checks the arguments user is passing through.
 - Param: None
 - Returns: None
'''
def arg_checking():
    if len( sys.argv ) != 9:
        print( "ERROR: <python script.py n ncpu seed lambda upperBound Tcs alpha Tslice>\n", file = sys.stderr )
        sys.exit(1)
    n = int( sys.argv[1] )
    ncpu = int( sys.argv[2] )    
    lambda_param = float( sys.argv[4] )
    upperBound = int( sys.argv[5] )
    Tcs = int( sys.argv[6] )
    alpha = float( sys.argv[7] )
    Tslice = int( sys.argv[8] )
    if( n > 260 or n <= 0):
        print( "ERROR: <invalid number of processes>\n", file = sys.stderr )
        sys.exit( 1 )
    if( ncpu > n or ncpu < 0):
        print( "ERROR: <invalid number of ncpu>\n", file = sys.stderr )
        sys.exit( 1 )
    if( lambda_param <= 0):
        print( "ERROR: <invalid lambda parameter>\n", file = sys.stderr )
        sys.exit( 1 )
    if( upperBound <= 0 ):
        print( "ERROR: <invalid upperbound>\n", file = sys.stderr )
        sys.exit( 1 )
    if( Tcs <= 0 or Tcs % 2 == 1 ):
        print( "ERROR: <invalid Tcs>\n", file=sys.stderr )
        sys.exit( 1 )
    if( alpha < 0.0 or alpha > 1.0 ):
        print( "ERROR: <invalid alpha>\n", file=sys.stderr )
        sys.exit( 1 )
    if( Tslice <= 0 ):
        print( "ERROR: <invalid Tslice>\n", file=sys.stderr )
        sys.exit( 1 )

'''
Returns a random value following a exponential distribution
 - Param: lambda_param
    Set the average value to be ( 1 / lambda )
 - Param: upperBound
    The largest value the function can return
 - Returns: a float following the exponential distribution
'''
def next_exp( lambda_param: float, upperBound: int ) -> float:   
    value = -math.log(rng.drand48(rng)) / lambda_param
    while ( value > upperBound):
        value = -math.log(rng.drand48(rng)) / lambda_param
    return value

'''
Creates a list of process ids starting from A0, A1, ..., A9, B0, ... Z9
 - Param: n
    Number of processes to name
 - Returns: Returns a list of process ids
'''
def generate_process_ids( n: int ) -> list:
    process_ids = []
    for i in range(n):
        letter = chr(65 + (i // 10)) 
        number = i % 10
        process_ids.append(Process(f"{letter}{number}"))
    return process_ids
'''
Calculates values needed to find averages
 - Param: process_type
    To identify if the process is CPU-bound or IO-bound
 - Param: process_id
    Id of the process
 - Returns: tuple
    a tuple of total cpu burst time, total io burst time, and number of cpu bursts
'''
def populateProcess( lambda_param: float, upperBound: int, process_type: str, curr_process: Process ):
    TOTAL_cpu_burst_time = 0.0
    TOTAL_IO_burst_time = 0.0

    arrival_time = math.floor( next_exp( lambda_param,upperBound ) )
    cpu_bursts = math.ceil(rng.drand48(rng) * 32)

    curr_process.defineProcessType(process_type)
    curr_process.defineArrivalTime(arrival_time)
    curr_process.defineCpuBursts(cpu_bursts)

    s = 's' if cpu_bursts > 1 else ''
    print(f"{process_type} process {curr_process.process_name}: arrival time {arrival_time}ms; {cpu_bursts} CPU burst{s}")
    
    for i in range( cpu_bursts ):
        cpu_burst_time = math.ceil(next_exp(lambda_param, upperBound))        
        if( process_type == "CPU-bound" ):
            cpu_burst_time *= 4
        curr_process.addCpuBurstTime(cpu_burst_time)
        TOTAL_cpu_burst_time += cpu_burst_time

        if i < cpu_bursts - 1: 
            io_burst_time = math.ceil(next_exp(lambda_param, upperBound))
            if( process_type == "I/O-bound" ):
                io_burst_time *= 8
            curr_process.addIOBurstTime(io_burst_time)
            TOTAL_IO_burst_time += io_burst_time
                
        #     print(f"==> CPU burst {cpu_burst_time:.0F}ms ==> I/O burst {io_burst_time}ms")
        # else:
        #     print(f"==> CPU burst {cpu_burst_time:.0F}ms")

'''
- First Come First Serve
- Creates map of all processes 
- Updates maps and objects
'''
def FCFS(processes: list, switchTime: int, current_time:int):
    processes.sort(key=lambda process: process.arrival_time)

    print(f"time 0ms: Simulator started for FCFS [Q empty]")
    cpu_process = None
    processes_in_action = []
    finished_processes = []

    # maps from process to its action's finish time / name. actions are:
    # - arrival
    # - CPU burst
    # - IO burst
    # ex: map[P0] = (5, "arrival")
    # ex: map[P1] = (25, "cpu")
    processes_to_action_finish_time = {}
    current_time = 0
    ready_queue = []
    
#   If different types of events occur at the same time, simulate these events in the following order:
    #   (a) CPU burst completion;
    #   (b) process starts using the CPU;
    #   (c) I/O burst completions;
    #   (d) new process arrivals.
#   Further, any “ties” that occur within one of these categories are to be broken using process ID order.

    for process in processes:
        process.cpu_burst_times_remaining = process.cpu_burst_times
        process.io_burst_times_remaining = process.io_burst_times
        processes_to_action_finish_time[process] = (process.arrival_time, "arrival")
        processes_in_action.append(process)

    # Loop until all processes are finished
    while len(finished_processes) < len(processes):
        # processes are being processed, find which one finishes its action first
        if (len(processes_in_action) > 0):
            earliest_finish_time = math.inf
            earliest_action = None
            next_process = None
            for process in processes_in_action:
                finish_time, action = processes_to_action_finish_time[process]
                if finish_time < earliest_finish_time:
                    earliest_finish_time = finish_time
                    earliest_action = action
                    next_process = process
            current_time = earliest_finish_time
            processes_in_action.remove(next_process)

            if earliest_action == "arrival":
                ready_queue.append(next_process)
                print(f"time {current_time}ms: Process {next_process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in ready_queue])}]")
                if cpu_process == None:
                    cpu_process = ready_queue[0]
                    ready_queue.pop(0)
                    processes_to_action_finish_time[cpu_process] = (current_time + cpu_process.cpu_burst_times_remaining[0], "cpu")
                    processes_in_action.append(cpu_process)
                    current_time += int(switchTime/2)
                    print(f"time {current_time}ms: Process {cpu_process.process_name} started using the CPU for {cpu_process.cpu_burst_times_remaining[0]}ms burst [Q empty]")
                    cpu_process.cpu_burst_times_remaining.pop(0)
            elif earliest_action == "cpu":
                # logic for unmounting a process from CPU
                if len(next_process.io_burst_times_remaining) > 0:
                    current_time += int(switchTime/2)
                    print(f"time {current_time}ms: Process {next_process.process_name} completed a CPU burst; {len(next_process.cpu_burst_times_remaining)} bursts to go [Q {' '.join([q.process_name for q in processes_in_action])}]")
                    current_time += int(switchTime/2)
                    processes_to_action_finish_time[next_process] = (current_time + next_process.io_burst_times_remaining.pop(0), "io")
                    processes_in_action.append(next_process)
                else:
                    print(f"time {current_time}ms: Process {process.process_name} terminated [Q {' '.join([q.process_name for q in processes_in_action])}]")
                    finished_processes.append(next_process)

                cpu_process = None
                if len(ready_queue)>0:
                    cpu_process = ready_queue[0]
                    ready_queue.pop(0)
                    current_time += int(switchTime/2)
                    print(f"time {current_time}ms: Process {cpu_process.process_name} started using the CPU for {cpu_process.cpu_burst_times_remaining[0]}ms burst [Q empty]")
                    processes_to_action_finish_time[cpu_process] = (current_time + cpu_process.cpu_burst_times_remaining[0], "cpu")
                    processes_in_action.append(cpu_process)
                    cpu_process.cpu_burst_times_remaining.pop(0)
            else: # logic for when something completes IO
                
                print(f"time {current_time}ms: Process {next_process.process_name} completed I/O; added to ready queue [Q {' '.join([q.process_name for q in processes_in_action])}]")
                ready_queue.append(next_process)
                if not cpu_process:
                    cpu_process = ready_queue.pop(0)
                    processes_to_action_finish_time[cpu_process] = (current_time + cpu_process.cpu_burst_times_remaining[0], "cpu")
                    print(f"time {current_time}ms: Process {cpu_process.process_name} started using the CPU for {cpu_process.cpu_burst_times_remaining[0]}ms burst [Q empty]")
                    processes_in_action.append(cpu_process)
                    cpu_process.cpu_burst_times_remaining.pop(0)
                        
        # no processes are waiting on I/O, are being run, or are arriving, grab from ready queue
        elif len(ready_queue) > 0:
            cpu_process = ready_queue.pop(0)
            processes_to_action_finish_time[cpu_process] = (current_time + cpu_process.cpu_burst_times_remaining[0], "cpu")
            processes_in_action.append(cpu_process)
            current_time += int(switchTime/2)
            print(f"time {current_time}ms: Process {cpu_process.process_name} started using the CPU for {cpu_process.cpu_burst_times_remaining[0]}ms burst [Q empty]")

        else:
            print("shouldn't be getting here")
            print("ready queue", ready_queue)
            print("processes_in_action", processes_in_action)
            print("finished processes", finished_processes)

    # pseudo code implementation

    # for process in processes:
        # process.cpu_burst_times_remaining = process.cpu_burst_times
        # process.io_burst_times_remaining = process.io_burst_times

    # processesInAction = []
    # runningProcess = None
    # while (len(finished_processes) < len(processes)):
        # if (len(processesInAction) > 0)
            # earliestFinishTime = infinity (example)
            # next_process = None
            # for process in processesInAction:
                # if processes_to_finish_time[process] < earliestFinishTime:
                    # earliestFinishTime = process
                    # next_process = process

            # now we know the next process to finish, update accordingly
            # currTime = earliestFinishTime
            # processesInAction.remove(process)
            # if process is runningProcess:
                # if it still has io_burst_times_remaining:
                    # remove first cpu_burst_time value
                    # print out stuff
                    # processToFinishTime[process] = currTime + Process.io_burst_times_remaining[0]
                    # processesInAction.add(process)
                # else:
                    # print out "terminated"
            # else: (is waiting for I/O)
                # remove first io_burst_time value
                # print out stuff
                # processToFinishTime[process] = currTime + Process.cpu_burst_times_remaining[0]
                # processesInAction.add(process)


        # Else, first step ever (no processes are waiting or being run, we run the first process in queue)
            # runningProcess = P0
            # processToFinishTime[P0] = currTime + P0.runTime
            # processesInAction.add(P0), 
   

   


    # current_time = current_time
    # print("time 0ms: Simulator started for FCFS [Q empty]")
    # # Process currently being run 
    # inProgress = None
    # # Keys are objects, values are time
    # processDict = {}
    # readyQueue = []
    # arrivalsequence = True
    # blocking = {}
    # def ioChecker(blocking, currentTime):
    #     for process in blocking:
    #         if blocking[process] < currentTime:
    #             print(f"time {currentTime}ms: Process {process.process_name} completed I/O; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
    #             readyQueue.append(process)
    #             del blocking[process]
    #     return blocking
     
    

    # # Sort to find smallest process
    # processes.sort(key=lambda process: process.arrival_time)
    
    # # Make all process in dictionary
    # for process in processes:
    #     processDict[process] = process.arrival_time
    
    
    # # Do until no more processes
    # while len(processDict)!= 0:
    #     if arrivalsequence == True:
    #         for process in processDict:
    #             # Check if process is first time
    #             if process.isFirstTime():
    #                 readyQueue.append(process)
    #                 process.changeFirst()
    #                 current_time = process.arrival_time
    #                 ioChecker(blocking, current_time)
    #                 print(f"time {process.arrival_time}ms: Process {process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
    #                 ioChecker(blocking, current_time)
    #                 if not fakeCPU:
    #                     fakeCPU.append(process)
    #                     readyQueue.pop(0)
    #                     processDict[process] += int(switchTime/2)
    #                     current_time = processDict[process]
    #                     ioChecker(blocking, current_time)
    #                     print(f"time {processDict[process]}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
    #                     ioChecker(blocking, current_time)
    #                     if all(value < processDict[process] + process.cpu_burst_times[0] for value in processDict.values()):
    #                         processDict = {key: processDict[process] + process.cpu_burst_times[0] for key in processDict}
    #                     current_time = processDict[process]
    #                     process.cpu_burst_times.pop(0)
    #         arrivalsequence = False
    #     else:
    #         if fakeCPU:
    #             current_time = processDict[fakeCPU[0]]
    #             ioChecker(blocking, current_time)
    #             print(f"time {processDict[fakeCPU[0]]}ms: Process {fakeCPU[0].process_name} completed a CPU burst; {len(fakeCPU[0].cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
    #             blockingTime = fakeCPU[0].io_burst_times[0] + processDict[fakeCPU[0]] + int(switchTime/2)   
    #             current_time = processDict[fakeCPU[0]]
    #             print(f"time {processDict[fakeCPU[0]]}ms: Process {fakeCPU[0].process_name} switching out of CPU; blocking on I/O until time {blockingTime}ms [Q {' '.join([q.process_name for q in readyQueue])}]")
    #             fakeCPU[0].io_burst_times.pop(0)
    #             blocking[process] = blockingTime
    #             processDict = {key: processDict[process] + int(switchTime/2) for key in processDict}
    #             processDict[fakeCPU[0]] = blockingTime
    #             fakeCPU.pop(0)
    #         else:
    #             ioChecker(blocking, current_time)
    #             fakeCPU.append(readyQueue[0])
    #             readyQueue.pop(0)
    #             processDict[fakeCPU[0]] += int(switchTime/2)
    #             current_time = processDict[fakeCPU[0]]
    #             print(f"time {processDict[fakeCPU[0]]}ms: Process {fakeCPU[0].process_name} started using the CPU for {fakeCPU[0].cpu_burst_times[0]}ms burst [Q empty]")
    #             processDict = {key: processDict[process] + process.cpu_burst_times[0] for key in processDict}
    #             fakeCPU[0].cpu_burst_times.pop(0)
            
            # processDict[process] += process.cpu_burst_times[0]
            # print(f"time {process.arrival_time}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
            # fakeCPU.append(process)
            # process.cpu_burst_times.pop(0)
            # readyQueue.pop(0)
        


        # # arriving bursts
        # for process in processDict:
        #     if len(fakeCPU) == 0:
        #         processTime = processDict[process]
        #         print(f"time {processTime}ms: Process {process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
        #         processDict[process] = processTime + process.cpu_burst_times[0]
        #         print(f"time {processTime}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
        #         fakeCPU.append(process)
        #         process.cpu_burst_times.pop(0)
        #         readyQueue.pop(0)
        #     else:
        #         continue
        # for process in processDict:
        #     if processDict[process] == 0:
        #         print(f"time {processDict[process]}ms: Process {process.process_name} terminated [Q empty]")
        #         del processDict[process]
        #     else:
        #         processDict[process] -= 1
        #         continue



    # for process in processDict:
    #     if len(process.cpu_burst_times)> 0:
    #         readyQueue.append(process)
    #         print(f"time {processDict[process]}ms: Process {process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
    #         processTime = processDict[process]
    #         processDict[process] = processTime + process.cpu_burst_times[0]
         
    #         if len(fakeCPU) == 0:
    #             print(f"time {processTime}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
    #             fakeCPU.append(process)
    #             process.cpu_burst_times.pop(0)
    #             readyQueue.pop(0)
    #         else:
    #             continue



    #     processTime = processDict[process]
    #     readyQueue.append(process)
    #     # Check readyQueue is empty
    #     if readyQueue:
    #         print(f"time {processTime}ms: Process {process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
    #     else:  
    #         print(f"time {processTime}ms: Process {process.process_name} arrived; added to ready queue [Q empty]")
    #     # Check if CPU is free
    #     if len(fakeCPU) == 0:
    #         readyQueue.pop(0)
    #         processTime += int(switchTime/2)
    #         print(f"time {processTime}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
    #         processDict[process] = processTime + process.cpu_burst_times[0]
    #         process.cpu_burst_times.pop(0)
    #         fakeCPU.append(process)
    #     else:
    #         # future things
    #         continue

    # # After all things have arrived, we check process in CPU if done yet

    # for process in processDict:
    #     if len(fakeCPU) ==  1:
    #         print(f"time {processDict[fakeCPU[0]]}ms: Process {fakeCPU[0].process_name} completed a CPU burst; {len(fakeCPU[0].cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
    #         blockingTime = process.io_burst_times[0] + processDict[process]+ int(switchTime/2)
    #         process.cpu_burst_times.pop(0)
    #         print(f"time {processDict[process]}ms: Process {process.process_name} switching out of CPU; blocking on I/O until time {blockingTime}ms [Q {' '.join([q.process_name for q in readyQueue])}]")
    #         # update the time of the process in dictionary and add it to blocking 
    #         # compare to blocking after each process iteration
    #         blocking.append(process)

    # def burstChecker(process):
    #     if process.cpu_burst_times > 0:
    #         return True
    #     return False
        
 
            # fakeCPU.pop(0)
            # currentTime = processDict[fakeCPU[0]]

            

        # if process.incpu == 1:
        #     print(f"time {processDict[process]}ms: Process {process.process_name} completed a CPU burst; {len(process.cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
        #     process.incpu = 0
        #     blockingTime = process.io_burst_times[0] + processDict[process]+ int(switchTime/2)
        #     currentTime = processDict[process]
        #     print(f"time {processDict[process]}ms: Process {process.process_name} switching out of CPU burst; blocking on I/O until time {blockingTime}ms [Q {' '.join([q.process_name for q in readyQueue])}]")    
        #     continue
        # if readyQueue:
        #     transitionTime = currentTime + int(switchTime)
        #     readyQueue.pop(0)
        #     print(f"time {transitionTime}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q {' '.join([q.process_name for q in readyQueue])}]")
        #     process.incpu = 1



      
            



        #         readyQueue.append(processDict[process].process_name)
        #        
        #         newTime =  processTime + processDict[processTime].cpu_burst_times[0] + int(switchTime/2)
        #         print(f"{newTime}")
        #         del processDict[processTime]
        #         processDict[newTime] = process
        #         print(f"{processDict[newTime]}")

                # processDict[newTime].cpu_burst_times.pop(0)
                # processDict[processTime].incpu = 1
                # print(f"{processDict[processTime]}")
                # del processDict[processTime]


       
           
            

        #      do something
        # for process in processDict:
        #     if processDict[process].incpu == 1:
        #         processDict[process].cpu_burst_times.pop(0)
        #         print(f"time {min_time}ms: Process {min_process.process_name} completed a CPU burst; {len(min_process.cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
    # This for-loop will only last until all processes have arrived.
   
        


        # if processDict:
        #     min_time = min(processDict)
        #     processArrival = process.arrival_time
        #     if min_time < processArrival:
        #         min_process = processDict[min_time]
        #         if len(min_process.cpu_burst_times) > 0:
        #             readyQueue.pop(0)
        #             if len(min_process.cpu_burst_times) > 1:
        #                 print(f"time {min_time}ms: Process {min_process.process_name} completed a CPU burst; {len(min_process.cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
        #             else:
        #                  print(f"time {min_time}ms: Process {min_process.process_name} completed a CPU burst; {len(min_process.cpu_burst_times)} burst to go [Q {' '.join([q.process_name for q in readyQueue])}]")
        #             min_process.cpu_burst_times.pop(0)
        #             min_process.incpu = 0
        #             relaxTime = min_time + min_process.io_burst_times[0] + 2
        #             processDict[relaxTime] = min_process
        #             del processDict[min_time]
        #             print(f"time {min_time}ms: Process {min_process.process_name} switching out of CPU; blocking on I/O until time {relaxTime}ms [Q {', '.join([q.process_name for q in readyQueue])}]")
        #             isFullCpu = 0
        #             continue
        #         else:
        #             print(f"time {min_time}ms: Process {min_process.process_name} terminated [Q empty]")
        #             del processDict[min_time]
                    
        #     isFullCpu = 1

        # readyQueue.append(process)
        # print(f"time {process.arrival_time}ms: Process {process.process_name} arrived; added to ready queue [Q {' '.join([q.process_name for q in readyQueue])}]")
        # # Check if CPU is empty
        # if isFullCpu == 0:
        #     processTime = process.arrival_time + int(switchTime/2)
        #     processDict[processTime] = process
        #     print(f"time {processTime}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
        #     readyQueue.pop(0)
        #     processDict[processTime + process.cpu_burst_times[0]] = process
        #     process.incpu = 1
        #     del processDict[processTime]
        #     process.cpu_burst_times.pop(0)
        #     isFullCpu = 1

        # for process in processDict:
        #     if processDict[process].incpu == 1:
        #         processDict[process].cpu_burst_times.pop(0)
        #         print(f"time {min_time}ms: Process {min_process.process_name} completed a CPU burst; {len(min_process.cpu_burst_times)} bursts to go [Q {' '.join([q.process_name for q in readyQueue])}]")
                
               

       
               
            # print(f"time {process.arrival_time}ms: Process {process.process_name} arrived; added to ready queue [Q {', '.join([q.process_name for q in readyQueue])}]")
            # readyQueue.append(process)
            # processDict[process.arrival_time] = process
           




 
    # for process in processes:
    #     if first_process == 1 and not waiting:
    #         queue.append(process)
    #         time += process.arrival_time
    #         print(f"time {time}ms: Process {process.process_name} arrived and added to ready queue [Q {process.process_name}]")
    #         time += int(time_switch/2)
    #         queue.pop(0)
    #         print(f"time {time}ms: Process {process.process_name} started using the CPU for {process.cpu_burst_times[0]}ms burst [Q empty]")
    #         waiting.append(time + process.cpu_burst_times[0])
    #         first_process = 0

    #     elif waiting[0] > process.arrival_time:
    #         time = process.arrival_time
    #         queue.append(process)
    #         print(f"time {time}ms: Process {process.process_name} arrived and added to ready queue [Q {', '.join([q.process_name for q in queue])}]")

    #     elif waiting[0] < process.arrival_time:
    #         time = waiting[0]
    #         process.cpu_burst_times.pop(0)
    #         print(f"time {time}ms: Process {process.process_name} completed a CPU burst; {len(process.cpu_burst_times)} to go [Q {', '.join([q.process_name for q in queue])}]")


                # print(f"time {time}ms: Process {process.process_name} arrived and added to ready queue [Q", end="")
                # for p in queue:
                #     print(f" {p.process_name}", end="")
                # print("]")
                # if len(queue) == 1:



                




'''
1. a process arrives
2. a process starts using the cpu
3. a process finishes using the cpu
4. recalculate its tau value
5. process preemption
6. start the process io burst
7. finish the process io burst
8. loop until last cpu burst
'''
def SJF( processes: list ):
    pq = PriorityQueue()
    total_time = 0
    Process_arrival_time = 0
    Process_starts_using_CPU_time = 0
    Process_finishes_using_CPU_time = 0
    Process_starts_IO_burst_time = 0
    Process_finishes_IO_burst_time = 0
    

    print( f"time {total_time}ms: Simulator started for SJF {pq}" )
    

    return

def SRT( processes: list ):
    return 

def RR( processes: list ):
    return 


'''
Round the float to three decimal places
 - Param: value to round
 - Return: rounded value
'''
def round3f( value: float ) -> float:
    return math.ceil( value * 1000 ) / 1000

if __name__ == "__main__":

    arg_checking()

    print("<<< PROJECT PART I")

    # Arguments passed in by the user
    n = int(sys.argv[1])  
    ncpu = int(sys.argv[2])  
    seed = int(sys.argv[3]) 
    lambda_param = float(sys.argv[4])  
    upperBound = int(sys.argv[5]) 
    Tcs = int( sys.argv[6] )
    alpha = float( sys.argv[7] )
    Tslice = int( sys.argv[8] )
    
    s = "es" if ncpu > 1 else ''
    print(f"<<< -- process set (n={n}) with {ncpu} CPU-bound process{s}")
    print(f"<<< -- seed={seed}; lambda={lambda_param:.6f}; bound={upperBound}")

    # Generate process IDs
    process_ids = generate_process_ids(n)
    rng = RandomNumberGenerator
    rng.srand48(rng, seed)

    # Variables needed to calculate averages
    CPU_bound_CPU_burst_time_total = 0.0
    IO_bound_CPU_burst_time_total = 0.0

    CPU_bound_IO_burst_time_total = 0.0
    IO_bound_IO_burst_time_total = 0.0

    CPU_bound_CPU_burst_total = 0.0
    IO_bound_CPU_burst_total = 0.0

    average_CPU_burst_time = 0
    average_IO_burst_time = 0

    for process in range(len(process_ids)):

        curr_process = process_ids[ process ]
        process_type = "CPU-bound" if process + 1 <= ncpu else "I/O-bound"
        populateProcess( lambda_param, upperBound, process_type, curr_process )
        # For CPU-bound
        if process + 1 <= ncpu:
            CPU_bound_CPU_burst_time_total += sum( curr_process.cpu_burst_times )
            CPU_bound_IO_burst_time_total += sum( curr_process.io_burst_times )
            CPU_bound_CPU_burst_total += curr_process.cpu_bursts

        # For I/O-bound
        else:
            IO_bound_CPU_burst_time_total += sum( curr_process.cpu_burst_times )
            IO_bound_IO_burst_time_total += sum( curr_process.io_burst_times )
            IO_bound_CPU_burst_total += curr_process.cpu_bursts     

    # write the output into the simout.txt
    f = open( "simout.txt", "w")

    f.write(f"-- number of processes: {len(process_ids)}\n")
    f.write(f"-- number of CPU-bound processes: {ncpu}\n")
    f.write(f"-- number of I/O-bound processes: {n - ncpu}\n")

    CPU_bound_avg_CPU_burst = round3f( CPU_bound_CPU_burst_time_total / max( CPU_bound_CPU_burst_total, 1 ) )
    f.write(f"-- CPU-bound average CPU burst time: {CPU_bound_avg_CPU_burst:.3f} ms\n")

    IO_bound_avg_CPU_burst = round3f( IO_bound_CPU_burst_time_total / max( IO_bound_CPU_burst_total, 1 ) )
    f.write(f"-- I/O-bound average CPU burst time: {IO_bound_avg_CPU_burst:.3f} ms\n")

    average_CPU_burst = round3f( ( CPU_bound_CPU_burst_time_total + IO_bound_CPU_burst_time_total ) / max( ( CPU_bound_CPU_burst_total + IO_bound_CPU_burst_total ), 1 ) )
    f.write(f"-- overall average CPU burst time: {average_CPU_burst:.3f} ms\n")

    CPU_bound_avg_IO_burst = round3f( CPU_bound_IO_burst_time_total / max( ( CPU_bound_CPU_burst_total - ncpu ), 1 ) )
    f.write(f"-- CPU-bound average I/O burst time: {CPU_bound_avg_IO_burst:.3f} ms\n")

    IO_bound_avg_IO_burst = round3f( IO_bound_IO_burst_time_total / max( ( IO_bound_CPU_burst_total - ( n - ncpu ) ), 1 ) )
    f.write(f"-- I/O-bound average I/O burst time: {IO_bound_avg_IO_burst:.3f} ms\n")

    average_IO_burst = round3f( ( CPU_bound_IO_burst_time_total + IO_bound_IO_burst_time_total ) / max( ( CPU_bound_CPU_burst_total + IO_bound_CPU_burst_total - n), 1 ) )

    f.write(f"-- overall average I/O burst time: {average_IO_burst:.3f} ms\n")

    f.close()

    """
    '''''''''''''''''''''''''''''''''''
    'EVERYTHING PAST HERE IS PROJECT 2'
    '''''''''''''''''''''''''''''''''''
    """

    Tcs = int( sys.argv[6] )
    alpha = float( sys.argv[7] )
    Tslice = int( sys.argv[8] )

    print( "\n<<< PROJECT PART II" )
    print( f"<<< -- t_cs={Tcs}ms; alpha={alpha}; t_slice={Tslice}ms")

    FCFS(process_ids, Tcs, 0)

    SJF( process_ids )

