class ControlledJunction:
    
    x = 0
    y = 0
    z = 0
    junctionId = ""

    def __init__(self, junctionId):
        self.junctionId = junctionId
        self.incomingLanes = []
        self.outgoingLanes = []
        self.neighbourJunctions = []
        self.laneGroups = {}
        coordinates = junctionId.split("/")
        self.x = int(coordinates[0])
        self.y = int(coordinates[1])
    