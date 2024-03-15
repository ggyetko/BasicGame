import random
from BasicGame import *

pName = getAString("Time to Create a Character\n\nName your Character:", 3, 20)
print ("Good\nYou have chosen the name: ", pName)
player = Player(pName)
player.display()

# doornames (all will be used) and potential (minx,miny) locations (not all used)
doorList = ["Blue","Red","Ancient","Golden","Ethereal","Rose","Glass"]
houseCorners = [(12,2), (20,2), (30,10), (37,2), (50,6), (2,16), (11,12), (23,16), (39,15), (49,14)]

mp1 = Map(60,25)
#Start House
xS = random.randrange(3,10)
yS = random.randrange(3,9)
drDir = random.randrange(1,3)
doorway = mp1.makeHouse(0,0,xS,yS,False,drDir==1,drDir==2,False)[0]
mp1.addMapObject(doorway, LockedDoor("Wood Door", Colors.BROWN) )
mp1.addMapObject((random.randrange(2,xS),random.randrange(2,yS)),Key("Wooden Key", "Wood Door"))

hiddenObject = None
while len(doorList):
    doorName = doorList.pop(random.randrange(0,len(doorList)))
    houseFirstCorner = houseCorners.pop(random.randrange(0,len(houseCorners)))
    # place house
    xS = random.randrange(3,7)
    yS = random.randrange(3,7)
    houseSecondCorner = (houseFirstCorner[0]+xS, houseFirstCorner[1]+yS)
    drDir = random.randrange(1,5)
    doorway = mp1.makeHouse(houseFirstCorner[0],houseFirstCorner[1],houseSecondCorner[0],houseSecondCorner[1],\
                            drDir==1,drDir==2,drDir==3,drDir==4)[0]
    mp1.addMapObject(doorway, LockedDoor(doorName+" Door", Colors.BROWN) )
    if hiddenObject == None:
        # hide the victory spot here
        mp1.setVictoryPoint(houseFirstCorner[0]+int(xS/2),houseFirstCorner[1]+int(yS/2))
    else:
        mp1.addMapObject((houseFirstCorner[0]+int(xS/2),houseFirstCorner[1]+int(yS/2)), hiddenObject)
    hiddenObject = Key(doorName+" Key", doorName+" Door")

        
# key must be out in the open, not in any house
success = False
while not success:
    x = random.randrange(1,mp1.x-1)
    y = random.randrange(1,mp1.y-1)
    if not mp1.isInAnyHouse(x,y):
        mp1.addMapObject((x,y), hiddenObject)
        success = True
        
player.move(1,1)

runGame(mp1, player)
