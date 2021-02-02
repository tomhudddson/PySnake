import york_graphics as yg
from random import randint
from time import sleep

import menu

"""
TODO:
    - Make max tiles increase as the snake's length increases.

BUGS:
"""

class SnakeSegment(object):
    """
    This class holds the info for a single segment of the snake. A segment is one tile which
    is drawn on the screen.
    """
    MOVING_STILL      = 0
    MOVING_LEFT       = 1
    MOVING_RIGHT      = 2
    MOVING_UP         = 3
    MOVING_DOWN       = 4
    MOVING_OFF_SCREEN = 5
    MOVING_CANT       = 6
    
    def __init__(self, x, y):
        """
        These are the (x, y) positions of the snake on the board. IMPORTANT, they are not pixels,
        they are indexes for the board array. So when moving the snake, only increment by +- 1, otherwise
        there will be large jumps in the movement.
        """
        self.x = x
        self.y = y
        self.direction = self.MOVING_STILL  # direction the snake is moving
        self.nextdirection = self.MOVING_STILL   # the next direction the snake will move after the current move

    @staticmethod
    def AddSegment(snake, board, snakeTileId):
        """
        Add a snake segment to the end of the snake.

        Param snake: the snake array.
        Param board: the 2D board array.
        Param snakeTileId: the tile Id of the snake so it can be put on the board.
        """
        lastseg = snake[len(snake) - 1]
        lastx = lastseg.x
        lasty = lastseg.y

        if lastseg.direction == SnakeSegment.MOVING_RIGHT:
            newseg = SnakeSegment(lastx, lasty)
            newseg.direction = SnakeSegment.MOVING_RIGHT
            snake.append(newseg)
            board[lasty][lastx] = snakeTileId

        elif lastseg.direction == SnakeSegment.MOVING_LEFT:
            newseg = SnakeSegment(lastx, lasty)
            newseg.direction = SnakeSegment.MOVING_LEFT
            snake.append(newseg)
            board[lasty][lastx] = snakeTileId

        elif lastseg.direction == SnakeSegment.MOVING_UP:
            newseg = SnakeSegment(lastx, lasty)
            newseg.direction = SnakeSegment.MOVING_UP
            snake.append(newseg)
            board[lasty][lastx]

        elif lastseg.direction == SnakeSegment.MOVING_DOWN:
            newseg = SnakeSegment(lastx, lasty)
            newseg.direction = SnakeSegment.MOVING_DOWN
            snake.append(newseg)
            board[lasty][lastx]



