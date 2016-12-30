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

import os
import sys
import optparse
import subprocess
import argparse

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

properties = {}

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
        if value.x != 0:
            value.incomingLanes.append(laneInfo[str(value.x-1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x-1)+"/"+str(value.y)+"_0"])
            
        if(value.x != (xNumber-1)):
            value.incomingLanes.append(laneInfo[str(value.x+1)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x+1)+"/"+str(value.y)+"_0"])
            
        if(value.y != 0):
            value.incomingLanes.append(laneInfo[str(value.x)+"/"+str(value.y-1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y-1)+"_0"])
            
        if(value.y != (yNumber-1)):
            value.incomingLanes.append(laneInfo[str(value.x)+"/"+str(value.y+1)+"to"+str(value.x)+"/"+str(value.y)+"_0"])
            value.outgoingLanes.append(laneInfo[str(value.x)+"/"+str(value.y)+"to"+str(value.x)+"/"+str(value.y+1)+"_0"])
            
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

def run():
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0
    
    observationInterval = int(properties["observationInterval"])
    updateInterval = int(properties["updateInterval"])
    observationWindow = int(properties["observationWindow"])

    junctionInfo = {}
    laneInfo = {}
    initializeNetworkInfo(junctionInfo, laneInfo)
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        if (step != 0 and step%observationInterval == 0):
            for key,value in laneInfo.iteritems():
                value.addNewObservation(traci.lane.getWaitingTime(key), observationWindow)
    
        if (step != 0 and step%updateInterval == 0):
            continue    #TODO
        
        step += 1
    traci.close()
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
