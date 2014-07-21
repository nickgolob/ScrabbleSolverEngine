"""

NEED:
- blank character handling
- extension word handling
- bridge, handling
"""

# GLOBALS: global values, boardLength, board, specials, dict

def setup():
    # Triple Words:
    for i in range(0, boardLength, 7):
        for j in range(0, boardLength, 7):
            if i != 7 and j != 7:
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
        content = []
        for line in f:
            content.append(line.strip())
    return content
def preprocess(wordList):
    content = {}
    for word in wordList:
        key = ''.join(sorted(word))
        if not key in content:
            content[key] = [word]
        else:
            content[key].append(word)
    return content
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
    global values, boardLength, board, specials, dict, tempFile
    values = {'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4,
          'g':3, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1,
          'm':2, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1,
          's':1, 't':1, 'u':1, 'v':5, 'w':2, 'x':8,
          'y':1, 'z':10}
    boardLength = 15
    board = [[None for i in range(boardLength)] for j in range(boardLength)]
    specials = [[None for i in range(boardLength)] for j in range(boardLength)]
    setup()
    dict = preprocess(wordList())
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

def powerSet(letters):
    content, stack = [], [''.join(sorted(letters))]
    while stack:
        current = stack.pop(0)
        content.append(current)
        for i in current:
            sub = current.replace(i, '', 1)
            if not sub in stack and not sub in content:
                stack.append(sub)
    return content

def score(word, coords, right):
    total, wordMod = 0, 1
    for i,char in enumerate(word):
        charMod = 1
        if right:
            var = specials[coords[0] + i][coords[1]]
        else:
            var = specials[coords[0]][coords[1] + i]
        if var:
            if var[0] == '+':
                charMod = int(var[1])
            elif var[0] == '*':
                wordMod *= int(var[1])
        total += values[char] * charMod
    return total * wordMod

def anchors(hand):
    """  :return: list (x, y, Right?) """
    content = []
    for i in range(boardLength):
        for j in range(boardLength):
            if board[i][j]:
                if (i == 0 and not board[i+1][j]) \
                    or (i == boardLength - 1 and not board[i-1][j]) \
                    or (i in range(1, boardLength - 1) and j in range(1, boardLength - 1) and
                        not board[i+1][j] and not board[i-1][j]):
                    content.append((i,j, True))
                if (j == 0 and not board[i][j+1]) \
                    or (j == boardLength - 1 and not board[i][j-1]) \
                    or (i in range(1, boardLength - 1) and j in range(1, boardLength - 1) and
                        not board[i][j+1] and not board[i][j-1]):
                    content.append((i,j, False))
    return content

def wordCheck(coords, right):
    global board, boardLength, dict
    word = []
    x, y = coords
    while x in range(boardLength) and y in range(boardLength) and board[x][y]:
        word.append(board[x][y])
        if right:
            x += 1
        else:
            y += 1
    x, y = coords
    word.pop(0)
    while x in range(boardLength) and y in range(boardLength) and board[x][y]:
        word.insert(0, board[x][y])
        if right:
            x -= 1
        else:
            y -= 1
    if ''.join(sorted(word)) in dict and \
        ''.join(word) in dict[''.join(sorted(word))]:
        return True
    else:
        return False

def boardCheck(word, coords, right):
    global board, boardLength, dict
    # coords check:
    if not (coords[0] in range(boardLength) and coords[1] in range(boardLength)):
        return False
    # conflict check:
    for i, j in enumerate(word):
        if right:
            if board[coords[0] + i][coords[1]] and \
                board[coords[0] + i][coords[1]] != j:
                return False
            if (coords[1] != 0 and board[coords[0] + i][coords[1] - 1]) or \
                (coords[1] != boardLength - 1 and board[coords[0] + i][coords[1] + 1]):
                out = False
                board[coords[0] + i][coords[1]], temp = j, board[coords[0] + i][coords[1]]
                if not wordCheck((coords[0] + i, coords[1]), False):
                    out = True
                board[coords[0] + i][coords[1]] = temp
                if out:
                    return False
        else:
            if board[coords[0]][coords[1] + i] and \
                board[coords[0]][coords[1] + i] != j:
                return False
            if (coords[0] != 0 and board[coords[0] - 1][coords[1] + i]) or \
                (coords[0] != boardLength - 1 and board[coords[0] + 1][coords[1] + i]):
                out = False
                board[coords[0] + i][coords[1]], temp = j, board[coords[0] + i][coords[1]]
                if not wordCheck((coords[0] + i, coords[1]), True):
                    out = True
                board[coords[0] + i][coords[1]] = temp
                if out:
                    return False

def candidates(freeLetters, anchorCoords, right): # anchor is '$'
    global board, dict
    content = []
    anchorChar = board[anchorCoords[0]][anchorCoords[1]]
    for word in powerSet(freeLetters + anchorChar):
        if word != anchorChar and word in dict:
            for i in dict[word]: # valid word
                for j, k in enumerate(i): # characters
                    if k == anchorChar:
                        if right:
                            tryCoords = (anchorCoords[0 - j], anchorCoords[1])
                        else:
                            tryCoords = (anchorCoords[0], anchorCoords[1 - j])
                        if boardCheck(i, tryCoords, right):
                            content.append((i, tryCoords, right))
    return content


