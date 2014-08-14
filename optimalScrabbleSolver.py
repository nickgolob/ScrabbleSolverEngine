"""
Scrabble solver. Returns the best possible play (in terms
of number of points) given a board state, and a hand of tiles.

started 6/20/14 by Nick Golob

PYTHON VERSION: Cpython 3.4.1

ALGORITHM DESCRIPTION:
This algorithm systematically builds words one letter at a time.
It begins by establishing all possible starting positions on the
board that may be built off of (denoted as anchors). It then
begins building characters off of that location, keeping track
of whether or not the current string being constructed can be
a valid word (i.e is a substring of a valid word), if not,
the algo immediately quits processing the word and moves on. Also
if a conflict arises with an adjecently intersecting word, the
current string is dropped as well (a conflict arises when an
intersecting string is not a valid word, not just an invalid
substring). The algorithm memoizes states that it has tried,
to alleviate redundent compuations. It finishes by returning the
"m" highest scoring placements resulting in valid words. A heap
is used to track the "m" best plays.

the primary data structure used for tracking substrings is a
dictionary of all possible substrings occuring from the valid
list of words. The values of the dictionary is a tuple,
consisting of a boolean denoting whether the current substring
is a valid word, and two lists denoting characters that may be
appended or prepended irrespectively such that the resulting
word is still a valid substring (so we can quickly tell whether
a substring can ever become a valid word with a given pool of
available chars).

TODO:
optimizations, experiment with different memoization hashKeys,
integrate ACROSS/DOWN constants for readability.
"""

# GLOBALS: values, boardLength, board, specials, subs
ACROSS, DOWN = True, False

