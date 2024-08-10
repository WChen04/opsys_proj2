class RandomNumberGenerator:
    def __init__(self):
        self.x_n = 0
    
    def srand48(self, seed):
        self.x_n= (seed << 16) + 0x330E
    
    def drand48(self):
        a = 0x5DEECE66D
        c = 0xB
        m = pow(2,48)
        x_n_plus_1 = (a * self.x_n + c) % m
        self.x_n = x_n_plus_1
        return x_n_plus_1/m