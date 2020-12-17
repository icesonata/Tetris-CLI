package main

import (
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"time"
)

var (
	colSize int = 10
	rowSize int = 20
	//
	shapeO = [][]int{
		{1, 1},
		{1, 1}}
	shapeL = [][]int{
		{0, 0, 1},
		{1, 1, 1},
		{0, 0, 0}}
	shapeJ = [][]int{
		{1, 0, 0},
		{1, 1, 1},
		{0, 0, 0}}
	shapeS = [][]int{
		{0, 1, 1},
		{1, 1, 0},
		{0, 0, 0}}
	shapeZ = [][]int{
		{1, 1, 0},
		{0, 1, 1},
		{0, 0, 0}}
	shapeI = [][]int{
		{0, 0, 0, 0},
		{1, 1, 1, 1},
		{0, 0, 0, 0},
		{0, 0, 0, 0}}
	shapeT = [][]int{
		{0, 1, 0},
		{1, 1, 1},
		{0, 0, 0}}
	//
	blockShape = [][][]int{shapeO, shapeL, shapeJ, shapeS, shapeZ, shapeI, shapeT}

	//
	colorCode = []string{
		"\033[0m  \033[m",       //blank
		"\033[0;31;41m[]\033[m", //Text: Red, Background: Red
		"\033[0;32;42m[]\033[m", //Text: Green, Background: Green
		"\033[0;33;43m[]\033[m", //Text: Yellow, Background: Yellow
		"\033[0;34;44m[]\033[m", //Text: Blue, Background: Blue
		"\033[0;35;45m[]\033[m", //Text: Purple, Background: Purple
		"\033[0;36;46m[]\033[m", //Text: Cyan, Background: Cyan
		"\033[0;37;47m[]\033[m"} //Text: White, Background: White
	//SRS rotation
	//Wall Kick case
	//apply for J,L,Z,S,T Tetromino's case following clockwise direction
	//test1 will be all {0,0} so we will skip test1
	case1 = [][]int{{-1, 0}, {-1, 1}, {0, -2}, {-1, -2}} //0->R
	case2 = [][]int{{1, 0}, {1, -1}, {0, 2}, {1, 2}}     //R->2
	case3 = [][]int{{1, 0}, {1, 1}, {0, -2}, {1, -2}}    //2->L
	case4 = [][]int{{-1, 0}, {-1, -1}, {0, 2}, {-1, 2}}  //L->0
	//for I Tetromino's case (clockwise direction)
	case1_i = [][]int{{-2, 0}, {1, 0}, {-2, -1}, {1, 2}} //0->R
	case2_i = [][]int{{-1, 0}, {2, 0}, {-1, 2}, {2, -1}} //R->2
	case3_i = [][]int{{2, 0}, {-1, 0}, {2, 1}, {-1, -2}} //2->L
	case4_i = [][]int{{1, 0}, {-2, 0}, {1, -2}, {-2, 1}} //L->0
)

//
type Block struct {
	x          int
	y          int
	shape      [][]int
	shapeType  int //store following index of blockShape (range [0,6] means shapeO->shapeT above). For rotation supporting
	rotateType int //store 1 number in range [0,3]. For rotation supporting
}

//
func (block *Block) reInit() {
	randomNum := rand.Intn(7-1) + 1
	for i := range block.shape {
		for j := range block.shape[0] {
			if block.shape[i][j] != 0 {
				block.shape[i][j] = randomNum
			}
		}
	}
}

//
func (block *Block) transpose() {
	for i := range block.shape {
		for j := 0 + i; j < len(block.shape[0]); j++ {
			//swap
			block.shape[j][i], block.shape[i][j] = block.shape[i][j], block.shape[j][i]
		}
	}
}

//
func (block *Block) reverseColumn() {
	temp := 0
	pivot := int(len(block.shape[0]) / 2)
	//swap column i with column len(block.shape)-1-i
	for i := range block.shape {
		for j := 0; j < pivot; j++ {
			temp = block.shape[i][j]
			block.shape[i][j] = block.shape[i][len(block.shape[0])-1-j]
			block.shape[i][len(block.shape[0])-1-j] = temp
		}
	}
}

