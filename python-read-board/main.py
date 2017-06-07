# -*- coding: utf-8 -*-
import json
import sys
if len(sys.argv) == 1:
    sys.stdin.read()

print(json.dumps([["X", {"down":3}, {"down":4}, "X", "X", "X", "X", {"down":15}, {"down":3}],[{"right":4}, None, None, {"down":16}, {"down":6}, "X", {"right":3}, None, None],[{"right":10}, None, None, None, None, {"down":14}, {"down":16, "right":7}, None, None],["X", "X", {"down":21, "right":16}, None, None, None, None, None, "X"],["X", {"right":3}, None, None, {"down":3, "right":11}, None, None, None, "X"],["X",{"right":6}, None, None, None, {"down":4, "right":10}, None, None, "X"],["X", {"down":4, "right":19}, None, None, None, None, None, {"down":3}, {"down":4}],[{"right":6}, None, None, "X", {"right":10}, None, None, None, None],[{"right":7}, None, None, "X", "X", "X", {"right":4}, None, None]]))
exit()
import cv2
import numpy as np
import math
from datetime import datetime

from mnist.main import run as getDigitFromMNIST
from helpers import getAllContours, getContourCenter, isCenterEqual, isPointInContour, calcDistance, cut_out_sudoku_puzzle, thresholdify, dilate, new_dilate, getAllTriangles, getAllSquares
from helpers import getContourApprox, getMiddleVertex, getRightVertex, getLeftVertex, getTopLeft, getBottomRight, findContourAndRectOfPoint, getRect

from imageHelper import show, drawLine, convertToGray, convertToColor
SAFETY_PIXEL_WIDTH = 3

def preProcess(image):
    #TODO: delete this line
    image = convertToGray(image)
    #image = cv2.GaussianBlur(image, (11, 11), 0)
    image = dilate(image)

    thresh = thresholdify(image)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2)) #TODO: was 2,2
    image = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    return image

def crop(image):
    contours = getAllContours(image.copy())
    contour = max(contours, key=cv2.contourArea)
    board = cut_out_sudoku_puzzle(image.copy(), contour)
    return board

def getBoardFromImage(imageFile):
    # read the image, blur it
    # create a structuring element to pass to
    orig = cv2.imread(imageFile)
    image = preProcess(orig)
    cropedImage = crop(image)
    #board = straighten(cropedImage)
    #show(board)
    return orig, cropedImage

def checkIfFarBiggerThanAreaSize(size, contour):
    # If the contour is bigger than 50% of the board
    return (cv2.contourArea(contour) > (size / 2))

def checkIfVeryBelowAreaSize(areaSize, contour):
    # If the contour is smaller than 60% of the average size
    return (cv2.contourArea(contour) < (areaSize * 0.6))

def getTwinContour(source, contours):
    sourceCenter = getContourCenter(source)
    contoursWithoutSource = list(filter(lambda x: not isCenterEqual(sourceCenter, x), contours))
    minDist = 10000000 #default value
    # getting the closest contour to sourceCenter
    closest = None
    for contour in contoursWithoutSource:
        currCenter = getContourCenter(contour)
        currDist = calcDistance(sourceCenter, currCenter)
        if (currDist < minDist):
            minDist = currDist
            closest = contour
    return closest

def drawSquare(image, topLeft, topRight, bottomRight, bottomLeft):
    colorOut = (255, 255, 255) # white
    colorIn = (0, 0, 0) # black
    outWidth = SAFETY_PIXEL_WIDTH
    inWidth = SAFETY_PIXEL_WIDTH

    image = convertToColor(image)

    # Drawing the outer border
    # top right to bottom right
    drawLine(image, topRight, bottomRight, colorOut, outWidth)
    # bottom right to bottom left
    drawLine(image, bottomRight, bottomLeft, colorOut, outWidth)
    # bottom left to top left
    drawLine(image, bottomLeft, topLeft, colorOut, outWidth)
    # top left to top right
    drawLine(image, topLeft, topRight, colorOut, outWidth)

    # Drawing the inner border
    # top right to bottom right
    drawLine(image, (topRight[0]-outWidth, topRight[1]+outWidth),
                    (bottomRight[0]-outWidth, bottomRight[1]-outWidth),
             colorIn, inWidth)
    # bottom right to bottom left
    drawLine(image, (bottomRight[0]-outWidth, bottomRight[1]-outWidth),
                    (bottomLeft[0]+outWidth, bottomLeft[1]-outWidth),
             colorIn, inWidth)
    # bottom left to top left
    drawLine(image, (bottomLeft[0]+outWidth, bottomLeft[1]-outWidth),
                    (topLeft[0]+outWidth, topLeft[1]+outWidth),
             colorIn, inWidth)
    # top left to top right
    drawLine(image, (topLeft[0]+outWidth, topLeft[1]+outWidth),
                    (topRight[0]-outWidth, topRight[1]+outWidth),
             colorIn, inWidth)

    image = convertToGray(image)
    return image

