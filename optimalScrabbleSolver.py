"""

NEED:
- blank character handling
- extension word handling
- bridge, handling
"""

# GLOBALS: global values, boardLength, board, specials, dict

ACROSS, DOWN = True, False


""" board processing / setup : """
def setupSpecials():
    # Triple Words:
    for i in range(0, boardLength, 7):
        for j in range(0, boardLength, 7):
            if not (i == 7 and j == 7):
                specials[i][j] = '*3'
    # Double Words:
    for i in range(1, 5):
        specials[i][i] = specials[i][boardLength - 1 - i] = \
        specials[boardLength - 1 - i][i] = \
        specials[boardLength - 1 - i][boardLength - 1 - i] = '*2'
    #Triple Letters:
    for i in range(1, boardLength, 4):
        for j in range(1, boardLength, 4):
            if not ((i == 1 and j == 1) or (i == 13 and j == 1) or
                (i == 1 and j == 13) or (i == 13 and j == 13)):
                specials[i][j] = '+3'
    #Double Letters:
    for i in range(3, boardLength, 8):
        specials[0][i] = specials[i][0] = \
        specials[boardLength - 1][i] = \
        specials[i][boardLength - 1] = '+2'
    specials[6][6] = specials[6][8] = \
    specials[8][6] = specials[8][8] = \
    specials[6][2] = specials[8][2] = \
    specials[2][6] = specials[2][8] = \
    specials[6][12] = specials[8][12] = \
    specials[12][6] = specials[12][8] = \
    specials[3][7] = specials[7][3] = \
    specials[7][11] = specials[11][7] = '+2'
def wordList():
    with open('wordsEn.txt', 'r') as f:
        content = {}
        for line in f:
            word = line.strip('\n')
            if word and len(word) < 16:
                content[word] = True
    return content
def substringProcess(dict):
    subs = {}
    for word in dict:
        n = len(word)
        for i in range(n):
            for j in range(i + 1, n + 1):
                if not word[i:j] in subs:
                    if word[i:j] in dict:
                        subs[word[i:j]] = (True, [], [])
                    else:
                        subs[word[i:j]] = (False, [], [])
                ref = subs[word[i:j]]
                if 0 < i and not word[i - 1] in ref[1]:
                    ref[1].append( word[i - 1] )
                if j < n and not word[j] in ref[2]:
                    ref[2].append( word[j] )
    return subs

def saveDictionary():
    import pickle
    data = open('subs.data', 'wb')
    pickle.dump(subs, data)
    data.close()
def loadDictionary():
    import pickle
    data = open('subs.data', 'rb')
    subs = pickle.load(data)
    data.close()
    return subs

def saveBoard():
    with open(tempFile, 'w') as f:
        p = lambda x : print(x, file=f, end='')
        for j in range(boardLength):
            for i in range(boardLength):
                if board[i][j]:
                    p(board[i][j])
                else:
                    p(' ')
            p('\n')
def loadBoard():
    import os.path
    if os.path.isfile(tempFile):
        content = [[j if j != ' ' else None for j in list(i.strip('\n'))]
                   for i in open(tempFile).readlines()]
        return list(map(list, zip(*content)))
    else:
        return [[None for i in range(boardLength)] for j in range(boardLength)]
def init():
    global values, boardLength, board, specials, dict, tempFile, subs
    values = {'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4,
          'g':3, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1,
          'm':2, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1,
          's':1, 't':1, 'u':1, 'v':5, 'w':2, 'x':8,
          'y':1, 'z':10}
    boardLength = 15
    board = [[None for i in range(boardLength)] for j in range(boardLength)]
    specials = [[None for i in range(boardLength)] for j in range(boardLength)]
    setupSpecials()
    dict = wordList()
    subs = loadDictionary()

    tempFile = 'scrabbleTemp.out'
    board = loadBoard() # load from memory
init()

def displaySpecials():
    for i in range(boardLength):
        for j in range(boardLength):
            if specials[i][j]:
                print(specials[i][j].rjust(3), end='')
            else:
                print('   ', end='')
        print('')
def displayBoard():
    p = lambda x : print(x, end='')
    p('*')
    for i in range(boardLength):
        p('-')
    p('*\n')
    for j in range(boardLength):
        p('|')
        for i in range(boardLength):
            if board[i][j]:
                p(board[i][j])
            else:
                p(' ')
        p('|\n')
    p('*')
    for i in range(boardLength):
        p('-')
    p('*\n')
def addWord(word, coords, right):
    global board
    x, y = coords
    for i, j in enumerate(word):
        if right:
            board[x + i][y] = j
        else:
            board[x][y + i] = j