//
func (block *Block) rotate(land [][]int) {
	previousShape := makeCopy(block.shape) //store previouse shape after rotated shape
	block.transpose()
	block.reverseColumn()
	tempX := block.x
	tempY := block.y
	flag := false
	//
	if checkCollision(land, *block) {
		//following my code, index 5 is I Tetromino, which has its own wall kick case
		if block.shapeType != 5 {
			if block.rotateType == 0 { //0->R
				for i := range case1 {
					block.x += case1[i][0]
					block.y += case1[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else if block.rotateType == 1 { //R->2
				for i := range case2 {
					block.x += case2[i][0]
					block.y += case2[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else if block.rotateType == 2 { //2->L
				for i := range case3 {
					block.x += case3[i][0]
					block.y += case3[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else { //case == 3	//L->0
				for i := range case4 {
					block.x += case4[i][0]
					block.y += case4[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			}
		} else {
			if block.rotateType == 0 { //0->R
				for i := range case1_i {
					block.x += case1_i[i][0]
					block.y += case1_i[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else if block.rotateType == 1 { //R->2
				for i := range case2_i {
					block.x += case2_i[i][0]
					block.y += case2_i[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else if block.rotateType == 2 {
				for i := range case3_i {
					block.x += case3_i[i][0]
					block.y += case3_i[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			} else { //case == 3	//L->0
				for i := range case4_i {
					block.x += case4_i[i][0]
					block.y += case4_i[i][1]
					if !checkCollision(land, *block) {
						flag = true
						break
					} else {
						block.x = tempX
						block.y = tempY
					}
				}
			}
		}
	} else {
		flag = true
	}
	//if rotation was failed
	if flag == false {
		block.shape = previousShape
		return
	}
	//
	if block.rotateType == 3 {
		block.rotateType = 0
	} else {
		block.rotateType += 1
	}
}

//
func (block *Block) moveDown(land [][]int) {
	block.y++
	if checkCollision(land, *block) {
		block.y--
	}
}

//
func (block *Block) moveLeft(land [][]int) {
	block.x--
	if checkCollision(land, *block) {
		block.x++
	}
}

//
func (block *Block) moveRight(land [][]int) {
	block.x++
	if checkCollision(land, *block) {
		block.x--
	}
}

//
func (block *Block) hardDrop(land [][]int) {
	for !checkCollision(land, *block) {
		block.y++
	}
	block.y--
}

//
func makeCopy(arr [][]int) [][]int {
	newArray := make([][]int, len(arr))
	for i := range arr {
		newArray[i] = make([]int, len(arr[0]))
		for j := range arr[0] {
			newArray[i][j] = arr[i][j]
		}
	}
	return newArray
}

//
func checkCollision(land [][]int, block Block) bool {
	for i := range block.shape {
		for j := range block.shape[0] {
			if block.shape[i][j] != 0 {
				if block.x+j < 0 || block.x+j > colSize-1 || block.y+i > rowSize-1 {
					return true
				} else if block.x+j >= 0 && block.x+j <= colSize-1 && block.y+i <= rowSize-1 && block.y+i >= 0 {
					if land[block.y+i][block.x+j] != 0 {
						return true
					}
				}
			}
		}
	}
	return false
}

//
func randomBlock(board [][]int, Shape [][][]int) Block {
	randomNum := rand.Intn(len(Shape) - 1)
	randomShape := makeCopy(Shape[randomNum])
	coordinateX := int(len(board[0])/2) - len(randomShape[0]) + 1
	coordinateY := -2
	block := Block{coordinateX, coordinateY, randomShape, randomNum, 0}
	block.reInit()
	return block
}

//
func initBoard() [][]int {
	board := make([][]int, rowSize)
	for i := range board {
		board[i] = make([]int, colSize)
	}
	return board
}

//
func mergeBlock(board [][]int, block Block) [][]int {
	for i := range block.shape {
		for j := range block.shape[0] {
			if block.shape[i][j] != 0 {
				if block.y+i >= 0 && block.y+i <= rowSize-1 && block.x+j >= 0 && block.x+j <= colSize-1 {
					board[block.y+i][block.x+j] = block.shape[i][j]
				}
			}
		}
	}
	return board
}

//
func checkReachTop(land [][]int) bool {
	for i := range land[0] {
		if land[0][i] != 0 {
			return true
		}
	}
	return false
}

//
func handleFullLine(land [][]int, score int) ([][]int, int) {
	var line []int
	var flag bool
	for i := range land {
		flag = true
		for j := range land[0] {
			if land[i][j] == 0 {
				flag = false
				break
			}
		}
		if flag == true {
			line = append(line, i)
		}
	}
	//index is line (row), j is column
	for _, index := range line {
		for j := range land[index] {
			land[index][j] = 0
		}
		for j := index; j > 0; j-- {
			//swap
			land[j-1], land[j] = land[j], land[j-1]
		}
		score += 100
	}
	return land, score
}

//
func ClearScreen() {
	cmd := exec.Command("clear")
	cmd.Stdout = os.Stdout
	cmd.Run()
}

//
func Display(arr [][]int, nextBlock Block, score int, Color []string) {
	ClearScreen()
	tempIndexRow := 0
	tempIndexCol := 0
	for i := range arr {
		tempIndexCol = 0
		if i == 0 {
			fmt.Print("\r  ")
			for k := 0; k < len(arr[0]); k++ {
				fmt.Print("\033[1m_ ")
			}
			fmt.Println("\033[m")
		}
		fmt.Print("\033[1m||\033[m")
		for j := range arr[0] {
			// fmt.Print(arr[i][j]," ")		//for print out 0, 1 (real board)
			if arr[i][j] == 0 && i == len(arr)-1 {
				fmt.Print("\033[1m_ \033[m")
			} else {
				fmt.Print(Color[arr[i][j]])
			}
		}
		if i == 1 {
			fmt.Println("\033[1m||          Your score: ", score, "\033[m")
		} else if i == 3 {
			fmt.Println("\033[1m||          Next\033[m")
		} else if i > 4 && tempIndexRow < len(nextBlock.shape) {
			fmt.Print("\033[1m||          \033[m")
			for tempIndexCol < len(nextBlock.shape[0]) {
				fmt.Print(Color[nextBlock.shape[tempIndexRow][tempIndexCol]])
				tempIndexCol++
			}
			fmt.Println("")
			tempIndexRow++
		} else {
			fmt.Println("\033[1m||\033[m")
		}
	}
	fmt.Println("\rPress: W - Rotate, S - Fall down faster, A - Move left, D - Move Right")
	fmt.Println("\rPress: Spacebar - Hard Drop")
	fmt.Println("\rPress: X to exit the program ")
}

//
func readInputKey() string {
	// disable input buffering
	exec.Command("stty", "-F", "/dev/tty", "cbreak", "min", "1").Run()
	// do not display entered characters on the screen
	exec.Command("stty", "-F", "/dev/tty", "-echo").Run()
	var b []byte = make([]byte, 1)
	os.Stdin.Read(b)
	return string(b)
}

//
func threadGetKey(inputQueue chan string) {
	for {
		key := readInputKey()
		if key == "x" || key == "X" {
			exec.Command("stty", "-F", "/dev/tty", "echo").Run()
			os.Exit(0)
		}
		inputQueue <- key
	}
}

//
func clearChan(inputQueue chan string) chan string {
	for len(inputQueue) != 0 {
		<-inputQueue
	}
	return inputQueue
}

//
func doMovement(board [][]int, land [][]int, block Block, nextBlock Block, Color []string, inputQueue chan string, score int, levelUp int) ([][]int, [][]int, Block, chan string, string) {
	var key string
	var preSec int = int(time.Now().UnixNano() / 1000000)
	for len(inputQueue) != 0 {
		key = <-inputQueue
		if key == "w" || key == "W" {
			block.rotate(land)
		} else if key == "a" || key == "A" {
			block.moveLeft(land)
		} else if key == "d" || key == "D" {
			block.moveRight(land)
		} else if key == "s" || key == "S" {
			block.moveDown(land)
		} else if key == " " {
			block.hardDrop(land)
		} else {
			continue
		}
		board = makeCopy(land)
		board = mergeBlock(board, block)
		Display(board, nextBlock, score, Color)
		time.Sleep(time.Microsecond)
		//if time pass (1 sec or less depended on level_up var)
		if (int(time.Now().UnixNano()/1000000)-preSec >= 1000-levelUp) || key == " " {
			break
		}
	}
	return board, land, block, inputQueue, key
}

//Tetris's main game functin
func Tetris(Color []string, Shape [][][]int) {
	//initializing
	land := initBoard()
	board := initBoard()
	score := 0
	//score and time drop
	var levelUp int = int(160 * int(score/500))
	var preSec int = 0
	//
	var key string
	inputQueue := make(chan string, 100)
	//begin get key input thread
	go threadGetKey(inputQueue)
	//begin the game
	block := randomBlock(board, Shape)
	nextBlock := randomBlock(board, Shape)
	board = mergeBlock(board, block)
	Display(board, nextBlock, score, Color)
	//
	for {
		levelUp = int(160 * int(score/500))
		if score >= 3000 {
			levelUp = 900
		}
		//
		board, land, block, inputQueue, key = doMovement(board, land, block, nextBlock, Color, inputQueue, score, levelUp)
		if int(time.Now().UnixNano()/1000000)-preSec >= 1000-levelUp || key == " " {
			block.y++
			if checkCollision(land, block) {
				block.y--
				inputQueue = clearChan(inputQueue)
				land = makeCopy(board)
				land, score = handleFullLine(land, score)
				block = nextBlock
				nextBlock = randomBlock(board, Shape)
			}
			board = makeCopy(land)
			board = mergeBlock(board, block)
			Display(board, nextBlock, score, Color)
			preSec = int(time.Now().UnixNano() / 1000000)
		}
		if checkReachTop(land) {
			exec.Command("stty", "-F", "/dev/tty", "echo").Run()
			fmt.Println("\r\033[1;31mGAME OVER\033[m")
			os.Exit(0)
		} else {
			time.Sleep(time.Millisecond)
		}
	}
}

//Main
func main() {
	rand.Seed(time.Now().UnixNano())
	Tetris(colorCode, blockShape)
}