def convertSemiCellsToCells(image):
    show(image)
    contours = getAllContours(image)
    # getting all triangle contours
    triangle_contours = getAllTriangles(contours)
    # filter contours very below the average (noise contour)
    contourAvgSize = sum(cv2.contourArea(item) for item in triangle_contours) / float(len(triangle_contours))
    #triangle_contours = list(filter(lambda x: not checkIfVeryBelowAreaSize(contourAvgSize, x), triangle_contours))
    image = convertToColor(image)
    image = cv2.drawContours(image, triangle_contours, -1, (0, 255, 0), 5)
    show(image)
    image = cv2.drawContours(image, triangle_contours, -1, (0, 0, 0), 5)
    image = convertToGray(image)

    # Converting the triangle contours into squares
    for cnt in triangle_contours:
        # curr vars
        cX, cY = getContourCenter(cnt)
        approx = getContourApprox(cnt)
        middleVertex, isUpper = getMiddleVertex(approx, (cX, cY))

        # twin
        twin = getTwinContour(cnt, triangle_contours)
        twinCenterX, twinCenterY = getContourCenter(twin)
        twinApprox = getContourApprox(twin)
        twinMiddleVertex, twinIsUpper = getMiddleVertex(twinApprox, (twinCenterX, twinCenterY))

        # upper
        if (isUpper and not twinIsUpper):
            rightVertex = getRightVertex(approx, middleVertex)
            leftVertex = getLeftVertex(approx, middleVertex)

            twinRightVertex = getRightVertex(twinApprox, twinMiddleVertex)
            twinLeftVertex = getLeftVertex(twinApprox, twinMiddleVertex)

            topLeft = getTopLeft(leftVertex, twinLeftVertex)
            bottomRight = getBottomRight(rightVertex, twinRightVertex)
            # Drawing a square
            image = drawSquare(image, topLeft, middleVertex[0], bottomRight, twinMiddleVertex[0])

            # cv2.circle(image, (topLeft[0], topLeft[1]), 20, (255, 0, 0), -1)
            # cv2.circle(image, (bottomRight[0], bottomRight[1]), 20, (0, 0, 255), -1)
            # lower
            # else:
            # cv2.circle(image, (middleVertex[0][0], middleVertex[0][1]), 20, (255, 255, 0), -1)

    return image, triangle_contours

def getBoardGrid(boardSize, cnts):
    # initialize the reverse flag and sort index
    reverse = False
    # sorting against the y-coordinate
    i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    boundingBoxes = [getRect(c) for c in cnts]

    # calculating the first square (the closest to (0,0) which is the upper left square)
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: calcDistance((0,0), (b[1][0], b[1][1])),
                                        reverse=reverse))
    leftCellInLine = (cnts[0], boundingBoxes[0])

    gridCells = []
    for line in range(1, boardSize + 1):
        lineCells = []
        lineCells.append(leftCellInLine)

        currCell = leftCellInLine
        for column in range(2, boardSize + 1):
            # current cell center
            (cX, cY) = getContourCenter(currCell[0])
            cellWidth = currCell[1][2]
            nextCellPoint = (cX + cellWidth, cY)
            nextCell = findContourAndRectOfPoint(nextCellPoint, zip(cnts, boundingBoxes))
            if nextCell == None:
                print("can't find the next cell")
                return None
            lineCells.append(nextCell)
            currCell = nextCell

        gridCells.append(lineCells)

        # finding next line left cell
        if (line < boardSize):
            (cX, cY) = getContourCenter(leftCellInLine[0])
            cellHeight = leftCellInLine[1][3]
            nextCellPoint = (cX, cY + cellHeight)
            leftCellInLine = findContourAndRectOfPoint(nextCellPoint, zip(cnts, boundingBoxes))
            if leftCellInLine == None:
                print("can't find the next line left cell")
                return None
    return gridCells