def firstPlay(hand):
    global boardLength, dict
    bestScore, bestPlay = 0, None
    choices = powerSet(hand)
    for choice in choices:
        if choice in dict:
            for word in dict[choice]:
                for i in range(len(word)):
                    tryScore = score(word, (boardLength//2, boardLength//2 - i), False)
                    if tryScore > bestScore:
                        bestScore = tryScore
                        bestPlay = (word, (boardLength//2, boardLength//2 - i), False)
                    tryScore = score(word, (boardLength//2-i, boardLength//2), True)
                    if tryScore > bestScore:
                        bestScore = tryScore
                        bestPlay = (word, (boardLength//2 - i, boardLength//2), True)
    return bestScore, bestPlay
def best2(hand):
    if not board[boardLength // 2][boardLength // 2]: # first move
        return firstPlay(hand)

    bestScore, bestPlay = 0, None
    stack, power = anchors(hand), powerSet(hand)
    for anchor in stack:
        x, y = anchor
        # try right
        check = []
        if (x in range(1, boardLength - 1) and
            not board[x - 1][y] and not board[x + 1][y]) or \
            (x == 0 and not board[x + 1][y]) or \
            (x == boardLength - 1 and not board[x - 1][y]):
            check += candidates(hand, anchor, True)
        # try down
        if (y in range(1, boardLength - 1) and
            not board[x][y-1] and not board[x][y+1]) or \
            (y == 0 and not board[x][y+1]) or \
            (y == boardLength - 1 and not board[x][y-1]):
            check += candidates(hand, anchor, False)
        for word in check:
            tryscore = score(*word)
            if tryscore > bestScore:
                bestScore = tryscore
                bestPlay = word
    return bestScore, bestPlay

def best(hand):
    if not board[boardLength // 2][boardLength // 2]: # first move
        return firstPlay(hand)
    bestScore, bestPlay = 0, None
    allAnchors = anchors(hand)
    for x, y, justif in allAnchors:
        anchor = board[x][y]
        stack, memos = [], []

        for char in hand: # initialize
            # format (word-so-far, start-coord, front/back, remaining-hand)
            if justif:
                if x > 0:
                    stack.append( ([char, anchor], (x - 1, y), True, list(hand).remove(char)) )
                if x < boardLength - 1:
                    stack.append( ([anchor, char], (x, y), False, list(hand).remove(char)) )
            else:
                if y > 0:
                    stack.append( ([char, anchor], (x, y - 1), True, list(hand).remove(char)) )
                if y < boardLength - 1:
                    stack.append( ([anchor, char], (x, y), False, list(hand).remove(char)) )

        while stack:
            frame = stack.pop()
            word, (x, y), front, pool = frame
            print('{} {} {} {} {}'.format(word, x, y, front, pool))
            if justif:
                if front:
                    if (y == 0 and board[x][y+1]) \
                    or (y == boardLength - 1 and board[x][y-1]) \
                    or (y in range(1, boardLength - 1 )
                    and (board[x][y+1] or board[x][y-1])): # resolve adjacent conflicts (Right/front)
                        _y = y
                        while (_y > 0 and board[x][y-1]):
                            _y -= 1
                        valid = True
                        board[x][y], temp = word[0], board[x][y]
                        if wordCheck( (x, _y), False):
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
                        while (_y > 0 and board[x + L - 1][y - 1]):
                            _y -= 1
                        valid = True
                        board[x + L - 1][y], temp = word[0], board[x + L - 1][y]
                        if wordCheck( (x + L - 1, _y), False):
                            valid = False
                        board[x + L - 1][y] = temp
                        if not valid:
                            continue
            else:
                if front:
                    if (x == 0 and board[x + 1][y]) \
                    or (x == boardLength - 1 and board[x - 1][y]) \
                    or (x in range(1, boardLength - 1 )
                    and (board[x + 1][y] or board[x - 1][y])): # resolve adjacent conflicts (Down/front)
                        _x = x
                        while (_x > 0 and board[x - 1][y]):
                            _x -= 1
                        valid = True
                        board[x][y], temp = word[0], board[x][y]
                        if wordCheck( (_x, y), True):
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
                        while (_x > 0 and board[x - 1][y + L - 1]):
                            _x -= 1
                        valid = True
                        board[x][y + L - 1], temp = word[0], board[x][y + L - 1]
                        if wordCheck( (_x, y + L - 1), True):
                            valid = False
                        board[x][y + L - 1] = temp
                        if not valid:
                            continue

            key = ''.join(sorted(word))
            if key in dict and ''.join(word) in dict[key]: # check word
                tryScore = score(word, (x,y), justif)
                if tryScore > bestScore:
                    bestScore = tryScore
                    bestPlay = (word, (x,y), justif)

            for char in pool: # recurse:
                if justif:
                    if x > 0:
                        stack.append( ([char] + word, (x - 1, y), True, list(pool).remove(char)) )
                    if x < boardLength - 1:
                        stack.append( (word + [char], (x, y), False, list(pool).remove(char)) )
                else:
                    if y > 0:
                        stack.append( ([char] + word, (x, y - 1), True, list(pool).remove(char)) )
                    if y < boardLength - 1:
                        stack.append( (word + [char], (x, y), False, list(pool).remove(char)) )

    return bestPlay, bestScore

#print(best('rsliuhc'))



def main():
    while True:
        action = input('\nwhat up: ')
        if action == 'm': # get move
            hand = input('input hand: ')
            print('processing...')
            score, play = best(hand)
            print('{} starting at ({}, {}), {}'.format(
                play[0], play[1][0], play[1][1], 'rightward' if play[2] else 'downward'))
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
                    os.remove('')
                except OSError:
                    pass
        elif action == 'e': # exit
            saveBoard()
            return


if __name__ == '__main__':
    init()
    main()