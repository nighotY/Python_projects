#Memory Game

import random
import pygame
import sys
from pygame.locals import *
from playsound import playsound

frames_per_second = 30    # frames per second (general speed of the program)
window_width = 640        # size of window's width in pixels
window_height = 480       # size of windows' height in pixels
reveal_speed = 8          # reveal 8 boxes and cover
box_size = 40             # size of box height & width in pixels
gap_size = 10             # gap between boxes in pixel
board_width = 10          # number of columns of icons
board_height = 7          # number of rows of icons

#ensure that the board width and height selected should be an even number
assert (board_width * board_height) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'

#side margins of board in pixel
x_margin = int((window_width - (board_width * (box_size + gap_size))) / 2)
y_margin = int((window_height - (board_height * (box_size + gap_size))) / 2)

#color      R    G    B
gray     =  (100, 100, 100)
navyblue =  ( 60,  60, 100)
white    =  (255, 255, 255)
red      =  (255,   0,   0)
green    =  (  0, 255,   0)
blue     =  (  0,   0, 255)
yellow   =  (255, 255,   0)
orange   =  (255, 128,   0)
purple   =  (255,   0, 255)
cyan     =  (  0, 255, 255)

background_color = navyblue     #background color
light_bg_color = gray           #light back ground color
box_color = white               #box bolor
highlight_color = blue          #highlight color

#Icons
donut = 'donut'
square = 'square'
diamond = 'diamond'
lines = 'lines'
oval = 'oval'


all_colors = (red, green, blue, yellow, orange, purple, cyan)
all_shapes = (donut, square, diamond, lines, oval)

#make sure have enough color/shape combination for the board
assert len(all_colors) * len(all_shapes) * 2 >= board_width * board_height, "Board is too big for the number of shapes/colors defined."

def main():
    global frames_per_second_clock, display_surface
    pygame.init()
    frames_per_second_clock = pygame.time.Clock()
    display_surface = pygame.display.set_mode((window_width, window_height))

    mousex = 0 # used to store x coordinate of mouse event
    mousey = 0 # used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()    #function returns the list representing current state of the board
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    display_surface.fill(background_color) #drawing the window
    startGameAnimation(mainBoard)          #sneak-peek of which icons under which boxes 

    while True: # main game loop
        mouseClicked = False

        display_surface.fill(background_color) # drawing the window
        drawBoard(mainBoard, revealedBoxes)    #draw current state of the board

        for event in pygame.event.get(): # event handling loop
            #if the event object was either QUIT event or a KEYUP event for the ESC key then quit the game
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex, mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                mouseClicked = True

        boxx, boxy = getBoxAtPixel(mousex, mousey) #x, y co-ordinates of the box
        if boxx != None and boxy != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxx][boxy]:
                drawHighlightBox(boxx, boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxx, boxy)])
                revealedBoxes[boxx][boxy] = True # set the box as "revealed"
                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxx, boxy)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxx, boxy)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxx, boxy)])
                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxx][boxy] = False
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)
                    firstSelection = None # reset firstSelection variable

        # Redraw the screen and wait a clock tick.
        pygame.display.update()
        frames_per_second_clock.tick(frames_per_second)   #pause the program (frames_per_second s)


def generateRevealedBoxesData(val): #returns list of which boxes are covered
    revealedBoxes = []
    for i in range(board_width):
        revealedBoxes.append([val] * board_height)
    return revealedBoxes


def getRandomizedBoard():  #returns a list that represents state of the board
    # Get a list of every possible shape in every possible color.
    icons = []
    for color in all_colors:
        for shape in all_shapes:
            icons.append( (shape, color) )

    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(board_width * board_height / 2) # calculate how many icons are needed
    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(board_width):
        column = []
        for y in range(board_height):
            column.append(icons[0])
            del icons[0]                # remove the icons as we assign them
        board.append(column)
    return board


def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (box_size + gap_size) + x_margin
    top = boxy * (box_size + gap_size) + y_margin
    return (left, top)


def getBoxAtPixel(x, y):
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            boxRect = pygame.Rect(left, top, box_size, box_size)
            if boxRect.collidepoint(x, y):
                return (boxx, boxy)
    return (None, None)


def drawIcon(shape, color, boxx, boxy):
    quarter = int(box_size * 0.25) # syntactic sugar
    half =    int(box_size * 0.5)  # syntactic sugar

    left, top = leftTopCoordsOfBox(boxx, boxy) # get pixel coords from board coords
    # Draw the shapes
    if shape == donut:
        pygame.draw.circle(display_surface, color, (left + half, top + half), half - 5)
        pygame.draw.circle(display_surface, background_color, (left + half, top + half), quarter - 5)
    elif shape == square:
        pygame.draw.rect(display_surface, color, (left + quarter, top + quarter, box_size - half, box_size - half))
    elif shape == diamond:
        pygame.draw.polygon(display_surface, color, ((left + half, top), (left + box_size - 1, top + half), (left + half, top + box_size - 1), (left, top + half)))
    elif shape == lines:
        for i in range(0, box_size, 4):
            pygame.draw.line(display_surface, color, (left, top + i), (left + i, top))
            pygame.draw.line(display_surface, color, (left + i, top + box_size - 1), (left + box_size - 1, top + i))
    elif shape == oval:
        pygame.draw.ellipse(display_surface, color, (left, top + quarter, box_size, half))


def getShapeAndColor(board, boxx, boxy):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[boxx][boxy][0], board[boxx][boxy][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. 
    # "boxes" is a list of two-item lists, which have the x & y spot of the box.
    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(display_surface, background_color, (left, top, box_size, box_size))
        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])
        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(display_surface, box_color, (left, top, coverage, box_size))
    pygame.display.update()
    frames_per_second_clock.tick(frames_per_second)


def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(box_size, (-reveal_speed) - 1, -reveal_speed):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, box_size + reveal_speed, reveal_speed):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxx in range(board_width):
        for boxy in range(board_height):
            left, top = leftTopCoordsOfBox(boxx, boxy)
            if not revealed[boxx][boxy]:
                # Draw a covered box.
                pygame.draw.rect(display_surface, box_color, (left, top, box_size, box_size))
            else:
                # Draw the (revealed) icon.
                shape, color = getShapeAndColor(board, boxx, boxy)
                drawIcon(shape, color, boxx, boxy)


def drawHighlightBox(boxx, boxy):     #draw blue highlight around the box
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(display_surface, highlight_color, (left - 5, top - 5, box_size + 10, box_size + 10), 4)


def startGameAnimation(board):   #sneak-peek of which icons under which boxes
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(board_width):
        for y in range(board_height):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)


def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = light_bg_color
    color2 = background_color

    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        display_surface.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True


if __name__ == '__main__':
    main()


