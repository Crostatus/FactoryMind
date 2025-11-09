from enum import Enum

class MachinePowerProfile(Enum):
    IDLE = "idle"
    LOADING = "loading"
    PRODUCE = "produce"
    
    def __str__(self):        
        return self.value