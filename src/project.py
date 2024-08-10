import sys
import math
from RandomNumberGenerator import RandomNumberGenerator

'''
Checks the arguments user is passing through.
 - Param: None
 - Returns: None
'''
def arg_checking():
    if len( sys.argv ) != 6:
        print( "ERROR: <python script.py n ncpu seed lambda upperBound>\n", file = sys.stderr )
        sys.exit(1)
    n = int( sys.argv[1] )
    ncpu = int( sys.argv[2] )    
    lambda_param = float( sys.argv[4] )
    upperBound = int( sys.argv[5] )
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
        process_ids.append(f"{letter}{number}")
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
def processCalculations( process_type: str, process_id: str ) -> ( float, float, int ):
    TOTAL_cpu_burst_time = 0.0
    TOTAL_IO_burst_time = 0.0

    arrival_time = math.floor(next_exp(lambda_param,upperBound ))
    cpu_bursts = math.ceil(rng.drand48(rng) * 32)

    s = 's' if cpu_bursts > 1 else ''
    print(f"{process_type} process {process_ids[process-1]}: arrival time {arrival_time}ms; {cpu_bursts} CPU burst{s}:")
    
    for i in range( cpu_bursts ):
        cpu_burst_time = math.ceil(next_exp(lambda_param, upperBound))        
        if( process_type == "CPU-bound" ):
            cpu_burst_time *= 4
        TOTAL_cpu_burst_time += cpu_burst_time

        if i < cpu_bursts - 1: 
            io_burst_time = math.ceil(next_exp(lambda_param, upperBound))
            if( process_type == "I/O-bound" ):
                io_burst_time *= 8
            TOTAL_IO_burst_time += io_burst_time
                
            print(f"==> CPU burst {cpu_burst_time:.0F}ms ==> I/O burst {io_burst_time}ms")
        else:
            print(f"==> CPU burst {cpu_burst_time:.0F}ms")
     
    return TOTAL_cpu_burst_time, TOTAL_IO_burst_time, cpu_bursts

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

    s = "es" if ncpu > 1 else ''
    print(f"<<< -- process set (n={n}) with {ncpu} CPU-bound process{s}")
    print(f"<<< -- seed={seed}; lambda={lambda_param:.6f}; bound={upperBound}")

    # Generate process IDs
    process_ids = generate_process_ids(n)
    rng = RandomNumberGenerator
    rng.srand48(rng,seed)

    # Variables needed to calculate averages
    CPU_bound_CPU_burst_time_total = 0.0
    IO_bound_CPU_burst_time_total = 0.0

    CPU_bound_IO_burst_time_total = 0.0
    IO_bound_IO_burst_time_total = 0.0

    CPU_bound_CPU_burst_total = 0.0
    IO_bound_CPU_burst_total = 0.0

    average_CPU_burst_time = 0
    average_IO_burst_time = 0

    for process in range(1,len(process_ids)+1):

        # For CPU-bound
        if process <= ncpu:
            TOTAL_cpu_burst_time, TOTAL_IO_burst_time, cpu_bursts = processCalculations( "CPU-bound", process_ids[process - 1] )
            CPU_bound_CPU_burst_time_total += TOTAL_cpu_burst_time
            CPU_bound_IO_burst_time_total += TOTAL_IO_burst_time
            CPU_bound_CPU_burst_total += cpu_bursts

        # For I/O-bound
        else:
            TOTAL_cpu_burst_time, TOTAL_IO_burst_time, cpu_bursts = processCalculations( "I/O-bound", process_ids[process - 1] )
            IO_bound_CPU_burst_time_total += TOTAL_cpu_burst_time
            IO_bound_IO_burst_time_total += TOTAL_IO_burst_time
            IO_bound_CPU_burst_total += cpu_bursts

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


