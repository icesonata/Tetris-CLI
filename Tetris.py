import os, time, random, readchar, copy, sys, queue, threading
from datetime import datetime

#program requires pip and readchar library from pip
#game was written without using OOP method
#using 'class' as public method (or be called 'struct' in different language)
#the game are created for Ubuntu OS only

#init board's size
colSize = 10
rowSize = 20

#queue to manage threads
inputQueue = queue.Queue()

#init global array as square matrix, we will cut unneccesary parts of matrix (i.e row or column with fully '0') later
shapeO = [
    [1,1],
    [1,1]
]
shapeL = [
    [0,0,1],
    [1,1,1],
    [0,0,0]
]
shapeJ = [
    [1,0,0],
    [1,1,1],
    [0,0,0]
]
shapeS = [
    [0,1,1],
    [1,1,0],
    [0,0,0]
]
shapeZ = [
    [1,1,0],
    [0,1,1],
    [0,0,0]
]
shapeI = [
    [0,0,0,0],
    [1,1,1,1],
    [0,0,0,0],
    [0,0,0,0]
]
shapeT = [
    [0,1,0],
    [1,1,1],
    [0,0,0]
]

#initialize 3-Dimensional array contain various type of block's shape
blockShape = [shapeO,shapeL,shapeJ,shapeS,shapeZ,shapeI,shapeT]

#initialize color code array for display colorful block
#we don't use black color due to black theme Terminal are
colorCode = [
	"\033[0m  \033[m",          #blank
	"\033[0;31;41m[]\033[m",    #Text: Red, Background: Red
	"\033[0;32;42m[]\033[m",    #Text: Green, Background: Green
	"\033[0;33;43m[]\033[m",    #Text: Yellow, Background: Yellow
	"\033[0;34;44m[]\033[m",    #Text: Blue, Background: Blue
	"\033[0;35;45m[]\033[m",    #Text: Purple, Background: Purple
	"\033[0;36;46m[]\033[m",    #Text: Cyan, Background: Cyan
	"\033[0;37;47m[]\033[m"     #Text: White, Background: White
]

#SRS rotation
#Wall Kick case
#apply for J,L,Z,S,T Tetromino's case following clockwise direction
#test1 will be all {0,0} so we will skip test1
case1 = [[-1, 0], [-1, 1], [0, -2], [-1, -2]] #0->R     #R means Right
case2 = [[1, 0], [1, -1], [0, 2], [1, 2]]     #R->2     #2 means succeed 2nd rotation
case3 = [[1, 0], [1, 1], [0, -2], [1, -2]]    #2->L     #L means Left
case4 = [[-1, 0], [-1, -1], [0, 2], [-1, 2]]  #L->0
#for I Tetromino's case (clockwise direction)
case1_i = [[-2, 0], [1, 0], [-2, -1], [1, 2]] #0->R
case2_i = [[-1, 0], [2, 0], [-1, 2], [2, -1]] #R->2
case3_i = [[2, 0], [-1, 0], [2, 1], [-1, -2]] #2->L
case4_i = [[1, 0], [-2, 0], [1, -2], [-2, 1]] #L->0

