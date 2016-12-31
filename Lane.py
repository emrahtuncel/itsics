class Lane:

    laneId = ""
    startX = 0
    startY = 0
    endX = 0
    endY = 0
    startPoint = ""
    endPoint = ""

    def __init__(self, laneId):
        self.laneId = laneId
        self.waitingTime = []
        firstList = laneId.split("/")
        self.startX = int(firstList[0])
        secondList = firstList[1].split("to")
        self.startY = int(secondList[0])
        self.endX = int(secondList[1])
        secondList = firstList[2].split("_")
        self.endY = int(secondList[0])
        
    def addNewObservation(self, curTime, window):
        if len(self.waitingTime) < window:
            self.waitingTime.append(curTime)
        else:
            del self.waitingTime[0]
            self.waitingTime.append(curTime)
            