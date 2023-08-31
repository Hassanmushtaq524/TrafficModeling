import matplotlib.pyplot as plt
import math
import random

# Car Class
class Car:

    def __init__(self, ID, initialPos, lane, vMax) -> None:
        # id of the car
        self.ID = ID
        # store velocities at every time step
        self.velArr = [math.nan]
        # store positions at every time step
        self.posArr = [initialPos]
        # stores the lanes the car is at 
        self.laneArr = [lane]
        # minimum headway
        self.dMin = 5
        # maximum velocity of car
        self.vMax = vMax
        # lane of car
        self.lane = lane
        # previous time step position
        self.curPosition = self.posArr[0]
        # count the tolerance
        self.impatience = 0
        
    def getPosition(self, timeStep):
        return self.posArr[timeStep]
    
    def getVelocity(self, timeStep):
        return self.velArr[timeStep]

    def appendVelocity(self, v):
        self.velArr.append(v)

    def appendPosition(self, x):
        self.posArr.append(x)
        self.curPosition = self.posArr[len(self.posArr) - 1]

    def patienceExceeded(self):
        if (self.impatience > 500):
            self.impatience = 0
            return True
        else:
            return False


# Closed lane traffic light
class TrafficLight:

    def __init__(self, position, lane):
        self.position = position
        self.lane = lane

    def getPosition(self, timestep):
        return self.position

# lambd - slope dv/dh
# x1 - position of current car
# x2 - position of next car
# vMax - maximum velocity of current car
# dMin - minimum headway of current car
# delta - reaction time
def func(lambd, x1, x2, vMax, dMin, delta, L):
    if (x2-x1 == 0):
        result =  vMax - vMax*math.exp((-lambd/vMax)*(L-dMin)); 
    else:
        result = vMax - vMax*math.exp((-lambd/vMax)*(((x2-x1) % L)-dMin));
    return result

# mat: matrix of cars
# curCar: the object of the current car
# curHeadway: the headway right now for current car
# l: total number of lanes
# L: total length of road
# n: total number of cars
# timeStep: current time step 
def switch(mat, curCar, curHeadway, l, L, n, timeStep):
    if curHeadway == 0:
        return (False, None, -1)
    # headway in the other lane
    otherHeadway = 0
    curLane = []
    lanesToCheck = [curCar.lane + 1, curCar.lane - 1]
    # check the possible lanes we can move to
    for ln in lanesToCheck:
        if (ln >= 0 and ln <= l - 1):
            # make a deep copy
            for i in range(len(mat[ln])):
                curLane.append(mat[ln][i])
            # place the car and check for new possible headway
            curLane[len(curLane)-1] = curCar
            curLane.sort(key=lambda x : L if x is None else x.getPosition(timeStep-1))
            # find the next car
            for i, c in enumerate(curLane):
                if (c is not None):
                    if (c.ID == curCar.ID):
                        nextCar = curLane[(i + 1) % n]
                        if (nextCar == None):
                            nextCar = curLane[0]
            # get the other headway 
            if (nextCar.ID == curCar.ID):
                otherHeadway = L
            else:
                otherHeadway = (nextCar.getPosition(timeStep - 1) - curCar.getPosition(timeStep - 1)) % L
    
            if (otherHeadway > curHeadway):
                # add to the impatience counter
                curCar.impatience += 1
                # if we have exceeded the tolerance for the current car
                if (curCar.patienceExceeded()):
                    return (True, nextCar, ln)
                else:
                    break
            else:
                # this will reduce the counter twice if both lanes are worse
                if (curCar.impatience > 0):
                    curCar.impatience -= 1
    return (False, None, -1)
   