""" solvers : """
def scoreWord(word, coords, across):
    runningScore, wordMod = 0, 1
    x, y = coords
    for char in word:
        if not board[x][y]:
            thisWordMod, thisCharMod = 1, 1
            if specials[x][y] and specials[x][y][0] == '+':
                thisCharMod = int(specials[x][y][1])
            elif specials[x][y]:
                thisWordMod = int(specials[x][y][1])
                wordMod *= thisWordMod
            runningScore += values[char] * thisCharMod
            # check adjacencies:
            if across:
                if (y > 0 and board[x][y - 1]) or \
                (y < boardLength  - 1 and board[x][y + 1]): # check vertical intersect
                    j = y
                    while (j > 0 and board[x][j - 1]):
                        j -= 1
                    intersectScore = 0
                    while (j < boardLength and (board[x][j] or j == y)):
                        if j == y:
                            intersectScore += values[char] * thisCharMod
                        else:
                            intersectScore += values[board[x][j]]
                        j += 1
                    runningScore += intersectScore * thisWordMod
            else:
                if (x > 0 and board[x - 1][y]) or \
                (x < boardLength - 1 and board[x + 1][y]): # check horizontal intersect
                    i = x
                    while (i > 0 and board[i - 1][y]):
                        i -= 1
                    intersectScore = 0
                    while (i < boardLength and (board[i][y] or i == x)):
                        if i == x:
                            intersectScore += values[char] * thisCharMod
                        else:
                            intersectScore += values[board[i][y]]
                        i += 1
                    runningScore += intersectScore * thisWordMod
        else:
            runningScore += values[char]
        if across:
            x += 1
        else:
            y += 1
    return runningScore * wordMod

def wordCheck(coords, right):
    word = []
    x, y = coords
    while x in range(boardLength) and y in range(boardLength) and board[x][y]:
        word.append(board[x][y])
        if right:
            x += 1
        else:
            y += 1
    key = ''.join(word)
    return key in subs and subs[key][0]

""" needs to be refactored: """

