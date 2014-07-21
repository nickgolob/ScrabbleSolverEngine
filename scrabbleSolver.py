"""

NEED:
- blank character handling
- extension word handling
- bridge, handling
"""

# GLOBALS: global values, boardLength, board, specials, dict

def setup():
    global boardLength, specials
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
def init():
    global values, boardLength, board, specials, dict
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
    for i in range(boardLength):
        p('|')
        for j in range(boardLength):
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
    global board, boardLength, dict, values, specials
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
    global board, boardLength, dict
    content = []
    for i in range(boardLength):
        for j in range(boardLength):
            if board[i][j]:
                content.append((i,j))
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
def best(hand):
    global boardLength, dict
    if not board[boardLength // 2][boardLength // 2]: # first move
        return firstPlay(hand)

    bestScore, bestPlay = 0, None
    stack, power = anchors(hand), powerSet(hand)
    for anchor in stack:
        x, y = anchor
        # try right
        if (x in range(1, boardLength - 1) and
            not board[x - 1][y] and not board[x + 1][y]) or \
            (x == 0 and not board[x + 1][y]) or \
            (x == boardLength - 1 and not board[x - 1][y]):
            check = candidates(hand, anchor, True)
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

print(best('rsliuhc'))



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
        elif action == 'd': # display board
            print('')
            displayBoard()
        elif action == 's': # display specials
            print('')
            displaySpecials()

if __name__ == '__main__':
    init()
    main()






