import graphics as g
import york_graphics as yg
      
class Text(object):
    def __init__(self, string, x, y, size, colour):
        """
        param string: the text to be displayed.
        param x: the x position of the string at the center.
        param y: the y position of the string at the center.
        param size: the size of the displayed text.
        param colour: the colour of the displayed colour. The format of the string
                      is found using the york_graphics getRgbColour() function.
        """
        self.string = string
        self.x = x
        self.y = y
        self.size = size
        self.colour = colour

    def SetString(self, string):
        self.string = string

    def GetString(self):
        return self.string

    def GetPosition(self):
        return (self.x, self.y)

    def SetPosition(self, x, y):
        self.x = x
        self.y = y

    def GetColour(self):
        return self.colour

    def GetSize(self):
        return self.size
    
    def Draw(self):
        yg.moveTo(self.x, self.y)
        yg.setLineColour(self.colour)
        yg.setTextProperties(size = self.size)
        yg.drawText(self.string)     

    def _DrawBox(self):
        yg.moveTo(self.x, self.y + (self.height / 2))
        if self.hover:
            yg.setLineColour(self.hoverBgColour)
        else:
            yg.setLineColour(self.bgColour)
        yg.setLineThickness(self.height)
        yg.drawLine(self.width, 0)

        

class Button(object):
    """
    A clickable, hoverable, button.
    """
    MAIN_MENU_BTN_WIDTH  = 300
    MAIN_MENU_BTN_HEIGHT = 50
    
    BG_COLOUR         = yg.getRGBColour(46, 66, 63)
    TEXT_COLOUR       = yg.getRGBColour(210, 215, 211)
    HOVER_BG_COLOUR   = yg.getRGBColour(26, 40, 32)
    HOVER_TEXT_COLOUR = yg.getRGBColour(0, 255, 255)
    def __init__(self, x, y, width, height, text, bgColour, textColour, hoverBgColour, function):
        """
        param x:      the x position of the top left corner of the button.
        param y:      the y position of the top left corner of the button.
        param width:  the width of the button.
        param height: the height of the button.
        text:         the text displayed inside the button.
        function:     the function to be called when the button is clicked. Pass None if there is no callback.
        """
        self.x               = x
        self.y               = y
        self.width           = width
        self.height          = height
        self.bgColour        = bgColour
        self.hoverBgColour   = hoverBgColour
        self.textColour      = textColour
        self.function        = function

        self.text = Text(text, self.x + (self.width // 2), self.y + (self.height // 2), 14, self.textColour)

        self.hover = False

    def Hover(self):
        self.hover = True

    def UnHover(self):
        self.hover = False

    def Hovering(self):
        return self.hover
        
    def Click(self):
        """
        Call the callback function.
        """
        if self.function == None:
            return
        
        self.function()

    def Update(self, mousex, mousey):
        pass

    def Draw(self):
        self._DrawBox()
        self.text.Draw()
    
    def _DrawBox(self):
        yg.moveTo(self.x, self.y + (self.height / 2))
        if self.hover:
            yg.setLineColour(self.hoverBgColour)
        else:
            yg.setLineColour(self.bgColour)
        yg.setLineThickness(self.height)
        yg.drawLine(self.width, 0)



class TextEntry(object):
    """
    This class displays a text entry box, with a descriptive label to the left of it. 
    """
    LOWER_CASE_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    
    def __init__(self, screenWidth, labelText, entryText, maxCharacters):
        """
        param labelText:     the text string to be displayed in the label. This is a Text object.
        param entryText:     the text to appear in the entry box. If not empty, the texr is immediately replaced once the user starts typing.
        param maxCharacters: the maximum amount of characters allowed in the entry box. 
        """
        self.labelText = labelText
        self.entryText = entryText
        self.maxChars = maxCharacters

        # The background box is a button with no text,
        self.bgBtn = Button((screenWidth / 2) - ((Button.MAIN_MENU_BTN_WIDTH / 2)), 250,
                            Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                            "",
                            Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                            None)
        
    def Draw(self):
        self.bgBtn.Draw()
        self.labelText.Draw()
        self.entryText.Draw()

    def Update(self, key):
        if len(self.entryText.GetString()) > 0:
            if key == "BackSpace":
                self.entryText.SetString(self.entryText.GetString()[:-1])
                
        if key.lower() in self.LOWER_CASE_ALPHABET and len(self.entryText.GetString()) < self.maxChars:
            self.entryText.SetString(self.entryText.GetString() + key.upper())

    def GetEntryText(self):
        return self.entryText.GetString()


    
class Menu(object):
    """
    The base class for all menus in the game.

    To add a button to a menu, make a button object then append it to the buttons list. 
    """
    def __init__(self):
        # All buttons on the menu must be added to this list to allow keyboard selection.
        self.buttons = []
        
        # The index of the button in the buttons list currently being hovered over.
        self.currentHover = 0
        
    def HandleKeyboardInput(self):
        """
        Allow the user to navigate the menu using the keyboard.
        """
        if len(self.buttons) == 0:
            # No need to check for input regarding the buttons if the button list is empty.
            # If other keys are needed, overide this function.
            return  
        
        key = yg.getKeyPress()
        if key == "Down":
            self.buttons[self.currentHover].UnHover()
            if self.currentHover == len(self.buttons) - 1:
                self.currentHover = 0
            else:
                self.currentHover += 1
            
            self.buttons[self.currentHover].Hover()
            
            
        elif key == "Up":
            self.buttons[self.currentHover].UnHover()
            if self.currentHover == 0:
                self.currentHover = len(self.buttons) - 1
            else:
                self.currentHover -= 1
            
            self.buttons[self.currentHover].Hover()
            
        elif key == "Return":
            self.buttons[self.currentHover].Click()

    def DrawButtons(self):
        if len(self.buttons) == 0:
            return

        for button in self.buttons:
            button.Draw()

    def Update(self):
        raise NotImplementedError("All menus must be able to update.")
        
    def HandleInput(self):
        self.HandleKeyboardInput()


    
class StartMenu(Menu):
    """
    This menu is displayed at the very start of the game, and allows the user to begin play,
    view high scores or quit the game.
    """
    def __init__(self, screenWidth, startButtonFunc, viewScoresButtonFunc, quitButtonFunc):
        Menu.__init__(self)

        self.startBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 150,
                               Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                               "Start",
                               Button.BG_COLOUR, Button.TEXT_COLOUR,
                               Button.HOVER_BG_COLOUR,
                               startButtonFunc)
        
        self.viewScoresBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 250,
                                    Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                    "View High Scores",
                                    Button.BG_COLOUR, Button.TEXT_COLOUR,
                                    Button.HOVER_BG_COLOUR,
                                    viewScoresButtonFunc)

        self.quitBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH /2), 350,
                              Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                              "Quit",
                              Button.BG_COLOUR, Button.TEXT_COLOUR,
                              Button.HOVER_BG_COLOUR,
                              quitButtonFunc)

        self.buttons.append(self.startBtn)
        self.buttons.append(self.viewScoresBtn)
        self.buttons.append(self.quitBtn)

        self.buttons[0].Hover()
            
    def Draw(self):
       self.DrawButtons()

    def Update(self):
        pass