""" auxiliary data structures: """
class Heap():
    """ Heap that only supports 'pop' removal,
        can return a heap sorted generator of
        its payload, at the expense of its life. """
    def __init__(self, compare):
        self.heap, self.size = [], 0
        self.compare = compare
        """
        if min:
            self.compare = lambda x, y: x < y
        else:
            self.compare = lambda x, y: x > y
        """
    def insert(self, element):
        """ insert element into heap """
        self.size += 1
        self.heap.append(element)
        self._percolateUp()
    def pop(self):
        """ pop top element of heap """
        self.size -= 1
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        x = self.heap.pop()
        self._percolateDown()
        return x
    def heapSortGenerator(self):
        """ returns a generator yielding the elements of
            the heap sorted, in reverse order. The heap
            will be destroyed in the process. """
        while self.heap:
            yield self.pop()
    def _percolateUp(self):
        x = self.size - 1
        while x > 0:
            if self.compare(self.heap[x], self.heap[x // 2]):
                self.heap[x], self.heap[x // 2] = self.heap[x // 2], self.heap[x]
                x = x // 2
            else:
                break
    def _percolateDown(self):
        x = 0
        while 2*x < self.size:
            if 2*x + 1 < self.size and self.compare(self.heap[2*x + 1], self.heap[2*x]):
                y = 2*x + 1
            else:
                y = 2*x
            if self.compare(self.heap[y], self.heap[x]):
                self.heap[y], self.heap[x] = self.heap[x], self.heap[y]
                x = y
            else:
                break

""" setup / intermediate managers: """
class DictionaryManager():
    """ static class
        used to retrieve and write pre-processed dictionaries to disk
    """
    dataStore = 'subs.data'
    def init(self):
        pass
    def reprocess(self, dictionarySource):
        """ reprocesses the data on disk with a new base dictionary source """
        self._saveDictionary(self._substringProcess(self._wordList(dictionarySource)))
    def loadDictionary(self):
        """ loads preprocessed data from disk, returns dictionary object """
        import pickle
        data = open(self.dataStore, 'rb')
        subs = pickle.load(data)
        data.close()
        return subs
    def _wordList(self, source):
        with open(source, 'r') as f:
            content = {}
            for line in f:
                word = line.strip('\n')
                if word and len(word) in range(2, 16):
                    content[word] = True
        return content
    def _substringProcess(self, dict):
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
    def _saveDictionary(self, subDict):
        import pickle
        data = open(self.dataStore, 'wb')
        pickle.dump(subDict, data)
        data.close()

class BoardManager():
    """ used to setup/load game constants """
    boardLength = 15
    dataStore = 'board.data'
    def __init__(self):
        pass
    def getSpecials(self):
        specials = [[None for i in range(boardLength)] for j in range(boardLength)]
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
            specials[boardLength - 1][i]  = \
            specials[i][boardLength - 1]  = '+2'
        specials[6][6]  = specials[6][8]  = \
        specials[8][6]  = specials[8][8]  = \
        specials[6][2]  = specials[8][2]  = \
        specials[2][6]  = specials[2][8]  = \
        specials[6][12] = specials[8][12] = \
        specials[12][6] = specials[12][8] = \
        specials[3][7]  = specials[7][3]  = \
        specials[7][11] = specials[11][7] = '+2'

        return specials
    def saveBoard(self, board):
        with open(self.dataStore, 'w') as f:
            p = lambda x : print(x, file=f, end='')
            for j in range(boardLength):
                for i in range(boardLength):
                    if board[i][j]:
                        p(board[i][j])
                    else:
                        p(' ')
                p('\n')
    def loadBoard(self):
        import os.path
        if os.path.isfile(self.dataStore):
            content = [[j if j != ' ' else None for j in list(i.strip('\n'))]
                       for i in open(self.dataStore).readlines()]
            return list(map(list, zip(*content)))
        else:
            return [[None for i in range(boardLength)] for j in range(boardLength)]
    def display(self, object):
        n = self.boardLength
        p = lambda *x : print(*x, sep='', end='')
        p('    ', *[str(x).rjust(3) for x in range(n)] + ['\n'])
        p('   #', *[' --' for x in range(n)] + [' #\n'])
        for y in range(n):
            p(str(y).rjust(3), '|',
              *[object[x][y].rjust(3) if object[x][y] else '   ' for x in range(n)] + [' |\n'])
        p('   #', *[' --' for x in range(n)] + [' #\n'])
    def addWord(self, board, word, coords, right):
        x, y = coords
        k = 0
        blank = False
        for i, j in enumerate(word):
            if j == '*':
                blank = True
                k += 1
                continue
            elif right:
                if blank:
                    blank = False
                    board[x + i - k][y] = '*' + j
                else:
                    board[x + i - k][y] = j
            else:
                if blank:
                    blank = False
                    board[x][y + i - k] = '*' + j
                else:
                    board[x][y + i - k] = j
    def removeSection(self, board, coords, length, right):
        self.addWord(board, [None for i in range(length)], coords, right)
    def removeChar(self, board, coords):
        x, y = coords
        board[x][y] = None

def init():
    """ sets up global variables for program """
    global values, boardLength, board, specials, subs

    values = {'a':1, 'b':3, 'c':3, 'd':2, 'e':1, 'f':4,
          'g':2, 'h':4, 'i':1, 'j':8, 'k':5, 'l':1,
          'm':3, 'n':1, 'o':1, 'p':3, 'q':10, 'r':1,
          's':1, 't':1, 'u':1, 'v':5, 'w':4, 'x':8,
          'y':4, 'z':10, '*':0}
    boardLength = boardController.boardLength
    board = boardController.loadBoard()
    specials = boardController.getSpecials()
    subs = DictionaryManager().loadDictionary()

""" solver utilities: """
def scoreWord(word, coords, across):
    """ return scored generated by playing a word """
    runningScore, sideScores, wordMod = 0, 0, 1
    x, y = coords
    for char in map(lambda str : str[0], word):
        if not board[x][y]:
            thisWordMod, thisCharMod = 1, 1
            if specials[x][y] and specials[x][y][0] == '+':
                thisCharMod = int(specials[x][y][1])
            elif specials[x][y]:
                thisWordMod = int(specials[x][y][1])
                wordMod *= thisWordMod
            runningScore += values[char] * thisCharMod
            # get adjacent word completions:
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
                    sideScores += intersectScore * thisWordMod
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
                    sideScores += intersectScore * thisWordMod
        else:
            runningScore += values[char]
        if across:
            x += 1
        else:
            y += 1
    return sideScores + runningScore * wordMod

def wordCheck(coords, right):
    """ check if the specified string is a valid word """
    word = []
    x, y = coords
    while x in range(boardLength) and y in range(boardLength) and board[x][y]:
        word.append(board[x][y])
        if right:
            x += 1
        else:
            y += 1
    key = ''.join(word).replace('*', '')
    return key in subs and subs[key][0]

def anchors():
    """ get all possible starting locations for word building """
    n = boardLength
    if not board[n // 2][n // 2]: # first move
        return [([], (n // 2, n // 2), True),
                ([], (n // 2, n // 2), False)]
    content, memos = [], {}
    for x in range(n):
        for y in range(n):
            if board[x][y]:

                # horizonatal build
                word = list(board[x][y])
                _x = x
                while (_x < n - 1 and board[_x + 1][y]):
                    word.append(board[_x + 1][y])
                    _x += 1
                _x = x
                while (_x > 0 and board[_x - 1][y]):
                    word.insert(0, board[_x - 1][y])
                    _x -= 1
                    
                if not (_x, y, True) in memos:
                    content.append((word, (_x, y), ACROSS))
                    memos[(_x, y, True)] = None

                # vertical build
                word = list(board[x][y])
                _y = y
                while (_y < n - 1 and board[x][_y + 1]):
                    word.append(board[x][_y + 1])
                    _y += 1
                _y = y
                while (_y > 0 and board[x][_y - 1]):
                    word.insert(0, board[x][_y - 1])
                    _y -= 1
                    
                if not (x, _y, False) in memos:
                    content.append((word, (x, _y), DOWN))
                    memos[(x, _y, False)] = None

                # adjacent build
                TL, TR, BL, BR = \
                (x > 0 and y > 0 and not board[x - 1][y - 1],
                x < n - 1 and y > 0 and not board[x + 1][y - 1],
                x > 0 and y < n - 1 and not board[x - 1][y + 1],
                x < n - 1 and y < n - 1 and not board[x + 1][y + 1])

                if TL and TR and not board[x][y - 1] and not (x, y - 1, True) in memos:
                    content.append(([], (x, y - 1), ACROSS))
                    memos[(x, y - 1, True)] = None
                if TL and BL and not board[x - 1][y] and not (x - 1, y, False) in memos:
                    content.append(([], (x - 1, y), DOWN))
                    memos[(x - 1, y, False)] = None
                if BL and BR and not board[x][y + 1] and not (x, y + 1, True) in memos:
                    content.append(([], (x, y + 1), ACROSS))
                    memos[(x, y + 1, True)] = None
                if BR and TR and not board[x + 1][y] and not (x + 1, y, False) in memos:
                    content.append(([], (x + 1, y), DOWN))
                    memos[(x + 1, y, False)] = None
    return content

def adjecentCheck(char, coords, inverted):
    """ check if there are intersecting strings,
        and if so, if they are valid words
    """
    (x, y), n = coords, boardLength
    if not inverted:
        boardRef = lambda x, y : board[x][y]
        i, j = x, y
    else:
        boardRef = lambda y, x : board[x][y]
        j, i = x, y
    if (i == 0 and boardRef(i + 1, j)) \
    or (i == n - 1 and boardRef(i - 1, j)) \
    or (i in range(1, n - 1 )
    and (boardRef(i + 1, j) or boardRef(i - 1, j))):
        while (i > 0 and boardRef(i - 1, j)):
            i -= 1
        if inverted:
            i, j = j, i
        valid = True
        board[x][y] = char
        if not wordCheck((i, j), not inverted):
            valid = False
        board[x][y] = None
        return valid
    else:
        return True

""" main solver: """
def getBestPlays(hand, m):
    """
    :param hand: playable characters in hand
    :param m: number of best plays to be returned
    :returns: a heap containing top m best plays
    """
    n = boardLength
    bestplays = Heap(lambda x, y : x[0] < y[0]) # min-heap
    memos = {}

    # Get all possible start locations:
    allAnchors = anchors()
    for word, (x, y), across in allAnchors:

        # initialize stack:
        key = ''.join(word)
        stack = []

        # blank start location:
        if not key:
            for char in set(hand):
                remainder = list(hand)
                remainder.remove(char)
                if char == '*':
                    blanked = True
                    for _char in values:
                        stack.append( (['*' + _char], (x, y), True, remainder) )
                stack.append( ([char], (x, y), True, remainder) )

        # word isnt possible:
        elif not key in subs:
            continue

        # possible word:
        else:
            ref = subs[key]
            L = len(word)
            for char in set(hand):
                if char in ref[1] or char in ref[2]:
                    remainder = list(hand)
                    remainder.remove(char)
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
                elif char == '*':
                    remainder = list(hand)
                    remainder.remove('*')
                    for _char in values:
                        if across:
                            if x > 0 and _char in ref[1]:
                                stack.append( (['*' + _char] + word, (x - 1, y), True, list(remainder)) )
                            if x + L - 1 < n - 1 and _char in ref[2]:
                                stack.append( (word + ['*' + _char], (x, y), False, list(remainder)) )
                        else:
                            if y > 0 and _char in ref[1]:
                                stack.append( (['*' + _char] + word, (x, y - 1), True, list(remainder)) )
                            if y + L - 1 < n - 1 and _char in ref[2]:
                                stack.append( (word + ['*' + _char], (x, y), False, list(remainder)) )

        # build words
        while stack:
            frame = stack.pop()
            word, (x, y), front, pool = frame

            # memoization check:
            hashKey = (tuple(word), x, y, across) # fastest known hash key so far
            if hashKey in memos:
                continue
            memos[hashKey] = None

            L = len(word)

            # check adjacent word conflicts:
            if front:
                if across:
                    valid = adjecentCheck(word[0], (x, y), True)
                else:
                    valid = adjecentCheck(word[0], (x, y), False)
            else:
                if across:
                    valid = adjecentCheck(word[-1], (x + L - 1, y), True)
                else:
                    valid = adjecentCheck(word[-1], (x, y + L - 1), False)
            if not valid:
                continue

            # collect peripheral characters:
            if front or L == 1:
                # collect extra characters in front
                if across:
                    while (across and x > 0 and board[x - 1][y]):
                        x -= 1
                        word.insert(0, board[x][y])
                        L += 1
                else:
                    while (y > 0 and board[x][y - 1]):
                        y -= 1
                        word.insert(0, board[x][y])
                        L += 1
            if not front or L == 1:
                # collect extra characters off back
                if across:
                    while (x + L < n and board[x + L][y]):
                        word.append(board[x + L][y])
                        L += 1
                else:
                    while (y + L < n and board[x][y + L]):
                        word.append(board[x][y + L])
                        L += 1

            # check if word is still feasible:
            key = ''.join(word).replace('*', '')
            if not key in subs:
                continue
            ref = subs[key]

            # word check / scoring:
            if ref[0] and L > 1:
                tryScore = scoreWord(word, (x, y), across)
                if bestplays.size < m:
                    bestplays.insert((tryScore, word, (x, y), across))
                elif tryScore > bestplays.heap[0][0]:
                    bestplays.pop()
                    bestplays.insert((tryScore, word, (x, y), across))

            # recurse off of word so far:
            for char in set(pool): # remove duplicates
                if char in ref[1] or char in ref[2]:
                    remainder = list(pool)
                    remainder.remove(char)
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
                elif char == '*':
                    remainder = list(pool)
                    remainder.remove('*')
                    for _char in values:
                        if across:
                            if x > 0 and _char in ref[1]:
                                stack.append( (['*' + _char] + word, (x - 1, y), True, list(remainder)) )
                            if x + L - 1 < n - 1 and _char in ref[2]:
                                stack.append( (word + ['*' + _char], (x, y), False, list(remainder)) )
                        else:
                            if y > 0 and _char in ref[1]:
                                stack.append( (['*' + _char] + word, (x, y - 1), True, list(remainder)) )
                            if y + L - 1 < n - 1 and _char in ref[2]:
                                stack.append( (word + ['*' + _char], (x, y), False, list(remainder)) )

    return bestplays


""" USER I/O: """
def outputBestPlays(bestplays):
    """ displays contents of bestPlays, and the resulting
        adjacent words of a particular play """
    if bestplays.size == 0:
        print('no available plays now')
    for play in bestplays.heapSortGenerator():
        score, word, (x, y), across = play[0], play[1], play[2], play[3]
        adjacents = []
        for char in word:
            if not board[x][y]:
                if across:
                    if (y > 0 and board[x][y - 1]) or \
                    (y < boardLength  - 1 and board[x][y + 1]): # check vertical intersect
                        adjacents.append([char])
                        j = y
                        while (j > 0 and board[x][j - 1]):
                            j -= 1
                            adjacents[-1].insert(0, board[x][j])
                        j = y
                        while (j < boardLength - 1 and board[x][j + 1]):
                            j += 1
                            adjacents[-1].append(board[x][j])
                else:
                    if (x > 0 and board[x - 1][y]) or \
                    (x < boardLength - 1 and board[x + 1][y]): # check horizontal intersect
                        adjacents.append([char])
                        i = x
                        while (i > 0 and board[i - 1][y]):
                            i -= 1
                            adjacents[-1].insert(0, board[i][y])
                        i = x
                        while (i < boardLength - 1 and board[i + 1][y]):
                            i += 1
                            adjacents[-1].append(board[i][y])
            if across:
                x += 1
            else:
                y += 1
        (x, y) = play[2]
        print(' "{}" starting at ({}, {}), {}, for {} points'.format(
            ''.join(word), x, y, 'rightward' if across else 'downward', score))
        if adjacents:
            print('    RESULTING: {}'.format(', '.join( (''.join(i) for i in adjacents) ) ))

def main():
    from re import match
    from datetime import datetime
    global board
    while True:
        action = input('\nwhat up: ')
        try:
            if action == 'm': # get move
                hand = input('input hand: ').lower()
                assert match('^([a-z]|\*)+$', hand)
                m = int(input('# of plays: '))
                print('processing...')
                start = datetime.now()
                outputBestPlays(getBestPlays(list(hand), m))
                end = datetime.now()
                elapsed = end - start
                print(elapsed)
            elif action == 'u': # update board
                word = input('word: ').lower()
                assert match('^(([a-z])|(\*[a-z]))+$', word)
                x = int(input('x coordinate: '))
                y = int(input('y coordinate: '))
                justif = input('justification: ')
                assert justif == 'r' or justif == 'd'
                boardController.addWord(board, word, (x, y), True if justif == 'r' else False)
                boardController.saveBoard(board)
                print('updated successfully')
            elif action == 'r': # remove word
                x = int(input('x coordinate: '))
                y = int(input('y coordinate: '))
                L = int(input('length: '))
                justif = input('justification: ')
                assert justif == 'r' or justif == 'd'
                boardController.removeSection(board, (x, y), L, True if justif == 'r' else False)
                boardController.saveBoard(board)
                print('removed successfully')
            elif action == 'd': # display board
                boardController.display(board)
            elif action == 's': # display specials
                boardController.display(specials)
            elif action == 'c': # clear board
                confirm = input('you sure?: ')
                if confirm[0].lower() == 'y':
                    board = [[None for i in range(boardLength)] for j in range(boardLength)]
                    from os import remove
                    try:
                        remove(boardController.dataStore)
                    except OSError:
                        pass
            elif action == 'e': # exit
                boardController.saveBoard(board)
                return
            elif action == 'h':
                print('COMMANDS:\n'
                      ' m - get best moves\n u - input a word on board\n'
                      ' r - remove a section\n d - display current board\n'
                      ' s - display specials\n c - clear the board\n'
                      ' e - exit gracefully\n h - list of commands\n'
                      'CONSTANTS:\n'
                      ' r - rightward\n d - downward\n * - blank char prefix')
            else:
                raise SyntaxError
        except (AssertionError, ValueError, SyntaxError):
            print('invalid input. input "h" for help menu.')

if __name__ == '__main__':
    from os import path
    if not path.isfile(DictionaryManager.dataStore):
        DictionaryManager().reprocess('corncob_lowercase.txt')
    boardController = BoardManager()
    init()
    main()
