class ControlledJunction:

    def __init__(self, junctionId):
        self.junctionId = junctionId
        self.incomingLanes = []
        self.outgoingLanes = []
        self.neighbourJunctions = []
        self.laneGroups = {}
        coordinates = junctionId.split("/")
        self.x = int(coordinates[0])
        self.y = int(coordinates[1])
        self.totalCars = 0
    