class DeathMenu(Menu):
    """
    This menu is displayed when the user had died, and allows them to play again, view high scores,
    save their score, or quit.
    """
    def __init__(self, screenWidth, playAgainBtnFunc, viewScoresBtnFunc, saveScoreBtnFunc, quitBtnFunc):
        Menu.__init__(self)

        self.playAgainBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 150,
                                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                   "Play Again",
                                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                                   playAgainBtnFunc)

        self.saveScoreBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 250,
                                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                   "Save Score",
                                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                                   saveScoreBtnFunc)

        self.viewScoresBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 350,
                                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                   "View High Scores",
                                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                                   viewScoresBtnFunc)

        self.quitBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 450,
                                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                   "Quit",
                                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                                   quitBtnFunc)

        self.buttons.append(self.playAgainBtn)
        self.buttons.append(self.saveScoreBtn)
        self.buttons.append(self.viewScoresBtn)
        self.buttons.append(self.quitBtn)

        self.buttons[0].Hover()

    def Draw(self):
        self.DrawButtons()

    def Update(self):
        pass
        
        

class SaveScoreMenu(Menu):
    """
    This menu allows the user to save the score they just achieved, along with a 3 letter username
    to identify who achieved the score.
    """
    def __init__(self, screenWidth, saveBtnFunc):
        Menu.__init__(self)

        self.entryLabelText = Text("Enter Username: ", (screenWidth / 2) - ((Button.MAIN_MENU_BTN_WIDTH / 2) - 90), 250 + 25, 14, Button.TEXT_COLOUR)
        self.entryEntryText = Text("", (screenWidth / 2) - ((Button.MAIN_MENU_BTN_WIDTH / 2) - 200), 250 + 25, 14, Button.TEXT_COLOUR)
        self.entry = TextEntry(screenWidth, self.entryLabelText, self.entryEntryText, 3)

        self.saveScoreBtn = Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 350,
                                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                                   "Save",
                                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                                   saveBtnFunc)

        self.buttons.append(self.saveScoreBtn)

        self.buttons[0].Hover()

    def GetUsername(self):
        return self.entry.GetEntryText()

    def HandleKeyboardInput(self):
        """
        OVERIDE.
        """
        key = yg.getKeyPress()

        if key == "Return":
            self.buttons[self.currentHover].Click()
        else:
            self.entry.Update(key)

    def Draw(self):
        self.entry.Draw()
        self.DrawButtons()        

    def Update(self):
        pass