#initialize block as an Object (including elements: coordinate 'x':int, coordinate 'y':int, shape of block:[][]int)
#all element of object 'Block' are public, which means you can call it everytime you want
#it will be easier to work when using with coordinates
class Block(object):
    def __init__(self,x,y,shape,shapeType,rotateType):
        self.x = x              #storing horizontal coordinate x
        self.y = y              #storing vertical coordinate y
        self.shape = shape[:]   #shape[][]:int - storing shape of block
        self.shapeType = shapeType  #store following index of blockShape (range [0,6] means shapeO->shapeT above). For rotation supporting
        self.rotateType = rotateType    #store 1 number in range [0,3]. For rotation supporting
    #change all value 1 to another value in range [1,7] in order to get various colorful block 
    def reInit(self):
        num = random.randint(1,7)
        for i in range(len(self.shape)):
            for j in range(len(self.shape[0])):
                if self.shape[i][j] != 0:
                    self.shape[i][j] = num
    #transpose 2-Dimensional (square) matrix
    def transpose(self):
        for i in range(len(self.shape)): 
            for j in range(i+1,len(self.shape[0])):
                self.shape[i][j], self.shape[j][i] = self.shape[j][i], self.shape[i][j]
    #reverse (swap) each layer column of 2D matrix
    #input: arr[][]:int
    #output: arr[][]:int
    #reference: https://stackoverflow.com/questions/42519/how-do-you-rotate-a-two-dimensional-array/8664879#8664879?newreg=e1f2cab8974b45dcbe5ac61e8d1be2c9
    def reverseColumn(self):
        for i in range(len(self.shape)):
            for j in range(int(len(self.shape[0])/2)):
                self.shape[i][j], self.shape[i][len(self.shape[0])-1-j] = self.shape[i][len(self.shape[0])-1-j], self.shape[i][j]
    #rotate block
    def rotate(self,land):
        previousShape = copy.deepcopy(self.shape)
        self.transpose()
        self.reverseColumn()
        tempX = self.x
        tempY = self.y
        flag = False
        #if collision happen after the rotation
        #do all possible test in caseX array
        #X is number value in range [0,3] depends on rotateType, which shows transformation of block e.g 0->R, R->2)
        if checkCollision(land,self):
            #if block is not I Tetromino
            if self.shapeType != 5:
                if self.rotateType == 0:    #0->R
                    for i in range(len(case1)):
                        self.x += case1[i][0]
                        self.y += case1[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                elif self.rotateType == 1:  #R->2
                    for i in range(len(case2)):
                        self.x += case2[i][0]
                        self.y += case2[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                elif self.rotateType == 2:  #2->L
                    for i in range(len(case3)):
                        self.x += case3[i][0]
                        self.y += case3[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                else:   #== 3   #L->0
                    for i in range(len(case4)):
                        self.x += case4[i][0]
                        self.y += case4[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
            #if block is I Tetromino
            else:   #case shape I
                if self.rotateType == 0:    #0->R
                    for i in range(len(case1_i)):
                        self.x += case1_i[i][0]
                        self.y += case1_i[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                elif self.rotateType == 1:  #R->2
                    for i in range(len(case2_i)):
                        self.x += case2_i[i][0]
                        self.y += case2_i[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                elif self.rotateType == 2:  #2->L
                    for i in range(len(case3_i)):
                        self.x += case3_i[i][0]
                        self.y += case3_i[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
                else:   #== 3   #L->0
                    for i in range(len(case4_i)):
                        self.x += case4_i[i][0]
                        self.y += case4_i[i][0]
                        if not checkCollision(land,self):
                            flag = True
                            break
                        else:
                            self.x = tempX
                            self.y = tempY
        else:
            flag = True
        #check if rotate was succeed or not
        if flag == False:   #failed
            self.shape = previousShape
        else:               #succeed
            if self.rotateType == 3:
                self.rotateType = 0
            else:
                self.rotateType += 1
        
    def moveDown(self,land):
        self.y += 1
        if checkCollision(land,self):
            self.y -= 1

    def moveLeft(self,land):
        self.x -= 1
        if checkCollision(land,self):
            self.x += 1

    def moveRight(self,land):
        self.x += 1
        if checkCollision(land,self):
            self.x -= 1

    def hardDrop(self,land):
        while not checkCollision(land,self):
            self.y += 1
        #we make it into not checkCollision after force to drop it until collision happen
        self.y -= 1

#be careful with initializing 2-Dimensional array
#initialize board (new board)
#input:
#output: board[][]:int
def initBoard():
    board = [[0 for j in range(colSize)] for i in range(rowSize)]
    return board

#get random block
#input: shape[][][]:int (storing all shape of block), board[][]:int
#output: block:Block(object)
def randomBlock(shape,land):
    randomNumber = random.randint(0,6)
    randomShape = copy.deepcopy(shape[randomNumber])
    #block will display outside of land (more detail: block location will be higher than roof of land due to "-2" coordinate 'y')
    block = Block(int(len(land[0])/2) - len(randomShape[0]) + 1, -2, randomShape, randomNumber, 0)      #block will appear at the middle of the top of the board
    block.reInit()
    return block

#merge block with board (temporary board)
#input: board[][]:int, block:Block(object)
#output: board[][]:int
def mergeBlock(land,block):
    #create temporary variable to avoid change of array's elements' values
    temp = copy.deepcopy(land)
    for i in range(len(block.shape)):
        for j in range(len(block.shape[0])):
            if block.shape[i][j] != 0:
                #additional condition for display block even block is outside (above, higher from roof of land)
                if block.y + i <= rowSize - 1 and block.y + i >= 0 and block.x + j <= colSize - 1 and block.x + j >= 0:
                    temp[block.y+i][block.x+j] = block.shape[i][j]
    return temp

#collision between block and land (main board), between block and pieces of other previous block
#also the most important function
#input: land[][]:int, block:Block(object)
#output: True or False
def checkCollision(land,block):
    for i in range(len(block.shape)):
        for j in range(len(block.shape[0])):
            if block.shape[i][j] != 0:
                if block.x+j < 0 or block.x+j > colSize-1 or block.y+i > rowSize-1:
                    return True
                elif block.x+j >= 0 and block.x+j <= colSize - 1 and block.y+i >= 0 and block.y+i <= rowSize-1:
                    if land[block.y+i][block.x+j] != 0:
                        return True
    return False

#reach top??? we just need to check the first line at the top of the land
#if it has any piece, return True to alarm that the game will be over at the next move 
#input: land[][]:int
#output: True or False
def checkReachTop(land):
    for j in range(len(land[0])):
        if land[0][j] != 0:
            return True         #the game will be over
    return False                #the game is continuing
        
#check every single line of land array (main board)
#we will delete lines which is full by make it clear with 0 and swap very couple lines from i to 0 as (line[i] = line[i-1]), (line[i-1] = line[i-2]), ...
#swap from under line to top line 
#input: land[][]:int, score:int
#output: land[][]:int (after checking and re-merging), score:int 
def handleFullLine(land,score):
    flag = True
    line = []
    #collect all line was full
    for i in range(len(land)):
        flag = True
        for j in range(len(land[0])):
            if land[i][j] == 0:
                flag = False
                break
        if flag == True:
            line.append(i)
    
    for i in line:
        score += 100    #get score
        for j in range(len(land[0])):
            land[i][j] = 0
        #copy land's row which is clear with value 0
        temp = copy.deepcopy(land[i])
        #take that row out
        land.pop(i)
        #and insert it to the first position of array 'land'
        land.insert(0,temp)

    return land, score

#delay program for t second
#input: t:int
def sleep(t):
    time.sleep(t)

#clear console
def clearScreen():
    os.system("clear")

#in: arr:[][]int, nextblock:Block(object), score:int, color:[]string
#out: []string
def outputConvert(land,block,nextblock,score,color):
    arr = mergeBlock(land,block)
    #temporary variables for printing out next Block
    tempIndexRow = 0
    tempIndexCol = 0
    #output array type string
    strout = []
    tempstr = ""
    for i in range(len(arr)):
        #refresh
        tempIndexCol = 0
        tempstr = ""
        #
        if i == 0:
            strout.append("  " + "_ "*colSize)
        for j in range(len(arr[0])):
            if j == 0:
                tempstr += "||"
            if i == len(arr)-1 and arr[i][j] == 0:
                tempstr += "_ "
            else:
                tempstr += color[arr[i][j]]
            if j == len(arr[0])-1:
                tempstr += "||"
        if i == 1:
            tempstr += "   Score: " + str(score)
        elif i == 3:
            tempstr += "   Next"
        elif i > 4 and tempIndexRow < len(nextblock.shape):
            tempstr += "   "
            while tempIndexCol < len(nextblock.shape[0]):
                tempstr += color[nextblock.shape[tempIndexRow][tempIndexCol]]
                tempIndexCol += 1
            tempIndexRow += 1
         #   
        strout.append(tempstr)

    return strout 

#print out 2D array and score
#input: arr[][]:int, nextBlock:Block(object), score:int, color:[]string
def display(strout):
    clearScreen()
    for i in range(len(strout)):
        print("\r" + strout[i])
    print("\rPress: W - Rotate, S - Fall down faster, A - Move left, D - Move Right")
    print("\rPress: Spacebar - Hard Drop")
    print("\rPress: X to exit the program ")

#thread get input from keyboard
def getKey():
    while True:
        key = readchar.readkey()
        inputQueue.put(key)
        if key == "x" or key == "X":
            sys.exit()

#do movement according to input
#input: board, land:[][]int; block:Block(object); inputQueue:Queue; score:int; levelUp:int; color:[]string
#output: board, land:[][]int; block:Block(object); inputQueue:Queue; key:string
def doMovement(land,block,nextBlock,intputQueue,score,levelUp,color):
    key = ""
    preSec = int(round(time.time()*1000))
    while not inputQueue.empty():
        key = inputQueue.get()
        if key == "w" or key == "W":
            block.rotate(land)
        elif key == "a" or key == "A":
            block.moveLeft(land)
        elif key == "d" or key == "D":
            block.moveRight(land)
        elif key == "s" or key == "S":
            block.moveDown(land)
        elif key == " ":
            block.hardDrop(land)
        elif key == "x" or key == "X":
            break
        else:
            continue
        performArray = outputConvert(land,block,nextBlock,score,color)
        display(performArray)
        sleep(0.01)
        #do movement in only 1 second (can be decreased due to increasing of scores)
        if int(round(time.time()*1000)) - preSec >= 1000 - levelUp or key == " ":
            break
    return block, inputQueue, key

#input: color:[]string, shape:[][][]int, inputQueue:Queue(object)
def Tetris(color,shape,inputQueue):
    #Main program begin here:
    #Initialization
    land = initBoard()
    score = 0
    levelUp = 0
    preSec = 0
    key = ""
    #
    block = randomBlock(shape,land)
    nextBlock = randomBlock(shape,land)
    #Begin the game, print out the first scene
    performArray = outputConvert(land,block,nextBlock,score,color)
    display(performArray)
    while True:
        levelUp = int(160 * int(score/500))
        if score >= 3000:
            levelUp = 900
        block, inputQueue, key = doMovement(land,block,nextBlock,inputQueue,score,levelUp,color)
        if int(round(time.time()*1000)) - preSec >= 1000-levelUp or key == " ":
            block.y += 1
            if checkCollision(land,block):
                block.y -= 1
                inputQueue.queue.clear()
                land = mergeBlock(land,block)
                land, score = handleFullLine(land,score)
                block = nextBlock
                nextBlock = randomBlock(shape,land)
            preSec = int(round(time.time()*1000))
            performArray = outputConvert(land,block,nextBlock,score,color)
            display(performArray)
        if checkReachTop(land) or key == "x" or key == "X":
            print("\r\033[1;31mGAME OVER\033[m")
            sys.exit()
        else:
            sleep(0.01)

#initialize threads
drive1 = threading.Thread(target=Tetris,args=(colorCode,blockShape,inputQueue))
drive2 = threading.Thread(target=getKey)
#start threads
drive1.start()
drive2.start()