class Game(object):
    """
    The main class which holds all game functionality. I put everything in class to make using
    local and global variables easier as I was having trouble keeping the snake moving.
    """
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 768

    TILE_SIZE = 32
    TILE_ID_EMPTY = 0
    TILE_ID_SNAKE = 1
    TILE_ID_FOOD  = 2
    TILE_ID_NONE  = 3  # used for getting the next tile when the snake is not moving, see GetNextTile() for details
    TILE_ID_OFF   = 4  # used for when the snake moves off screen, see GetNextTile() for details
    TILE_COLOUR_EMPTY = yg.getRGBColour(0, 255, 0)
    TILE_COLOUR_SNAKE = yg.getRGBColour(0, 0, 0)
    TILE_COLOUR_FOOD  = yg.getRGBColour(0, 0, 255)

    # Make sure the tiles fit onto the screen perfectly
    assert SCREEN_WIDTH % TILE_SIZE == 0
    assert SCREEN_HEIGHT % TILE_SIZE == 0

    TILES_HORIZONTAL = SCREEN_WIDTH // TILE_SIZE  # number of tiles on screen on the x axis
    TILES_VERTICAL = SCREEN_HEIGHT // TILE_SIZE   # number of tiles on screen on the y axis

    SCORES_FILE = "scores.txt"  # file name of the text file scores are saved to
    
    def __init__(self):
        """
        Set the board up ready for use in the game.
        """
        self.firstGame = True
        self.activeMenu = None
        self.showingStartScreen = True  # True if the start screen is being displayed instead of the play again screen, false if the other way round
        self.playingAgain = False

    def Init(self, isPlayingAgain = False):
        """
        Initialise the game. MAKE SURE THIS HAS BEEN CALLED BEFORE ENTERING THE MAIN GAME LOOP EVERYTIME.
        """
        # This only has to be done at the start of the game, so when the user has clicked "Play Again" from the death
        # menu, do not do it.
        if self.firstGame:
            yg.openWindow(width = self.SCREEN_WIDTH, height = self.SCREEN_HEIGHT, title = "Snake Assignment")
            
            # Move the window to the top left of the screen to stop the bottom not being shown
            # on my laptop. Unfortunately, I had modify a private variable.
            yg._window.master.geometry("%ix%i+%i+%i" % (self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 100, 10))

            self.activeMenu = menu.StartMenu(self.SCREEN_WIDTH, self.Start, self.ViewHighScores, self.Quit)
            self.firstGame = False

        if isPlayingAgain:
            self.activeMenu = None

        self.maxFoodTiles = 1
        self.nFoodTiles = 0

        self.score = 0
        self.running = False
        self.hasLost = False

        self.board = []  # hold the board tiles
        self.snake = []  # hold the snake segments
        
        # Fill the board array with empty tiles.
        for i in range(self.TILES_VERTICAL):
            row = []
            for j in range(self.TILES_HORIZONTAL):
                row.append(self.TILE_ID_EMPTY)
            self.board.append(row)

        # Spawn the snakes head
        snakex = randint(0, self.TILES_HORIZONTAL - 1)
        snakey = randint(0, self.TILES_VERTICAL - 1)
        self.board[snakey][snakex] = self.TILE_ID_SNAKE
        self.snake.append(SnakeSegment(snakex, snakey))

        self.scoreText = menu.Text("Score: 0", 75, 50, 12, yg.getRGBColour(0, 0, 0))

        self.DrawBoard()

        # The game is in the process of quitting. This means the main game loop will finish its current
        # loop then the game will close.
        self.quitting = False

    def DrawTile(self, x, y, size, colour):
        """
        Draw a single square at a given position, with a given size and colour,
        on the screen. Note the size, is both the width and height.
        """
        yg.moveTo(x, y + (size / 2))
        yg.setLineColour(colour)
        yg.setLineThickness(size)
        yg.drawLine(size, 0)

    def DrawBoard(self):
        yg.clearCanvas()
        yg.setCanvasColour(self.TILE_COLOUR_EMPTY)
        for row in range(self.TILES_VERTICAL):
            for col in range(self.TILES_HORIZONTAL):
                if self.board[row][col] == self.TILE_ID_SNAKE:
                    self.DrawTile(col*self.TILE_SIZE, row*self.TILE_SIZE, self.TILE_SIZE, self.TILE_COLOUR_SNAKE)
                elif self.board[row][col] == self.TILE_ID_FOOD:
                    self.DrawTile(col*self.TILE_SIZE, row*self.TILE_SIZE, self.TILE_SIZE, self.TILE_COLOUR_FOOD)

    def Draw(self):        
        self.DrawBoard()
        self.scoreText.Draw()

        if self.activeMenu != None:
            self.activeMenu.Draw()

        yg.updateCanvas()

    def HandleInput(self):
        """
        Handle user input when moving the snake, and starting and pausing the game.
        """
        if self.activeMenu == None:
            key = yg.getKeyPress()
            if key == "Left":
                self.snake[0].direction = SnakeSegment.MOVING_LEFT
            elif key == "Right":
                self.snake[0].direction = SnakeSegment.MOVING_RIGHT
            elif key == "Up":
                self.snake[0].direction = SnakeSegment.MOVING_UP            
            elif key == "Down":
                self.snake[0].direction = SnakeSegment.MOVING_DOWN
        else:
            self.activeMenu.HandleInput()
    
    def SpawnFood(self):
        """
        Randomly spawn a food tile on the board. Only spawn the tile if there is an available empty tile,
        and there are less than the maximum amount of tiles currently on the board. The maximum amount
        increases as the snake's length increases.
        """
        spawnx = randint(0, self.TILES_HORIZONTAL - 1)
        spawny = randint(0, self.TILES_VERTICAL - 1)
        if self.board[spawny][spawnx] == self.TILE_ID_EMPTY and self.nFoodTiles < self.maxFoodTiles:
            self.board[spawny][spawnx] = self.TILE_ID_FOOD
            self.nFoodTiles += 1         

    def GetNextTile(self, index, direction = None):
        """
        Return a tuple containing tile id and the (row, column) coordinates of the next tile the snake's head
        is going to pass through. If the snake is not moving, TILE_ID_NONE and the current coordinates of the
        snake's head are returned. If the snake is moving off the screen, TILE_ID_OFF and the current coordinates
        of the snake are returned.

        Params:
            - index:     the index of the snake segment getting the next tile
            - direction: the specified direction to check the next tile in. If not given, or is set to None, it
                         is automatically set to the current moving direction of that segment.

        Return tuple: (tileid, row, column, direction).
            - tileid: the id of the next tile
            - row: the row of the next tile
            - column: the column of the next tile
        """
        if direction == None:
           direction = self.snake[index].direction  # No direction given so automatically assigned 
        
        if direction == SnakeSegment.MOVING_LEFT:
            if self.snake[index].x - 1 < 0:
                return (self.TILE_ID_OFF, self.snake[index].y, self.snake[index].x)
            else:
                return (self.board[self.snake[index].y][self.snake[index].x - 1], self.snake[index].y, self.snake[index].x - 1)
        
        if direction == SnakeSegment.MOVING_RIGHT:
            if self.snake[index].x + 1 >= self.TILES_HORIZONTAL:
                return (self.TILE_ID_OFF, self.snake[index].y, self.snake[index].x)
            else:                              
                return (self.board[self.snake[index].y][self.snake[index].x + 1], self.snake[index].y, self.snake[index].x + 1)
        
        if direction == SnakeSegment.MOVING_UP:
            if self.snake[index].y - 1< 0:
                return (self.TILE_ID_OFF, self.snake[index].y, self.snake[index].x)
            else:
                return (self.board[self.snake[index].y - 1][self.snake[index].x], self.snake[index].y - 1, self.snake[index].x)
        
        if direction == SnakeSegment.MOVING_DOWN:
            if self.snake[index].y + 1 >= self.TILES_VERTICAL:
                return (self.TILE_ID_OFF, self.snake[index].y, self.snake[index].x)
            else:
                return (self.board[self.snake[index].y + 1][self.snake[index].x], self.snake[index].y + 1, self.snake[index].x)

        # The snake is not moving so return the not moving tuple
        return (self.TILE_ID_NONE, self.snake[index].y, self.snake[index].x)        

    def EatFood(self, nextTile):
        """
        Check if the snake's head is going to pass over a food tile, and if it is, remove the that food tile.
        If a food tile gets eaten, a new one is spawned.

        Return true if food has been eaten, return false if it hasn't.
        """
        if nextTile[0] == self.TILE_ID_FOOD:
            self.board[nextTile[1]][nextTile[2]] = self.TILE_ID_EMPTY
            self.nFoodTiles -= 1
            self.score += 1
            self.scoreText.SetString("Score: " + str(self.score))
            return True
        return False

    def CanHeadMove(self):
        if self.GetNextTile(0, SnakeSegment.MOVING_RIGHT) == self.TILE_ID_OFF:
            return False

        if self.GetNextTile(0, SnakeSegment.MOVING_LEFT) == self.TILE_ID_OFF:
            return False

        if self.GetNextTile(0, SnakeSegment.MOVING_UP) == self.TILE_ID_OFF:
            return False

        if self.GetNextTile(0, SnakeSegment.MOVING_DOWN) == self.TILE_ID_OFF:
            return False

        return True
    
    def MoveSnake(self):
        if not self.CanHeadMove():
            self.running = False
            return
        
        for i in range(1, len(self.snake)):
            self.snake[i].direction = self.snake[i].nextdirection

        # Move each segement.
        for i in range(len(self.snake)):
            nextTile = self.GetNextTile(i)
            seg = self.snake[i]  # make the rest of the function easier to read
            
            # Check for snake going off screen. If it does, the player has lost.
            if nextTile[0] == self.TILE_ID_OFF:
                self.activeMenu = menu.DeathMenu(self.SCREEN_WIDTH, self.PlayAgain, self.ViewHighScores, self.SaveScoreScreen, self.Quit)
                self.showingStartScreen = False  
                break

            # Only the head of the snake can eat food
            if i == 0:
                if self.EatFood(nextTile):
                    self.SpawnFood()
                    SnakeSegment.AddSegment(self.snake, self.board, self.TILE_ID_SNAKE)

            if seg.direction == SnakeSegment.MOVING_LEFT:
                self.board[seg.y][seg.x] = self.TILE_ID_EMPTY
                self.board[seg.y][seg.x - 1] = self.TILE_ID_SNAKE
                seg.x -= 1

            if seg.direction == SnakeSegment.MOVING_RIGHT:
                self.board[seg.y][seg.x] = self.TILE_ID_EMPTY
                self.board[seg.y][seg.x + 1] = self.TILE_ID_SNAKE
                seg.x += 1

            if seg.direction == SnakeSegment.MOVING_UP:
                self.board[seg.y][seg.x] = self.TILE_ID_EMPTY
                self.board[seg.y - 1][seg.x] = self.TILE_ID_SNAKE
                seg.y -= 1

            if seg.direction == SnakeSegment.MOVING_DOWN:
                self.board[seg.y][seg.x] = self.TILE_ID_EMPTY
                self.board[seg.y + 1][seg.x] = self.TILE_ID_SNAKE
                seg.y += 1

        # Set the direction of all segments, except the head, to the direction of the one in front.
        for i in range(1, len(self.snake)):           
            self.snake[i].nextdirection = self.snake[i - 1].direction

    def Update(self):
        self.SpawnFood()
        self.MoveSnake()
     
    def Start(self):
        self.activeMenu = None

    def ViewHighScores(self):
        if not self.showingStartScreen:
            self.activeMenu = menu.ViewHighScoresMenu(self.SCORES_FILE, self.SCREEN_WIDTH, self.PlayAgainScreen)
        else:
            self.activeMenu = menu.ViewHighScoresMenu(self.SCORES_FILE, self.SCREEN_WIDTH, self.StartScreen)
            
    def Quit(self):
        self.running = False
        self.quitting = True
        self.playingAgain = False

    def SaveScore(self):
        """
        Called when the user presses "Save" on the save scores menu.
        """
        with open(self.SCORES_FILE, "a") as file:
            file.write("%s,%i\n" % (self.activeMenu.GetUsername(), self.score))
            
        self.activeMenu = menu.DeathMenu(self.SCREEN_WIDTH, self.PlayAgain, self.ViewHighScores, self.SaveScoreScreen, self.Quit)

    def SaveScoreScreen(self):
        """
        Called when the user is saving a score. This function changes the menu to the view scores menu.
        """
        self.activeMenu = menu.SaveScoreMenu(self.SCREEN_WIDTH, self.SaveScore)

    def PlayAgainScreen(self):
        self.activeMenu = menu.DeathMenu(self.SCREEN_WIDTH, self.PlayAgain, self.ViewHighScores, self.SaveScoreScreen, self.Quit)

    def StartScreen(self):
        self.activeMenu = menu.StartMenu(self.SCREEN_WIDTH, self.Start, self.ViewHighScores, self.Quit)
        
    def PlayAgain(self):
        """
        Prepare to play another game.
        """
        self.running = False
        self.playingAgain = True
        self.activeMenu = None
    
    def Main(self, isPlayingAgain):
        if isPlayingAgain:                                            
            self.Init(True)
        else:
            self.Init(False)
        
        self.running = True
        while self.running:                
            self.HandleInput()

            if self.activeMenu == None:
                self.Update()
            else:
                self.activeMenu.Update()

            self.Draw()

            sleep(0.1)

        if self.playingAgain:
            self.Main(True)

        if self.quitting:
            sleep(0.5)
            yg.closeWindow()

snakeGame = Game()
snakeGame.Main(False)