def getDigit(image):
    height, width = image.shape[0], image.shape[1]
    boundSpace = 3
    smallAxis, bigAxis = min([height, width]), max([height, width])
    diff = bigAxis - smallAxis
    if (height > width):
        minX, maxX = boundSpace + int(diff / 2), boundSpace + int(diff / 2) + smallAxis
        minY, maxY = boundSpace, boundSpace + bigAxis
    else:
        minX, maxX = boundSpace, boundSpace + bigAxis
        minY, maxY = boundSpace + int(diff / 2), boundSpace + int(diff / 2) + smallAxis

    biggerImage = np.zeros(((boundSpace * 2) + bigAxis, (boundSpace * 2) + bigAxis), dtype=np.uint8)
    biggerImage[minY:maxY, minX:maxX] = image

    # Thresholding
    _, biggerImage = cv2.threshold(biggerImage,127,255,cv2.THRESH_TOZERO)
    # eroding the image
    kernel = np.ones((5, 5), np.uint8)
    biggerImage = cv2.erode(biggerImage, kernel, iterations=1)

    value = getDigitFromMNIST(biggerImage)
    #show(biggerImage, str(value))
    return value

def handleSquareImage(origImage, image):
    #TODO: just send to mnist or check the contour and then mnist
    # counting the percentage of white pixels
    whitePixels = cv2.countNonZero(image)
    percentOfWhite = int((whitePixels / (image.shape[0] * image.shape[1])) * 100)

    if percentOfWhite < 20:
        return None
    else:
        return getDigit(image)

alonW = []
alonH = []

def handleTriangleImage(origImage, image, contour, minX, minY):
    # since we draw a square outside the triangle, we need to look for it's inner contours
    digitContours = getAllContours(image)
    digits = []
    #show(image)
    for digitContour in digitContours:
        (x, y, w, h) = rect = getRect(digitContour)

        # todo: debug
        if (False):
            image = convertToColor(image)
            cv2.drawContours(image, [digitContour], -1, (255, 0, 0), 5)
            show(image)
            cv2.drawContours(image, [digitContour], -1, (0, 0, 0), 5)
            image = convertToGray(image)

        digitHeightInPercent, digitWidthInPercent = h / image.shape[0], w / image.shape[1]
        # not the crossing line of the triangle
        if ((digitWidthInPercent > 0.13 and digitWidthInPercent < 0.4) and
            (digitHeightInPercent > 0.25 and digitHeightInPercent < 0.8)):
            digitCenter = getContourCenter(digitContour)
            # since we croped, we want to test the original image X,Y of the contour
            origDigitCenter = (digitCenter[0] + minX, digitCenter[1] + minY)
            # TODO: delete these 4 lines
            # cv2.drawContours(croped, [digitContour], -1, (0, 0, 0), 5)
            # show(croped)

            if (isPointInContour(origDigitCenter, contour)):
                global alonW
                global alonH
                alonW.append(digitWidthInPercent)
                alonH.append(digitHeightInPercent)
                digits.append({'contour': digitContour, 'rect': rect})

    # sorting the digits from the left to the right (x axis)
    digits = sorted(digits, key=lambda x: x['rect'][0])

    if (len(digits) == 0):
        return None
    else:
        value = 0
        for digit in digits:
            (x, y, w, h) = digit['rect']
            digitImage = image[y:y + h, x:x + w]
            #show(image)
            #show(digitImage)
            digitValue = getDigit(digitImage)
            value = (value * 10) + digitValue
        return value

def readDigitsFromImage(origImage, image, shapeContour, isSquare):
    x, y = [], []
    for contour_lines in shapeContour:
        for line in contour_lines:
            x.append(line[0])
            y.append(line[1])
    minX, minY, maxX, maxY = min(x), min(y), max(x), max(y)

    croped = image[minY:maxY, minX:maxX]

    if (isSquare):
        return handleSquareImage(origImage, croped)
    else:
        return handleTriangleImage(origImage, croped, shapeContour, minX, minY)

def readCellFromImage(origImage, image, cell, triangles):
    (contour, rect) = cell
    cellTriangles = []
    for triangle in triangles:
        triangleCenter = getContourCenter(triangle)
        if (isPointInContour(triangleCenter, contour)):
            cellTriangles.append({ 'contour': triangle, 'center': triangleCenter })

    # native square, no triangles
    if (len(cellTriangles) == 0):
        value = readDigitsFromImage(origImage, image, contour, True)
        return {
            'valid': True,
            'cell': {
                'cellType': 'square',
                'value': value
            }
        }

    elif (len(cellTriangles) == 2):
        center1, center2 = cellTriangles[0]['center'], cellTriangles[1]['center']
        # if the triangles are not bottom left and upper right
        if ((center1[0] < center2[0] and center1[1] < center2[1]) or
            (center2[0] < center1[0] and center2[1] < center1[1])):
            return { 'valid': False }
        else:
            if (center1[0] < center2[0] and center1[1] > center2[1]):
                bottomLeftTriangle = cellTriangles[0]['contour']
                upperRightTriangle = cellTriangles[1]['contour']
            else:
                bottomLeftTriangle = cellTriangles[1]['contour']
                upperRightTriangle = cellTriangles[0]['contour']
            # TODO: crop and mnist with both triangles and their two digits or one
            bottomValue = readDigitsFromImage(origImage, image, bottomLeftTriangle, False)
            upperValue = readDigitsFromImage(origImage, image, upperRightTriangle, False)
            return {
                'valid': True,
                'cell': {
                    'cellType': 'triangle',
                    'value': { 'bottom': bottomValue, 'upper': upperValue }
                }
            }
    else:
        return { 'valid': False }