def main():
    # number of cars
    n = 40
    # lanes
    l = 2
    # length of the road
    L = 3000
    # note the no. of cars at a time
    carsAtATimeList = []
    # note the fully switched times
    fullySwitchedTList = []
    for num in range(1, n//2):
        # SETTING UP CARS
        # represents the lanes
        mat = [[None]*(n+1) for _ in range(l+1)] # lane 2 is the merge lane 
        # stores number of cars in each lane
        cars = [n//2, n//2]
        # place the cars
        ID = 0
        for i in range(l):
            for j in range(cars[i]):
                mat[i][j] = Car(ID, j*5, i, 40)
                ID += 1
        # the time
        t = 0
        # what time step we are at
        timeStep = 0
        # when to end
        endTime = 300
        # TRAFFIC LIGHT PARAMS
        # when lane 0 closes
        mergeTime = 0.01
        # signal means the lane the car is in
        signal = 1
        # set the crossing point
        crossingPoint = 0
        # number of cars crossed
        numCarsCrossed = 0
        # notes the time taken for all cars to fully switch
        fullySwitchedTime = 0
        # mark the cars that will switch
        switchingCars = []
        # SIMULATION
        # start the time
        while t <= endTime:
            t += 0.01
            timeStep += 1
            # its time to close lane 0
            if (timeStep == (mergeTime/0.01)):
                for a in range(len(mat[signal])):
                    if (mat[signal][a] is None):
                        # we reached the first none slot, use the leading car's position to place the traffic light
                        crossingPoint = mat[signal][a - 1].getPosition(timeStep - 1) + 5
                        mat[signal][a] = TrafficLight(crossingPoint, signal)
                        break
            
            if (timeStep > (mergeTime/0.01)):
                # switch the cars that have crossed
                for (curCar, ln) in switchingCars:
                    # print(str(curCar.ID) + " switched: " + str(curCar.lane) + " to " + str(ln) + " timeStep: " + str(timeStep) + " pos: " + str(curCar.getPosition(timeStep - 1)))
                    # switch the car
                    mat[ln][len(mat[ln]) - 1] = curCar
                    # remove car from previous lane
                    for a, c in enumerate(mat[curCar.lane]):
                        if (c is not None and isinstance(c, Car)):
                            if (c.ID == curCar.ID):
                                mat[curCar.lane][a] = None
                    # sort both lanes
                    mat[ln].sort(key=lambda x : L if x is None else x.getPosition(timeStep-1))
                    mat[curCar.lane].sort(key=lambda x : L if x is None else x.getPosition(timeStep-1))
                    # change lane of the car
                    curCar.lane = ln
                # if all cars have merged
                if ((mat[0][0] is None or isinstance(mat[0][0], TrafficLight)) and (mat[1][0] is None or isinstance(mat[1][0], TrafficLight)) and 
                    fullySwitchedTime == 0):
                    print("noting..")
                    fullySwitchedTime = timeStep - (mergeTime/0.01)
                # reset the switching cars once switched
                switchingCars = []
                # switching traffic light if number of cars that crossed is 5
                if (numCarsCrossed == num or (mat[int(not signal)][0] is None or isinstance(mat[int(not signal)][0], TrafficLight))):
                    numCarsCrossed = 0
                    # now we switch the traffic light
                    for i in range(len(mat[signal])):
                        if (isinstance(mat[signal][i], TrafficLight)):
                            # switch to the other lane
                            mat[signal][i] = None
                            # sort the lane where traffic light is removed
                            mat[signal].sort(key=lambda x : L if x is None else x.getPosition(timeStep-1))
                            signal = int(not signal)
                            # place in the new lane
                            mat[signal][len(mat[signal]) - 1] = TrafficLight(crossingPoint, signal)
                            mat[signal].sort(key=lambda x : L if x is None else x.getPosition(timeStep-1))
                            break
                    # display the positions
                    # for a in range(l + 1):
                    #     for b in range(n):
                    #         if (mat[a][b] is None):
                    #             print(None, end=" ")
                    #         else:
                    #             if (isinstance(mat[a][b], Car)):
                    #                 print(str(mat[a][b].ID) + "-" + str(mat[a][b].getPosition(timeStep - 1)), end=" ")
                    #             else:
                    #                 print("T-" + str(mat[a][b].getPosition(0)), end=" ")
                    #     print("\n")
            # go through each lane
            i = 0
            while i < l + 1:
                j = 0
                # go through every car
                while j < n + 1:
                    # current car's index
                    curCar = mat[i][j]
                    # if no more cars in this lane, that means no cars anywhere after
                    if (curCar == None):
                        break
                    # if current car is a traffic light, skip
                    if (isinstance(curCar, TrafficLight)):
                        j += 1
                        continue         
                    # next car's index
                    nextCar = mat[i][(j + 1) % n]
                    if (nextCar == None):
                        # see if merged lane ahead has a car
                        if (mat[2][0] == None):
                            nextCar = mat[i][0]
                        else:
                            nextCar = mat[2][0]
                    # current car's position
                    x1 = curCar.getPosition(timeStep - 1)
                    # next car's position
                    x2 = nextCar.getPosition(timeStep - 1)
                    # we have to see if the next car is the same car
                    if (nextCar == curCar):
                        curCar.appendVelocity(func(1, x1, x2, curCar.vMax, curCar.dMin, 0, L))
                    else:     
                        if ((x2 - x1) % L <= curCar.dMin):
                            curCar.appendVelocity(0)
                        else:
                            curCar.appendVelocity(func(1, x1, x2, curCar.vMax, curCar.dMin, 0, L))
                    # get next position
                    curCar.appendPosition((curCar.getPosition(timeStep-1) + 0.01*curCar.getVelocity(timeStep)) % L) 
                    # check if the car has crossed the crossing point now
                    if (curCar.getPosition(timeStep) > crossingPoint and timeStep > (mergeTime/0.01) and curCar.lane != 2):
                        # print(str(curCar.getPosition(timeStep)) + " " + str(crossingPoint))
                        # count the number of cars that have crossed
                        numCarsCrossed += 1
                        switchingCars.append((curCar, 2))
                    # inc to next car
                    j += 1     
                # inc to next lane
                i += 1

        # append to list
        carsAtATimeList.append(num)
        # append time to fully merge
        fullySwitchedTList.append(fullySwitchedTime)
    print(fullySwitchedTList)
    print(carsAtATimeList)
    # DISPLAYING RESULTS
    plt.plot(carsAtATimeList, fullySwitchedTList)
    plt.xlabel("# of cars at a time")
    plt.ylabel("Time to fully merge")
    plt.show()

if __name__ == "__main__":
    main()

  