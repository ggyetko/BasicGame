from linecache import cache
import msvcrt
from pydoc import visiblename
import string
from os import system, name
from time import sleep
from tkinter import HIDDEN
from unittest.case import _AssertRaisesContext

class Colors:
    """ ANSI color codes """
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def getChar(permitted, allowBs, allowCr):
    ch = " "
    while str(ch) not in permitted:
        ch = msvcrt.getch().decode("utf-8")
        ch = ch.lower()
        if ord(ch) == 13:
            if allowCr:
                return chr(13)
        if ord(ch) == 8:
            if allowCr:
                return chr(8)
    return ch

def getAString(prompt, minLen, maxLen):
    out = ""
    done = False
    while not done:
        clear ()
        print (prompt)
        print (out)
        ch = getChar(string.ascii_lowercase, True, True)
        if ord(ch) == 13:
            if len(out) >= minLen:
                done = True
        elif ord(ch) == 8:
            if len(out):
                out = out[:-1]
        else:
            if ch in string.ascii_lowercase and len(out) < maxLen:
                if len(out) == 0:
                    out += ch.upper()
                elif out[-1] == " ":
                    out += ch.upper()
                else:
                    out += ch
    return out

class Player:
    def __init__(self,name):
        self.name = name
        self.maxHp = 10
        self.hp = 10
        self.str = 5
        self.dex = 5
        self.wis = 5
        self.armour = []
        self.weapon = []
        self.inv = []
        self.gp = 100
        self.x = 0
        self.y = 0
    def getLocTuple(self):
        return (self.x, self.y)
    def move(self, x, y):
        self.x = x
        self.y = y
    def getLocAfterMove(self, moveTup):
        return (self.x + moveTup[0], self.y + moveTup[1])
    def takeInvItem(self, item):
        self.inv.append(item)
        return item.name
    def display(self):
        clear()
        print ("{}{}".format( Colors.WHITE, self.name))
        print (Colors.LIGHT_CYAN+"-"*len(self.name)+Colors.WHITE)
        print ("Str: {}   Hp: {}/{}".format(self.str,self.hp,self.maxHp))
        print ("Dex: {}   ".format(self.dex))
        print ("Wis: {}   Gp: {}".format(self.wis,self.gp))
        print ("Str: {}   ".format(self.str))
        print ("Armour: ",self.armour)
        print ("Weapon: ",self.weapon)
        print ("Inventory:\n ",self.inv)
        print("Press Enter to continue")
        getChar("",False,True)

class MapResponse:
    def __init__(self, use=False, pickup=False, unlock=False, victory=False):
        self.use = use
        self.pickup = pickup
        self.unlock = unlock
        self.victory = victory
    def __repr__(self):
        out = "Response:"
        out += "use" if self.use else ""
        out += "pickup" if self.pickup else ""
        out += "unlock" if self.unlock else ""
        return out

class BlockedReason:
    def __init__(self, bString, bTuple):
        self.bString = bString
        self.bTuple = bTuple

class Map:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.victoryPoint = None
        self.contents = {}
        self.walls = []
        self.known = []
        self.houses = []
        for xCo in range(0,self.x):
            row = []
            knownRow = []
            for yCo in range(0, self.y):
                row.append(0)
                knownRow.append(0)
            self.walls.append(row)
            self.known.append(knownRow)
        self.addWall(0,0,self.x-1,0)
        self.addWall(0,1,0,self.y-1)
        self.addWall(self.x-1,1,self.x-1,self.y-1)
        self.addWall(0,self.y-1,self.x-1,self.y-1)     
        
    def isInAnyHouse(self, x, y):
        for h in self.houses:
            if h.isWithinWall(x,y):
                return True
        return False
        
    def setVictoryPoint(self, x, y):
        self.victoryPoint = (x,y)
 
    def takeItem(self, player):
        if player.getLocTuple() in self.contents:
            return self.contents.pop(player.getLocTuple())
        
    def unlock(self, locTuple, player):
        if locTuple not in self.contents:
            return BlockedReason("Nothing There",locTuple)
        if type(self.contents[locTuple]) != LockedDoor:
            return BlockedReason("Not a Lock",locTuple)
        for item in player.inv:
            if type(item) == Key:
                if self.contents[locTuple].tryUnlock(item) == True:
                    return True
        return BlockedReason("You don't have the key",locTuple)
    
    def getObjName(self, tuple):
        if tuple in self.contents:
            return self.contents[tuple].name
        return "No object"

    def addWall(self, x1, y1, x2, y2):
        for x in range(x1,x2+1):
            for y in range (y1,y2+1):
                self.walls[x][y] = 1
                
    def addMapObject(self, locTup, obj):
        self.contents[locTup] = obj
        
    def display(self, player):
        mr = MapResponse()
        clear()
        # Mark a 5x5 grid around the player as known
        for x in range(max(0,player.x-2), min(self.x, player.x+3)):
            for y in range(max(0,player.y-2), min(self.y, player.y+3)):
                visible = True
                for h in self.houses:
                    if h.isSpotHiddenFromPlayer(x,y,player):
                        visible = False
                        break
                if visible:
                    self.known[x][y] = 1
        
        #print the whole grid
        for y in range(0,self.y):
            line = ""
            for x in range(0,self.x):
                # only known things get printed
                if self.known[x][y]:
                    if x==player.x and y==player.y:
                        line += Colors.WHITE + "X"
                        # if we're over top of a potential pick-up item, note it
                        if (x,y) in self.contents and isinstance(self.contents[(x,y)],InvObject):
                            mr.pickup = True
                        if (x,y) == self.victoryPoint:
                            mr.victory = True
                    elif (x,y) == self.victoryPoint:
                        line += Colors.YELLOW + "!"
                    elif (x,y) in self.contents:
                        line += Colors.LIGHT_CYAN + self.contents[(x,y)].getLetter()
                    elif self.walls[x][y]:
                        line += Colors.WHITE + "□"
                    else:
                        line += Colors.DARK_GRAY + "."
                else:
                    line += " "
            print (line)
        return mr
    def isLegalSpot(self, loc):
        if self.walls[loc[0]][loc[1]] == 1:
            return BlockedReason("Wall",loc)
        if loc not in self.contents:
            return True
        if self.contents[loc].getPassable() == True:
            return True
        return BlockedReason(self.contents[loc].getPassable(),loc)
    def makeHouse(self,x1,y1,x2,y2,doorNorth,doorEast,doorSouth,doorWest):
        self.houses.append(MapHouse(x1,y1,x2,y2))
        self.addWall(x1,y1,x1,y2)
        self.addWall(x2,y1,x2,y2)
        self.addWall(x1,y1,x2,y1)
        self.addWall(x1,y2,x2,y2)
        openings = []
        if doorNorth:
            openings.append((int( (x2+x1)/2 ),y1))
        if doorEast:
            openings.append((x2,int( (y2+y1)/2 )))
        if doorSouth:
            openings.append((int( (x2+x1)/2 ),y2))
        if doorWest:
            openings.append((x1,int( (y2+y1)/2 )))
        for o in openings:
            self.walls[o[0]][o[1]] = 0
        return openings
       