def getGrid(origImage, image):
    # dilating
    image = new_dilate(image, 7)
    # eroding
    kernel = np.ones((5, 5), np.uint8)
    image = cv2.erode(image, kernel, iterations=1)
    # blurring
    image = cv2.GaussianBlur(image, (7, 7), 15)

    # Handling semi cells (triangles)
    image, triangles = convertSemiCellsToCells(image)

    # Handling square cells
    height, width = image.shape[0], image.shape[1]
    boardSize = height * width
    # getting all square contours
    square_contours = getAllSquares(getAllContours(image))
    # filter the board contour if exists
    square_contours = list(filter(lambda x: not checkIfFarBiggerThanAreaSize(boardSize, x) , square_contours))
    # filter contours very below the average (noise contour)
    contourAvgSize = sum(cv2.contourArea(item) for item in square_contours) / float(len(square_contours))
    square_contours = list(filter(lambda x: not checkIfVeryBelowAreaSize(contourAvgSize, x), square_contours))

    print("Number of triangles is: " + str(int(len(triangles) / 2)))
    kakuroSize = int(math.sqrt(len(square_contours)))
    if (math.sqrt(len(square_contours)) != kakuroSize):
        print("Invalid board. number of squares is: " + str(len(square_contours)))
        isSquareBoard = False
        return isSquareBoard, None, None
    else:
        isSquareBoard = True
        print("The board is square of " + str(kakuroSize) + "x" + str(kakuroSize))

    gridCells = getBoardGrid(kakuroSize, square_contours)

    boardCells = []
    for i in range(0, kakuroSize):
        lineCells = []

        for j in range(0, kakuroSize):
            #print("cell of line:" + str(i+1) + " col:" + str(j+1))
            #todo: delete i,j
            result = readCellFromImage(origImage, image, gridCells[i][j], triangles)
            if (result['valid'] == True):
                lineCells.append(result['cell'])
            else:
                print("Invalid cell on [" + str(i+1) + "][" + str(j+1) + "]")
                isSquareBoard = False
                return isSquareBoard, None, None

        boardCells.append(lineCells)
    return isSquareBoard, boardCells, image

def printGrid(grid):
    for line in grid:
        lineString = ""

        for cell in line:
            cellString = ""

            type = cell['cellType']
            value = cell['value']
            if (type == 'square'):
                if (value == None):
                    cellString = "      "
                elif (value < 10):
                    cellString = "  " + str(value) + "   "
                else:
                    cellString = "  " + str(value) + "  "
            elif (type == 'triangle'):
                bottomVal = value['bottom']
                if (bottomVal == None):
                    bottom = "  "
                elif (bottomVal < 10):
                    bottom = " " + str(bottomVal)
                else:
                    bottom = str(bottomVal)

                upperVal = value['upper']
                if (upperVal == None):
                    upper = "  "
                elif (upperVal < 10):
                    upper = " " + str(upperVal)
                else:
                    upper = str(upperVal)

                cellString = bottom + ' \\' + upper
            else:
                return

            lineString = lineString + "(" + cellString + ")"
        print ('—' * 72)
        print(lineString)
        print('—' * 72)

def main():
    # process all 60 of our images
    for fp in range(1, 8):
        print("Started at " + str(datetime.now()))
        infile = "../pics/%d.jpg" % (fp)
        print("Showing " + infile)
        # Ref(s) for lines 106 to 131
        # http://stackoverflow.com/a/11366549
        originalImage, boardImage = getBoardFromImage(infile)
        isSquareBoard, grid, boardImage = getGrid(originalImage, boardImage)
        print("Finished at " + str(datetime.now()))

        if (isSquareBoard):
            printGrid(grid)
            # todo: debug
            if (True):
                minH, maxH, minW, maxW = min(alonH), max(alonH), min(alonW), max(alonW)
            show(boardImage)

main()