class ViewHighScoresMenu(Menu):
    """
    This menu allows the user to view the top 5 high scores. If there are not 5 scores saved, display them all.
    """
    def __init__(self, scoresFile, screenWidth, goBackBtnFunc):
        """
        param calledFromStartScreen: true if this menu is being viewed straight from the start menu, false if not.
        """
        Menu.__init__(self)
    
        scores = self._LoadScores(scoresFile)
        scores.sort(key = lambda x : int(x.split(",")[0]), reverse = True)   

        i = 0
        while i < 5 and i < len(scores):            
            btnstr = str(i + 1) + ".\t " + scores[i].split(",")[1] + " " + scores[i].split(",")[0] + "\t\t"
            
            self.buttons.append( 
                Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 50 + (100 * i),
                       Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                       btnstr,
                       Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                       None))
            i += 1

        self.buttons.append(
            Button((screenWidth / 2) - (Button.MAIN_MENU_BTN_WIDTH / 2), 50 + (i*100),
                   Button.MAIN_MENU_BTN_WIDTH, Button.MAIN_MENU_BTN_HEIGHT,
                   "Back",
                   Button.BG_COLOUR, Button.TEXT_COLOUR, Button.HOVER_BG_COLOUR,
                   goBackBtnFunc))

        self.buttons[len(self.buttons) - 1].Hover()
        
    def HandleKeyboardInput(self):
        """
        OVERIDE.

        Overide to prevent the user from hovering over any of the buttons displaying the scores.
        """
        key = yg.getKeyPress()
        if key == "Return":
            self.buttons[len(self.buttons) - 1].Click()
    
    def Draw(self):
        self.DrawButtons()

    def Update(self):
        pass

    def _LoadScores(self, scoresFile):
        """
        Load the usernames and scores from the scores file into 2 separate lists, where the names and scores correspond with
        the index. e.g. names[2] has the score stored in scores[2].
        """
        scores = []
        with open(scoresFile, "r") as file:
            for line in file:
                # Make a string with the score in front of the name so it can be sorted.
                temp = line.split(",")[1].rstrip() + "," + line.split(",")[0]
                scores.append(temp)
        return scores