class MapHouse:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def isWithinWall(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    def isInsideHouse(self, x, y):
        return self.x1 < x < self.x2 and self.y1 < y < self.y2
    def isSpotHiddenFromPlayer(self, x, y, player):
        return self.isInsideHouse(x,y) and not self.isWithinWall(player.x, player.y) or \
            self.isInsideHouse(player.x,player.y) and not self.isWithinWall(x,y)
    def __repr__(self):
        return str(self.x1) + " " +str(self.y1) + " " +str(self.x2) + " " +str(self.y2)
        
        
class MapObject:
    def __init__(self, name, passable, letter=""):
        self.name = name
        if len(letter) == 1:
            self.letter = letter[0]
        else:
            self.letter = self.name[0]
        self.passable = passable
    def getPassable(self):
        return self.passable
    def getLetter(self):
        return self.letter
    def __repr__(self):
        return self.name + " " + self.letter
    
class LockedDoor(MapObject):
    def __init__(self,name,colour=Colors.LIGHT_CYAN):
        self.name = name
        self.locked = True
        self.letter = colour+"|"
    def getPassable(self):
        if self.locked:
            return "Locked Door ("+self.name+")"
        else:
            return True
    def tryUnlock(self, key):
        if key.lockName == self.name:
            self.locked = False
            self.letter = "O"
            return True
        return False

class InvObject:
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return self.name
    def getLetter(self):
        return "?"
    def getPassable(self):
        return True

class Key(InvObject):
    def __init__(self, name, lockName):
        self.name = name
        self.lockName = lockName
    def getLockName(self):
        return self.lockName
    def getLetter(self):
        return "p"

moveDict = {"a":(-1,0), "d":(1,0), "w":(0,-1), "s":(0,1)}
def runGame(mp1, player):
    playing = True
    blockedReason = None
    message = ""
    while playing:
        mr = mp1.display(player)
        #print(player.x,player.y)
        #print (mp1.houses)
        print("-" * mp1.x)
        unlockTuple = None
        if blockedReason:
            print (Colors.LIGHT_RED + blockedReason.bString + Colors.WHITE)
            unlockTuple = blockedReason.bTuple
            blockedReason = None
        elif len(message):
            print (Colors.LIGHT_GREEN + message)
            message = ""
        else:
            print ("")
        print("{}\n Move: ASWD  (E)xamine {}{}{}e(X)it".format(\
            Colors.WHITE,\
            "(P)ick-up " if mr.pickup else "",\
            "(U)nlock " if unlockTuple else "",\
            "(V)ictory " if mr.victory else ""))
        resp = "asdwex"
        if mr.pickup:
            resp += "p"
        if unlockTuple:
            resp += "u"
        if mr.victory:
            resp += "v"
        ch = getChar(resp,False,False)
    
        if ch == "x":
            print ("Exit. Are you sure (y/n)?")
            ch = getChar("yn",False,False)
            if ch == "y":
                print ("Game Over")
                playing = False
        elif ch == "e":
            player.display()
        elif ch == "p":
            itemName = player.takeInvItem(mp1.takeItem(player))
            message = "You picked up " + itemName
        elif ch == "u":
            result = mp1.unlock(unlockTuple, player)
            if result == True:
                message = "You unlocked " + mp1.getObjName(unlockTuple)
            else:
                blockedReason = result
        elif ch == "v":
            print (Colors.GREEN + "!!! YOU WIN !!!")
            playing = False
        else:
            nextLoc = player.getLocAfterMove(moveDict[ch])
            #print (nextLoc)
            result = mp1.isLegalSpot(nextLoc)
            if result == True:
                player.move(nextLoc[0], nextLoc[1])
            else:
                blockedReason = result
