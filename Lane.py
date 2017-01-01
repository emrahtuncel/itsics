class Lane:

    def __init__(self, laneId):
        self.laneId = laneId
        self.startPoint = ""
        self.endPoint = ""
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
            
    def getAverageWaitingTime(self):
        total = 0
        
        if len(self.waitingTime) == 0:
            return 0
        
        for curValue in self.waitingTime:
            total = total + curValue
            
        return total / len(self.waitingTime)
           