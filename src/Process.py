class Process:
    def __init__( self, process_name: str):
        self.process_name = process_name
        self.process_type = ''
        self.arrival_time = 0
        self.cpu_bursts = 0
        self.tau = 0

        self.cpu_burst_times = []
        self.io_burst_times = []
    
    def defineProcessType( self, process_type: str ):
        self.process_type = process_type

    def defineArrivalTime( self, arrival_time: int ):
        self.arrival_time = arrival_time
    
    def defineCpuBursts( self, cpu_bursts: int ):
        self.cpu_bursts = cpu_bursts

    def defineTau( self, tau: int ):
        self.tau = tau

    def addCpuBurstTime( self, cpu_burst_time: int):
        self.cpu_burst_times.append(cpu_burst_time)
    
    def addIOBurstTime( self, io_burst_time: int ):
        self.io_burst_times.append(io_burst_time)