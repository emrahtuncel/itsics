class ControlledJunction:
    
    x = 0
    y = 0
    junctionId = ""
    incomingLanes = []
    outgoingLanes = []
    neighbourJunctions = []

    def __init__(self, junctionId):
        self.junctionId = junctionId
        coordinates = junctionId.split("/")
        self.x = int(coordinates[0])
        self.y = int(coordinates[1])
    