def anchors():
    n = boardLength
    if not board[n // 2][n // 2]: # first move
        return [([], n // 2, n // 2, True),
                ([], n // 2, n // 2, False)]
    content, memos = [], []
    for x in range(n):
        for y in range(n):
            if board[x][y]:

                word = list(board[x][y])
                _x = x
                while (_x < n - 1 and board[_x + 1][y]):
                    _x += 1
                    word.append(board[_x + 1][y])
                _x = x
                while (_x > 0 and board[_x - 1][y]):
                    _x -= 1
                    word.insert(0, board[_x - 1][y])

                if not (_x, y, True) in memos:
                    content.append((word, _x, y, True))
                    memos.append((_x, y, True))

                word = list(board[x][y])
                _y = y
                while (_y < n - 1 and board[_y + 1]):
                    _y += 1
                    word.append(board[x][_y + 1])
                _y = y
                while (_y > 0 and board[x][_y - 1]):
                    _y -= 1
                    word.insert(0, board[x][_y - 1])

                if not (_x, y, True) in memos:
                    content.append((word, _x, y, True))
                    memos.append((_x, y, True))

                TL, TR, BL, BR = \
                (x > 0 and y > 0 and not board[x - 1][y - 1],
                x < n - 1 and y > 0 and not board[x + 1][y - 1],
                x > 0 and y < n - 1 and not board[x - 1][y + 1],
                x < n - 1 and y < n - 1 and not board[x + 1][y + 1])

                if TL and TR and not (x, y - 1, True) in memos:
                    content.append((x, y - 1, True))
                    memos.append((x, y - 1, True))
                if TL and BL and not (x - 1, y, False) in memos:
                    content.append((x - 1, y, False))
                    memos.append((x - 1, y, False))
                if BL and BR and not (x, y + 1, True) in memos:
                    content.append((x, y + 1, True))
                    memos.append((x, y + 1, True))
                if BR and TR and not (x + 1, y, False) in memos:
                    content.append((x + 1, y, False))
                    memos.append((x + 1, y, False))
    return content

def best(hand):
    n = boardLength
    bestScore, bestPlay = 0, None
    allAnchors = anchors()
    for word, x, y, across in allAnchors:
        key = ''.join(word)
        if not key in subs:
            continue
        stack = []
        ref = subs[key]
        for char in hand:
            if char in ref[1] or char in ref[2]:
                remainder = list(hand)
                remainder.remove(char)
                L = len(word)
                if across:
                    if x > 0 and char in ref[1]:
                        stack.append( ([char] + word, (x - 1, y), True, remainder) )
                    if x + L - 1 < n - 1 and char in ref[2]:
                        stack.append( (word + [char], (x, y), False, remainder) )
                else:
                    if y > 0 and char in ref[1]:
                        stack.append( ([char] + word, (x, y - 1), True, remainder) )
                    if y + L - 1 < n - 1 and char in ref[2]:
                        stack.append( (word + [char], (x, y), False, remainder) )

        while stack:
            frame = stack.pop()
            word, (x, y), front, pool = frame

            if across:
                if front:
                    if (y == 0 and board[x][y+1]) \
                    or (y == boardLength - 1 and board[x][y-1]) \
                    or (y in range(1, boardLength - 1 )
                    and (board[x][y+1] or board[x][y-1])): # resolve adjacent conflicts (Right/front)
                        _y = y
                        while (_y > 0 and board[x][_y - 1]):
                            _y -= 1
                        valid = True
                        board[x][y], temp = word[0], board[x][y]
                        if not wordCheck( (x, _y), False):
                            valid = False
                        board[x][y] = temp
                        if not valid:
                            continue
                    while (x > 0 and board[x - 1][y]): # collect extra characters
                        x -= 1
                        word.insert(0, board[x][y])
                else:
                    L = len(word)
                    if (y == 0 and board[x + L - 1][y + 1]) \
                    or (y == boardLength - 1 and board[x + L - 1][y - 1]) \
                    or (y in range(1, boardLength - 1)
                    and (board[x + L - 1][y + 1] or board[x + L - 1][y - 1])): # resolve adjacent conflicts (Right/back)
                        _y = y
                        while (_y > 0 and board[x + L - 1][_y - 1]):
                            _y -= 1
                        valid = True
                        board[x + L - 1][y], temp = word[-1], board[x + L - 1][y]
                        if not wordCheck( (x + L - 1, _y), False):
                            valid = False
                        board[x + L - 1][y] = temp
                        if not valid:
                            continue
                    c = 0
                    while (x + L + c < boardLength and board[x + L + c][y]): # collect extra characters
                        word.append(board[x + L + c][y])
                        c += 1
            else:
                if front:
                    if (x == 0 and board[x + 1][y]) \
                    or (x == boardLength - 1 and board[x - 1][y]) \
                    or (x in range(1, boardLength - 1 )
                    and (board[x + 1][y] or board[x - 1][y])): # resolve adjacent conflicts (Down/front)
                        _x = x
                        while (_x > 0 and board[_x - 1][y]):
                            _x -= 1
                        valid = True
                        board[x][y], temp = word[0], board[x][y]
                        if not wordCheck( (_x, y), True):
                            valid = False
                        board[x][y] = temp
                        if not valid:
                            continue
                    while (y > 0 and board[x][y - 1]): # collect extra characters
                        y -= 1
                        word.insert(0, board[x][y])
                else:
                    L = len(word)
                    if (x == 0 and board[x + 1][y + L - 1]) \
                    or (x == boardLength - 1 and board[x - 1][y + L - 1]) \
                    or (x in range(1, boardLength - 1 )
                    and (board[x + 1][y + L - 1] or board[x - 1][y + L - 1])): # resolve adjacent conflicts (Down/front)
                        _x = x
                        while (_x > 0 and board[_x - 1][y + L - 1]):
                            _x -= 1
                        valid = True
                        board[x][y + L - 1], temp = word[-1], board[x][y + L - 1]
                        if not wordCheck( (_x, y + L - 1), True):
                            valid = False
                        board[x][y + L - 1] = temp
                        if not valid:
                            continue
                    c = 0
                    while (y + L + c < boardLength and board[x][y + L + c]): # collect extra characters
                        word.append(board[x][y + L + c])
                        c += 1

            ref = subs[''.join(word)]
            if ref[0]: # check word
                tryScore = scoreWord(word, (x,y), across)
                if tryScore > bestScore:
                    bestScore = tryScore
                    bestPlay = (word, (x,y), across)

            for char in pool: # recurse:
                if char in ref[1] or char in ref[2]:
                    remainder = list(pool)
                    remainder.remove(char)
                    L = len(word)
                    if across:
                        if x > 0 and char in ref[1]:
                            stack.append( ([char] + word, (x - 1, y), True, remainder) )
                        if x + L - 1 < n - 1 and char in ref[2]:
                            stack.append( (word + [char], (x, y), False, remainder) )
                    else:
                        if y > 0 and char in ref[1]:
                            stack.append( ([char] + word, (x, y - 1), True, remainder) )
                        if y + L - 1 < n - 1 and char in ref[2]:
                            stack.append( (word + [char], (x, y), False, remainder) )

    return list(bestPlay), bestScore

def main():
    global board
    while True:
        action = input('\nwhat up: ')
        if action == 'm': # get move
            hand = input('input hand: ')
            print('processing...')
            play, score = best(hand)
            print(play)
            print(score)
            print('{} starting at ({}, {}), {}, {} points'.format(
                ''.join(play[0]), play[1][0], play[1][1], 'rightward' if play[2] else 'downward', int(score)))
        elif action == 'u': # update board
            word = input('word: ')
            x = input('x coordinate: ')
            y = input('y coordinate: ')
            right = input('justification: ')
            addWord(word, (int(x), int(y)), True if right[0] == 'r' else False)
            saveBoard()
        elif action == 'd': # display board
            print('')
            displayBoard()
        elif action == 's': # display specials
            print('')
            displaySpecials()
        elif action == 'c': # clear board
            confirm = input('you sure?: ')
            if confirm[0] == 'y':
                board = [[None for i in range(boardLength)] for j in range(boardLength)]
                import os
                try:
                    os.remove(tempFile)
                except OSError:
                    pass
        elif action == 'e': # exit
            saveBoard()
            return

if __name__ == '__main__':
    init()
    main()