from projectprocess import Process
class PriorityQueue:
    '''
    Constructor
    '''
    def __init__( self ):
        self.queue = []

    '''
    print overload
    '''
    def __str__( self ):
        string = ""
        string += "[Q"
        if( len( self.queue ) == 0 ):
            return string + "empty]"
        else: 
            for curr_process in self.queue:
                string += f" { curr_process.process_name }"
            return string + "]" 
    
    '''
    checks if the queue is empty
    '''
    def isEmpty( self ):
        return len( self.queue ) == 0
    '''
    sort the queue based on the processes tau value
    '''
    def addPriority( self, process_to_check: Process ):
        index = 0
        for process in self.queue:
            if process.tau >= process_to_check.tau:
                break
            index += 1
        self.queue.insert( index, process_to_check )
    
    '''
    pop the first value in the queue
    '''
    def pop( self ) -> Process:
        return self.queue.pop( 0 )
