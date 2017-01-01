#!/usr/bin/env python
"""
@file    runner.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@date    2009-03-26
@version $Id: runner.py 19535 2015-12-05 13:47:18Z behrisch $

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2015 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""

from __future__ import division
import os
import sys
import optparse
import subprocess
import random

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
# the port used for communicating with your sumo instance
PORT = 8873

from Lane import Lane
from ControlledJunction import ControlledJunction
from TlGroup import TlGroup

properties = {}

file = open("output.txt", "w")

def initializeNetworkInfo(junctionInfo, laneInfo):
    
    junctionList = traci.junction.getIDList()
    laneList = traci.lane.getIDList()
    xNumber = int(properties["xNumber"])
    yNumber = int(properties["yNumber"])
    
    for cur in junctionList:
        newJunction = ControlledJunction(cur)
        junctionInfo[cur] = newJunction
        
    for cur in laneList:
        if not cur.startswith(":"):
            newLane = Lane(cur)
            laneInfo[cur] = newLane
        
    for key,value in junctionInfo.iteritems():
        value.laneGroups["X_" + str(value.x)] = TlGroup("X_" + str(value.x))
        value.laneGroups["Y_" + str(value.y)] = TlGroup("Y_" + str(value.y))
        if value.x != 0:
            value.incomingLanes.append(laneInfo[str(value.x-1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x-1)+"/"+str(value.y)+"_0"])
            value.neighbourJunctions.append(junctionInfo[str(value.x-1)+"/"+str(value.y)])
            value.laneGroups["Y_" + str(value.y)].laneList.append(laneInfo[str(value.x-1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            
        if(value.x != (xNumber-1)):
            value.incomingLanes.append(laneInfo[str(value.x+1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x+1)+"/"+str(value.y)+"_0"])
            value.neighbourJunctions.append(junctionInfo[str(value.x+1)+"/"+str(value.y)])
            value.laneGroups["Y_" + str(value.y)].laneList.append(laneInfo[str(value.x+1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            
        if(value.y != 0):
            value.incomingLanes.append(laneInfo[str(value.x)+"/"+str(value.y-1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y-1)+"_0"])
            value.neighbourJunctions.append(junctionInfo[str(value.x)+"/"+str(value.y-1)])
            value.laneGroups["X_" + str(value.x)].laneList.append(laneInfo[str(value.x)+"/"+str(value.y-1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            
        if(value.y != (yNumber-1)):
            value.incomingLanes.append(laneInfo[str(value.x)+"/"+str(value.y+1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y+1)+"_0"])
            value.neighbourJunctions.append(junctionInfo[str(value.x)+"/"+str(value.y+1)])
            value.laneGroups["X_" + str(value.x)].laneList.append(laneInfo[str(value.x)+"/"+str(value.y+1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            
    for key,value in laneInfo.iteritems():
        value.startPoint = junctionInfo[str(value.startX)+"/"+str(value.startY)]
        value.endPoint = junctionInfo[str(value.endX)+"/"+str(value.endY)]
        
        
        
def readPropertiesFile(filepath):
    with open(filepath, "rt") as f:
        for cur in f:
            line = cur.strip()
            if line:
                key_value = line.split("=")
                key = key_value[0].strip()
                value = key_value[1].strip()
                properties[key] = value
                
def updateTlLogic(junctionInfo, laneInfo):
    
    xNumber = int(properties["xNumber"])
    yNumber = int(properties["yNumber"])
    cycleLength = int(properties["cycleLength"])
    minTime = int(properties["minTime"])
        
    for key,value in junctionInfo.iteritems():
        value.totalCars = 0
        if(value.x == 0 or value.x == (xNumber-1) or value.y == 0 or value.y == (yNumber-1)):
            continue
        
        for groupKey, groupValue in value.laneGroups.iteritems():
            groupValue.averageCars = 0
            for curLane in groupValue.laneList:
                groupValue.averageCars = groupValue.averageCars + curLane.getAverageWaitingTime()
            
            count = 2
            for cur in value.neighbourJunctions:
                for nGroupKey, nGroupValue in cur.laneGroups.iteritems():
                    if nGroupKey == groupKey:
                        for nCur in nGroupValue.laneList:
                            if value.x == nCur.endX and value.y == nCur.endY:
                                continue
                            else:
                                groupValue.averageCars = groupValue.averageCars + nCur.getAverageWaitingTime() / 2
                                count = count + 1
            groupValue.averageCars = groupValue.averageCars / count
            value.totalCars = value.totalCars + groupValue.averageCars
            
    for key,value in junctionInfo.iteritems():
        
        if(value.x == 0 or value.x == (xNumber-1) or value.y == 0 or value.y == (yNumber-1)):
            continue
        
        totalLen = 0
        for groupKey, groupValue in value.laneGroups.iteritems():
            if value.totalCars == 0:
                proportionGroup = 0
            else:
                proportionGroup = groupValue.averageCars / value.totalCars
            groupValue.time = round(cycleLength*proportionGroup)
            if(groupValue.time < minTime):
                groupValue.time = minTime
            totalLen = totalLen + groupValue.time
            
        while totalLen != cycleLength:
            curGroup = random.choice(value.laneGroups.values())
            if totalLen < cycleLength:
                curGroup.time = curGroup.time + 1
                totalLen = totalLen + 1
            else:
                if curGroup.time == minTime:
                    continue           
                curGroup.time = curGroup.time - 1
                totalLen = totalLen - 1
                
        curTlLogic = traci.trafficlights.getCompleteRedYellowGreenDefinition(key)[0]
        
        for groupKey, groupValue in value.laneGroups.iteritems():
            groupValue.time = groupValue.time * 1000
            if groupKey.startswith("X"):
                curTlLogic._phases[0]._duration = groupValue.time
                curTlLogic._phases[0]._duration1 = groupValue.time
                curTlLogic._phases[0]._duration2 = groupValue.time
            elif groupKey.startswith("Y"):
                curTlLogic._phases[2]._duration = groupValue.time
                curTlLogic._phases[2]._duration1 = groupValue.time
                curTlLogic._phases[2]._duration2 = groupValue.time
            file.write(key + " - " + groupKey + " - " + str(groupValue.time) + " - " + str(groupValue.averageCars) +"\n")
        
        traci.trafficlights.setCompleteRedYellowGreenDefinition(key, curTlLogic)
                      

def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    
    observationInterval = int(properties["observationInterval"])
    updateInterval = int(properties["updateInterval"])
    observationWindow = int(properties["observationWindow"])
    simulationTime = int(properties["simulationTime"])

    junctionInfo = {}
    laneInfo = {}
    initializeNetworkInfo(junctionInfo, laneInfo)
    waitingTime = 0

    while simulationTime > step:
        traci.simulationStep()
        vehicleIdList = traci.vehicle.getIDList()
        for cur in vehicleIdList:
            if traci.vehicle.getWaitingTime(cur) > 0:
                waitingTime += 1
        
        if (step != 0 and step%observationInterval == 0):
            for key,value in laneInfo.iteritems():
                value.addNewObservation(traci.lane.getLastStepVehicleNumber(key), observationWindow)
    
        if (step != 0 and step%updateInterval == 0):
            updateTlLogic(junctionInfo, laneInfo)
        
        step += 1
    traci.close()
    
    file.write("TotalWaitingTime: " + str(waitingTime))
    file.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    optParser.add_option("-f", "--filename",
                  metavar="FILE", default="config.properties", help="Config file")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()
    readPropertiesFile(options.filename)

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    sumoProcess = subprocess.Popen([sumoBinary, "-c", "/home/emrah/Desktop/Sumo/mobility.sumo.cfg", "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    run()
    sumoProcess.wait()
